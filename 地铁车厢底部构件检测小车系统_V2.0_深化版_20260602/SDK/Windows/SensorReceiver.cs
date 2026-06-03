using System;
using System.Collections.Concurrent;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;

namespace RobotLinkSDK
{
    /// <summary>
    /// 传感器数据接收器（UDP）
    /// 
    /// 接收主控板推送的传感器数据：
    /// - IMU数据 50Hz
    /// - 测距数据 20Hz
    /// - 里程数据 50Hz
    /// - BMS数据 1Hz
    /// - 激光雷达数据 10Hz
    /// 
    /// 注意：UDP为不可靠通道，数据可能丢失，仅供显示参考
    /// </summary>
    public class SensorReceiver : IDisposable
    {
        #region 私有字段
        
        private UdpClient? _udpClient;
        private CancellationTokenSource? _cts;
        private Task? _recvTask;
        private readonly object _lock = new();
        
        // 最新数据缓存
        private IMUData? _latestIMU;
        private RangingData? _latestRanging;
        private OdometryData? _latestOdometry;
        private BMSData? _latestBMS;
        
        // 端口
        private readonly int _port;
        
        #endregion

        #region 事件定义
        
        /// <summary>IMU数据回调（50Hz）</summary>
        public event EventHandler<IMUData>? OnIMU;
        
        /// <summary>测距数据回调（20Hz）</summary>
        public event EventHandler<RangingData>? OnRanging;
        
        /// <summary>里程数据回调（50Hz）</summary>
        public event EventHandler<OdometryData>? OnOdometry;
        
        /// <summary>BMS数据回调（1Hz）</summary>
        public event EventHandler<BMSData>? OnBMS;
        
        /// <summary>激光雷达数据回调（10Hz）</summary>
        public event EventHandler<byte[]>? OnLidar;
        
        /// <summary>系统状态回调（UDP冗余，1Hz）</summary>
        public event EventHandler<SystemStatusData>? OnSystemStatus;
        
        #endregion

        #region 属性
        
        /// <summary>最新IMU数据</summary>
        public IMUData? LatestIMU
        {
            get { lock (_lock) return _latestIMU; }
            private set { lock (_lock) _latestIMU = value; }
        }
        
        /// <summary>最新测距数据</summary>
        public RangingData? LatestRanging
        {
            get { lock (_lock) return _latestRanging; }
            private set { lock (_lock) _latestRanging = value; }
        }
        
        /// <summary>最新里程数据</summary>
        public OdometryData? LatestOdometry
        {
            get { lock (_lock) return _latestOdometry; }
            private set { lock (_lock) _latestOdometry = value; }
        }
        
        /// <summary>最新BMS数据</summary>
        public BMSData? LatestBMS
        {
            get { lock (_lock) return _latestBMS; }
            private set { lock (_lock) _latestBMS = value; }
        }
        
        #endregion

        #region 构造与销毁
        
        /// <summary>
        /// 构造传感器接收器
        /// </summary>
        /// <param name="port">UDP监听端口，默认5002</param>
        public SensorReceiver(int port = 5002)
        {
            _port = port;
        }

        public void Dispose()
        {
            Stop();
            GC.SuppressFinalize(this);
        }

        ~SensorReceiver()
        {
            Dispose();
        }

        #endregion

        #region 启动/停止
        
        /// <summary>
        /// 启动接收
        /// </summary>
        public void Start()
        {
            lock (_lock)
            {
                if (_udpClient != null) return;
                
                _udpClient = new UdpClient(_port);
                _udpClient.Client.ReceiveTimeout = 5000;
                
                _cts = new CancellationTokenSource();
                _recvTask = Task.Run(() => ReceiveLoop(_cts.Token));
            }
            
            Console.WriteLine($"[SensorReceiver] 启动，监听UDP {_port}");
        }
        
        /// <summary>
        /// 停止接收
        /// </summary>
        public void Stop()
        {
            lock (_lock)
            {
                try { _cts?.Cancel(); } catch { }
                try { _udpClient?.Close(); } catch { }
                _udpClient = null;
                _cts = null;
                _recvTask = null;
            }
            
            Console.WriteLine("[SensorReceiver] 已停止");
        }

        #endregion

        #region 接收循环
        
        /// <summary>
        /// UDP接收循环
        /// </summary>
        private async Task ReceiveLoop(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested && _udpClient != null)
            {
                try
                {
                    var result = await _udpClient.ReceiveAsync(ct);
                    ProcessUDPPacket(result.Buffer, result.Buffer.Length);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    if (!ct.IsCancellationRequested)
                    {
                        Console.WriteLine($"[SensorReceiver] 接收异常: {ex.Message}");
                        await Task.Delay(100, ct);
                    }
                }
            }
        }
        
        /// <summary>
        /// 处理UDP数据包
        /// 
        /// 帧格式：
        /// Header(1B) + Timestamp(4B) + Sequence(2B) + SensorType(1B) + Payload(NB) + CRC32(4B)
        /// </summary>
        private void ProcessUDPPacket(byte[] data, int length)
        {
            if (length < 12) return; // 最小帧长度
            
            int offset = 0;
            
            // 帧头
            if (data[offset++] != 0xAA) return;
            
            // 时间戳
            uint timestamp = ReadUInt32(data, offset);
            offset += 4;
            
            // 序列号（跳过）
            offset += 2;
            
            // 传感器类型
            byte sensorType = data[offset++];
            
            // 载荷长度（总长度 - 12字节头 - 4字节CRC）
            int payloadLen = length - offset - 4;
            if (payloadLen < 0) return;
            
            // 解析传感器数据
            switch (sensorType)
            {
                case 0x01: ParseIMU(data, offset, payloadLen, timestamp); break;
                case 0x02: ParseRanging(data, offset, payloadLen, timestamp); break;
                case 0x03: ParseOdometry(data, offset, payloadLen, timestamp); break;
                case 0x04: ParseBMS(data, offset, payloadLen, timestamp); break;
                case 0x05: ParseLidar(data, offset, payloadLen); break;
                case 0x06: ParseSystemStatus(data, offset, payloadLen, timestamp); break;
            }
        }
        
        private void ParseIMU(byte[] data, int offset, int length, uint timestamp)
        {
            if (length < 36) return;
            
            var imu = new IMUData
            {
                Roll = ReadFloat(data, offset);
                Pitch = ReadFloat(data, offset + 4);
                Yaw = ReadFloat(data, offset + 8),
                Wx = ReadFloat(data, offset + 12),
                Wy = ReadFloat(data, offset + 16),
                Wz = ReadFloat(data, offset + 20),
                Ax = ReadFloat(data, offset + 24),
                Ay = ReadFloat(data, offset + 28),
                Az = ReadFloat(data, offset + 32),
                Timestamp = DateTimeOffset.FromUnixTimeMilliseconds(timestamp).DateTime
            };
            
            LatestIMU = imu;
            OnIMU?.Invoke(this, imu);
        }
        
        private void ParseRanging(byte[] data, int offset, int length, uint timestamp)
        {
            if (length < 8) return;
            
            var ranging = new RangingData
            {
                Front = ReadFloat(data, offset),
                Rear = ReadFloat(data, offset + 4),
                Timestamp = DateTimeOffset.FromUnixTimeMilliseconds(timestamp).DateTime
            };
            
            LatestRanging = ranging;
            OnRanging?.Invoke(this, ranging);
        }
        
        private void ParseOdometry(byte[] data, int offset, int length, uint timestamp)
        {
            if (length < 8) return;
            
            var odom = new OdometryData
            {
                Distance = ReadFloat(data, offset),
                Speed = ReadFloat(data, offset + 4),
                Timestamp = DateTimeOffset.FromUnixTimeMilliseconds(timestamp).DateTime
            };
            
            LatestOdometry = odom;
            OnOdometry?.Invoke(this, odom);
        }
        
        private void ParseBMS(byte[] data, int offset, int length, uint timestamp)
        {
            if (length < 14) return;
            
            var bms = new BMSData
            {
                Voltage = ReadFloat(data, offset),
                Current = ReadFloat(data, offset + 4),
                SOC = data[offset + 8],
                TempMax = (sbyte)data[offset + 9],
                TempMin = (sbyte)data[offset + 10],
                CycleCount = (ushort)((data[offset + 11] << 8) | data[offset + 12]),
                Status = data[offset + 13],
                Timestamp = DateTimeOffset.FromUnixTimeMilliseconds(timestamp).DateTime
            };
            
            LatestBMS = bms;
            OnBMS?.Invoke(this, bms);
        }
        
        private void ParseLidar(byte[] data, int offset, int length)
        {
            if (length < 4) return;
            
            uint pointCount = ReadUInt32(data, offset);
            byte[] pointCloud = new byte[length - 4];
            Array.Copy(data, offset + 4, pointCloud, 0, pointCloud.Length);
            
            OnLidar?.Invoke(this, pointCloud);
        }
        
        private void ParseSystemStatus(byte[] data, int offset, int length, uint timestamp)
        {
            if (length < 11) return;
            
            var status = new SystemStatusData
            {
                Mode = (RunMode)data[offset],
                ErrorCode = (ErrorCode)data[offset + 1],
                CpuTemp = (short)((data[offset + 2] << 8) | data[offset + 3]),
                MemoryUsage = (ushort)((data[offset + 4] << 8) | data[offset + 5]),
                BoardTemp = (short)((data[offset + 6] << 8) | data[offset + 7]),
                WifiRSSI = data[offset + 8],
                WifiQuality = data[offset + 9],
                UptimeSeconds = ReadUInt32(data, offset + 10),
                Timestamp = DateTimeOffset.FromUnixTimeMilliseconds(timestamp).DateTime
            };
            
            OnSystemStatus?.Invoke(this, status);
        }
        
        #endregion

        #region 辅助方法
        
        private static float ReadFloat(byte[] data, int offset)
        {
            uint bits = ReadUInt32(data, offset);
            return BitConverter.SingleToUInt32Bits(bits);
        }
        
        private static uint ReadUInt32(byte[] data, int offset)
        {
            return ((uint)data[offset] << 24) | ((uint)data[offset + 1] << 16) 
                   | ((uint)data[offset + 2] << 8) | data[offset + 3];
        }
        
        #endregion
    }
}
