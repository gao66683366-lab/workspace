#!/usr/bin/env python3
import sys, os
sys.path.insert(0, '/root/.openclaw/workspace/word_tools')
from docx import Document
from docx_gen import parse_md

folder = '/root/.openclaw/workspace/列车底部构件检测机器人_技术文档章节拆分_20260526_1546/'
fname = '列车底部构件检测机器人_技术文档_V1.0_第01章_项目概述与核心定位_20260526_1546.md'
path = os.path.join(folder, fname)

doc = Document()
with open(path, encoding='utf-8') as f:
    content = f.read()

in_code = False
code_lines = []
lines = content.split('\n')
i = 0
table_count = 0
while i < len(lines):
    line = lines[i]
    if line.strip().startswith('```'):
        if not in_code:
            in_code = True
            code_lines = []
        else:
            in_code = False
        i += 1
        continue
    if in_code:
        code_lines.append(line)
        i += 1
        continue
    if line.startswith('# '):
        print(f'H1: {line[2:].strip()[:50]}')
    elif line.startswith('## '):
        print(f'H2: {line[3:].strip()[:50]}')
    elif line.startswith('### '):
        print(f'H3: {line[4:].strip()[:50]}')
    elif line.strip().startswith('|'):
        parts = [p.strip() for p in line.split('|')]
        interior = parts[1:-1]
        is_sep = all(p == '---' for p in interior)
        if len(parts) > 2 and not is_sep:
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row_line = lines[i]
                row_parts = [p.strip() for p in row_line.split('|')]
                row_interior = row_parts[1:-1]
                row_is_sep = all(p == '---' for p in row_interior)
                if row_interior and not row_is_sep:
                    table_rows.append([p for p in row_line.split('|') if p.strip()])
                i += 1
            if len(table_rows) > 1:
                print(f'TABLE with {len(table_rows)} rows (multi-row merge)')
                table_count += 1
            else:
                print(f'TABLE with {len(table_rows)} rows (single)')
            i -= 1
        else:
            i += 1
    else:
        i += 1

print(f'Total multi-row tables: {table_count}')