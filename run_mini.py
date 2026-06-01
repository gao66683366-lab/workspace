#!/usr/bin/env python3
import sys, os, signal
sys.path.insert(0, '/root/.openclaw/workspace/word_tools')

def timeout_handler(signum, frame):
    raise TimeoutError('Timed out!')

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(20)

try:
    from docx import Document
    from docx_gen import h1, h2, h3, body, add_table, parse_md
    
    folder = '/root/.openclaw/workspace/列车底部构件检测机器人_技术文档章节拆分_20260526_1546/'
    doc = Document()
    
    # Run parse_md but with a counter to track progress
    files = sorted([f for f in os.listdir(folder) if f.endswith('.md')])
    print(f'Files: {len(files)}')
    for fname in files:
        print(f'Processing {fname[:40]}...')
        path = os.path.join(folder, fname)
        with open(path, encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        print(f'  {len(lines)} lines')
    
    print('Done listing files')
except TimeoutError as e:
    print(f'TIMEOUT!')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()