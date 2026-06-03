using System;
using System.IO;

namespace RobotLinkSDK
{
    /// <summary>
    /// 控制指令帧构造器
    /// </summary>
    public class CommandFrame
    {
        public const ushort Header = 0xAA55;
        
        /// <summary>
        /// 序列号（递增）
        /// </summary>
        public ushort Sequence { get; set; }
        
        /// <summary>
        /// 命令字
        /// </summary>
        public byte CMD { get; set; }
        
        /// <summary>
        /// 子命令字
        /// </summary>
        public byte SubCmd { get; set; }
        
        /// <summary>
        /// 参数数据
        /// </summary>
        public byte[]? Payload { get; set; }

        /// <summary>
        /// 编码为字节数组
        /// </summary>
        public byte[] Encode()
        {
            int payloadLen = Payload?.Length ?? 0;
            int frameLen = 2 + 2 + 2 + 1 + 1 + payloadLen + 2; // Header+Seq+Len+CMD+SubCMD+Payload+CRC
            using var ms = new MemoryStream();
            using var bw = new BinaryWriter(ms);
            
            bw.Write(BinaryPrimitives.ReverseEndianness(Header)); // 0xAA55
            bw.Write(BinaryPrimitives.ReverseEndianness(Sequence));
            ushort length = (ushort)(2 + 1 + payloadLen); // SubCMD + CMD + Payload
            bw.Write(BinaryPrimitives.ReverseEndianness(length));
            bw.Write(CMD);
            bw.Write(SubCmd);
            if (Payload != null && Payload.Length > 0)
                bw.Write(Payload);
            
            // CRC16覆盖Header~Payload
            byte[] frameWithoutCRC = ms.ToArray();
            ushort crc = CRC16.Calc(frameWithoutCRC);
            bw.Write(BinaryPrimitives.ReverseEndianness(crc));
            
            return ms.ToArray();
        }

        /// <summary>
        /// 解析字节数组为帧
        /// </summary>
        public static CommandFrame? Decode(byte[] data, int offset = 0, int length = -1)
        {
            if (length < 0) length = data.Length - offset;
            if (length < 8) return null; // 最少8字节
            
            using var ms = new MemoryStream(data, offset, length);
            using var br = new BinaryReader(ms);
            
            ushort header = BinaryPrimitives.ReverseEndianness(br.ReadUInt16());
            if (header != Header) return null;
            
            var frame = new CommandFrame
            {
                Sequence = BinaryPrimitives.ReverseEndianness(br.ReadUInt16()),
                CMD = br.ReadByte(),
                SubCmd = br.ReadByte()
            };
            
            int payloadLen = length - 8;
            if (payloadLen > 0)
                frame.Payload = br.ReadBytes(payloadLen - 2); // 减去CRC2字节
            
            return frame;
        }
    }

    /// <summary>
    /// 应答帧解析器
    /// </summary>
    public class AckFrame
    {
        public ushort Sequence { get; set; }
        public byte Status { get; set; }
        
        // Status值定义
        public const byte ACK_OK = 0x00;
        public const byte NACK_CMD_NOT_SUPPORTED = 0x01;
        public const byte NACK_PARAM_ERROR = 0x02;
        public const byte NACK_SEQ_DUPLICATE = 0x03;
        public const byte NACK_BUSY = 0x04;
        public const byte NACK_UNKNOWN = 0xFF;
        
        public static AckFrame? Decode(byte[] data, int offset = 0)
        {
            if (data.Length - offset < 6) return null;
            using var ms = new MemoryStream(data, offset, data.Length - offset);
            using var br = new BinaryReader(ms);
            
            ushort header = BinaryPrimitives.ReverseEndianness(br.ReadUInt16());
            if (header != CommandFrame.Header) return null;
            
            return new AckFrame
            {
                Sequence = BinaryPrimitives.ReverseEndianness(br.ReadUInt16()),
                Status = br.ReadByte()
            };
        }
    }
    
    /// <summary>
    /// BinaryPrimitives辅助（.NET 5+内置，但兼容写法）
    /// </summary>
    public static class BinaryPrimitives
    {
        public static ushort ReverseEndianness(ushort value)
        {
            return (ushort)((value >> 8) | (value << 8));
        }
        public static uint ReverseEndianness(uint value)
        {
            return (value >> 24) | ((value >> 8) & 0x0000FF00) | ((value << 8) & 0x00FF0000) | (value << 24);
        }
        public static ushort ReadUInt16(byte[] data, int offset = 0)
        {
            return (ushort)((data[offset] << 8) | data[offset + 1]);
        }
        public static uint ReadUInt32(byte[] data, int offset = 0)
        {
            return (uint)((data[offset] << 24) | (data[offset+1] << 16) | (data[offset+2] << 8) | data[offset+3]);
        }
        public static void WriteUInt16(byte[] data, ushort value, int offset = 0)
        {
            data[offset] = (byte)(value >> 8);
            data[offset + 1] = (byte)(value & 0xFF);
        }
        public static void WriteUInt32(byte[] data, uint value, int offset = 0)
        {
            data[offset] = (byte)(value >> 24);
            data[offset + 1] = (byte)((value >> 16) & 0xFF);
            data[offset + 2] = (byte)((value >> 8) & 0xFF);
            data[offset + 3] = (byte)(value & 0xFF);
        }
    }
}