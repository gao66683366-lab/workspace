using System;
using System.Collections.Concurrent;
using System.IO;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;

namespace RobotLinkSDK
{
    /// <summary>
    /// RobotClient - 机器人主控制客户端
    /// 
    /// 设计原则（针对WiFi无线链路）：
    /// 1. 所有指令必须等待应答，超时重发
    /// 2. 序列号递增，防止指令重复执行
    /// 3. 心跳保活，断线自动重连
    /// 4. 事件驱动，线程安全
    /// </summary>
    public class RobotClient : IDisposable
    {
        #region 私有字段
        
        private TcpClient? _tcpClient;
        private NetworkStream? _stream;
        private readonly object _sendLock = new();
        private readonly ConcurrentDictionary<ushort, TaskCompletionSource<AckFrame>> _pendingAcks = new();
        private CancellationTokenSource? _recvCts;
        private CancellationTokenSource? _heartbeatCts;
        private Task? _recvTask;
        private Task? _heartbeatTask;
        private ushort _nextSequence = 1;
        private bool _disposed = false;
        
        // 连接参数
        private string _ip = "";
        private int _port = 5000;
        private int _timeoutMs = 500;      // 指令应答超时
        private int _maxRetries = 3;      // 最大重发次数
        private int _heartbeatIntervalMs = 2000;  // 心跳间隔
        
        // 连接状态（volatile保证跨线程可见）
        private volatile bool _isConnected = false;
        private volatile int _consecutiveHeartbeatFailures = 0;
        private const int MAX_HEARTBEAT_FAILURES = 3;
        
        // 接收缓冲区
        private readonly byte[] _recvBuffer = new byte[8192];
        private int _recvOffset = 0;
        private int _recvLength = 0;
        
        #endregion

        #region 事件定义
        
        /// <summary>连接状态变化事件</summary>
        public event EventHandler<bool>? OnConnectionChanged;
        
        /// <summary>系统状态变化事件（1Hz推送）</summary>
        public event EventHandler<SystemStatusData>? OnSystemStatus;
        
        /// <summary>报警事件（异常时立即推送）</summary>
        public event EventHandler<AlarmEventArgs>? OnAlarm;
        
        /// <summary>自检结果事件</summary>
        public event EventHandler<SelfTestResult>? OnSelfTestResult;
        
        #endregion

        #region 属性
        
        /// <summary>是否已连接</summary>
        public bool IsConnected => _isConnected && _tcpClient?.Connected == true;
        
        /// <summary>当前连接IP</summary>
        public string ConnectedIP => _ip;
        
        /// <summary>当前延迟（ms）</summary>
        public int Latency { get; private set; } = 0;
        
        #endregion

        #region 构造与销毁
        
        public RobotClient() { }

        public RobotClient(string ip, int port = 5000)
        {
            _ip = ip;
            _port = port;
        }

        public void Dispose()
        {
            if (_disposed) return;
            _disposed = true;
            Disconnect();
            GC.SuppressFinalize(this);
        }

        ~RobotClient() => Dispose();

        #endregion

        #region 连接管理
        
        /// <summary>连接到机器人（异步）</summary>
        public async Task<bool> ConnectAsync(string ip, int port = 5000)
        {
            if (_disposed) throw new ObjectDisposedException(nameof(RobotClient));
            
            _ip = ip;
            _port = port;
            
            try
            {
                _tcpClient = new TcpClient
                {
                    NoDelay = true,
                    Client = { NoDelay = true }
                };
                
                using var cts = new CancellationTokenSource(5000);
                await _tcpClient.ConnectAsync(ip, port, cts.Token);
                
                _stream = _tcpClient.GetStream();
                _stream.ReadTimeout = 5000;
                _stream.WriteTimeout = 5000;
                
                _recvCts = new CancellationTokenSource();
                _recvTask = Task.Run(() => ReceiveLoop(_recvCts.Token), _recvCts.Token);
                
                _heartbeatCts = new CancellationTokenSource();
                _heartbeatTask = Task.Run(() => HeartbeatLoop(_heartbeatCts.Token), _heartbeatCts.Token);
                
                _isConnected = true;
                _consecutiveHeartbeatFailures = 0;
                OnConnectionChanged?.Invoke(this, true);
                
                // 同步获取一次系统状态
                await RequestSystemStatusAsync();
                
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[RobotClient] 连接失败: {ex.Message}");
                CleanupConnection();
                return false;
            }
        }

        /// <summary>断开连接</summary>
        public void Disconnect() => CleanupConnection();
        
        /// <summary>内部清理连接</summary>
        private void CleanupConnection()
        {
            _isConnected = false;
            
            try { _heartbeatCts?.Cancel(); } catch { }
            try { _recvCts?.Cancel(); } catch { }
            try { _stream?.Close(); } catch { }
            try { _tcpClient?.Close(); } catch { }
            
            _stream = null;
            _tcpClient = null;
            _recvCts = null;
            _heartbeatCts = null;
            _recvOffset = 0;
            _recvLength = 0;
            
            foreach (var kvp in _pendingAcks)
                kvp.Value.TrySetCanceled();
            _pendingAcks.Clear();
            
            OnConnectionChanged?.Invoke(this, false);
        }

        #endregion

        #region 核心发送逻辑
        
        /// <summary>
        /// 发送指令并等待应答（带超时重发）
        /// </summary>
        private async Task<AckFrame> SendCommandAsync(byte cmd, byte subcmd, byte[]? payload = null)
        {
            if (!IsConnected || _stream == null)
                throw new InvalidOperationException("未连接到机器人");
            
            ushort seq;
            lock (_sendLock)
            {
                seq = _nextSequence++;
            }
            
            // 构建帧（不包含CRC）
            int payloadLen = payload?.Length ?? 0;
            int frameLen = 2 + 2 + 2 + 1 + 1 + payloadLen; // Header+Seq+Len+CMD+SubCMD+Payload
            byte[] frameWithoutCRC = new byte[frameLen];
            int offset = 0;
            
            // Header: 0xAA55 (big-endian)
            frameWithoutCRC[offset++] = 0xAA;
            frameWithoutCRC[offset++] = 0x55;
            
            // Sequence: little-endian
            frameWithoutCRC[offset++] = (byte)(seq & 0xFF);
            frameWithoutCRC[offset++] = (byte)(seq >> 8);
            
            // Length: little-endian (SubCMD + CMD + Payload)
            ushort length = (ushort)(2 + payloadLen);
            frameWithoutCRC[offset++] = (byte)(length & 0xFF);
            frameWithoutCRC[offset++] = (byte)(length >> 8);
            
            // CMD
            frameWithoutCRC[offset++] = cmd;
            
            // SubCMD
            frameWithoutCRC[offset++] = subcmd;
            
            // Payload
            if (payload != null && payload.Length > 0)
                Buffer.BlockCopy(payload, 0, frameWithoutCRC, offset, payload.Length);
            
            // CRC16
            ushort crc = CRC16.Calc(frameWithoutCRC);
            byte[] sendData = new byte[frameLen + 2];
            Buffer.BlockCopy(frameWithoutCRC, 0, sendData, 0, frameLen);
            sendData[frameLen] = (byte)(crc & 0xFF);
            sendData[frameLen + 1] = (byte)(crc >> 8);
            
            // 创建应答等待
            var tcs = new TaskCompletionSource<AckFrame>(TaskCreationOptions.RunContinuationsAsynchronously);
            if (!_pendingAcks.TryAdd(seq, tcs))
                throw new Exception($"序列号冲突: {seq}");
            
            try
            {
                for (int retry = 0; retry < _maxRetries; retry++)
                {
                    try
                    {
                        lock (_sendLock)
                        {
                            _stream.Write(sendData, 0, sendData.Length);
                            _stream.Flush();
                        }
                        
                        using var cts = new CancellationTokenSource(_timeoutMs);
                        var ack = await tcs.Task.WaitAsync(cts.Token);
                        
                        if (ack.Status != AckFrame.ACK_OK)
                            throw new RobotNACKException(ack.Status, seq);
                        
                        return ack;
                    }
                    catch (TimeoutException)
                    {
                        if (retry == _maxRetries - 1)
                            throw new TimeoutException($"指令0x{cmd:X2}/{subcmd:X2}应答超时（序列{seq}）");
                        Console.WriteLine($"[RobotClient] 指令超时，重试 {retry + 1}/{_maxRetries}");
                    }
                }
                throw new TimeoutException("达到最大重试次数");
            }
            finally
            {
                _pendingAcks.TryRemove(seq, out _);
            }
        }

        #endregion

        #region 接收循环
        
        /// <summary>接收循环（后台运行）</summary>
        private async Task ReceiveLoop(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested && _stream != null)
            {
                try
                {
                    int available = _recvLength - _recvOffset;
                    if (available < 7)
                    {
                        if (_recvOffset > 0)
                        {
                            if (_recvLength > _recvOffset)
                                Buffer.BlockCopy(_recvBuffer, _recvOffset, _recvBuffer, 0, _recvLength - _recvOffset);
                            _recvLength -= _recvOffset;
                            _recvOffset = 0;
                        }
                        
                        if (_recvLength == _recvBuffer.Length)
                            _recvOffset = 0;
                    }
                    
                    int bytesRead = await _stream.ReadAsync(_recvBuffer, _recvLength, _recvBuffer.Length - _recvLength, ct);
                    
                    if (bytesRead == 0)
                    {
                        Console.WriteLine("[RobotClient] 连接已关闭");
                        break;
                    }
                    
                    _recvLength += bytesRead;
                    ProcessReceiveBuffer();
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    if (!ct.IsCancellationRequested)
                    {
                        Console.WriteLine($"[RobotClient] 接收异常: {ex.Message}");
                        await Task.Delay(100, ct);
                    }
                }
            }
            
            _isConnected = false;
            OnConnectionChanged?.Invoke(this, false);
        }
        
        /// <summary>处理接收缓冲区中的数据</summary>
        private void ProcessReceiveBuffer()
        {
            int offset = _recvOffset;
            
            while (offset + 7 <= _recvLength)
            {
                if (_recvBuffer[offset] == 0xAA && _recvBuffer[offset + 1] == 0x55)
                {
                    int frameLen = _recvLength - offset;
                    var ack = TryDecodeAck(_recvBuffer, offset, frameLen);
                    if (ack != null)
                    {
                        if (_pendingAcks.TryRemove(ack.Sequence, out var tcs))
                            tcs.TrySetResult(ack);
                        
                        offset += 7;
                        continue;
                    }
                }
                offset++;
            }
            
            _recvOffset = offset;
        }
        
        /// <summary>尝试解码应答帧（7字节最小帧：Header+Seq+Status+CRC）</summary>
        private AckFrame? TryDecodeAck(byte[] buffer, int offset, int available)
        {
            if (available < 7) return null;
            
            ushort seq = (ushort)((buffer[offset + 2]) | (buffer[offset + 3] << 8));
            byte status = buffer[offset + 4];
            ushort recvCRC = (ushort)((buffer[offset + 5]) | (buffer[offset + 6] << 8));
            ushort calcCRC = CRC16.Calc(buffer, offset, 5);
            
            if (recvCRC == calcCRC)
                return new AckFrame { Sequence = seq, Status = status };
            
            return null;
        }

        #endregion

        #region 心跳循环
        
        /// <summary>心跳循环（后台运行）</summary>
        private async Task HeartbeatLoop(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested)
            {
                try
                {
                    await Task.Delay(_heartbeatIntervalMs, ct);
                    
                    if (!IsConnected) break;
                    
                    await HeartbeatAsync();
                    // 心跳成功，重置失败计数
                    Interlocked.Exchange(ref _consecutiveHeartbeatFailures, 0);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    int failures = Interlocked.Increment(ref _consecutiveHeartbeatFailures);
                    Console.WriteLine($"[RobotClient] 心跳失败: {ex.Message} ({failures}/{MAX_HEARTBEAT_FAILURES})");
                    
                    if (failures >= MAX_HEARTBEAT_FAILURES)
                    {
                        Console.WriteLine("[RobotClient] 心跳丢失次数过多，触发重连");
                        _ = ReconnectAsync();
                    }
                }
            }
        }
        
        /// <summary>重新连接</summary>
        private async Task ReconnectAsync()
        {
            CleanupConnection();
            await Task.Delay(1000);
            await ConnectAsync(_ip, _port);
        }

        #endregion

        #region 运动控制API
        
        public async Task SetSpeedAsync(float speed)
        {
            speed = Math.Clamp(speed, 0f, 0.5f);
            byte[] payload = BitConverter.GetBytes(speed);
            await SendCommandAsync(CMD.Motion, SubCMD_Motion.SetSpeed, payload);
        }
        
        public async Task MoveForwardAsync() => await SendCommandAsync(CMD.Motion, SubCMD_Motion.Forward);
        public async Task MoveBackwardAsync() => await SendCommandAsync(CMD.Motion, SubCMD_Motion.Backward);
        public async Task MoveStopAsync() => await SendCommandAsync(CMD.Motion, SubCMD_Motion.Stop);
        public async Task MoveEstopAsync() => await SendCommandAsync(CMD.Motion, SubCMD_Motion.EStop);

        #endregion

        #region 云台控制API
        
        public async Task PTZControlAsync(byte camera, short pan, short tilt)
        {
            pan = (short)Math.Clamp(pan, (short)-180, (short)180);
            tilt = (short)Math.Clamp(tilt, (short)-90, (short)90);
            
            byte[] payload = new byte[5];
            payload[0] = camera;
            payload[1] = (byte)(pan & 0xFF);
            payload[2] = (byte)((pan >> 8) & 0xFF);
            payload[3] = (byte)(tilt & 0xFF);
            payload[4] = (byte)((tilt >> 8) & 0xFF);
            
            await SendCommandAsync(CMD.PTZ, SubCMD_PTZ.AngleControl, payload);
        }
        
        public async Task PTZResetAsync(byte camera) => await SendCommandAsync(CMD.PTZ, SubCMD_PTZ.Reset, new byte[] { camera });
        public async Task PTZSavePresetAsync(byte camera, byte presetId) => await SendCommandAsync(CMD.PTZ, SubCMD_PTZ.SavePreset, new byte[] { camera, presetId });
        public async Task PTZLoadPresetAsync(byte camera, byte presetId) => await SendCommandAsync(CMD.PTZ, SubCMD_PTZ.LoadPreset, new byte[] { camera, presetId });

        #endregion

        #region 光源控制API
        
        public async Task SetLightBrightnessAsync(byte brightness)
        {
            brightness = (byte)Math.Clamp(brightness, (byte)0, (byte)100);
            await SendCommandAsync(CMD.Light, SubCMD_Light.SetBrightness, new byte[] { brightness });
        }
        
        public async Task SetFrontLightAsync(bool onoff) => await SendCommandAsync(CMD.Light, SubCMD_Light.FrontLight, new byte[] { (byte)(onoff ? 1 : 0) });
        public async Task SetRearLightAsync(bool onoff) => await SendCommandAsync(CMD.Light, SubCMD_Light.RearLight, new byte[] { (byte)(onoff ? 1 : 0) });

        #endregion

        #region 采集控制API
        
        public async Task StartCaptureAsync(byte mode = 0) => await SendCommandAsync(CMD.Capture, SubCMD_Capture.Start, new byte[] { mode });
        public async Task StopCaptureAsync() => await SendCommandAsync(CMD.Capture, SubCMD_Capture.Stop);
        public async Task ForceSaveDataAsync() => await SendCommandAsync(CMD.Capture, SubCMD_Capture.SaveData);

        #endregion

        #region 系统控制API
        
        public async Task RequestSelfTestAsync() => await SendCommandAsync(CMD.System, SubCMD_System.SelfTest);
        
        public async Task CalibrateSensorsAsync(byte type) => await SendCommandAsync(CMD.System, SubCMD_System.Calibrate, new byte[] { type });
        
        public async Task SyncTimeAsync()
        {
            long timestamp = DateTimeOffset.Now.ToUnixTimeMilliseconds();
            byte[] payload = BitConverter.GetBytes(timestamp);
            await SendCommandAsync(CMD.System, SubCMD_System.SyncTime, payload);
        }
        
        public async Task RequestSystemStatusAsync() => await SendCommandAsync(CMD.System, SubCMD_System.RequestStatus);
        public async Task EnterSleepAsync() => await SendCommandAsync(CMD.System, SubCMD_System.EnterSleep);
        public async Task WakeUpAsync() => await SendCommandAsync(CMD.System, SubCMD_System.WakeUp);
        
        public async Task HeartbeatAsync()
        {
            uint clientTime = (uint)Environment.TickCount;
            byte[] payload = BitConverter.GetBytes(clientTime);
            await SendCommandAsync(CMD.Heartbeat, SubCMD_Heartbeat.Beat, payload);
        }

        #endregion

        #region 同步方法包装
        
        public bool Connect(string ip, int port = 5000) => ConnectAsync(ip, port).GetAwaiter().GetResult();
        public void SetSpeed(float speed) => SetSpeedAsync(speed).GetAwaiter().GetResult();
        public void MoveForward() => MoveForwardAsync().GetAwaiter().GetResult();
        public void MoveBackward() => MoveBackwardAsync().GetAwaiter().GetResult();
        public void MoveStop() => MoveStopAsync().GetAwaiter().GetResult();
        public void MoveEstop() => MoveEstopAsync().GetAwaiter().GetResult();
        public void PTZControl(byte camera, short pan, short tilt) => PTZControlAsync(camera, pan, tilt).GetAwaiter().GetResult();
        public void PTZReset(byte camera) => PTZResetAsync(camera).GetAwaiter().GetResult();
        public void PTZSavePreset(byte camera, byte presetId) => PTZSavePresetAsync(camera, presetId).GetAwaiter().GetResult();
        public void PTZLoadPreset(byte camera, byte presetId) => PTZLoadPresetAsync(camera, presetId).GetAwaiter().GetResult();
        public void SetLightBrightness(byte brightness) => SetLightBrightnessAsync(brightness).GetAwaiter().GetResult();
        public void SetFrontLight(bool onoff) => SetFrontLightAsync(onoff).GetAwaiter().GetResult();
        public void SetRearLight(bool onoff) => SetRearLightAsync(onoff).GetAwaiter().GetResult();
        public void StartCapture(byte mode = 0) => StartCaptureAsync(mode).GetAwaiter().GetResult();
        public void StopCapture() => StopCaptureAsync().GetAwaiter().GetResult();
        public void ForceSaveData() => ForceSaveDataAsync().GetAwaiter().GetResult();
        public void RequestSelfTest() => RequestSelfTestAsync().GetAwaiter().GetResult();
        public void CalibrateSensors(byte type) => CalibrateSensorsAsync(type).GetAwaiter().GetResult();
        public void SyncTime() => SyncTimeAsync().GetAwaiter().GetResult();
        public void RequestSystemStatus() => RequestSystemStatusAsync().GetAwaiter().GetResult();
        public void EnterSleep() => EnterSleepAsync().GetAwaiter().GetResult();
        public void WakeUp() => WakeUpAsync().GetAwaiter().GetResult();

        #endregion
    }

    /// <summary>机器人NACK异常</summary>
    public class RobotNACKException : Exception
    {
        public byte Status { get; }
        public ushort Sequence { get; }
        
        public RobotNACKException(byte status, ushort sequence) 
            : base($"收到NACK: Status=0x{status:X2}, Seq={sequence}")
        {
            Status = status;
            Sequence = sequence;
        }
    }
}