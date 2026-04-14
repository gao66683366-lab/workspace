# -*- coding: utf-8 -*-
from docx import Document

doc = Document('D:\\铁路线路智能检测机器人\\04-项目文档\\设计文档\\机器人硬件系统架构设计文档 V1.0.docx')

# 查找并更新串口配置
for para in doc.paragraphs:
    if '串口：≥2个RS485接口' in para.text:
        para.text = '  • 串口：≥3个RS485接口（传感器×1、陀螺仪×1、备用×1）'
        break

doc.save('D:\\铁路线路智能检测机器人\\04-项目文档\\设计文档\\机器人硬件系统架构设计文档 V1.0.docx')
print('[OK] 已修正串口配置为至少3个RS485')
