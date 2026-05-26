#!/usr/bin/env python3
import sys
sys.path.insert(0, '/root/.openclaw/workspace/word_tools')
import docx_gen
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('folder')
parser.add_argument('output')
parser.add_argument('--cover', nargs=4, default=[])
args = parser.parse_args()

doc = docx_gen.Document()
if args.cover:
    docx_gen.add_cover(doc, *args.cover)
docx_gen.parse_md(args.folder, doc)
docx_gen.add_page_numbers(doc)
doc.save(args.output)
print(f'Saved: {args.output}')