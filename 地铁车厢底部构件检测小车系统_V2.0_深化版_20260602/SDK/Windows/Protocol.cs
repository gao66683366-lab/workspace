using System;

namespace RobotLinkSDK
{
    /// <summary>
    /// 通信协议定义
    /// 
    /// 帧格式：STX(1B) + CMD(1B) + LEN(2B, little-endian) + Payload(N) + CRC16(2B) + ETX(1B)
    /// CRC16覆盖 STX~Payload（不含CRC和ETX）
    /// </summary>
    public static class Protocol
    {
        public const byte STX = 0x02;           // 帧起始符
        public const byte ETX = 0x03;           // 帧结束符
        public const ushort CRC16_POLY = 0x8005; // CRC16-Modbus多项式
        
        #region 帧构建
        
        /// <summary>
        /// 构建发送帧
        /// </summary>
        public static byte[] BuildFrame(byte cmd, byte[]? payload = null)
        {
            int payloadLen = payload?.Length ?? 0;
            int frameLen = 1 + 1 + 2 + payloadLen + 2 + 1; // STX+CMD+LEN+Payload+CRC16+ETX
            
            byte[] frame = new byte[frameLen];
            int offset = 0;
            
            // STX
            frame[offset++] = STX;
            
            // CMD
            frame[offset++] = cmd;
            
            // LEN (little-endian)
            frame[offset++] = (byte)(payloadLen & 0xFF);
            frame[offset++] = (byte)(payloadLen >> 8);
            
            // Payload
            if (payload != null && payloadLen > 0)
                Buffer.BlockCopy(payload, 0, frame, offset, payloadLen);
            offset += payloadLen;
            
            // CRC16 (覆盖 STX~Payload)
            ushort crc = CRC16.Calc(frame, 0, 1 + 1 + 2 + payloadLen);
            frame[offset++] = (byte)(crc & 0xFF);
            frame[offset++] = (byte)(crc >> 8);
            
            // ETX
            frame[offset++] = ETX;
            
            return frame;
        }
        
        /// <summary>
        /// 解析接收帧
        /// </summary>
        public static byte[]? ParseFrame(byte[] data, int length, out byte cmd, out byte[]? payload)
        {
            cmd = 0;
            payload = null;
            
            if (length < 7) return null;  // 最小帧: STX+CMD+LEN(2)+CRC16(2)+ETX = 7
            
            // 找STX
            int offset = 0;
            while (offset < length - 6 && data[offset] != STX)
                offset++;
            
            if (offset >= length - 6) return null;
            if (data[offset] != STX) return null;
            
            int frameStart = offset;
            
            // CMD
            cmd = data[++offset];
            
            // LEN (little-endian)
            ushort payloadLen = (ushort)(data[++offset] | (data[++offset] << 8));
            
            // 检查数据完整性
            int frameEnd = offset + 1 + payloadLen + 2 + 1; // +CRC16+ETX
            if (frameEnd > length) return null;
            
            // 提取Payload
            if (payloadLen > 0)
            {
                payload = new byte[payloadLen];
                Buffer.BlockCopy(data, offset + 1, payload, 0, payloadLen);
            }
            
            // CRC验证
            ushort recvCRC = (ushort)(data[frameStart + 1 + 1 + 2 + payloadLen] 
                                     | (data[frameStart + 1 + 1 + 2 + payloadLen + 1] << 8));
            ushort calcCRC = CRC16.Calc(data, frameStart, 1 + 1 + 2 + payloadLen);
            
            if (recvCRC != calcCRC) return null;
            
            // ETX验证
            if (data[frameEnd - 1] != ETX) return null;
            
            // 返回完整帧
            byte[] frame = new byte[frameEnd - frameStart];
            Buffer.BlockCopy(data, frameStart, frame, 0, frame.Length);
            return frame;
        }
        
        #endregion
        
        #region 命令码定义 (20条)
        
        /// <summary>心跳</summary>
        public const byte CMD_HEARTBEAT = 0x01;
        
        /// <summary>运动控制 - 绝对运动</summary>
        public const byte CMD_MOTION_ABS = 0x10;
        /// <summary>运动控制 - 相对运动</summary>
        public const byte CMD_MOTION_REL = 0x11;
        /// <summary>运动控制 - 停止</summary>
        public const byte CMD_MOTION_STOP = 0x12;
        /// <summary>运动控制 - 回零</summary>
        public const byte CMD_MOTION_HOME = 0x13;
        /// <summary>运动控制 - 速度设置</summary>
        public const byte CMD_MOTION_SPEED = 0x14;
        
        /// <summary>云台控制 - 角度控制</summary>
        public const byte CMD_PTZ_ANGLE = 0x20;
        /// <summary>云台控制 - 预置位</summary>
        public const byte CMD_PTZ_PRESET = 0x21;
        /// <summary>云台控制 - 云台复位</summary>
        public const byte CMD_PTZ_RESET = 0x22;
        
        /// <summary>相机控制 - 变倍</summary>
        public const byte CMD_CAMERA_ZOOM = 0x30;
        /// <summary>相机控制 - 聚焦</summary>
        public const byte CMD_CAMERA_FOCUS = 0x31;
        /// <summary>相机控制 - 抓拍</summary>
        public const byte CMD_CAMERA_CAPTURE = 0x32;
        
        /// <summary>光源控制 - 亮度设置</summary>
        public const byte CMD_LIGHT_BRIGHTNESS = 0x40;
        /// <summary>光源控制 - 开关控制</summary>
        public const byte CMD_LIGHT_SWITCH = 0x41;
        
        /// <summary>IO控制 - 数字输出</summary>
        public const byte CMD_IO_DO = 0x50;
        /// <summary>IO控制 - 数字输入读取</summary>
        public const byte CMD_IO_DI = 0x51;
        /// <summary>IO控制 - PWM输出</summary>
        public const byte CMD_IO_PWM = 0x52;
        
        /// <summary>系统 - 状态查询</summary>
        public const byte CMD_SYS_STATUS = 0xE0;
        /// <summary>系统 - 时间同步</summary>
        public const byte CMD_SYS_TIME = 0xE1;
        /// <summary>系统 - 参数配置</summary>
        public const byte CMD_SYS_CONFIG = 0xE2;
        
        /// <summary>升级 - 开始</summary>
        public const byte CMD_UPDATE_START = 0xF0;
        /// <summary>升级 - 数据</summary>
        public const byte CMD_UPDATE_DATA = 0xF1;
        /// <summary>升级 - 完成</summary>
        public const byte CMD_UPDATE_END = 0xF2;
        
        #endregion
        
        #region 状态码
        
        public const byte STATUS_OK = 0x00;       // 执行成功
        public const byte STATUS_ERROR = 0x01;    // 执行失败
        public const byte STATUS_BUSY = 0x02;     // 设备忙
        public const byte STATUS_INVALID = 0x03;  // 无效参数
        public const byte STATUS_TIMEOUT = 0x04;  // 执行超时
        public const byte STATUS_NACK = 0xFF;     // 不确认
        
        #endregion
    }
}
