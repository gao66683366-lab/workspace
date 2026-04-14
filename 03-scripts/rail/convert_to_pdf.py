#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将Word文档转换为PDF
"""

from docx2pdf import convert
import os

word_path = r"D:\铁路线路智能检测机器人\03-论文编撰\铁路线路智能检测机器人学术论文提纲 V2.0.docx"
pdf_path = r"D:\铁路线路智能检测机器人\03-论文编撰\铁路线路智能检测机器人学术论文提纲 V2.0.pdf"

print(f"[INFO] 开始转换...")
print(f"[INFO] 输入: {word_path}")
print(f"[INFO] 输出: {pdf_path}")

try:
    convert(word_path, pdf_path)
    print(f"[OK] 转换成功!")
    
    file_size = os.path.getsize(pdf_path)
    print(f"[INFO] PDF大小: {file_size/1024:.1f} KB")
    
except Exception as e:
    print(f"[ERROR] 转换失败: {e}")
    print("[INFO] 正在尝试使用COM方式...")
    
    # 使用win32com方式
    import win32com.client
    import pythoncom
    
    pythoncom.CoInitialize()
    
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    
    doc = word.Documents.Open(word_path)
    doc.SaveAs(pdf_path, FileFormat=17)  # 17 = PDF格式
    doc.Close()
    word.Quit()
    
    pythoncom.CoUninitialize()
    
    file_size = os.path.getsize(pdf_path)
    print(f"[OK] 转换成功 (COM方式)!")
    print(f"[INFO] PDF大小: {file_size/1024:.1f} KB")
