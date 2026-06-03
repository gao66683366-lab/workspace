using System;
using System.IO.Ports;
using System.Threading;
using System.Threading.Tasks;

namespace RobotLinkSDK
{
    /// <summary>
    /// IO控制器 - 数字输入/输出 + PWM控制
    /// 
    /// DI: 8路数字输入
    /// DO: 8路数字输出
    /// PWM: 4路LED调光
    /// </summary>
    public class IOController : IDisposable
    {
        #region 私有字段
        
        private SerialPort? _serialPort;
        private CancellationTokenSource? _cts;
        private Task? _monitorTask;
        private readonly object _lock = new();
        private bool _isRunning = false;
        
        // 当前状态
        private byte _diStatus = 0;      // DI0-7状态
        private byte _doStatus = 0;      // DO0-7状态
        private byte[] _pwmDuty = { 0, 0, 0, 0 };  // PWM0-3占空比
        
        // 轮询间隔
        private int _pollIntervalMs = 100;  // 10Hz
        
        #endregion

        #region 事件定义
        
        /// <summary>数字输入状态变化事件</summary>
        public event EventHandler<DIChangedEventArgs>? OnDIChanged;
        
        #endregion

        #region 属性
        
        /// <summary>数字输入状态 (DI0-DI7)</summary>
        public byte DIStatus => _diStatus;
        
        /// <summary>数字输出状态 (DO0-DO7)</summary>
        public byte DOStatus => _doStatus;
        
        /// <summary>PWM占空比</summary>
        public byte[] PWMduty => _pwmDuty;
        
        /// <summary>是否已连接</summary>
        public bool IsConnected => _serialPort?.IsOpen == true;
        
        #endregion

        #region 构造与销毁
        
        public IOController(string portName = "COM2", int baudRate = 9600)
        {
            _serialPort = new SerialPort(portName, baudRate, Parity.None, 8, StopBits.One);
            _serialPort.ReadTimeout = 500;
            _serialPort.WriteTimeout = 500;
        }

        public void Dispose()
        {
            Stop();
            _serialPort?.Dispose();
            GC.SuppressFinalize(this);
        }

        ~IOController() => Dispose();

        #endregion

        #region 启动/停止
        
        public void Start()
        {
            lock (_lock)
            {
                if (_isRunning) return;
                
                if (_serialPort == null)
                    throw new InvalidOperationException("串口未初始化");
                
                if (!_serialPort.IsOpen)
                    _serialPort.Open();
                
                _cts = new CancellationTokenSource();
                _isRunning = true;
                _monitorTask = Task.Run(() => MonitorLoop(_cts.Token));
            }
            
            Console.WriteLine("[IOController] 启动，轮询间隔 {_pollIntervalMs}ms");
        }
        
        public void Stop()
        {
            lock (_lock)
            {
                _isRunning = false;
                try { _cts?.Cancel(); } catch { }
                try { _serialPort?.Close(); } catch { }
                _cts = null;
                _monitorTask = null;
            }
            
            Console.WriteLine("[IOController] 已停止");
        }
        
        public void SetPollInterval(int ms)
        {
            _pollIntervalMs = Math.Clamp(ms, 10, 1000);
        }

        #endregion

        #region 数字输出控制
        
        /// <summary>
        /// 设置单个数字输出
        /// </summary>
        public void SetDO(byte index, bool value)
        {
            if (index >= 8) throw new ArgumentOutOfRangeException(nameof(index));
            
            lock (_lock)
            {
                if (value)
                    _doStatus |= (byte)(1 << index);
                else
                    _doStatus &= (byte)~(1 << index);
                
                SendDOStatus();
            }
        }
        
        /// <summary>
        /// 批量设置数字输出
        /// </summary>
        public void SetDO(byte mask, byte values)
        {
            lock (_lock)
            {
                _doStatus = (byte)((_doStatus & ~mask) | (values & mask));
                SendDOStatus();
            }
        }
        
        /// <summary>
        /// 获取数字输入状态
        /// </summary>
        public byte GetDI()
        {
            lock (_lock)
            {
                return _diStatus;
            }
        }
        
        /// <summary>
        /// 读取指定数字输入
        /// </summary>
        public bool GetDI(byte index)
        {
            if (index >= 8) throw new ArgumentOutOfRangeException(nameof(index));
            return ((_diStatus >> index) & 1) == 1;
        }
        
        private void SendDOStatus()
        {
            if (_serialPort == null || !_serialPort.IsOpen) return;
            
            // 发送DO状态命令
            byte[] cmd = new byte[6];
            cmd[0] = 0x01;  // 地址
            cmd[1] = 0x05;  // 功能码：写单个线圈
            cmd[2] = 0x00;  // 寄存器地址高字节（DO控制）
            cmd[3] = 0x00;  // 寄存器地址低字节
            cmd[4] = _doStatus;  // 输出值
            cmd[5] = 0x00;  // 校验占位
            
            ushort crc = CRC16Modbus.Calc(cmd, 0, 5);
            cmd[5] = (byte)(crc & 0xFF);
            
            _serialPort.Write(cmd, 0, 6);
        }

        #endregion

        #region PWM控制
        
        /// <summary>
        /// 设置PWM占空比
        /// </summary>
        public void SetPWM(byte channel, byte dutyCycle)
        {
            if (channel >= 4) throw new ArgumentOutOfRangeException(nameof(channel));
            
            lock (_lock)
            {
                _pwmDuty[channel] = dutyCycle;
                SendPWMConfig();
            }
        }
        
        /// <summary>
        /// 设置所有PWM占空比
        /// </summary>
        public void SetPWM(byte duty0, byte duty1, byte duty2, byte duty3)
        {
            lock (_lock)
            {
                _pwmDuty[0] = duty0;
                _pwmDuty[1] = duty1;
                _pwmDuty[2] = duty2;
                _pwmDuty[3] = duty3;
                SendPWMConfig();
            }
        }
        
        private void SendPWMConfig()
        {
            if (_serialPort == null || !_serialPort.IsOpen) return;
            
            // 发送PWM配置命令
            byte[] cmd = new byte[9];
            cmd[0] = 0x01;
            cmd[1] = 0x10;  // 功能码：写多个寄存器
            cmd[2] = 0x00;  // 起始地址高字节（PWM配置）
            cmd[3] = 0x10;
            cmd[4] = 0x00;  // 寄存器数量高字节
            cmd[5] = 0x04;  // 4个寄存器
            cmd[6] = 0x08;  // 字节数
            cmd[7] = _pwmDuty[0];
            cmd[8] = _pwmDuty[1];
            cmd[9] = _pwmDuty[2];
            cmd[10] = _pwmDuty[3];
            
            // 实际需要调整，这里是占位
        }

        #endregion

        #region 监控循环
        
        private async Task MonitorLoop(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested)
            {
                try
                {
                    await PollDIAsync();
                    await Task.Delay(_pollIntervalMs, ct);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    if (!ct.IsCancellationRequested)
                    {
                        Console.WriteLine($"[IOController] 监控异常: {ex.Message}");
                        await Task.Delay(100, ct);
                    }
                }
            }
        }
        
        private async Task PollDIAsync()
        {
            if (_serialPort == null || !_serialPort.IsOpen) return;
            
            try
            {
                // 读保持寄存器 (功能码0x03) - DI状态
                byte[] request = new byte[8];
                request[0] = 0x01;  // 地址
                request[1] = 0x03;  // 功能码
                request[2] = 0x00;  // 起始地址
                request[3] = 0x00;
                request[4] = 0x00;  // 数量
                request[5] = 0x01;
                
                ushort crc = CRC16Modbus.Calc(request, 0, 6);
                request[6] = (byte)(crc & 0xFF);
                request[7] = (byte)(crc >> 8);
                
                lock (_lock)
                {
                    _serialPort.Write(request, 0, request.Length);
                }
                
                await Task.Delay(5);
                
                int bytesToRead = _serialPort.BytesToRead;
                if (bytesToRead >= 7)
                {
                    byte[] response = new byte[bytesToRead];
                    _serialPort.Read(response, 0, bytesToRead);
                    
                    if (ModbusRTU.CheckCRC(response))
                    {
                        byte newDI = response[3];
                        if (newDI != _diStatus)
                        {
                            byte changed = (byte)(newDI ^ _diStatus);
                            _diStatus = newDI;
                            OnDIChanged?.Invoke(this, new DIChangedEventArgs(changed, newDI));
                        }
                    }
                }
            }
            catch { }
        }

        #endregion
    }
    
    public class DIChangedEventArgs : EventArgs
    {
        public byte ChangedBits { get; }
        public byte DIStatus { get; }
        
        public DIChangedEventArgs(byte changed, byte status)
        {
            ChangedBits = changed;
            DIStatus = status;
        }
    }
}
