using System;
using System.Threading;

namespace RobotLinkSDK.Demo
{
    /// <summary>
    /// RobotLinkSDK 使用示例
    /// 
    /// 演示Windows触控屏控制软件与机器人主控板的完整交互流程
    /// </summary>
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=== RobotLinkSDK 演示程序 ===\n");
            
            // ===== 1. 设备发现 =====
            Console.WriteLine("[1] 设备发现...");
            var discoverer = new DeviceDiscoverer();
            discoverer.OnDeviceFound += (s, device) =>
            {
                Console.WriteLine($"    发现设备: {device.DeviceID} @ {device.IP}");
                Console.WriteLine($"    固件版本: {device.FirmwareVersionString}");
            };
            discoverer.StartDiscovery(3000);
            Thread.Sleep(3500);
            discoverer.StopDiscovery();
            
            Console.WriteLine();
            
            // ===== 2. 连接机器人 =====
            Console.WriteLine("[2] 连接机器人...");
            var robot = new RobotClient();
            robot.OnConnectionChanged += (s, connected) =>
            {
                Console.WriteLine($"    连接状态: {(connected ? "已连接" : "断开")}");
            };
            robot.OnSystemStatus += (s, status) =>
            {
                Console.WriteLine($"    系统状态: Mode={status.Mode} Error={status.ErrorCode} RSSI={status.WifiRSSI}dBm");
            };
            robot.OnAlarm += (s, alarm) =>
            {
                Console.WriteLine($"    [报警 {alarm.Level}] {alarm.Description}");
            };
            
            // 连接到第一个发现的设备，或使用默认IP
            var devices = discoverer.Devices;
            string ip = devices.Count > 0 ? devices[0].IP : "192.168.1.100";
            Console.WriteLine($"    连接到: {ip}");
            
            if (!robot.Connect(ip, 5000))
            {
                Console.WriteLine("    连接失败！");
                Console.WriteLine("    （请确保机器人已开机且与控制端在同一网络）");
                return;
            }
            
            Console.WriteLine();
            
            // ===== 3. 启动传感器接收 =====
            Console.WriteLine("[3] 启动传感器接收...");
            var sensor = new SensorReceiver(5002);
            sensor.OnIMU += (s, imu) =>
            {
                // Console.WriteLine($"    IMU: Roll={imu.Roll:F2} Pitch={imu.Pitch:F2} Yaw={imu.Yaw:F2}");
            };
            sensor.OnBMS += (s, bms) =>
            {
                Console.WriteLine($"    BMS: {bms.Voltage:F1}V {bms.SOC}% {bms.TempMax}℃");
            };
            sensor.OnOdometry += (s, odom) =>
            {
                // Console.WriteLine($"    里程: {odom.Distance:F1}mm 速度: {odom.Speed:F2}m/s");
            };
            sensor.Start();
            Console.WriteLine("    传感器接收已启动");
            
            // ===== 4. 启动视频接收 =====
            Console.WriteLine("[4] 启动视频接收...");
            var video = new VideoReceiver();
            video.OnFrontFrame += (s, frame) =>
            {
                // 实际项目中处理视频帧，如显示在UI上
                // Console.WriteLine($"    前视帧: {frame.Length} bytes");
            };
            video.OnRearFrame += (s, frame) =>
            {
                // Console.WriteLine($"    后视帧: {frame.Length} bytes");
            };
            video.Connect(
                $"rtsp://{ip}/stream/front?latency=0",
                $"rtsp://{ip}/stream/rear?latency=0",
                latency: 0
            );
            Console.WriteLine("    视频接收已启动");
            
            Console.WriteLine();
            
            // ===== 5. 控制操作 =====
            Console.WriteLine("[5] 控制操作演示...");
            
            try
            {
                // 设置速度
                Console.WriteLine("    设置速度 0.3m/s...");
                robot.SetSpeed(0.3f);
                
                // 前进
                Console.WriteLine("    前进...");
                robot.MoveForward();
                Thread.Sleep(2000);
                
                // 云台控制
                Console.WriteLine("    云台调整到 45°,-30°...");
                robot.PTZControl(0, 45, -30); // 前视云台
                Thread.Sleep(1000);
                robot.PTZControl(1, -30, 20);  // 后视云台
                
                // 光源控制
                Console.WriteLine("    设置光源亮度 80%...");
                robot.SetLightBrightness(80);
                Thread.Sleep(500);
                Console.WriteLine("    开启前照明灯...");
                robot.SetFrontLight(true);
                
                Thread.Sleep(2000);
                
                // 停止
                Console.WriteLine("    停止...");
                robot.MoveStop();
                
                // 关闭照明
                robot.SetFrontLight(false);
                robot.SetRearLight(false);
                
                // 请求系统状态
                Console.WriteLine("    请求系统状态...");
                var status = robot.RequestSystemStatus();
                Console.WriteLine($"    当前状态: Mode={status.Mode} Error={status.ErrorCode}");
                
                // BMS状态
                var bms = sensor.LatestBMS;
                if (bms.HasValue)
                {
                    Console.WriteLine($"    电池: {bms.Value.Voltage:F1}V {bms.Value.SOC}%");
                }
                
            }
            catch (RobotNACKException ex)
            {
                Console.WriteLine($"    NACK: {ex.Message}");
            }
            catch (TimeoutException ex)
            {
                Console.WriteLine($"    超时: {ex.Message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"    异常: {ex.Message}");
            }
            
            Console.WriteLine();
            
            // ===== 6. 清理 =====
            Console.WriteLine("[6] 清理资源...");
            video.Disconnect();
            sensor.Stop();
            robot.Disconnect();
            robot.Dispose();
            
            Console.WriteLine();
            Console.WriteLine("=== 演示完成 ===");
        }
    }
}
