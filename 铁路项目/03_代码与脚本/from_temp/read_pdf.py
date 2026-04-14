import os
import sys

def extract_pdf():
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        from PyPDF2 import PdfReader

    pdf_path = r"C:\Users\Administrator\Desktop\CC1系列+GigE工业面阵相机使用说明书_V2.1.0(CN)(1).pdf"
    out_path = r"D:\铁路线路智能检测机器人\07-临时文件\cc1_manual.txt"

    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"--- Page {i+1} ---\n"
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("PDF extraction complete.")

if __name__ == "__main__":
    extract_pdf()
