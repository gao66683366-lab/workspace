using System;

namespace RobotLinkSDK
{
    /// <summary>
    /// 运行模式枚举
    /// </summary>
    public enum RunMode : byte
    {
        Idle = 0,      // 待机
        Auto = 1,      // 自动模式
        Manual = 2,    // 手动模式
        Emergency = 3  // 应急模式
    }

    /// <summary>
    /// 错误码枚举
    /// </summary>
    public enum ErrorCode : byte
    {
        OK = 0,
        // 通信错误 (0x01~0x0F)
        ERR_TIMEOUT = 0x01,
        ERR_FRAME = 0x02,
        ERR_CRC = 0x03,
        ERR_NOT_CONNECTED = 0x04,
        // 电机错误 (0x10~0x1F)
        ERR_MOTOR_FAULT = 0x10,
        ERR_OVERCURRENT = 0x11,
        ERR_OVERHEAT = 0x12,
        ERR_STALL = 0x13,
        // 相机错误 (0x20~0x2F)
        ERR_CAMERA_OFFLINE = 0x20,
        ERR_CAMERA_TRIGGER = 0x21,
        // BMS错误 (0x30~0x3F)
        ERR_BMS_UNDERVOLT = 0x30,
        ERR_BMS_OVERCURRENT = 0x31,
        ERR_BMS_OVERTEMP = 0x32,
        ERR_BMS_DEAD = 0x33,
        // 传感器错误 (0x40~0x4F)
        ERR_IMU_OFFLINE = 0x40,
        ERR_RANGING_OFFLINE = 0x41,
        ERR_LIDAR_OFFLINE = 0x42,
        ERR_ODOMETRY_ERROR = 0x43
    }

    /// <summary>
    /// 报警级别枚举
    /// </summary>
    public enum AlarmLevel : byte
    {
        INFO = 1,
        WARNING = 2,
        ERROR = 3,
        CRITICAL = 4
    }

    /// <summary>
    /// 命令字定义
    /// </summary>
    public static class CMD
    {
        public const byte Motion = 0x01;       // 运动控制
        public const byte PTZ = 0x02;          // 云台控制
        public const byte Light = 0x03;        // 光源控制
        public const byte Capture = 0x04;      // 采集控制
        public const byte System = 0x05;       // 系统控制
        public const byte Heartbeat = 0xFF;    // 心跳
    }

    /// <summary>
    /// 运动控制子命令
    /// </summary>
    public static class SubCMD_Motion
    {
        public const byte SetSpeed = 0x01;
        public const byte Forward = 0x02;
        public const byte Backward = 0x03;
        public const byte Stop = 0x04;
        public const byte EStop = 0x05;
    }

    /// <summary>
    /// 云台控制子命令
    /// </summary>
    public static class SubCMD_PTZ
    {
        public const byte AngleControl = 0x01;
        public const byte Reset = 0x02;
        public const byte SavePreset = 0x03;
        public const byte LoadPreset = 0x04;
    }

    /// <summary>
    /// 光源控制子命令
    /// </summary>
    public static class SubCMD_Light
    {
        public const byte SetBrightness = 0x01;
        public const byte FrontLight = 0x02;
        public const byte RearLight = 0x03;
    }

    /// <summary>
    /// 采集控制子命令
    /// </summary>
    public static class SubCMD_Capture
    {
        public const byte Start = 0x01;
        public const byte Stop = 0x02;
        public const byte SaveData = 0x03;
    }

    /// <summary>
    /// 系统控制子命令
    /// </summary>
    public static class SubCMD_System
    {
        public const byte SelfTest = 0x01;
        public const byte Calibrate = 0x02;
        public const byte SyncTime = 0x03;
        public const byte RequestStatus = 0x04;
        public const byte EnterSleep = 0x05;
        public const byte WakeUp = 0x06;
    }

    /// <summary>
    /// 心跳子命令
    /// </summary>
    public static class SubCMD_Heartbeat
    {
        public const byte Beat = 0x01;
        public const byte QueryStatus = 0x02;
    }
}