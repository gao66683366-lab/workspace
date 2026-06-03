using System;
using System.Collections.Concurrent;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;

namespace RobotLinkSDK
{
    /// <summary>
    /// 机器人控制客户端
    /// 
    /// 协议：STX(0x02) + CMD(1B) + LEN(2B, LE) + Payload(N) + CRC16(2B) + ETX(0x03)
    /// 端口：8001 (TCP命令), 8002 (TCP遥测)
    /// </summary>
    public class RobotClient : IDisposable
    {
        #region 私有字段
        
        private TcpClient? _tcpCommand;
        private TcpClient? _tcpTelemetry;
        private NetworkStream? _commandStream;
        private NetworkStream? _telemetryStream;
        private readonly object _sendLock = new();
        private readonly object _reconnectLock = new();
        private readonly ConcurrentDictionary<uint, TaskCompletionSource<AckFrame>> _pendingAcks = new();
        private CancellationTokenSource? _recvCts;
        private CancellationTokenSource? _heartbeatCts;
        private CancellationTokenSource? _telemetryCts;
        private Task? _recvTask;
        private Task? _heartbeatTask;
        private Task? _telemetryTask;
        private uint _nextSequence = 1;
        private bool _disposed = false;
        private bool _isReconnecting = false;
        
        private string _ip = "";
        private int _commandPort = 8001;
        private int _telemetryPort = 8002;
        private int _timeoutMs = 500;
        private int _maxRetries = 3;
        private int _heartbeatIntervalMs = 2000;
        
        private volatile bool _isConnected = false;
        private volatile int _consecutiveHeartbeatFailures = 0;
        private const int MAX_HEARTBEAT_FAILURES = 3;
        
        private readonly byte[] _recvBuffer = new byte[8192];
        private int _recvOffset = 0;
        private int _recvLength = 0;
        
        #endregion

        #region 事件定义
        
        public event EventHandler<bool>? OnConnectionChanged;
        public event EventHandler<SystemStatusData>? OnSystemStatus;
        public event EventHandler<AlarmEventArgs>? OnAlarm;
        public event EventHandler<SelfTestResult>? OnSelfTestResult;
        public event EventHandler<TelemetryData>? OnTelemetry;
        
        #endregion

        #region 属性
        
        public bool IsConnected => _isConnected && _tcpCommand?.Connected == true;
        public string ConnectedIP => _ip;
        public int Latency { get; private set; } = 0;
        
        #endregion

        #region 构造与销毁
        
        public RobotClient() { }
        public RobotClient(string ip, int commandPort = 8001, int telemetryPort = 8002) 
        { 
            _ip = ip; 
            _commandPort = commandPort; 
            _telemetryPort = telemetryPort; 
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
        
        public async Task<bool> ConnectAsync(string ip, int commandPort = 8001, int telemetryPort = 8002)
        {
            if (_disposed) throw new ObjectDisposedException(nameof(RobotClient));
            
            _ip = ip;
            _commandPort = commandPort;
            _telemetryPort = telemetryPort;
            
            try
            {
                // 连接命令通道
                _tcpCommand = new TcpClient { NoDelay = true };
                _tcpCommand.Client.NoDelay = true;
                using var cts = new CancellationTokenSource(5000);
                await _tcpCommand.ConnectAsync(ip, commandPort, cts.Token);
                _commandStream = _tcpCommand.GetStream();
                _commandStream.ReadTimeout = Timeout.Infinite;
                _commandStream.WriteTimeout = Timeout.Infinite;
                
                // 连接遥测通道
                _tcpTelemetry = new TcpClient { NoDelay = true };
                using var cts2 = new CancellationTokenSource(5000);
                await _tcpTelemetry.ConnectAsync(ip, telemetryPort, cts2.Token);
                _telemetryStream = _tcpTelemetry.GetStream();
                
                _recvCts = new CancellationTokenSource();
                _recvTask = Task.Run(() => ReceiveLoop(_recvCts.Token), _recvCts.Token);
                
                _telemetryCts = new CancellationTokenSource();
                _telemetryTask = Task.Run(() => TelemetryLoop(_telemetryCts.Token), _telemetryCts.Token);
                
                _heartbeatCts = new CancellationTokenSource();
                _heartbeatTask = Task.Run(() => HeartbeatLoop(_heartbeatCts.Token), _heartbeatCts.Token);
                
                _isConnected = true;
                _consecutiveHeartbeatFailures = 0;
                OnConnectionChanged?.Invoke(this, true);
                
                // 同步获取一次系统状态
                await RequestStatusAsync();
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[RobotClient] 连接失败: {ex.Message}");
                CleanupConnection();
                return false;
            }
        }

        public void Disconnect() => CleanupConnection();
        
        private void CleanupConnection()
        {
            _isConnected = false;
            
            try { _heartbeatCts?.Cancel(); } catch { }
            try { _recvCts?.Cancel(); } catch { }
            try { _telemetryCts?.Cancel(); } catch { }
            try { _commandStream?.Close(); } catch { }
            try { _telemetryStream?.Close(); } catch { }
            try { _tcpCommand?.Close(); } catch { }
            try { _tcpTelemetry?.Close(); } catch { }
            
            _commandStream = null;
            _telemetryStream = null;
            _tcpCommand = null;
            _tcpTelemetry = null;
            _recvCts = null;
            _heartbeatCts = null;
            _telemetryCts = null;
            _recvOffset = 0;
            _recvLength = 0;
            
            foreach (var kvp in _pendingAcks)
                kvp.Value.TrySetCanceled();
            _pendingAcks.Clear();
            
            OnConnectionChanged?.Invoke(this, false);
        }

        #endregion

        #region 核心发送逻辑
        
        private async Task<AckFrame> SendCommandAsync(byte cmd, byte[]? payload = null)
        {
            if (!IsConnected || _commandStream == null)
                throw new InvalidOperationException("未连接到机器人");
            
            int payloadLen = payload?.Length ?? 0;
            
            for (int retry = 0; retry < _maxRetries; retry++)
            {
                uint seq;
                byte[] frame;
                
                lock (_sendLock)
                {
                    seq = _nextSequence++;
                    frame = Protocol.BuildFrame(cmd, payload);
                }
                
                var tcs = new TaskCompletionSource<AckFrame>(TaskCreationOptions.RunContinuationsAsynchronously);
                if (!_pendingAcks.TryAdd(seq, tcs))
                    throw new Exception($"序列号冲突: {seq}");
                
                try
                {
                    lock (_sendLock)
                    {
                        _commandStream.Write(frame, 0, frame.Length);
                        _commandStream.Flush();
                    }
                    
                    using var cts = new CancellationTokenSource(_timeoutMs);
                    var ack = await tcs.Task.WaitAsync(cts.Token);
                    
                    if (ack.Status != Protocol.STATUS_OK)
                        throw new RobotNACKException(ack.Status, seq);
                    
                    return ack;
                }
                catch (TimeoutException)
                {
                    _pendingAcks.TryRemove(seq, out _);
                    if (retry == _maxRetries - 1)
                        throw new TimeoutException($"指令0x{cmd:X2}应答超时（序列{seq}）");
                    Console.WriteLine($"[RobotClient] 指令超时，重试 {retry + 1}/{_maxRetries}");
                }
                catch (RobotNACKException)
                {
                    _pendingAcks.TryRemove(seq, out _);
                    throw;
                }
                catch (Exception)
                {
                    _pendingAcks.TryRemove(seq, out _);
                    if (retry == _maxRetries - 1) throw;
                }
            }
            
            throw new TimeoutException("达到最大重试次数");
        }

        #endregion

        #region 接收循环
        
        private async Task ReceiveLoop(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested && _commandStream != null)
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
                        else if (_recvLength == _recvBuffer.Length)
                        {
                            Console.WriteLine("[RobotClient] 接收缓冲区溢出，丢弃数据");
                            _recvLength = 0;
                            _recvOffset = 0;
                        }
                    }
                    
                    int bytesRead = await _commandStream.ReadAsync(_recvBuffer, _recvLength, 
                        _recvBuffer.Length - _recvLength, ct);
                    
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
        
        private void ProcessReceiveBuffer()
        {
            int offset = _recvOffset;
            
            while (offset + 7 <= _recvLength)
            {
                if (_recvBuffer[offset] == Protocol.STX)
                {
                    var ack = TryDecodeAck(_recvBuffer, offset, _recvLength - offset);
                    if (ack != null)
                    {
                        if (_pendingAcks.TryRemove(ack.Sequence, out var tcs))
                            tcs.TrySetResult(ack);
                        
                        offset += ack.FrameLength;
                        continue;
                    }
                }
                offset++;
            }
            
            _recvOffset = offset;
        }
        
        private AckFrame? TryDecodeAck(byte[] buffer, int offset, int available)
        {
            // 最小帧: STX(1)+CMD(1)+STATUS(1)+LEN(2)+CRC16(2)+ETX(1) = 8字节
            if (available < 8) return null;
            
            byte cmd = buffer[offset + 1];
            byte status = buffer[offset + 2];
            ushort payloadLen = (ushort)(buffer[offset + 3] | (buffer[offset + 4] << 8));
            
            int frameLen = 1 + 1 + 1 + 2 + payloadLen + 2 + 1;
            if (offset + frameLen > _recvLength) return null;
            
            ushort recvCRC = (ushort)(buffer[offset + 1 + 1 + 1 + 2 + payloadLen] 
                                     | (buffer[offset + 1 + 1 + 1 + 2 + payloadLen + 1] << 8));
            ushort calcCRC = CRC16.Calc(buffer, offset, 1 + 1 + 1 + 2 + payloadLen);
            
            if (recvCRC != calcCRC) return null;
            
            if (buffer[offset + frameLen - 1] != Protocol.ETX) return null;
            
            uint seq = (uint)(offset & 0xFFFFFFFF);  // 简化的序列号（用于匹配）
            return new AckFrame { Sequence = seq, Status = status, FrameLength = frameLen };
        }
        
        #endregion

        #region 遥测循环
        
        private async Task TelemetryLoop(CancellationToken ct)
        {
            byte[] telemetryBuffer = new byte[8192];
            
            while (!ct.IsCancellationRequested && _telemetryStream != null)
            {
                try
                {
                    int bytesRead = await _telemetryStream.ReadAsync(telemetryBuffer, 0, telemetryBuffer.Length, ct);
                    if (bytesRead == 0) break;
                    
                    // 解析遥测数据
                    ProcessTelemetry(telemetryBuffer, bytesRead);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    if (!ct.IsCancellationRequested)
                    {
                        Console.WriteLine($"[RobotClient] 遥测异常: {ex.Message}");
                        await Task.Delay(100, ct);
                    }
                }
            }
        }
        
        private void ProcessTelemetry(byte[] data, int length)
        {
            var telemetry = Protocol.ParseFrame(data, length, out byte cmd, out byte[]? payload);
            if (telemetry == null) return;
            
            switch (cmd)
            {
                case Protocol.CMD_SYS_STATUS:
                    if (payload != null && payload.Length >= 11)
                        OnSystemStatus?.Invoke(this, new SystemStatusData(payload));
                    break;
                case Protocol.CMD_HEARTBEAT:
                    // 心跳响应处理
                    break;
            }
        }
        
        #endregion

        #region 心跳循环
        
        private async Task HeartbeatLoop(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested)
            {
                try
                {
                    await Task.Delay(_heartbeatIntervalMs, ct);
                    if (!IsConnected) break;
                    
                    await HeartbeatAsync();
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
                        _ = ReconnectAsync();
                }
            }
        }
        
        private async Task ReconnectAsync()
        {
            lock (_reconnectLock)
            {
                if (_isReconnecting) return;
                _isReconnecting = true;
            }
            
            try
            {
                CleanupConnection();
                await Task.Delay(1000);
                await ConnectAsync(_ip, _commandPort, _telemetryPort);
            }
            finally
            {
                lock (_reconnectLock) { _isReconnecting = false; }
            }
        }

        #endregion

        #region 运动控制API
        
        public async Task SetSpeedAsync(float speed)
        {
            speed = Math.Clamp(speed, 0f, 0.5f);
            await SendCommandAsync(Protocol.CMD_MOTION_SPEED, BitConverter.GetBytes(speed));
        }
        
        public async Task MoveAbsAsync(float distance) => await SendCommandAsync(Protocol.CMD_MOTION_ABS, BitConverter.GetBytes(distance));
        public async Task MoveRelAsync(float distance) => await SendCommandAsync(Protocol.CMD_MOTION_REL, BitConverter.GetBytes(distance));
        public async Task MoveStopAsync() => await SendCommandAsync(Protocol.CMD_MOTION_STOP);
        public async Task MoveHomeAsync() => await SendCommandAsync(Protocol.CMD_MOTION_HOME);

        #endregion

        #region 云台控制API
        
        public async Task PTZAngleAsync(byte camera, short pan, short tilt)
        {
            pan = (short)Math.Clamp(pan, (short)-180, (short)180);
            tilt = (short)Math.Clamp(tilt, (short)-90, (short)90);
            
            byte[] payload = new byte[5];
            payload[0] = camera;
            payload[1] = (byte)(pan & 0xFF);
            payload[2] = (byte)((pan >> 8) & 0xFF);
            payload[3] = (byte)(tilt & 0xFF);
            payload[4] = (byte)((tilt >> 8) & 0xFF);
            
            await SendCommandAsync(Protocol.CMD_PTZ_ANGLE, payload);
        }
        
        public async Task PTZPresetAsync(byte camera, byte presetId) => await SendCommandAsync(Protocol.CMD_PTZ_PRESET, new byte[] { camera, presetId });
        public async Task PTZResetAsync(byte camera) => await SendCommandAsync(Protocol.CMD_PTZ_RESET, new byte[] { camera });

        #endregion

        #region 相机控制API
        
        public async Task CameraZoomAsync(byte camera, ushort zoom) => await SendCommandAsync(Protocol.CMD_CAMERA_ZOOM, new byte[] { camera, (byte)(zoom & 0xFF), (byte)(zoom >> 8) });
        public async Task CameraFocusAsync(byte camera, ushort focus) => await SendCommandAsync(Protocol.CMD_CAMERA_FOCUS, new byte[] { camera, (byte)(focus & 0xFF), (byte)(focus >> 8) });
        public async Task CameraCaptureAsync(byte camera) => await SendCommandAsync(Protocol.CMD_CAMERA_CAPTURE, new byte[] { camera });

        #endregion

        #region 光源控制API
        
        public async Task SetBrightnessAsync(byte brightness)
        {
            brightness = (byte)Math.Clamp(brightness, (byte)0, (byte)100);
            await SendCommandAsync(Protocol.CMD_LIGHT_BRIGHTNESS, new byte[] { brightness });
        }
        
        public async Task SetLightSwitchAsync(byte lightId, bool onoff) => await SendCommandAsync(Protocol.CMD_LIGHT_SWITCH, new byte[] { lightId, (byte)(onoff ? 1 : 0) });

        #endregion

        #region IO控制API
        
        public async Task SetDOAsync(byte index, bool value) => await SendCommandAsync(Protocol.CMD_IO_DO, new byte[] { index, (byte)(value ? 1 : 0) });
        public async Task GetDIAsync() => await SendCommandAsync(Protocol.CMD_IO_DI);
        public async Task SetPWMAsync(byte channel, byte dutyCycle) => await SendCommandAsync(Protocol.CMD_IO_PWM, new byte[] { channel, dutyCycle });

        #endregion

        #region 系统控制API
        
        public async Task RequestStatusAsync() => await SendCommandAsync(Protocol.CMD_SYS_STATUS);
        public async Task SyncTimeAsync()
        {
            long timestamp = DateTimeOffset.Now.ToUnixTimeMilliseconds();
            await SendCommandAsync(Protocol.CMD_SYS_TIME, BitConverter.GetBytes(timestamp));
        }
        public async Task SendConfigAsync(byte[] config) => await SendCommandAsync(Protocol.CMD_SYS_CONFIG, config);
        
        public async Task HeartbeatAsync()
        {
            uint clientTime = (uint)Environment.TickCount;
            await SendCommandAsync(Protocol.CMD_HEARTBEAT, BitConverter.GetBytes(clientTime));
        }

        #endregion

        #region 升级API
        
        public async Task UpdateStartAsync(uint fileSize, uint crc32) => await SendCommandAsync(Protocol.CMD_UPDATE_START, BitConverter.GetBytes(fileSize).Concat(BitConverter.GetBytes(crc32)).ToArray());
        public async Task UpdateDataAsync(byte[] data) => await SendCommandAsync(Protocol.CMD_UPDATE_DATA, data);
        public async Task UpdateEndAsync() => await SendCommandAsync(Protocol.CMD_UPDATE_END);

        #endregion

        #region 同步方法包装
        
        public bool Connect(string ip, int commandPort = 8001, int telemetryPort = 8002) => 
            ConnectAsync(ip, commandPort, telemetryPort).GetAwaiter().GetResult();
        public void SetSpeed(float speed) => SetSpeedAsync(speed).GetAwaiter().GetResult();
        public void MoveAbs(float distance) => MoveAbsAsync(distance).GetAwaiter().GetResult();
        public void MoveRel(float distance) => MoveRelAsync(distance).GetAwaiter().GetResult();
        public void MoveStop() => MoveStopAsync().GetAwaiter().GetResult();
        public void MoveHome() => MoveHomeAsync().GetAwaiter().GetResult();
        public void PTZAngle(byte camera, short pan, short tilt) => PTZAngleAsync(camera, pan, tilt).GetAwaiter().GetResult();
        public void PTZPreset(byte camera, byte presetId) => PTZPresetAsync(camera, presetId).GetAwaiter().GetResult();
        public void PTZReset(byte camera) => PTZResetAsync(camera).GetAwaiter().GetResult();
        public void CameraZoom(byte camera, ushort zoom) => CameraZoomAsync(camera, zoom).GetAwaiter().GetResult();
        public void CameraFocus(byte camera, ushort focus) => CameraFocusAsync(camera, focus).GetAwaiter().GetResult();
        public void CameraCapture(byte camera) => CameraCaptureAsync(camera).GetAwaiter().GetResult();
        public void SetBrightness(byte brightness) => SetBrightnessAsync(brightness).GetAwaiter().GetResult();
        public void SetLightSwitch(byte lightId, bool onoff) => SetLightSwitchAsync(lightId, onoff).GetAwaiter().GetResult();
        public void SetDO(byte index, bool value) => SetDOAsync(index, value).GetAwaiter().GetResult();
        public void GetDI() => GetDIAsync().GetAwaiter().GetResult();
        public void SetPWM(byte channel, byte dutyCycle) => SetPWMAsync(channel, dutyCycle).GetAwaiter().GetResult();
        public void RequestStatus() => RequestStatusAsync().GetAwaiter().GetResult();
        public void SyncTime() => SyncTimeAsync().GetAwaiter().GetResult();
        public void Heartbeat() => HeartbeatAsync().GetAwaiter().GetResult();

        #endregion
    }

    public class RobotNACKException : Exception
    {
        public byte Status { get; }
        public uint Sequence { get; }
        
        public RobotNACKException(byte status, uint sequence) 
            : base($"收到NACK: Status=0x{status:X2}, Seq={sequence}")
        {
            Status = status;
            Sequence = sequence;
        }
    }
    
    public class AckFrame
    {
        public uint Sequence { get; set; }
        public byte Status { get; set; }
        public int FrameLength { get; set; }
    }
}
