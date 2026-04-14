const docx = require('docx');
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableCell, TableRow, HeadingLevel, AlignmentType, WidthType, BorderStyle } = docx;

// 创建三个Word文档
async function createDocuments() {
    // 1. 机器人系统架构文档
    const doc1 = new Document({
        sections: [{
            properties: {},
            children: [
                new Paragraph({
                    text: "铁路线路智能检测机器人系统架构",
                    heading: HeadingLevel.HEADING_1,
                    alignment: AlignmentType.CENTER
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "系统定位",
                    heading: HeadingLevel.HEADING_2
                }),
                new Paragraph({
                    text: "软硬件一体化智能检测机器人，用于铁路线路状态检测。"
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "硬件组成",
                    heading: HeadingLevel.HEADING_2
                }),
                new Paragraph({
                    text: "1. 底盘系统",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "• ", bold: true }),
                        new TextRun({ text: "4个伺服电机 + 4个伺服驱动器", bold: true })
                    ]
                }),
                new Paragraph({
                    text: "  - 控制4个车轮在铁路轨道上运行",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "  - 由工控机（工业控制计算机）控制",
                    indent: { left: 400 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "2. 视觉检测系统",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "• ", bold: true }),
                        new TextRun({ text: "6个工业相机", bold: true })
                    ]
                }),
                new Paragraph({
                    text: "检测对象：",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "- 两根钢轨轨面（磨损、鱼鳞纹、脱落等状态）",
                    indent: { left: 800 }
                }),
                new Paragraph({
                    text: "- 两根轨道旁的螺栓（每侧4颗，共8颗螺栓的完好状态）",
                    indent: { left: 800 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "3. 3D轮廓检测",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "• ", bold: true }),
                        new TextRun({ text: "2个3D线激光", bold: true })
                    ]
                }),
                new Paragraph({
                    text: "- 用于两根钢轨的轮廓检测",
                    indent: { left: 400 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "4. 轨距检测",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "• ", bold: true }),
                        new TextRun({ text: "8个测距传感器", bold: true })
                    ]
                }),
                new Paragraph({
                    text: "- 用于轨道轨距的检测",
                    indent: { left: 400 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "5. 姿态检测",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "• ", bold: true }),
                        new TextRun({ text: "2个陀螺仪", bold: true })
                    ]
                }),
                new Paragraph({
                    text: "检测参数：",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "- 钢轨水平度",
                    indent: { left: 800 }
                }),
                new Paragraph({
                    text: "- 高低差",
                    indent: { left: 800 }
                }),
                new Paragraph({
                    text: "- 轨向（轨道方向）",
                    indent: { left: 800 }
                }),
                new Paragraph({
                    text: "- 其他空间姿态",
                    indent: { left: 800 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "控制架构",
                    heading: HeadingLevel.HEADING_2
                }),
                new Paragraph({
                    text: "主控制器",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "• 工控机", bold: true }),
                        new TextRun({ text: "（工业控制计算机）" })
                    ]
                }),
                new Paragraph({
                    text: "- 统一控制所有硬件设备",
                    indent: { left: 400 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "运动控制层",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "• 运动控制器", bold: true }),
                        new TextRun({ text: " → 控制4个伺服电机" })
                    ]
                }),
                new Paragraph({
                    text: "- 通信方式：EtherCAT 总线（工业以太网）",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "- 驱动：4个伺服驱动器",
                    indent: { left: 400 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "软件架构",
                    heading: HeadingLevel.HEADING_2
                }),
                new Paragraph({
                    text: "上位机软件",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    text: "• 平台: 工控机",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "• 语言: C# .NET 8.0",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "• 功能: 设备控制、数据采集、本地处理",
                    indent: { left: 400 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "云端服务器",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    text: "• 语言: Python",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "• 功能: 数据处理、算法分析、远程管理",
                    indent: { left: 400 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "系统层级",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    text: "云端服务器 (Python)",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "    ↑",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "工控上位机 (C# .NET 8.0)",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "    ↓",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "运动控制器 (EtherCAT 总线)",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "    ↓",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "伺服驱动器 × 4 → 伺服电机 × 4",
                    indent: { left: 400 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "传感器通信架构",
                    heading: HeadingLevel.HEADING_2
                }),
                new Paragraph({
                    text: "视觉与3D扫描",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    text: "• 6个工业相机 - 以太网连接（网线）",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "• 2个3D线激光 - 以太网连接（网线）",
                    indent: { left: 400 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "测距与姿态传感器",
                    heading: HeadingLevel.HEADING_3
                }),
                new Paragraph({
                    text: "• 8个测距传感器 - Modbus RS485 串口连接",
                    indent: { left: 400 }
                }),
                new Paragraph({
                    text: "• 2个陀螺仪 - Modbus RS485 串口连接",
                    indent: { left: 400 }
                }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "通信协议总览",
                    heading: HeadingLevel.HEADING_2
                }),
                // 创建表格
                new Table({
                    width: { size: 100, type: WidthType.PERCENTAGE },
                    rows: [
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "设备类型", alignment: AlignmentType.CENTER })],
                                    shading: { fill: "D9D9D9" }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "数量", alignment: AlignmentType.CENTER })],
                                    shading: { fill: "D9D9D9" }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "通信方式", alignment: AlignmentType.CENTER })],
                                    shading: { fill: "D9D9D9" }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "协议", alignment: AlignmentType.CENTER })],
                                    shading: { fill: "D9D9D9" }
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({ children: [new Paragraph("伺服电机")] }),
                                new TableCell({ children: [new Paragraph({ text: "4", alignment: AlignmentType.CENTER })] }),
                                new TableCell({ children: [new Paragraph("工业以太网")] }),
                                new TableCell({ children: [new Paragraph("EtherCAT")] })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({ children: [new Paragraph("工业相机")] }),
                                new TableCell({ children: [new Paragraph({ text: "6", alignment: AlignmentType.CENTER })] }),
                                new TableCell({ children: [new Paragraph("以太网")] }),
                                new TableCell({ children: [new Paragraph("GigE Vision / 厂商协议")] })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({ children: [new Paragraph("3D线激光")] }),
                                new TableCell({ children: [new Paragraph({ text: "2", alignment: AlignmentType.CENTER })] }),
                                new TableCell({ children: [new Paragraph("以太网")] }),
                                new TableCell({ children: [new Paragraph("TCP/IP")] })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({ children: [new Paragraph("测距传感器")] }),
                                new TableCell({ children: [new Paragraph({ text: "8", alignment: AlignmentType.CENTER })] }),
                                new TableCell({ children: [new Paragraph("串口")] }),
                                new TableCell({ children: [new Paragraph("Modbus RS485")] })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({ children: [new Paragraph("陀螺仪")] }),
                                new TableCell({ children: [new Paragraph({ text: "2", alignment: AlignmentType.CENTER })] }),
                                new TableCell({ children: [new Paragraph("串口")] }),
                                new TableCell({ children: [new Paragraph("Modbus RS485")] })
                            ]
                        })
                    ]
                }),
                new Paragraph({ text: "" }),
                new Paragraph({ text: "" }),
                new Paragraph({
                    text: "创建时间: 2026-03-05 16:07",
                    italics: true
                })
            ]
        }]
    });

    // 保存文档
    const buffer1 = await Packer.toBuffer(doc1);
    fs.writeFileSync('D:\\铁路线路智能检测机器人\\04-项目文档\\设计文档\\机器人系统架构.docx', buffer1);
    
    console.log('✓ 机器人系统架构.docx 已创建');
}

createDocuments().catch(console.error);
