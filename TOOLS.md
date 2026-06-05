# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Word 文档生成（永久工具）

### 工具路径
`/root/.openclaw/workspace/word_tools/docx_gen.py`（完整版，含架构图自动渲染）
`/root/.openclaw/workspace/build_minimal.py`（无matplotlib轻量版，生成更快更稳）

### 标准生成流程（必须固化！）

**第一步**：先确认MD文件中没有会导致内存溢出的内容：
- 架构图ASCII格式（`┌┬┐`类字符块）→ 会触发matplotlib渲染，内存杀手，**必须先替换为正文描述或单行文字**
- 超大代码块 → 逐个文件检查，控制总代码行数

**第二步**：用轻量版 `build_minimal.py` 生成（推荐），或完整版 `docx_gen.py`：
```bash
python3 build_minimal.py
# 或完整版（内存充足时）：
python3 word_tools/docx_gen.py <md文件夹/> <输出.docx> \
  --cover "文档标题" "副标题" "日期" "单位"
```

**⚠️ 内存警告**：生成前用 `free -m` 确认可用内存 ≥ 200MB。内存不足时（<200MB），必须用 `build_minimal.py`（无架构图渲染）而非完整版。

### 排版规范（生成时自动应用）
- 封面：黑体28pt大标题 + 副标题黑体18pt + 分隔线 + 日期(黑体13pt) + 单位(黑体11pt)，居中
- 页码：页脚居中，Word打开后自动更新 `当前页 / 总页数`
- 页面：A4，边距2.54cm
- 一级标题(#)：黑体16pt居中，段前20pt/段后8pt
- 二级标题(##)：黑体14pt左对齐，段前14pt/段后6pt
- 三级标题(###)：黑体12pt，段前10pt/段后4pt
- 正文：宋体12pt，首行缩进0.74cm，行距22pt
- 表格：表头蓝底(D9E2F3)+黑体粗体11.5pt；正文宋体10.5pt，行距17pt；列宽按内容比例分配
- `**粗体**` → Word粗体，`行内代码` → 斜体

### 常见问题
- **SIGKILL / 内存溢出**：MD文件含ASCII架构图，触发matplotlib渲染 → 先移除架构图代码块，换用build_minimal.py
- **排版乱**：表格列宽不均 → 使用col_widths()函数按内容比例分配
- **字体发虚**：宋体/黑体未嵌入 → Word打开后手动选"嵌入字体"或转PDF
