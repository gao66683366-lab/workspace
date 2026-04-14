import os
import sys
import glob

def extract_pdf():
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        from PyPDF2 import PdfReader

    # Get Desktop path dynamically
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    # Use glob to find the file without worrying about exact string encoding in the terminal
    pdf_files = glob.glob(os.path.join(desktop, 'CC1*GigE*.pdf'))
    
    if not pdf_files:
        print("未找到对应的 PDF 文件。")
        return

    pdf_path = pdf_files[0]
    out_path = os.path.join(os.getcwd(), 'cc1_manual.txt')

    print(f"正在读取: {pdf_path}")
    
    try:
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
        print("PDF 提取完成！")
    except Exception as e:
        print(f"提取出错: {str(e)}")

if __name__ == "__main__":
    extract_pdf()
