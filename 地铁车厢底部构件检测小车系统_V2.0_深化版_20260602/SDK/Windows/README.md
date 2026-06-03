# RobotLinkSDK - Windows控制端SDK

## 概述

本SDK用于Windows触控屏控制软件与机器人主控板之间的WiFi无线通信，适用于地铁车厢底部构件检测机器人系统。

### 设计背景

WiFi无线链路特性：
- 典型延迟：10~50ms
- 最大延迟：200ms（拥堵时）
- 丢包率：0.1%~2%
- 可能随时断线

### 设计原则

1. **所有指令必须应答**：无应答即重发，防止"石沉大海"
2. **幂等性设计**：重复指令不产生副作用
3. **序列号防重放**：防止网络延迟导致指令重复执行
4. **断线自动重连**：心跳检测+自动重连机制
5. **数据完整性校验**：CRC16/CRC32保护

## 通信矩阵

| 通道 | 协议 | 端口 | 可靠性 |
|---|---|---|---|
| 控制指令 | TCP | 5000 | 可靠（应答确认）|
| 状态数据 | TCP | 5001 | 可靠 |
| 传感器数据 | UDP | 5002 | 不可靠（允许丢包）|
| 视频流 | RTSP | 8554 | 不可靠 |
| 设备发现 | UDP | 5004 | 不可靠 |

## 目录结构

```
Windows/
├── RobotLinkSDK.csproj    # SDK项目文件
├── CRC16.cs               # CRC16校验工具
├── CRC32.cs               # CRC32校验工具
├── CommandFrame.cs        # 指令帧构造器/解析器
├── CommandTypes.cs        # 命令字/子命令字/枚举定义
├── DataStructures.cs      # 数据结构定义
├── RobotClient.cs         # 主控制客户端（核心）
├── SensorReceiver.cs      # 传感器数据接收器
├── VideoReceiver.cs      # 视频流接收器
├── DeviceDiscoverer.cs   # 设备发现器
├── Demo.cs               # 使用示例
└── README.md             # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
dotnet add package OpenCvSharp4
dotnet add package OpenCvSharp4.runtime.win
```

### 2. 设备发现

```csharp
var discoverer = new DeviceDiscoverer();
discoverer.OnDeviceFound += (s, device) =>
{
    Console.WriteLine($"发现设备: {device.DeviceID} @ {device.IP}");
};
discoverer.StartDiscovery(3000);  // 3秒超时
Thread.Sleep(3500);
discoverer.StopDiscovery();
```

### 3. 连接机器人

```csharp
var robot = new RobotClient();
robot.OnConnectionChanged += (s, connected) =>
    Console.WriteLine($"连接状态: {connected}");
robot.OnAlarm += (s, alarm) =>
    Console.WriteLine($"[报警 {alarm.Level}] {alarm.Description}");

robot.Connect("192.168.1.100", 5000);
```

### 4. 运动控制

```csharp
// 设置速度
robot.SetSpeed(0.3f);

// 前进
robot.MoveForward();
Thread.Sleep(2000);

// 停止
robot.MoveStop();

// 急停（最快响应）
robot.MoveEstop();
```

### 5. 云台控制

```csharp
// camera: 0=前视, 1=后视
// pan: 水平角度 -180~+180度
// tilt: 垂直角度 -90~+90度
robot.PTZControl(0, 45, -30);  // 前视云台转到45°,-30°
robot.PTZReset(0);              // 前视云台复位
```

### 6. 传感器接收

```csharp
var sensor = new SensorReceiver(5002);
sensor.OnIMU += (s, imu) =>
    Console.WriteLine($"IMU: Roll={imu.Roll:F2} Pitch={imu.Pitch:F2}");
sensor.OnBMS += (s, bms) =>
    Console.WriteLine($"BMS: {bms.Voltage:F1}V {bms.SOC}%");
sensor.OnOdometry += (s, odom) =>
    Console.WriteLine($"里程: {odom.Distance:F1}mm 速度: {odom.Speed:F2}m/s");
sensor.Start();

// 获取最新数据
var bms = sensor.LatestBMS;
```

### 7. 视频接收

```csharp
var video = new VideoReceiver();
video.OnFrontFrame += (s, frame) =>
{
    // 处理前视视频帧
};
video.Connect(
    "rtsp://192.168.1.100:8554/stream/front?latency=0",
    "rtsp://192.168.1.100:8554/stream/rear?latency=0"
);

// 获取当前帧
var frame = video.GetFrontFrame();
```

### 8. 清理资源

```csharp
video.Disconnect();
sensor.Stop();
robot.Disconnect();
robot.Dispose();
```

## API参考

### RobotClient

| 方法 | 说明 | 异步版本 |
|---|---|---|
| Connect(ip, port) | 连接机器人 | ConnectAsync |
| Disconnect() | 断开连接 | - |
| SetSpeed(speed) | 设置速度 0.0~0.5m/s | SetSpeedAsync |
| MoveForward() | 前进 | MoveForwardAsync |
| MoveBackward() | 后退 | MoveBackwardAsync |
| MoveStop() | 停止 | MoveStopAsync |
| MoveEstop() | 急停 | MoveEstopAsync |
| PTZControl(cam, pan, tilt) | 云台角度控制 | PTZControlAsync |
| PTZReset(cam) | 云台复位 | PTZResetAsync |
| PTZSavePreset(cam, presetId) | 保存预设位 | PTZSavePresetAsync |
| PTZLoadPreset(cam, presetId) | 调用预设位 | PTZLoadPresetAsync |
| SetLightBrightness(brightness) | 光源亮度 0~100 | SetLightBrightnessAsync |
| SetFrontLight(onoff) | 前照明灯开关 | SetFrontLightAsync |
| SetRearLight(onoff) | 后照明灯开关 | SetRearLightAsync |
| StartCapture(mode) | 开始采集 | StartCaptureAsync |
| StopCapture() | 停止采集 | StopCaptureAsync |
| ForceSaveData() | 强制保存数据 | ForceSaveDataAsync |
| RequestSelfTest() | 系统自检 | RequestSelfTestAsync |
| CalibrateSensors(type) | 传感器标定 | CalibrateSensorsAsync |
| SyncTime() | 时间同步 | SyncTimeAsync |
| RequestSystemStatus() | 请求系统状态 | RequestSystemStatusAsync |
| EnterSleep() | 进入休眠 | EnterSleepAsync |
| WakeUp() | 唤醒 | WakeUpAsync |
| Heartbeat() | 发送心跳 | HeartbeatAsync |

### 事件

| 事件 | 说明 |
|---|---|
| OnConnectionChanged | 连接状态变化 |
| OnSystemStatus | 系统状态变化（1Hz）|
| OnAlarm | 报警事件 |
| OnSelfTestResult | 自检结果 |

### SensorReceiver

| 方法/事件 | 说明 |
|---|---|
| Start() | 启动接收 |
| Stop() | 停止接收 |
| OnIMU | IMU数据回调（50Hz）|
| OnRanging | 测距数据回调（20Hz）|
| OnOdometry | 里程数据回调（50Hz）|
| OnBMS | BMS数据回调（1Hz）|
| OnLidar | 激光雷达回调（10Hz）|
| OnSystemStatus | 系统状态回调（1Hz）|
| LatestIMU | 最新IMU数据 |
| LatestRanging | 最新测距数据 |
| LatestOdometry | 最新里程数据 |
| LatestBMS | 最新BMS数据 |

### VideoReceiver

| 方法/事件 | 说明 |
|---|---|
| Connect(frontUrl, rearUrl, latency) | 连接视频流 |
| Disconnect() | 断开 |
| SetLatency(ms) | 设置延迟模式 |
| GetFrontFrame() | 获取前视当前帧 |
| GetRearFrame() | 获取后视当前帧 |
| OnFrontFrame | 前视帧回调 |
| OnRearFrame | 后视帧回调 |

### DeviceDiscoverer

| 方法/事件 | 说明 |
|---|---|
| StartDiscovery(timeoutMs) | 开始发现 |
| StopDiscovery() | 停止发现 |
| ClearDevices() | 清除设备列表 |
| OnDeviceFound | 发现设备回调 |
| Devices | 已发现设备列表 |

## 数据结构

### IMUData

```csharp
public struct IMUData
{
    public float Roll, Pitch, Yaw;     // 角度（度）
    public float Wx, Wy, Wz;          // 角速度（deg/s）
    public float Ax, Ay, Az;          // 加速度（g）
    public DateTime Timestamp;
}
```

### BMSData

```csharp
public struct BMSData
{
    public float Voltage;      // 总电压（V）
    public float Current;      // 电流（A）
    public byte SOC;           // 荷电状态（%）
    public sbyte TempMax;      // 最高温度（℃）
    public sbyte TempMin;      // 最低温度（℃）
    public ushort CycleCount;   // 循环次数
    public byte Status;        // 状态位
    public DateTime Timestamp;
}
```

### SystemStatusData

```csharp
public struct SystemStatusData
{
    public RunMode Mode;           // 运行模式
    public ErrorCode ErrorCode;   // 错误码
    public short CpuTemp;         // CPU温度（0.1℃）
    public ushort MemoryUsage;    // 内存使用率（0.1%）
    public short BoardTemp;       // 板级温度（0.1℃）
    public byte WifiRSSI;         // WiFi信号强度（dBm）
    public byte WifiQuality;      // WiFi质量（0~100）
    public uint UptimeSeconds;     // 运行时长（秒）
}
```

## 帧格式

### 控制指令帧（TCP:5000）

```
+--------+----------+--------+----------+----------+----------+
| Header | Sequence | Length |  CMD     | Payload  | Checksum |
| 2字节  | 2字节    | 2字节  | 1字节    | N字节    | 2字节    |
+--------+----------+--------+----------+----------+----------+
```

- Header: 0xAA55
- Sequence: 0~65535递增
- Length: CMD + Payload长度
- CMD: 主命令字
- Payload: 参数数据
- Checksum: CRC16

### 应答帧

```
+--------+----------+--------+----------+
| Header | Sequence | Status | Checksum |
| 2字节  | 2字节    | 1字节  | 2字节    |
+--------+----------+--------+----------+
```

- Status: 0x00=ACK, 0x01~0x04=NACK, 0xFF=未知错误

### 传感器数据帧（UDP:5002）

```
+--------+----------+----------+----------+----------+
| Header | Timestamp| Sequence | Payload  | Checksum |
| 1字节  | 4字节    | 2字节    | N字节    | 4字节    |
+--------+----------+----------+----------+----------+
```

- Header: 0xAA
- Timestamp: Unix毫秒时间戳
- Sequence: 序列号（可能不连续，因UDP丢包）
- Checksum: CRC32

## 错误码

| 值 | 名称 | 说明 |
|---|---|---|
| 0x00 | OK | 正常 |
| 0x01 | ERR_TIMEOUT | 通信超时 |
| 0x02 | ERR_FRAME | 帧格式错误 |
| 0x03 | ERR_CRC | 校验失败 |
| 0x04 | ERR_NOT_CONNECTED | 未连接 |
| 0x10 | ERR_MOTOR_FAULT | 电机故障 |
| 0x11 | ERR_OVERCURRENT | 过流保护 |
| 0x12 | ERR_OVERHEAT | 过温保护 |
| 0x13 | ERR_STALL | 堵转 |
| 0x20 | ERR_CAMERA_OFFLINE | 相机离线 |
| 0x30 | ERR_BMS_UNDERVOLT | 电池欠压 |
| 0x40 | ERR_IMU_OFFLINE | IMU离线 |
