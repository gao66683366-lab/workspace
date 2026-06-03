using System;

namespace RobotLinkSDK
{
    /// <summary>
    /// IMU姿态数据
    /// </summary>
    public struct IMUData
    {
        public float Roll { get; set; }      // 横滚角，度
        public float Pitch { get; set; }     // 俯仰角，度
        public float Yaw { get; set; }       // 航向角，度
        public float Wx { get; set; }        // 角速度X，deg/s
        public float Wy { get; set; }        // 角速度Y，deg/s
        public float Wz { get; set; }        // 角速度Z，deg/s
        public float Ax { get; set; }        // 加速度X，g
        public float Ay { get; set; }        // 加速度Y，g
        public float Az { get; set; }        // 加速度Z，g
        public DateTime Timestamp { get; set; }
        
        public override string ToString() => $"IMU Roll:{Roll:F2} Pitch:{Pitch:F2} Yaw:{Yaw:F2}";
    }

    /// <summary>
    /// 测距数据
    /// </summary>
    public struct RangingData
    {
        public float Front { get; set; }  // 前方距离，mm
        public float Rear { get; set; }   // 后方距离，mm
        public DateTime Timestamp { get; set; }
        
        public override string ToString() => $"Ranging Front:{Front:F1}mm Rear:{Rear:F1}mm";
    }

    /// <summary>
    /// 里程数据
    /// </summary>
    public struct OdometryData
    {
        public float Distance { get; set; }  // 累计里程，mm
        public float Speed { get; set; }    // 当前速度，m/s
        public DateTime Timestamp { get; set; }
        
        public override string ToString() => $"Odom Distance:{Distance:F1}mm Speed:{Speed:F2}m/s";
    }

    /// <summary>
    /// BMS电池管理数据
    /// </summary>
    public struct BMSData
    {
        public float Voltage { get; set; }      // 总电压，V
        public float Current { get; set; }      // 电流，A
        public byte SOC { get; set; }           // 荷电状态，%
        public sbyte TempMax { get; set; }      // 最高温度，℃
        public sbyte TempMin { get; set; }      // 最低温度，℃
        public ushort CycleCount { get; set; }   // 循环次数
        public byte Status { get; set; }        // 状态位
        public DateTime Timestamp { get; set; }
        
        // 状态位辅助属性
        public bool IsAlarm => (Status & 0x01) != 0;
        public bool IsOverTemp => (Status & 0x02) != 0;
        public bool IsUnderVolt => (Status & 0x04) != 0;
        public bool IsOverCurrent => (Status & 0x08) != 0;
        
        public override string ToString() => $"BMS {Voltage:F1}V {SOC}% {TempMax}℃";
    }

    /// <summary>
    /// 系统状态数据
    /// </summary>
    public struct SystemStatusData
    {
        public RunMode Mode { get; set; }
        public ErrorCode ErrorCode { get; set; }
        public short CpuTemp { get; set; }       // 0.1℃
        public ushort MemoryUsage { get; set; }  // 0.1%
        public short BoardTemp { get; set; }     // 0.1℃
        public byte WifiRSSI { get; set; }       // dBm
        public byte WifiQuality { get; set; }    // 0~100
        public uint UptimeSeconds { get; set; }
        public DateTime Timestamp { get; set; }
        
        public override string ToString() => $"Status Mode:{Mode} Error:{ErrorCode} RSSI:{WifiRSSI}dBm";
    }

    /// <summary>
    /// 报警事件参数
    /// </summary>
    public class AlarmEventArgs : EventArgs
    {
        public AlarmLevel Level { get; set; }
        public byte Code { get; set; }
        public ushort Data { get; set; }
        public DateTime Timestamp { get; set; }
        public string Description { get; set; } = "";
        
        public override string ToString() => $"[Alarm {Level}] {Code:X2}h {Description}";
    }

    /// <summary>
    /// 设备信息
    /// </summary>
    public class DeviceInfo
    {
        public string IP { get; set; } = "";
        public uint SubnetMask { get; set; }
        public uint Gateway { get; set; }
        public string DeviceID { get; set; } = "";
        public uint FirmwareVersion { get; set; }
        public uint Capability { get; set; }
        
        public string FirmwareVersionString => $"{((FirmwareVersion >> 16) & 0xFF)}.{((FirmwareVersion >> 8) & 0xFF)}.{(FirmwareVersion & 0xFF)}";
        
        public override string ToString() => $"Device {DeviceID} @ {IP} v{FirmwareVersionString}";
    }

    /// <summary>
    /// 自检结果
    /// </summary>
    public class SelfTestResult : EventArgs
    {
        public bool Success { get; set; }
        public byte[]? Details { get; set; }
        public string Message { get; set; } = "";
    }
}