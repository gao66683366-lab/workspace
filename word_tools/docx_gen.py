"""
docx_gen.py — 标准化 Word 文档生成工具 v4
永久工具 v4：ASCII架构图加灰底背景框

用法:
  python docx_gen.py <md文件夹/> <输出.docx> [--cover "标题" "副标题" "日期" "单位"]
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os, re, sys, argparse

PAGE_W_CM = 21.0
PAGE_H_CM = 29.7
MARGIN_CM = 2.54
TEXT_W_CM = PAGE_W_CM - 2 * MARGIN_CM

LH_BODY   = Pt(22)
LH_CODE   = Pt(15)
LH_TABLE  = Pt(17)
INDENT_BODY  = Cm(0.74)
INDENT_TABLE = Cm(0.2)
HDR_FILL  = 'D9E2F3'

# ── 工具函数 ────────────────────────────────────────────

def sf(run, cn, size, bold=False, italic=False, color=None):
    run.font.name = 'Times New Roman'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), cn)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)

def pfmt(p, before, after, lh, indent=None,
         align=WD_ALIGN_PARAGRAPH.LEFT):
    f = p.paragraph_format
    f.space_before = before
    f.space_after  = after
    f.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    f.line_spacing = lh
    if indent is not None:
        f.first_line_indent = indent
    f.alignment = align
    f.keep_with_next = True

def shade_cell(cell, hex_fill):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_fill)
    tcPr.append(shd)

def set_border(cell, color='000000', sz='6'):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    borders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):
        t = OxmlElement(f'w:{edge}')
        t.set(qn('w:val'), 'single')
        t.set(qn('w:sz'), sz)
        t.set(qn('w:space'), '0')
        t.set(qn('w:color'), color)
        borders.append(t)
    tcPr.append(borders)

def set_table_border(tbl, color='000000', sz='6'):
    tblPr = tbl._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        t = OxmlElement(f'w:{edge}')
        t.set(qn('w:val'), 'single')
        t.set(qn('w:sz'), sz)
        t.set(qn('w:space'), '0')
        t.set(qn('w:color'), color)
        tblBorders.append(t)
    tblPr.append(tblBorders)

def col_widths(rows_data):
    if not rows_data:
        return []
    ncols = max(len(r) for r in rows_data)
    weights = [0.0] * ncols
    for ri, row in enumerate(rows_data):
        for ci, val in enumerate(row):
            if ci < ncols:
                txt = str(val)
                score = sum(1 if '\u4e00' <= c <= '\u9fff' else 0.55
                             for c in txt) + len(txt) * 0.2
                if ri == 0:
                    score *= 2
                weights[ci] = max(weights[ci], score)
    total = sum(weights)
    if total == 0:
        return [TEXT_W_CM / ncols] * ncols
    return [TEXT_W_CM * w / total for w in weights]

def fmt_text(p, text, font_cn, font_size):
    for seg in re.split(r'(\*\*.+?\*\*|`.+?`)', text):
        if not seg:
            continue
        elif seg.startswith('**') and seg.endswith('**'):
            r = p.add_run(seg[2:-2])
            sf(r, font_cn, font_size, bold=True)
        elif seg.startswith('`') and seg.endswith('`'):
            r = p.add_run(seg[1:-1])
            sf(r, font_cn, font_size, italic=True)
        else:
            r = p.add_run(seg)
            sf(r, font_cn, font_size)

# ── 页码 ────────────────────────────────────────────────

def add_page_numbers(doc):
    section = doc.sections[0]
    footer = section.footer
    footer.is_linked_to_previous = False
    for p in footer.paragraphs:
        for r in p.runs:
            r.text = ''
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.clear()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)

    def page_field(run, instr):
        fc1 = OxmlElement('w:fldChar')
        fc1.set(qn('w:fldCharType'), 'begin')
        run._r.append(fc1)
        it = OxmlElement('w:instrText')
        it.set(qn('xml:space'), 'preserve')
        it.text = f' {instr} '
        run._r.append(it)
        fc2 = OxmlElement('w:fldChar')
        fc2.set(qn('w:fldCharType'), 'separate')
        run._r.append(fc2)
        t = OxmlElement('w:t')
        t.text = '1'
        run._r.append(t)
        fc3 = OxmlElement('w:fldChar')
        fc3.set(qn('w:fldCharType'), 'end')
        run._r.append(fc3)

    r = p.add_run()
    r.font.size = Pt(10)
    r.font.name = 'Times New Roman'
    r._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    page_field(r, 'PAGE')
    r2 = p.add_run(' / ')
    sf(r2, '宋体', 10)
    r3 = p.add_run()
    r3.font.size = Pt(10)
    r3.font.name = 'Times New Roman'
    r3._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    page_field(r3, 'NUMPAGES')

# ── 封面 ────────────────────────────────────────────────

def add_cover(doc, title, subtitle='', date='', unit=''):
    section = doc.sections[0]
    section.top_margin = Cm(5)

    for _ in range(6):
        p = doc.add_paragraph()
        pfmt(p, Pt(0), Pt(0), LH_BODY)

    p_title = doc.add_paragraph()
    pfmt(p_title, Pt(0), Pt(14), Pt(40),
         align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p_title.add_run(title)
    sf(r, '黑体', 28, bold=True)

    if subtitle:
        p_sub = doc.add_paragraph()
        pfmt(p_sub, Pt(4), Pt(10), Pt(24),
             align=WD_ALIGN_PARAGRAPH.CENTER)
        r2 = p_sub.add_run(subtitle)
        sf(r2, '黑体', 18)

    p_line = doc.add_paragraph()
    pfmt(p_line, Pt(14), Pt(14), Pt(18),
         align=WD_ALIGN_PARAGRAPH.CENTER)
    r3 = p_line.add_run('─' * 44)
    sf(r3, '宋体', 10, color=(120, 120, 120))

    if date:
        p_date = doc.add_paragraph()
        pfmt(p_date, Pt(8), Pt(6), Pt(15),
             align=WD_ALIGN_PARAGRAPH.CENTER)
        r4 = p_date.add_run(date)
        sf(r4, '宋体', 13)

    if unit:
        p_unit = doc.add_paragraph()
        pfmt(p_unit, Pt(42), Pt(4), Pt(13),
             align=WD_ALIGN_PARAGRAPH.CENTER)
        r5 = p_unit.add_run(unit)
        sf(r5, '宋体', 11, color=(80, 80, 80))

    section.top_margin = Cm(MARGIN_CM)
    doc.add_page_break()

# ── 文档元素 ────────────────────────────────────────────

def empty(doc):
    p = doc.add_paragraph()
    pfmt(p, Pt(0), Pt(0), LH_BODY)

def h1(doc, text):
    p = doc.add_paragraph()
    pfmt(p, Pt(20), Pt(8), Pt(30), Cm(0),
         WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run(text)
    sf(r, '黑体', 16, bold=True)

def h2(doc, text):
    p = doc.add_paragraph()
    pfmt(p, Pt(14), Pt(6), Pt(22), Cm(0))
    r = p.add_run(text)
    sf(r, '黑体', 14, bold=True)

def h3(doc, text):
    p = doc.add_paragraph()
    pfmt(p, Pt(10), Pt(4), Pt(22), Cm(0))
    r = p.add_run(text)
    sf(r, '黑体', 12, bold=True)

def body(doc, text):
    p = doc.add_paragraph()
    pfmt(p, Pt(2), Pt(2), LH_BODY, INDENT_BODY)
    fmt_text(p, text, '宋体', 12)

# ── 表格 ────────────────────────────────────────────────

def add_table(doc, rows_data):
    if not rows_data:
        return
    ncols = max(len(r) for r in rows_data)
    tbl = doc.add_table(rows=len(rows_data), cols=ncols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'
    widths = col_widths(rows_data)
    set_table_border(tbl, '000000', '6')

    for ri, row_vals in enumerate(rows_data):
        row = tbl.rows[ri]
        is_head = (ri == 0)
        for ci, val in enumerate(row_vals):
            if ci >= ncols:
                break
            cell = row.cells[ci]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_border(cell)
            cell.width = Cm(widths[ci])
            for p in cell.paragraphs:
                p.clear()
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_head else WD_ALIGN_PARAGRAPH.LEFT
            pfmt(p, Pt(2), Pt(2), LH_TABLE,
                 Cm(0) if is_head else INDENT_TABLE)
            fmt_text(p, str(val), '黑体' if is_head else '宋体', 10.5)
            if is_head:
                shade_cell(cell, HDR_FILL)
                for r in p.runs:
                    r.font.bold = True
    return tbl

# ── ASCII 架构图（加灰底背景表格） ──────────────────────

def is_diagram(lines):
    count = sum(1 for l in lines for c in l
                if c in '┌┬┐└┴┘├┼─│┃━╋ ')
    return count >= 8

def add_diagram_as_table(doc, lines, text_w=TEXT_W_CM):
    """
    ASCII 架构图用灰底表格呈现，每行一个段落单元格，
    左对齐，仿宋9.5pt，浅灰底(F2F2F2)，灰边框。
    """
    # 用2列表格：左列留白标签区，右列内容
    tbl = doc.add_table(rows=len(lines), cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl.style = 'Table Grid'

    tblPr = tbl._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        t = OxmlElement(f'w:{edge}')
        t.set(qn('w:val'), 'single')
        t.set(qn('w:sz'), '4')
        t.set(qn('w:space'), '0')
        t.set(qn('w:color'), '999999')
        borders.append(t)
    tblPr.append(borders)

    # 灰底
    shd2 = OxmlElement('w:shd')
    shd2.set(qn('w:val'), 'clear')
    shd2.set(qn('w:color'), 'auto')
    shd2.set(qn('w:fill'), 'F2F2F2')
    tblPr.append(shd2)

    # 列宽 = TEXT_W
    for ri, line in enumerate(lines):
        row = tbl.rows[ri]
        cell = row.cells[0]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        # 单元格灰底
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        cshd = OxmlElement('w:shd')
        cshd.set(qn('w:val'), 'clear')
        cshd.set(qn('w:color'), 'auto')
        cshd.set(qn('w:fill'), 'F2F2F2')
        tcPr.append(cshd)
        # 灰边框
        cborders = OxmlElement('w:tcBorders')
        for edge in ('top', 'left', 'bottom', 'right'):
            et = OxmlElement(f'w:{edge}')
            et.set(qn('w:val'), 'single')
            et.set(qn('w:sz'), '4')
            et.set(qn('w:space'), '0')
            et.set(qn('w:color'), 'AAAAAA')
            cborders.append(et)
        tcPr.append(cborders)
        cell.width = Cm(text_w)

        for p in cell.paragraphs:
            p.clear()
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pfmt(p, Pt(1), Pt(1), LH_CODE, Cm(0))
        r = p.add_run(line.expandtabs(4))
        sf(r, '仿宋', 9.5)

# ── Markdown 解析 ────────────────────────────────────────



# ══════════════════════════════════════════════════════════════
#  matplotlib 架构图生成（自动识别类型并渲染为图片）
# ══════════════════════════════════════════════════════════════

def make_architecture_matplotlib(lines, text_w=TEXT_W_CM):
    all_text = '\n'.join(lines)

    if '感知层' in all_text and '运动层' in all_text:
        return _make_hw_arch_png(lines, text_w)
    elif '三网物理隔离' in all_text or all(x in all_text for x in ['控制网络', '采集网络', '传输网络']):
        return _make_network_arch_png(lines, text_w)
    elif '应用层' in all_text and 'AI算法层' in all_text:
        return _make_sw_arch_png(lines, text_w)
    elif '主显示区' in all_text:
        return _make_hmi_arch_png(lines, text_w)
    else:
        return _make_generic_arch_png(lines, text_w)

def _get_cjk_font():
    import matplotlib.font_manager as fm
    for f in fm.fontManager.ttflist:
        if 'Noto Serif CJK' in f.name:
            return f.fname
    return None

def _make_hw_arch_png(lines, text_w):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import matplotlib.font_manager as fm

    font_path = _get_cjk_font()
    prop = None
    if font_path:
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)

    fig, ax = plt.subplots(1, 1, figsize=(text_w * 0.55, 3.5))
    ax.set_xlim(0, text_w); ax.set_ylim(0, 3.5); ax.axis('off')
    fig.patch.set_facecolor('white')

    outer = FancyBboxPatch((0.3, 0.4), text_w - 0.6, 2.7,
        boxstyle="round,pad=0.06", linewidth=1.2,
        edgecolor='#444444', facecolor='#F7F7F7', zorder=0)
    ax.add_patch(outer)

    cols_data = [
        {'name': '感知层', 'color': '#D9E2F3', 'items': ['摄像模块\n(2×工业相机)', '照明模块\n(频闪补光)', '传感融合\n(IMU+里程计)']},
        {'name': '运动层', 'color': '#E2F0D9', 'items': ['轨底平台\n(4驱动轮+1电缸)', '电动云台\n(双云台俯仰)', '线缆收放\n(自动拖链)']},
        {'name': '计算层', 'color': '#F2D9D9', 'items': ['主控单元\n(Intel i7工控机)', 'AI加速\n(GPU扩展)', '通信单元\n(4G/wifi)']},
        {'name': '交互层', 'color': '#E2D9F2', 'items': ['手持终端\n(Android)', '急停装置\n(硬件保护)', '状态指示\n(LED声光)']},
    ]

    col_w = (text_w - 0.8) / 4
    row_y = [2.85, 1.85, 0.85]

    for ci, col in enumerate(cols_data):
        x = 0.5 + ci * col_w
        title_box = FancyBboxPatch((x + 0.05, 2.95), col_w - 0.1, 0.45,
            boxstyle="round,pad=0.03", linewidth=0.8,
            edgecolor='#666666', facecolor=col['color'], zorder=2)
        ax.add_patch(title_box)
        ax.text(x + col_w/2, 3.175, col['name'],
                ha='center', va='center', fontsize=9, fontweight='bold',
                fontproperties=prop)
        ax.plot([x + col_w, x + col_w], [0.5, 3.3], color='#BBBBBB', linewidth=0.5, linestyle='--', zorder=1)
        for ii, item in enumerate(col['items']):
            item_box = FancyBboxPatch((x + 0.05, row_y[2-ii] - 0.35), col_w - 0.1, 0.55,
                boxstyle="round,pad=0.04", linewidth=0.6,
                edgecolor='#BBBBBB', facecolor='white', zorder=2)
            ax.add_patch(item_box)
            ax.text(x + col_w/2, row_y[2-ii] - 0.08, item,
                    ha='center', va='center', fontsize=7.5, fontproperties=prop or None)

    ax.text(text_w/2, 3.42, '列车底部构件检测机器人 — 硬件系统总体架构',
            ha='center', va='center', fontsize=10, fontweight='bold', fontproperties=prop)

    out_path = f'/tmp/arch_hw_{hash(tuple(lines)) % 100000}.png'
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    return out_path

def _make_network_arch_png(lines, text_w):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import matplotlib.font_manager as fm

    font_path = _get_cjk_font()
    prop = None
    if font_path:
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)

    fig, ax = plt.subplots(1, 1, figsize=(text_w * 0.55, 2.8))
    ax.set_xlim(0, text_w); ax.set_ylim(0, 2.8); ax.axis('off')
    fig.patch.set_facecolor('white')

    outer = FancyBboxPatch((0.3, 0.4), text_w - 0.6, 2.0,
        boxstyle="round,pad=0.06", linewidth=1.2,
        edgecolor='#444444', facecolor='#F7F7F7', zorder=0)
    ax.add_patch(outer)

    nets = [
        {'name': '控制网络\n(EtherCAT)', 'color': '#D9E2F3', 'items': ['伺服驱动\n毫秒级响应', '步进电机\n闭环控制']},
        {'name': '采集网络\n(千兆以太网)', 'color': '#E2F0D9', 'items': ['相机数据\n高速传输', 'AI推理\n实时分析']},
        {'name': '传输网络\n(4G/5G)', 'color': '#F2D9D9', 'items': ['远程监控\n数据上报', '指令下发\n状态回传']},
    ]
    col_w = (text_w - 0.8) / 3
    row_y = [2.1, 1.2, 0.7]

    for ci, net in enumerate(nets):
        x = 0.5 + ci * col_w
        title_box = FancyBboxPatch((x + 0.08, 1.85), col_w - 0.16, 0.55,
            boxstyle="round,pad=0.03", linewidth=0.8,
            edgecolor='#666666', facecolor=net['color'], zorder=2)
        ax.add_patch(title_box)
        ax.text(x + col_w/2, 2.12, net['name'],
                ha='center', va='center', fontsize=8.5, fontweight='bold', fontproperties=prop)
        ax.plot([x + col_w, x + col_w], [0.5, 2.3], color='#BBBBBB', linewidth=0.5, linestyle='--', zorder=1)
        for ii, item in enumerate(net['items']):
            item_box = FancyBboxPatch((x + 0.08, row_y[2-ii] - 0.28), col_w - 0.16, 0.5,
                boxstyle="round,pad=0.04", linewidth=0.6,
                edgecolor='#BBBBBB', facecolor='white', zorder=2)
            ax.add_patch(item_box)
            ax.text(x + col_w/2, row_y[2-ii] - 0.03, item, ha='center', va='center', fontsize=7.5, fontproperties=prop)

    ax.text(text_w/2, 2.62, '三网物理隔离架构', ha='center', va='center', fontsize=10, fontweight='bold', fontproperties=prop)
    out_path = f'/tmp/arch_net_{hash(tuple(lines)) % 100000}.png'
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    return out_path

def _make_sw_arch_png(lines, text_w):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import matplotlib.font_manager as fm

    font_path = _get_cjk_font()
    prop = None
    if font_path:
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)

    fig, ax = plt.subplots(1, 1, figsize=(text_w * 0.55, 3.0))
    ax.set_xlim(0, text_w); ax.set_ylim(0, 3.0); ax.axis('off')
    fig.patch.set_facecolor('white')

    outer = FancyBboxPatch((0.3, 0.4), text_w - 0.6, 2.3,
        boxstyle="round,pad=0.06", linewidth=1.2,
        edgecolor='#444444', facecolor='#F7F7F7', zorder=0)
    ax.add_patch(outer)

    layers = [
        {'name': '应用层', 'color': '#D9E2F3', 'items': ['人机交互', '任务管理', '报告生成', '系统对接']},
        {'name': 'AI算法层', 'color': '#E2F0D9', 'items': ['目标检测', '缺陷识别', '数据融合', '决策推理']},
        {'name': '数据层', 'color': '#F2D9D9', 'items': ['实时采集', '存储管理', '预处理', '安全传输']},
        {'name': '基础层', 'color': '#E2D9F2', 'items': ['操作系统', '设备驱动', '通信中间件', '系统监控']},
    ]
    col_w = (text_w - 0.8) / 4
    row_y = [2.45, 1.7, 0.85]

    for ci, layer in enumerate(layers):
        x = 0.5 + ci * col_w
        title_box = FancyBboxPatch((x + 0.05, 2.5), col_w - 0.1, 0.4,
            boxstyle="round,pad=0.03", linewidth=0.8,
            edgecolor='#666666', facecolor=layer['color'], zorder=2)
        ax.add_patch(title_box)
        ax.text(x + col_w/2, 2.7, layer['name'], ha='center', va='center', fontsize=9, fontweight='bold', fontproperties=prop)
        ax.plot([x + col_w, x + col_w], [0.5, 2.8], color='#BBBBBB', linewidth=0.5, linestyle='--', zorder=1)
        for ii, item in enumerate(layer['items']):
            item_box = FancyBboxPatch((x + 0.05, row_y[2-ii] - 0.28), col_w - 0.1, 0.48,
                boxstyle="round,pad=0.04", linewidth=0.6,
                edgecolor='#BBBBBB', facecolor='white', zorder=2)
            ax.add_patch(item_box)
            ax.text(x + col_w/2, row_y[2-ii] - 0.04, item, ha='center', va='center', fontsize=7.5, fontproperties=prop)

    ax.text(text_w/2, 2.92, '软件系统总体架构', ha='center', va='center', fontsize=10, fontweight='bold', fontproperties=prop)
    out_path = f'/tmp/arch_sw_{hash(tuple(lines)) % 100000}.png'
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    return out_path

def _make_hmi_arch_png(lines, text_w):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import matplotlib.font_manager as fm

    font_path = _get_cjk_font()
    prop = None
    if font_path:
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)

    fig, ax = plt.subplots(1, 1, figsize=(text_w * 0.55, 3.2))
    ax.set_xlim(0, text_w); ax.set_ylim(0, 3.2); ax.axis('off')
    fig.patch.set_facecolor('white')

    outer = FancyBboxPatch((0.3, 0.4), text_w - 0.6, 2.5,
        boxstyle="round,pad=0.06", linewidth=1.2,
        edgecolor='#444444', facecolor='#F7F7F7', zorder=0)
    ax.add_patch(outer)

    main_box = FancyBboxPatch((0.5, 0.5), text_w * 0.55, 1.6,
        boxstyle="round,pad=0.06", linewidth=1.0,
        edgecolor='#888888', facecolor='#D9E2F3', zorder=2)
    ax.add_patch(main_box)
    ax.text(text_w * 0.30 + 0.25, 1.75, '主显示区（>=4K）', ha='center', va='center', fontsize=8, fontweight='bold', fontproperties=prop)
    ax.text(text_w * 0.30 + 0.25, 1.55, '实时视频 / 局部放大 / 画中画 / 冻结', ha='center', va='center', fontsize=7, fontproperties=prop)

    left_box = FancyBboxPatch((0.5, 2.2), text_w * 0.25, 0.55,
        boxstyle="round,pad=0.04", linewidth=0.8, edgecolor='#888888', facecolor='#E2F0D9', zorder=2)
    ax.add_patch(left_box)
    ax.text(text_w * 0.125 + 0.25, 2.47, '状态栏\n(电量/里程/模式)', ha='center', va='center', fontsize=7.5, fontproperties=prop)

    right_box = FancyBboxPatch((text_w * 0.30 + 0.55, 2.2), text_w * 0.25, 0.55,
        boxstyle="round,pad=0.04", linewidth=0.8, edgecolor='#888888', facecolor='#F2D9D9', zorder=2)
    ax.add_patch(right_box)
    ax.text(text_w * 0.425 + 0.55, 2.47, '控制栏\n(快捷操作/告警)', ha='center', va='center', fontsize=7.5, fontproperties=prop)

    bottom_box = FancyBboxPatch((0.5, 0.5), text_w * 0.55, 0.55,
        boxstyle="round,pad=0.04", linewidth=0.8, edgecolor='#888888', facecolor='#E2D9F2', zorder=2)
    ax.add_patch(bottom_box)
    ax.text(text_w * 0.30 + 0.25, 0.77, '任务列表 / 检测结果 / 导出操作', ha='center', va='center', fontsize=7.5, fontproperties=prop)

    ax.text(text_w/2, 3.02, 'HMI 界面布局', ha='center', va='center', fontsize=10, fontweight='bold', fontproperties=prop)
    out_path = f'/tmp/arch_hmi_{hash(tuple(lines)) % 100000}.png'
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    return out_path

def _make_generic_arch_png(lines, text_w):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import matplotlib.font_manager as fm

    font_path = _get_cjk_font()
    prop = None
    if font_path:
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)

    h = max(2.5, len(lines) * 0.35)
    fig, ax = plt.subplots(1, 1, figsize=(text_w * 0.55, h))
    ax.set_xlim(0, text_w); ax.set_ylim(0, h); ax.axis('off')
    fig.patch.set_facecolor('white')

    expanded = [l.expandtabs(4) for l in lines]
    for ri, line in enumerate(expanded):
        y = h - ri * 0.32
        bg = FancyBboxPatch((0.3, y - 0.22), text_w - 0.6, 0.28,
            boxstyle="round,pad=0.02", linewidth=0.5,
            edgecolor='#CCCCCC', facecolor='#F9F9F9', zorder=0)
        ax.add_patch(bg)
        ax.text(0.5, y - 0.08, line, ha='left', va='center', fontsize=8, fontproperties=prop or None)

    out_path = f'/tmp/arch_generic_{hash(tuple(lines)) % 100000}.png'
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    return out_path

def add_arch_image(doc, lines, text_w=TEXT_W_CM):
    """将架构图转为图片并插入文档"""
    try:
        img_path = make_architecture_matplotlib(lines, text_w)
        if img_path and os.path.exists(img_path):
            p = doc.add_paragraph()
            pfmt(p, Pt(8), Pt(8), Pt(14), Cm(0))
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(img_path, width=Cm(text_w * 0.95))
            try:
                os.remove(img_path)
            except:
                pass
    except Exception:
        add_diagram_as_table(doc, lines, text_w)



def parse_md(doc, lines):
    i = 0
    tbl_buf = []
    in_tbl = False

    while i < len(lines):
        line = lines[i].rstrip('\n')
        i += 1

        if line.startswith('# ') and i == 2:
            continue

        if line.startswith('## '):
            if in_tbl and tbl_buf:
                add_table(doc, tbl_buf); tbl_buf = []; in_tbl = False
            h1(doc, line[3:].strip())

        elif line.startswith('### '):
            if in_tbl and tbl_buf:
                add_table(doc, tbl_buf); tbl_buf = []; in_tbl = False
            h2(doc, line[4:].strip())

        elif line.startswith('#### '):
            if in_tbl and tbl_buf:
                add_table(doc, tbl_buf); tbl_buf = []; in_tbl = False
            h3(doc, line[4:].strip())

        elif line.strip().startswith('```'):
            if in_tbl and tbl_buf:
                add_table(doc, tbl_buf); tbl_buf = []; in_tbl = False
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i].rstrip('\n'))
                i += 1
            i += 1
            if code_lines:
                empty(doc)
                if is_diagram(code_lines):
                    add_arch_image(doc, code_lines)
                else:
                    for ln in code_lines:
                        p = doc.add_paragraph()
                        pfmt(p, Pt(1), Pt(1), LH_CODE, Cm(1.5))
                        r = p.add_run(ln)
                        sf(r, '仿宋', 10)
                empty(doc)

        elif line.startswith('|') and line.endswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if cells and all(re.match(r'^[-: ]+$', c) for c in cells):
                continue
            tbl_buf.append(cells)
            in_tbl = True

        elif not line.strip():
            if in_tbl and tbl_buf:
                add_table(doc, tbl_buf); tbl_buf = []; in_tbl = False
            empty(doc)

        else:
            if in_tbl and tbl_buf:
                add_table(doc, tbl_buf); tbl_buf = []; in_tbl = False
            body(doc, line)

    if in_tbl and tbl_buf:
        add_table(doc, tbl_buf)

# ── 核心函数 ────────────────────────────────────────────

def setup_page(doc):
    section = doc.sections[0]
    section.page_width    = Cm(PAGE_W_CM)
    section.page_height   = Cm(PAGE_H_CM)
    section.top_margin    = Cm(MARGIN_CM)
    section.bottom_margin = Cm(MARGIN_CM)
    section.left_margin   = Cm(MARGIN_CM)
    section.right_margin  = Cm(MARGIN_CM)
    add_page_numbers(doc)

def md_to_docx(md_path, docx_path, title='', sub='', date='', unit=''):
    doc = Document()
    setup_page(doc)
    if title:
        add_cover(doc, title, sub, date, unit)
    else:
        with open(md_path, encoding='utf-8') as f:
            first = f.readline().strip()
        if first.startswith('# '):
            add_cover(doc, first[2:].strip())
    with open(md_path, encoding='utf-8') as f:
        lines = f.readlines()
    parse_md(doc, lines)
    doc.save(docx_path)
    return docx_path

def merge_to_docx(folder, docx_path, title='', sub='', date='', unit=''):
    files = sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith('.md')
    ])
    doc = Document()
    setup_page(doc)
    if title:
        add_cover(doc, title, sub, date, unit)
    for fpath in files:
        with open(fpath, encoding='utf-8') as f:
            lines = f.readlines()
        parse_md(doc, lines)
        empty(doc)
    doc.save(docx_path)
    return docx_path

# ── CLI ────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('src')
    parser.add_argument('dst')
    parser.add_argument('--cover', nargs='+', default=[])
    args = parser.parse_args()

    cov = args.cover
    title = cov[0] if len(cov) > 0 else ''
    sub   = cov[1] if len(cov) > 1 else ''
    date  = cov[2] if len(cov) > 2 else ''
    unit  = cov[3] if len(cov) > 3 else ''

    if os.path.isdir(args.src):
        r = merge_to_docx(args.src, args.dst, title, sub, date, unit)
    else:
        r = md_to_docx(args.src, args.dst, title, sub, date, unit)

    sz = os.path.getsize(r)
    print(f'OK: {r}  ({sz/1024:.1f} KB)')
