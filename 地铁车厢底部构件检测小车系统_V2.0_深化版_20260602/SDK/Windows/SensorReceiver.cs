using System;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;

namespace RobotLinkSDK
{
    public class SensorReceiver : IDisposable
    {
        #region 私有字段
        
        private UdpClient? _udpClient;
        private CancellationTokenSource? _cts;
        private Task? _recvTask;
        private readonly object _lock = new();
        private bool _isRunning = false;
        
        private IMUData? _latestIMU;
        private RangingData? _latestRanging;
        private OdometryData? _latestOdometry;
        private BMSData? _latestBMS;
        
        private readonly int _port;
        
        #endregion

        #region 事件定义
        
        public event EventHandler<IMUData>? OnIMU;
        public event EventHandler<RangingData>? OnRanging;
        public event EventHandler<OdometryData>? OnOdometry;
        public event EventHandler<BMSData>? OnBMS;
        public event EventHandler<byte[]>? OnLidar;
        public event EventHandler<SystemStatusData>? OnSystemStatus;
        
        #endregion

        #region 属性
        
        public IMUData? LatestIMU { get; private set; }
        public RangingData? LatestRanging { get; private set; }
        public OdometryData? LatestOdometry { get; private set; }
        public BMSData? LatestBMS { get; private set; }
        
        #endregion

        #region 构造与销毁
        
        public SensorReceiver(int port = 5002) { _port = port; }

        public void Dispose()
        {
            Stop();
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
                
                if (_udpClient != null)
                    Stop();  // 先停止旧的
                
                _udpClient = new UdpClient(_port);
                _udpClient.Client.ReceiveTimeout = 5000;
                _cts = new CancellationTokenSource();
                _isRunning = true;
                _recvTask = Task.Run(() => ReceiveLoop(_cts.Token));
            }
            
            Console.WriteLine($"[SensorReceiver] 启动，监听UDP {_port}");
        }
        
        public void Stop()
        {
            lock (_lock)
            {
                _isRunning = false;
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
        
        private void ProcessUDPPacket(byte[] data, int length)
        {
            // 最小帧: Header(1)+TS(4)+Seq(2)+Type(1)+CRC(4) = 12字节
            if (length < 12) return;
            
            // CRC32校验（最后4字节）
            uint recvCRC = ReadUInt32(data, length - 4);
            uint calcCRC = CRC32.Calc(data, 0, length - 4);
            if (recvCRC != calcCRC)
            {
                Console.WriteLine($"[SensorReceiver] CRC校验失败，丢弃数据包");
                return;
            }
            
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
            
            LatestIMU = new IMUData
            {
                Roll = ReadFloat(data, offset),
                Pitch = ReadFloat(data, offset + 4),
                Yaw = ReadFloat(data, offset + 8),
                Wx = ReadFloat(data, offset + 12),
                Wy = ReadFloat(data, offset + 16),
                Wz = ReadFloat(data, offset + 20),
                Ax = ReadFloat(data, offset + 24),
                Ay = ReadFloat(data, offset + 28),
                Az = ReadFloat(data, offset + 32),
                Timestamp = DateTimeOffset.FromUnixTimeMilliseconds(timestamp).DateTime
            };
            OnIMU?.Invoke(this, LatestIMU);
        }
        
        private void ParseRanging(byte[] data, int offset, int length, uint timestamp)
        {
            if (length < 8) return;
            
            LatestRanging = new RangingData
            {
                Front = ReadFloat(data, offset),
                Rear = ReadFloat(data, offset + 4),
                Timestamp = DateTimeOffset.FromUnixTimeMilliseconds(timestamp).DateTime
            };
            OnRanging?.Invoke(this, LatestRanging);
        }
        
        private void ParseOdometry(byte[] data, int offset, int length, uint timestamp)
        {
            if (length < 8) return;
            
            LatestOdometry = new OdometryData
            {
                Distance = ReadFloat(data, offset),
                Speed = ReadFloat(data, offset + 4),
                Timestamp = DateTimeOffset.FromUnixTimeMilliseconds(timestamp).DateTime
            };
            OnOdometry?.Invoke(this, LatestOdometry);
        }
        
        private void ParseBMS(byte[] data, int offset, int length, uint timestamp)
        {
            if (length < 14) return;
            
            LatestBMS = new BMSData
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
            OnBMS?.Invoke(this, LatestBMS);
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
            uint bits = (uint)data[offset] | ((uint)data[offset + 1] << 8) 
                     | ((uint)data[offset + 2] << 16) | ((uint)data[offset + 3] << 24);
            return BitConverter.ToSingle(BitConverter.GetBytes(bits), 0);
        }
        
        private static uint ReadUInt32(byte[] data, int offset)
        {
            return (uint)data[offset] | ((uint)data[offset + 1] << 8) 
                 | ((uint)data[offset + 2] << 16) | ((uint)data[offset + 3] << 24);
        }
        
        #endregion
    }
}
