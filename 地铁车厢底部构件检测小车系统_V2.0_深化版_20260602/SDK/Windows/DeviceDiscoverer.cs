using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace RobotLinkSDK
{
    /// <summary>
    /// 设备发现器
    /// 
    /// 通过UDP广播查询同一网络中的机器人设备
    /// 协议：控制端发送查询帧（0xFF 0x01）到255.255.255.255:5004
    ///       机器人回复设备信息帧
    /// </summary>
    public class DeviceDiscoverer : IDisposable
    {
        #region 私有字段
        
        private UdpClient? _udpClient;
        private CancellationTokenSource? _cts;
        private Task? _recvTask;
        private readonly List<DeviceInfo> _devices = new();
        private readonly object _lock = new();
        
        private const int DiscoveryPort = 5004;
        private const string BroadcastAddress = "255.255.255.255";
        
        #endregion

        #region 事件定义
        
        /// <summary>发现设备回调</summary>
        public event EventHandler<DeviceInfo>? OnDeviceFound;
        
        #endregion

        #region 属性
        
        /// <summary>已发现的设备列表</summary>
        public IReadOnlyList<DeviceInfo> Devices
        {
            get
            {
                lock (_lock)
                {
                    return _devices.ToArray();
                }
            }
        }
        
        #endregion

        #region 构造与销毁
        
        public DeviceDiscoverer()
        {
        }

        public void Dispose()
        {
            StopDiscovery();
            GC.SuppressFinalize(this);
        }

        ~DeviceDiscoverer()
        {
            Dispose();
        }

        #endregion

        #region 发现控制
        
        /// <summary>
        /// 开始设备发现
        /// </summary>
        /// <param name="timeoutMs">发现超时时间，默认3000ms</param>
        public void StartDiscovery(int timeoutMs = 3000)
        {
            StopDiscovery();
            
            _udpClient = new UdpClient();
            _udpClient.Client.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.Broadcast, true);
            _udpClient.Client.ReceiveTimeout = timeoutMs + 500;
            _udpClient.Client.Bind(new IPEndPoint(IPAddress.Any, DiscoveryPort));
            
            _cts = new CancellationTokenSource();
            _recvTask = Task.Run(() => ReceiveLoop(_cts.Token));
            
            // 发送广播查询
            byte[] queryFrame = new byte[] { 0xFF, 0x01 };
            
            // 发送3次查询，间隔500ms
            for (int i = 0; i < 3; i++)
            {
                try
                {
                    _udpClient.Send(
                        queryFrame, 
                        queryFrame.Length,
                        new IPEndPoint(IPAddress.Broadcast, DiscoveryPort)
                    );
                    Console.WriteLine($"[DeviceDiscoverer] 广播查询已发送 (#{i + 1})");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[DeviceDiscoverer] 广播发送失败: {ex.Message}");
                }
                
                if (i < 2)
                    Thread.Sleep(500);
            }
        }
        
        /// <summary>
        /// 停止设备发现
        /// </summary>
        public void StopDiscovery()
        {
            try { _cts?.Cancel(); } catch { }
            try { _udpClient?.Close(); } catch { }
            
            _udpClient = null;
            _cts = null;
            _recvTask = null;
            
            Console.WriteLine("[DeviceDiscoverer] 已停止");
        }
        
        /// <summary>
        /// 清除已发现的设备列表
        /// </summary>
        public void ClearDevices()
        {
            lock (_lock)
            {
                _devices.Clear();
            }
        }

        #endregion

        #region 接收循环
        
        /// <summary>
        /// 接收响应循环
        /// </summary>
        private async Task ReceiveLoop(CancellationToken ct)
        {
            Console.WriteLine("[DeviceDiscoverer] 开始监听响应");
            
            while (!ct.IsCancellationRequested && _udpClient != null)
            {
                try
                {
                    var result = await _udpClient.ReceiveAsync(ct);
                    var deviceInfo = ParseDeviceResponse(result.Buffer, result.Buffer.Length);
                    
                    if (deviceInfo != null)
                    {
                        // 添加到设备列表
                        lock (_lock)
                        {
                            // 检查是否已存在（根据DeviceID判断）
                            bool exists = false;
                            for (int i = 0; i < _devices.Count; i++)
                            {
                                if (_devices[i].DeviceID == deviceInfo.DeviceID)
                                {
                                    _devices[i] = deviceInfo; // 更新
                                    exists = true;
                                    break;
                                }
                            }
                            
                            if (!exists)
                            {
                                _devices.Add(deviceInfo);
                            }
                        }
                        
                        // 触发回调
                        OnDeviceFound?.Invoke(this, deviceInfo);
                        Console.WriteLine($"[DeviceDiscoverer] 发现设备: {deviceInfo}");
                    }
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (SocketException ex) when (ex.SocketErrorCode == SocketError.TimedOut)
                {
                    // 超时，停止监听
                    Console.WriteLine("[DeviceDiscoverer] 监听超时");
                    break;
                }
                catch (Exception ex)
                {
                    if (!ct.IsCancellationRequested)
                    {
                        Console.WriteLine($"[DeviceDiscoverer] 接收异常: {ex.Message}");
                        await Task.Delay(100, ct);
                    }
                }
            }
            
            Console.WriteLine("[DeviceDiscoverer] 监听结束");
        }
        
        /// <summary>
        /// 解析设备响应帧
        /// 
        /// 帧格式：
        /// Byte[0]:   0xFE  // 发现响应标识
        /// Byte[1]:   0x01  // 版本号
        /// Byte[2-5]: uint32 ip_address    // 机器人IP（little-endian）
        /// Byte[6-9]: uint32 subnet_mask   // 子网掩码
        /// Byte[10-13]: uint32 gateway     // 网关
        /// Byte[14-17]: uint32 dns         // DNS
        /// Byte[18-25]: char[8] device_id  // 设备ID（如"ROBOT001"）
        /// Byte[26-29]: uint32 firmware_version  // 固件版本
        /// Byte[30-33]: uint32 capability  // 能力掩码
        /// </summary>
        private DeviceInfo? ParseDeviceResponse(byte[] data, int length)
        {
            if (length < 34) return null; // 最小帧长度
            
            int offset = 0;
            
            // 响应标识
            if (data[offset++] != 0xFE) return null;
            
            // 版本号
            offset++; // 跳过版本号
            
            var device = new DeviceInfo
            {
                IP = $"{data[offset++]}.{data[offset++]}.{data[offset++]}.{data[offset++]}",
                SubnetMask = ReadUInt32(data, offset); offset += 4;
                Gateway = ReadUInt32(data, offset); offset += 4;
                // DNS跳过
                offset += 4;
                DeviceID = Encoding.ASCII.GetString(data, offset, 8).TrimEnd('\0');
                offset += 8;
                FirmwareVersion = ReadUInt32(data, offset); offset += 4;
                Capability = ReadUInt32(data, offset)
            };
            
            return device;
        }
        
        private static uint ReadUInt32(byte[] data, int offset)
        {
            return ((uint)data[offset] << 24) | ((uint)data[offset + 1] << 16) 
                   | ((uint)data[offset + 2] << 8) | data[offset + 3];
        }

        #endregion
    }
}
