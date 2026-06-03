using System;
using System.Threading;

namespace RobotLinkSDK.Demo
{
    /// <summary>
    /// RobotLinkSDK 使用示例
    /// </summary>
    class Program
    {
        static void Main(string[] args) => MainAsync().GetAwaiter().GetResult();

        static async Task MainAsync()
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
                Console.WriteLine($"    连接状态: {(connected ? "已连接" : "断开")}");
            robot.OnSystemStatus += (s, status) =>
                Console.WriteLine($"    系统状态: Mode={status.Mode} Error={status.ErrorCode} RSSI={status.WifiRSSI}dBm");
            robot.OnAlarm += (s, alarm) =>
                Console.WriteLine($"    [报警 {alarm.Level}] {alarm.Description}");
            
            var devices = discoverer.Devices;
            string ip = devices.Count > 0 ? devices[0].IP : "192.168.1.100";
            Console.WriteLine($"    连接到: {ip}");
            
            if (!await robot.ConnectAsync(ip, 5000))
            {
                Console.WriteLine("    连接失败！");
                return;
            }
            
            Console.WriteLine();
            
            // ===== 3. 启动传感器接收 =====
            Console.WriteLine("[3] 启动传感器接收...");
            var sensor = new SensorReceiver(5002);
            sensor.OnBMS += (s, bms) =>
                Console.WriteLine($"    BMS: {bms.Voltage:F1}V {bms.SOC}% {bms.TempMax}℃");
            sensor.Start();
            Console.WriteLine("    传感器接收已启动");
            
            // ===== 4. 启动视频接收 =====
            Console.WriteLine("[4] 启动视频接收...");
            var video = new VideoReceiver();
            video.OnFrontFrame += (s, frame) => { };
            video.OnRearFrame += (s, frame) => { };
            video.Connect(
                $"rtsp://{ip}/stream/front?latency=0",
                $"rtsp://{ip}/stream/rear?latency=0"
            );
            Console.WriteLine("    视频接收已启动");
            
            Console.WriteLine();
            
            // ===== 5. 控制操作 =====
            Console.WriteLine("[5] 控制操作演示...");
            
            try
            {
                Console.WriteLine("    设置速度 0.3m/s...");
                await robot.SetSpeedAsync(0.3f);
                
                Console.WriteLine("    前进...");
                await robot.MoveForwardAsync();
                Thread.Sleep(2000);
                
                Console.WriteLine("    云台调整到 45°,-30°...");
                await robot.PTZControlAsync(0, 45, -30);
                Thread.Sleep(1000);
                await robot.PTZControlAsync(1, -30, 20);
                
                Console.WriteLine("    设置光源亮度 80%...");
                await robot.SetLightBrightnessAsync(80);
                Thread.Sleep(500);
                Console.WriteLine("    开启前照明灯...");
                await robot.SetFrontLightAsync(true);
                
                Thread.Sleep(2000);
                
                Console.WriteLine("    停止...");
                await robot.MoveStopAsync();
                
                await robot.SetFrontLightAsync(false);
                await robot.SetRearLightAsync(false);
                
                Console.WriteLine("    请求系统状态...");
                await robot.RequestSystemStatusAsync();
                
                // BMS是struct，直接访问（不用HasValue）
                var bms = sensor.LatestBMS;
                if (bms != null)
                    Console.WriteLine($"    电池: {bms.Value.Voltage:F1}V {bms.Value.SOC}%");
                
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
