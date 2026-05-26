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

**工具路径：** `/root/.openclaw/workspace/word_tools/docx_gen.py`

**用法：**
```bash
# 合并文件夹内所有md为一个docx（自动封面+页码）
python3 /root/.openclaw/workspace/word_tools/docx_gen.py \
  "/path/to/md/" \
  "/path/to/output.docx" \
  --cover "文档标题" "副标题" "日期" "单位"
```

**排版规范（自动应用）：**
- 封面：黑体28pt大标题 + 副标题 + 分隔线 + 日期 + 单位，居中布局
- 页码：页脚居中 `当前页 / 总页数`，Word打开后自动更新
- 页面：A4，边距2.54cm
- 一级标题(##)：黑体16pt居中，段前20pt/段后8pt
- 二级标题(###)：黑体14pt，段前14pt/段后6pt
- 三级标题(####)：黑体12pt，段前10pt/段后4pt
- 正文：宋体12pt，首行缩进0.74cm，行距22pt
- 代码块（非架构图）：仿宋10pt，左缩进1.5cm
- ASCII架构图 → matplotlib图片（支持V1.0四层/五层硬件架构、网络三网隔离、软件四层、HMI、数据流、核心价值等类型）
- 表格：列宽按内容比例分配；表头蓝底(D9E2F3)+黑体粗体；正文宋体10.5pt
- `**粗体**` → Word粗体，`` `行内代码` `` → Word斜体

**重要：生成 Word 统一用此工具，不手工写 python-docx 代码。**
