using System;
using System.Collections.Concurrent;
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
        private int _maxRetries = 3;        // 最大重发次数
        private int _heartbeatIntervalMs = 2000;  // 心跳间隔
        
        // 连接状态
        private bool _isConnected = false;
        private int _consecutiveHeartbeatFailures = 0;
        private const int MAX_HEARTBEAT_FAILURES = 3;
        
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
        public bool IsConnected
        {
            get => _isConnected && _tcpClient?.Connected == true;
            private set
            {
                if (_isConnected != value)
                {
                    _isConnected = value;
                    OnConnectionChanged?.Invoke(this, value);
                }
            }
        }
        
        /// <summary>当前连接IP</summary>
        public string ConnectedIP => _ip;
        
        /// <summary>当前延迟（ms）</summary>
        public int Latency { get; private set; } = 0;
        
        #endregion

        #region 构造与销毁
        
        public RobotClient()
        {
            // 默认构造函数
        }

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

        ~RobotClient()
        {
            Dispose();
        }

        #endregion

        #region 连接管理
        
        /// <summary>
        /// 连接到机器人
        /// </summary>
        /// <param name="ip">机器人IP地址</param>
        /// <param name="port">控制端口，默认5000</param>
        public async Task<bool> ConnectAsync(string ip, int port = 5000)
        {
            if (_disposed) throw new ObjectDisposedException(nameof(RobotClient));
            
            _ip = ip;
            _port = port;
            
            try
            {
                // 创建TCP连接
                _tcpClient = new TcpClient();
                _tcpClient.NoDelay = true;  // 禁用Nagle，降低延迟
                _tcpClient.Client.SetSocketOption(SocketOptionLevel.TCP, SocketOptionName.NoDelay, true);
                
                var connectTask = _tcpClient.ConnectAsync(ip, port);
                var timeoutTask = Task.Delay(5000);
                
                if (await Task.WhenAny(connectTask, timeoutTask) == timeoutTask)
                {
                    throw new TimeoutException("连接超时（5秒）");
                }
                
                await connectTask; // 重新抛出异常
                
                _stream = _tcpClient.GetStream();
                _stream.ReadTimeout = 5000;
                _stream.WriteTimeout = 5000;
                
                // 启动接收线程
                _recvCts = new CancellationTokenSource();
                _recvTask = Task.Run(() => ReceiveLoop(_recvCts.Token));
                
                // 启动心跳
                _heartbeatCts = new CancellationTokenSource();
                _heartbeatTask = Task.Run(() => HeartbeatLoop(_heartbeatCts.Token));
                
                IsConnected = true;
                _consecutiveHeartbeatFailures = 0;
                
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

        /// <summary>
        /// 断开连接
        /// </summary>
        public void Disconnect()
        {
            CleanupConnection();
        }
        
        /// <summary>
        /// 内部清理连接
        /// </summary>
        private void CleanupConnection()
        {
            IsConnected = false;
            
            try { _heartbeatCts?.Cancel(); } catch { }
            try { _recvCts?.Cancel(); } catch { }
            try { _stream?.Close(); } catch { }
            try { _tcpClient?.Close(); } catch { }
            
            _stream = null;
            _tcpClient = null;
            _recvCts = null;
            _heartbeatCts = null;
            
            // 清理所有未完成的应答
            foreach (var kvp in _pendingAcks)
            {
                kvp.Value.TrySetCanceled();
            }
            _pendingAcks.Clear();
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
            
            var frame = new CommandFrame
            {
                Sequence = seq,
                CMD = cmd,
                SubCmd = subcmd,
                Payload = payload
            };
            
            // 创建应答等待
            var tcs = new TaskCompletionSource<AckFrame>();
            _pendingAcks[seq] = tcs;
            
            try
            {
                for (int retry = 0; retry < _maxRetries; retry++)
                {
                    try
                    {
                        // 发送帧
                        byte[] sendData = frame.Encode();
                        lock (_sendLock)
                        {
                            _stream.Write(sendData, 0, sendData.Length);
                        }
                        
                        // 等待应答（带超时）
                        using var cts = new CancellationTokenSource(_timeoutMs);
                        try
                        {
                            var ack = await tcs.Task.WaitAsync(cts.Token);
                            
                            // 检查NACK
                            if (ack.Status != AckFrame.ACK_OK)
                            {
                                throw new RobotNACKException(ack.Status, seq);
                            }
                            
                            return ack;
                        }
                        catch (TimeoutException)
                        {
                            if (retry == _maxRetries - 1)
                                throw new TimeoutException($"指令0x{cmd:X2}/{subcmd:X2}应答超时（序列{seq}）");
                            // 重试
                            Console.WriteLine($"[RobotClient] 指令超时，重试 {retry + 1}/{_maxRetries}");
                        }
                    }
                    catch (RobotNACKException)
                    {
                        throw;
                    }
                    catch (Exception ex)
                    {
                        if (retry == _maxRetries - 1)
                            throw new Exception($"发送失败: {ex.Message}");
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
        
        /// <summary>
        /// 接收循环（后台运行）
        /// </summary>
        private async Task ReceiveLoop(CancellationToken ct)
        {
            var buffer = new byte[4096];
            
            while (!ct.IsCancellationRequested && _stream != null)
            {
                try
                {
                    int bytesRead = await _stream.ReadAsync(buffer, 0, buffer.Length, ct);
                    
                    if (bytesRead == 0)
                    {
                        // 连接断开
                        Console.WriteLine("[RobotClient] 连接已关闭");
                        break;
                    }
                    
                    // 处理接收到的数据
                    ProcessReceivedData(buffer, bytesRead);
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
            
            // 连接断开处理
            IsConnected = false;
        }
        
        /// <summary>
        /// 处理接收到的数据
        /// </summary>
        private void ProcessReceivedData(byte[] buffer, int length)
        {
            // 简单实现：按固定格式解析（Header 2B + Seq 2B + Status 1B + CRC 2B = 7B最小帧）
            int offset = 0;
            
            while (offset + 7 <= length)
            {
                // 查找帧头0xAA55
                if (buffer[offset] == 0xAA && buffer[offset + 1] == 0x55)
                {
                    var ack = AckFrame.Decode(buffer, offset, length - offset);
                    if (ack != null)
                    {
                        // 尝试匹配等待的应答
                        if (_pendingAcks.TryRemove(ack.Sequence, out var tcs))
                        {
                            tcs.TrySetResult(ack);
                        }
                        
                        // 心跳应答处理
                        if (ack.Status == AckFrame.ACK_OK)
                        {
                            _consecutiveHeartbeatFailures = 0;
                        }
                        
                        offset += 7; // 最小应答帧长度
                        continue;
                    }
                }
                
                // 未找到完整帧，跳过1字节继续搜索
                offset++;
            }
        }

        #endregion

        #region 心跳循环
        
        /// <summary>
        /// 心跳循环（后台运行）
        /// </summary>
        private async Task HeartbeatLoop(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested)
            {
                try
                {
                    await Task.Delay(_heartbeatIntervalMs, ct);
                    
                    if (!IsConnected) break;
                    
                    try
                    {
                        await HeartbeatAsync();
                    }
                    catch (Exception ex)
                    {
                        _consecutiveHeartbeatFailures++;
                        Console.WriteLine($"[RobotClient] 心跳失败: {ex.Message} ({_consecutiveHeartbeatFailures}/{MAX_HEARTBEAT_FAILURES})");
                        
                        if (_consecutiveHeartbeatFailures >= MAX_HEARTBEAT_FAILURES)
                        {
                            Console.WriteLine("[RobotClient] 心跳丢失次数过多，触发重连");
                            await ReconnectAsync();
                        }
                    }
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[RobotClient] 心跳循环异常: {ex.Message}");
                }
            }
        }
        
        /// <summary>
        /// 重新连接
        /// </summary>
        private async Task ReconnectAsync()
        {
            Console.WriteLine("[RobotClient] 尝试重连...");
            CleanupConnection();
            await Task.Delay(1000);
            await ConnectAsync(_ip, _port);
        }

        #endregion

        #region 运动控制API
        
        /// <summary>
        /// 设置速度
        /// </summary>
        /// <param name="speed">速度 m/s，范围0.0~0.5</param>
        public async Task SetSpeedAsync(float speed)
        {
            speed = Math.Clamp(speed, 0f, 0.5f);
            byte[] payload = BitConverter.GetBytes(speed);
            await SendCommandAsync(CMD.Motion, SubCMD_Motion.SetSpeed, payload);
        }
        
        /// <summary>
        /// 前进
        /// </summary>
        public async Task MoveForwardAsync()
        {
            await SendCommandAsync(CMD.Motion, SubCMD_Motion.Forward);
        }
        
        /// <summary>
        /// 后退
        /// </summary>
        public async Task MoveBackwardAsync()
        {
            await SendCommandAsync(CMD.Motion, SubCMD_Motion.Backward);
        }
        
        /// <summary>
        /// 停止
        /// </summary>
        public async Task MoveStopAsync()
        {
            await SendCommandAsync(CMD.Motion, SubCMD_Motion.Stop);
        }
        
        /// <summary>
        /// 急停（最快响应）
        /// </summary>
        public async Task MoveEstopAsync()
        {
            await SendCommandAsync(CMD.Motion, SubCMD_Motion.EStop);
        }

        #endregion

        #region 云台控制API
        
        /// <summary>
        /// 云台角度控制
        /// </summary>
        /// <param name="camera">相机 0=前视, 1=后视</param>
        /// <param name="pan">水平角度 -180~+180度</param>
        /// <param name="tilt">垂直角度 -90~+90度</param>
        public async Task PTZControlAsync(byte camera, short pan, short tilt)
        {
            pan = (short)Math.Clamp(pan, (short)-180, (short)180);
            tilt = (short)Math.Clamp(tilt, (short)-90, (short)90);
            
            byte[] payload = new byte[5];
            payload[0] = camera;
            payload[1] = (byte)(pan >> 8);
            payload[2] = (byte)(pan & 0xFF);
            payload[3] = (byte)(tilt >> 8);
            payload[4] = (byte)(tilt & 0xFF);
            
            await SendCommandAsync(CMD.PTZ, SubCMD_PTZ.AngleControl, payload);
        }
        
        /// <summary>
        /// 云台复位
        /// </summary>
        /// <param name="camera">相机 0=前视, 1=后视</param>
        public async Task PTZResetAsync(byte camera)
        {
            await SendCommandAsync(CMD.PTZ, SubCMD_PTZ.Reset, new byte[] { camera });
        }
        
        /// <summary>
        /// 保存云台预设位
        /// </summary>
        public async Task PTZSavePresetAsync(byte camera, byte presetId)
        {
            await SendCommandAsync(CMD.PTZ, SubCMD_PTZ.SavePreset, new byte[] { camera, presetId });
        }
        
        /// <summary>
        /// 调用云台预设位
        /// </summary>
        public async Task PTZLoadPresetAsync(byte camera, byte presetId)
        {
            await SendCommandAsync(CMD.PTZ, SubCMD_PTZ.LoadPreset, new byte[] { camera, presetId });
        }

        #endregion

        #region 光源控制API
        
        /// <summary>
        /// 设置主光源亮度
        /// </summary>
        /// <param name="brightness">亮度 0~100</param>
        public async Task SetLightBrightnessAsync(byte brightness)
        {
            brightness = Math.Clamp(brightness, (byte)0, (byte)100);
            await SendCommandAsync(CMD.Light, SubCMD_Light.SetBrightness, new byte[] { brightness });
        }
        
        /// <summary>
        /// 前照明灯开关
        /// </summary>
        public async Task SetFrontLightAsync(bool onoff)
        {
            await SendCommandAsync(CMD.Light, SubCMD_Light.FrontLight, new byte[] { (byte)(onoff ? 1 : 0) });
        }
        
        /// <summary>
        /// 后照明灯开关
        /// </summary>
        public async Task SetRearLightAsync(bool onoff)
        {
            await SendCommandAsync(CMD.Light, SubCMD_Light.RearLight, new byte[] { (byte)(onoff ? 1 : 0) });
        }

        #endregion

        #region 采集控制API
        
        /// <summary>
        /// 开始采集
        /// </summary>
        /// <param name="mode">0=自动模式, 1=手动模式</param>
        public async Task StartCaptureAsync(byte mode = 0)
        {
            await SendCommandAsync(CMD.Capture, SubCMD_Capture.Start, new byte[] { mode });
        }
        
        /// <summary>
        /// 停止采集
        /// </summary>
        public async Task StopCaptureAsync()
        {
            await SendCommandAsync(CMD.Capture, SubCMD_Capture.Stop);
        }
        
        /// <summary>
        /// 强制保存数据
        /// </summary>
        public async Task ForceSaveDataAsync()
        {
            await SendCommandAsync(CMD.Capture, SubCMD_Capture.SaveData);
        }

        #endregion

        #region 系统控制API
        
        /// <summary>
        /// 请求系统自检
        /// </summary>
        public async Task RequestSelfTestAsync()
        {
            await SendCommandAsync(CMD.System, SubCMD_System.SelfTest);
        }
        
        /// <summary>
        /// 传感器标定
        /// </summary>
        /// <param name="type">0=里程计, 1=IMU</param>
        public async Task CalibrateSensorsAsync(byte type)
        {
            await SendCommandAsync(CMD.System, SubCMD_System.Calibrate, new byte[] { type });
        }
        
        /// <summary>
        /// 时间同步
        /// </summary>
        public async Task SyncTimeAsync()
        {
            long timestamp = DateTimeOffset.Now.ToUnixTimeMilliseconds();
            byte[] payload = BitConverter.GetBytes(timestamp);
            await SendCommandAsync(CMD.System, SubCMD_System.SyncTime, payload);
        }
        
        /// <summary>
        /// 请求系统状态（绕过1Hz周期）
        /// </summary>
        public async Task RequestSystemStatusAsync()
        {
            await SendCommandAsync(CMD.System, SubCMD_System.RequestStatus);
        }
        
        /// <summary>
        /// 进入休眠
        /// </summary>
        public async Task EnterSleepAsync()
        {
            await SendCommandAsync(CMD.System, SubCMD_System.EnterSleep);
        }
        
        /// <summary>
        /// 唤醒
        /// </summary>
        public async Task WakeUpAsync()
        {
            await SendCommandAsync(CMD.System, SubCMD_System.WakeUp);
        }
        
        /// <summary>
        /// 发送心跳
        /// </summary>
        public async Task HeartbeatAsync()
        {
            uint clientTime = (uint)Environment.TickCount;
            byte[] payload = BitConverter.GetBytes(clientTime);
            await SendCommandAsync(CMD.Heartbeat, SubCMD_Heartbeat.Beat, payload);
        }

        #endregion

        #region 同步方法包装
        
        /// <summary>连接（同步版本）</summary>
        public bool Connect(string ip, int port = 5000)
            => ConnectAsync(ip, port).GetAwaiter().GetResult();

        /// <summary>设置速度（同步版本）</summary>
        public void SetSpeed(float speed)
            => SetSpeedAsync(speed).GetAwaiter().GetResult();
        
        /// <summary>前进（同步版本）</summary>
        public void MoveForward()
            => MoveForwardAsync().GetAwaiter().GetResult();
        
        /// <summary>后退（同步版本）</summary>
        public void MoveBackward()
            => MoveBackwardAsync().GetAwaiter().GetResult();
        
        /// <summary>停止（同步版本）</summary>
        public void MoveStop()
            => MoveStopAsync().GetAwaiter().GetResult();
        
        /// <summary>急停（同步版本）</summary>
        public void MoveEstop()
            => MoveEstopAsync().GetAwaiter().GetResult();
        
        /// <summary>云台控制（同步版本）</summary>
        public void PTZControl(byte camera, short pan, short tilt)
            => PTZControlAsync(camera, pan, tilt).GetAwaiter().GetResult();
        
        /// <summary>云台复位（同步版本）</summary>
        public void PTZReset(byte camera)
            => PTZResetAsync(camera).GetAwaiter().GetResult();
        
        /// <summary>设置光源亮度（同步版本）</summary>
        public void SetLightBrightness(byte brightness)
            => SetLightBrightnessAsync(brightness).GetAwaiter().GetResult();
        
        /// <summary>前照明灯（同步版本）</summary>
        public void SetFrontLight(bool onoff)
            => SetFrontLightAsync(onoff).GetAwaiter().GetResult();
        
        /// <summary>后照明灯（同步版本）</summary>
        public void SetRearLight(bool onoff)
            => SetRearLightAsync(onoff).GetAwaiter().GetResult();
        
        /// <summary>开始采集（同步版本）</summary>
        public void StartCapture(byte mode = 0)
            => StartCaptureAsync(mode).GetAwaiter().GetResult();
        
        /// <summary>停止采集（同步版本）</summary>
        public void StopCapture()
            => StopCaptureAsync().GetAwaiter().GetResult();
        
        /// <summary>系统自检（同步版本）</summary>
        public void RequestSelfTest()
            => RequestSelfTestAsync().GetAwaiter().GetResult();
        
        /// <summary>传感器标定（同步版本）</summary>
        public void CalibrateSensors(byte type)
            => CalibrateSensorsAsync(type).GetAwaiter().GetResult();
        
        /// <summary>时间同步（同步版本）</summary>
        public void SyncTime()
            => SyncTimeAsync().GetAwaiter().GetResult();
        
        /// <summary>请求系统状态（同步版本）</summary>
        public void RequestSystemStatus()
            => RequestSystemStatusAsync().GetAwaiter().GetResult();
        
        /// <summary>进入休眠（同步版本）</summary>
        public void EnterSleep()
            => EnterSleepAsync().GetAwaiter().GetResult();
        
        /// <summary>唤醒（同步版本）</summary>
        public void WakeUp()
            => WakeUpAsync().GetAwaiter().GetResult();

        #endregion
    }

    /// <summary>
    /// 机器人NACK异常
    /// </summary>
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
