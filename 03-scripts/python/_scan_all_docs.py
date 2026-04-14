import os, json, zipfile, re
from pathlib import Path
root = Path(r"D:\铁路线路智能检测机器人")
out = Path(r"C:\Users\DELL\.openclaw\workspace\analysis_pass1.txt")
text_ext = {'.txt','.md','.py','.json','.csv','.log','.ps1','.js'}
files = sorted([p for p in root.rglob('*') if p.is_file()])
parts = []
parts.append(f"ROOT: {root}")
parts.append(f"FILES: {len(files)}")
for p in files:
    ext = p.suffix.lower()
    parts.append(f"\n=== FILE: {p} ===")
    try:
        if ext in text_ext:
            data = p.read_text(encoding='utf-8', errors='ignore')
            data = data.replace('\x00',' ')
            lines = [ln.strip() for ln in data.splitlines() if ln.strip()]
            preview = '\n'.join(lines[:40])
            parts.append(preview[:4000])
        elif ext == '.docx':
            with zipfile.ZipFile(p, 'r') as z:
                xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
            text = re.sub(r'<[^>]+>', '\n', xml)
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            preview = '\n'.join(lines[:80])
            parts.append(preview[:5000])
        else:
            parts.append(f"[SKIP_BINARY] {ext}")
    except Exception as e:
        parts.append(f"[ERROR] {e}")
out.write_text('\n'.join(parts), encoding='utf-8')
print(out)
