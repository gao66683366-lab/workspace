using System;
using System.IO;
using System.IO.Ports;
using System.Threading;
using System.Threading.Tasks;

namespace RobotLinkSDK
{
    /// <summary>
    /// 传感器接收器 - RS-485 Modbus RTU 轮询
    /// 
    /// 总线参数：9600-115200bps, 半双工, 主从模式
    /// 支持：IMU、测距传感器、BMS等Modbus从机设备
    /// </summary>
    public class SensorReceiver : IDisposable
    {
        #region 私有字段
        
        private SerialPort? _serialPort;
        private CancellationTokenSource? _cts;
        private Task? _pollTask;
        private readonly object _lock = new();
        private bool _isRunning = false;
        
        // Modbus从机地址
        private const byte ADDR_IMU = 0x01;
        private const byte ADDR_RANGING = 0x02;
        private const byte ADDR_BMS = 0x03;
        
        // 轮询间隔
        private int _pollIntervalMs = 50;  // 20Hz轮询频率
        
        // 最新数据
        private IMUData? _latestIMU;
        private RangingData? _latestRanging;
        private BMSData? _latestBMS;
        
        #endregion

        #region 事件定义
        
        public event EventHandler<IMUData>? OnIMU;
        public event EventHandler<RangingData>? OnRanging;
        public event EventHandler<BMSData>? OnBMS;
        
        #endregion

        #region 属性
        
        public IMUData? LatestIMU => _latestIMU;
        public RangingData? LatestRanging => _latestRanging;
        public BMSData? LatestBMS => _latestBMS;
        
        #endregion

        #region 构造与销毁
        
        public SensorReceiver(string portName = "COM1", int baudRate = 115200)
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

        ~SensorReceiver() => Dispose();

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
                _pollTask = Task.Run(() => PollLoop(_cts.Token));
            }
            
            Console.WriteLine($"[SensorReceiver] 启动，轮询间隔 {_pollIntervalMs}ms");
        }
        
        public void Stop()
        {
            lock (_lock)
            {
                _isRunning = false;
                try { _cts?.Cancel(); } catch { }
                try { _serialPort?.Close(); } catch { }
                _cts = null;
                _pollTask = null;
            }
            
            Console.WriteLine("[SensorReceiver] 已停止");
        }
        
        public void SetPollInterval(int ms)
        {
            _pollIntervalMs = Math.Clamp(ms, 10, 1000);
        }

        #endregion

        #region 轮询循环
        
        private async Task PollLoop(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested)
            {
                try
                {
                    // 轮询IMU
                    await PollIMUAsync();
                    
                    // 轮询问距
                    await PollRangingAsync();
                    
                    // 轮询BMS
                    await PollBMSAsync();
                    
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
                        Console.WriteLine($"[SensorReceiver] 轮询异常: {ex.Message}");
                        await Task.Delay(100, ct);
                    }
                }
            }
        }
        
        private async Task PollIMUAsync()
        {
            if (_serialPort == null || !_serialPort.IsOpen) return;
            
            try
            {
                // 读保持寄存器 (功能码0x03)
                // 地址 0x0000-0x0005: Roll, Pitch, Yaw, Wx, Wy, Wz (float各2寄存器)
                byte[] request = ModbusRTU.BuildReadHoldingRegisters(ADDR_IMU, 0x0000, 12);
                
                lock (_lock)
                {
                    _serialPort.Write(request, 0, request.Length);
                }
                
                await Task.Delay(5);  // 等待响应
                
                int bytesToRead = _serialPort.BytesToRead;
                if (bytesToRead >= 31)  // 响应: ADDR(1)+FUNC(1)+LEN(1)+12字节数据+CRC(2)
                {
                    byte[] response = new byte[bytesToRead];
                    _serialPort.Read(response, 0, bytesToRead);
                    
                    if (ModbusRTU.CheckCRC(response))
                    {
                        _latestIMU = new IMUData
                        {
                            Roll = ModbusRTU.ReadFloat(response, 3, 0),
                            Pitch = ModbusRTU.ReadFloat(response, 3, 4),
                            Yaw = ModbusRTU.ReadFloat(response, 3, 8),
                            Wx = ModbusRTU.ReadFloat(response, 3, 12),
                            Wy = ModbusRTU.ReadFloat(response, 3, 16),
                            Wz = ModbusRTU.ReadFloat(response, 3, 20),
                            Ax = 0, Ay = 0, Az = 0,
                            Timestamp = DateTime.Now
                        };
                        OnIMU?.Invoke(this, _latestIMU);
                    }
                }
            }
            catch { }
        }
        
        private async Task PollRangingAsync()
        {
            if (_serialPort == null || !_serialPort.IsOpen) return;
            
            try
            {
                byte[] request = ModbusRTU.BuildReadHoldingRegisters(ADDR_RANGING, 0x0000, 4);
                
                lock (_lock)
                {
                    _serialPort.Write(request, 0, request.Length);
                }
                
                await Task.Delay(5);
                
                int bytesToRead = _serialPort.BytesToRead;
                if (bytesToRead >= 15)
                {
                    byte[] response = new byte[bytesToRead];
                    _serialPort.Read(response, 0, bytesToRead);
                    
                    if (ModbusRTU.CheckCRC(response))
                    {
                        _latestRanging = new RangingData
                        {
                            Front = ModbusRTU.ReadFloat(response, 3, 0),
                            Rear = ModbusRTU.ReadFloat(response, 3, 4),
                            Timestamp = DateTime.Now
                        };
                        OnRanging?.Invoke(this, _latestRanging);
                    }
                }
            }
            catch { }
        }
        
        private async Task PollBMSAsync()
        {
            if (_serialPort == null || !_serialPort.IsOpen) return;
            
            try
            {
                byte[] request = ModbusRTU.BuildReadHoldingRegisters(ADDR_BMS, 0x0000, 10);
                
                lock (_lock)
                {
                    _serialPort.Write(request, 0, request.Length);
                }
                
                await Task.Delay(5);
                
                int bytesToRead = _serialPort.BytesToRead;
                if (bytesToRead >= 27)
                {
                    byte[] response = new byte[bytesToRead];
                    _serialPort.Read(response, 0, bytesToRead);
                    
                    if (ModbusRTU.CheckCRC(response))
                    {
                        _latestBMS = new BMSData
                        {
                            Voltage = ModbusRTU.ReadFloat(response, 3, 0),
                            Current = ModbusRTU.ReadFloat(response, 3, 4),
                            SOC = response[11],
                            TempMax = (sbyte)response[12],
                            TempMin = (sbyte)response[13],
                            CycleCount = (ushort)((response[14] << 8) | response[15]),
                            Status = response[16],
                            Timestamp = DateTime.Now
                        };
                        OnBMS?.Invoke(this, _latestBMS);
                    }
                }
            }
            catch { }
        }

        #endregion
    }
    
    /// <summary>
    /// Modbus RTU 工具类
    /// </summary>
    public static class ModbusRTU
    {
        /// <summary>读保持寄存器 (功能码0x03)</summary>
        public static byte[] BuildReadHoldingRegisters(byte addr, ushort startAddr, ushort count)
        {
            byte[] frame = new byte[8];
            frame[0] = addr;
            frame[1] = 0x03;  // 功能码：读保持寄存器
            frame[2] = (byte)(startAddr >> 8);
            frame[3] = (byte)(startAddr & 0xFF);
            frame[4] = (byte)(count >> 8);
            frame[5] = (byte)(count & 0xFF);
            
            ushort crc = CRC16Modbus.Calc(frame, 0, 6);
            frame[6] = (byte)(crc & 0xFF);
            frame[7] = (byte)(crc >> 8);
            
            return frame;
        }
        
        /// <summary>CRC校验</summary>
        public static bool CheckCRC(byte[] frame)
        {
            if (frame.Length < 3) return false;
            
            ushort recvCRC = (ushort)((frame[frame.Length - 1] << 8) | frame[frame.Length - 2]);
            ushort calcCRC = CRC16Modbus.Calc(frame, 0, frame.Length - 2);
            
            return recvCRC == calcCRC;
        }
        
        /// <summary>读取float (big-endian)</summary>
        public static float ReadFloat(byte[] frame, int dataOffset, int index)
        {
            int offset = dataOffset + index;
            if (offset + 4 > frame.Length) return 0;
            
            uint bits = (uint)(frame[offset] << 24) | ((uint)frame[offset + 1] << 16) 
                     | ((uint)frame[offset + 2] << 8) | frame[offset + 3];
            return BitConverter.ToSingle(BitConverter.GetBytes(bits), 0);
        }
    }
    
    /// <summary>
    /// CRC16-Modbus 校验
    /// </summary>
    public static class CRC16Modbus
    {
        private static readonly ushort[] Table = new ushort[256];
        
        static CRC16Modbus()
        {
            const ushort poly = 0x8005;
            for (int i = 0; i < 256; i++)
            {
                ushort value = 0;
                ushort temp = (ushort)(i << 8);
                for (int j = 0; j < 8; j++)
                {
                    if (((value ^ temp) & 0x8000) != 0)
                        value = (ushort)((value << 1) ^ poly);
                    else
                        value = (ushort)(value << 1);
                    temp = (ushort)(temp << 1);
                }
                Table[i] = value;
            }
        }
        
        public static ushort Calc(byte[] data, int offset, int length)
        {
            ushort crc = 0xFFFF;
            for (int i = offset; i < offset + length; i++)
            {
                crc = (ushort)((crc << 8) ^ Table[((crc >> 8) ^ data[i]) & 0xFF]);
            }
            return crc;
        }
    }
}
