using System;

namespace RobotLinkSDK
{
    #region 数据模型
    
    /// <summary>IMU姿态数据</summary>
    public class IMUData
    {
        public float Roll { get; set; }       // 横滚角 (°)
        public float Pitch { get; set; }     // 俯仰角 (°)
        public float Yaw { get; set; }        // 偏航角 (°)
        public float Wx { get; set; }         // 角速度X (°/s)
        public float Wy { get; set; }         // 角速度Y (°/s)
        public float Wz { get; set; }         // 角速度Z (°/s)
        public float Ax { get; set; }         // 加速度X (g)
        public float Ay { get; set; }         // 加速度Y (g)
        public float Az { get; set; }         // 加速度Z (g)
        public DateTime Timestamp { get; set; }
    }
    
    /// <summary>测距数据</summary>
    public class RangingData
    {
        public float Front { get; set; }      // 前方距离 (m)
        public float Rear { get; set; }       // 后方距离 (m)
        public DateTime Timestamp { get; set; }
    }
    
    /// <summary>里程计数据</summary>
    public class OdometryData
    {
        public float Distance { get; set; }   // 累计距离 (m)
        public float Speed { get; set; }      // 当前速度 (m/s)
        public DateTime Timestamp { get; set; }
    }
    
    /// <summary>BMS电池数据</summary>
    public class BMSData
    {
        public float Voltage { get; set; }    // 电压 (V)
        public float Current { get; set; }    // 电流 (A)
        public byte SOC { get; set; }         // 荷电状态 (%)
        public sbyte TempMax { get; set; }    // 最高温度 (℃)
        public sbyte TempMin { get; set; }    // 最低温度 (℃)
        public ushort CycleCount { get; set; } // 循环次数
        public byte Status { get; set; }       // 状态字
        public DateTime Timestamp { get; set; }
    }
    
    /// <summary>系统状态数据</summary>
    public class SystemStatusData
    {
        public RunMode Mode { get; set; }     // 运行模式
        public ErrorCode ErrorCode { get; set; } // 错误码
        public short CpuTemp { get; set; }    // CPU温度 (℃)
        public ushort MemoryUsage { get; set; } // 内存使用 (%)
        public short BoardTemp { get; set; }  // 板温 (℃)
        public byte WifiRSSI { get; set; }    // WiFi信号强度 (dBm)
        public byte WifiQuality { get; set; } // WiFi质量 (0-100)
        public uint UptimeSeconds { get; set; } // 运行时间 (s)
        public DateTime Timestamp { get; set; }
        
        public SystemStatusData() { }
        
        public SystemStatusData(byte[] payload)
        {
            if (payload == null || payload.Length < 11) return;
            
            Mode = (RunMode)payload[0];
            ErrorCode = (ErrorCode)payload[1];
            CpuTemp = (short)((payload[2] << 8) | payload[3]);
            MemoryUsage = (ushort)((payload[4] << 8) | payload[5]);
            BoardTemp = (short)((payload[6] << 8) | payload[7]);
            WifiRSSI = payload[8];
            WifiQuality = payload[9];
            UptimeSeconds = (uint)((payload[10] << 24) | (payload[11] << 16) 
                                 | (payload[12] << 8) | payload[13]);
            Timestamp = DateTime.Now;
        }
    }
    
    /// <summary>遥测数据</summary>
    public class TelemetryData
    {
        public IMUData? IMU { get; set; }
        public RangingData? Ranging { get; set; }
        public OdometryData? Odometry { get; set; }
        public BMSData? BMS { get; set; }
        public SystemStatusData? System { get; set; }
        public DateTime Timestamp { get; set; }
    }
    
    /// <summary>报警事件</summary>
    public class AlarmEventArgs : EventArgs
    {
        public AlarmLevel Level { get; set; }
        public string Description { get; set; } = "";
        public DateTime Timestamp { get; set; }
    }
    
    /// <summary>自检结果</summary>
    public class SelfTestResult
    {
        public bool MotorOK { get; set; }
        public bool IMUOK { get; set; }
        public bool BMSOK { get; set; }
        public bool CameraOK { get; set; }
        public bool WifiOK { get; set; }
        public bool Overall => MotorOK && IMUOK && BMSOK && CameraOK && WifiOK;
    }
    
    #endregion
    
    #region 枚举定义
    
    /// <summary>运行模式</summary>
    public enum RunMode : byte
    {
        Idle = 0,
        Manual = 1,
        Auto = 2,
        EStop = 3,
        Fault = 4
    }
    
    /// <summary>错误码</summary>
    public enum ErrorCode : byte
    {
        None = 0,
        MotorFault = 1,
        IMUFault = 2,
        BatteryLow = 3,
        Collision = 4,
        Communication = 5,
        EStopTriggered = 6,
        OverTemp = 7
    }
    
    /// <summary>报警级别</summary>
    public enum AlarmLevel : byte
    {
        Info = 0,
        Warning = 1,
        Error = 2,
        Critical = 3
    }
    
    #endregion
}
