# Skills Gap Plan (2026-03-08)

## Objective
在不依赖 ClawHub 登录的前提下，先保证当前项目能力可用；登录恢复后再做官方同步。

## Current conclusion
- 当前并非“完全缺 skill”，而是“无法登录导致无法从 ClawHub 继续安装/更新”。
- 已安装技能足以覆盖当前铁路项目主线：
  - `senior-computer-vision`
  - `computer-vision-expert`
  - `engineering`
  - `architecture-designer`
  - `DOCX`
  - `mermaid-diagrams`
  - Feishu 系列 skills

## Immediate fallback strategy (no login)
1. 优先使用已安装技能，不中断工作流。
2. 若出现能力缺口，直接在 `workspace/skills/<skill-name>/SKILL.md` 本地补齐等效 skill。
3. 对关键产物（参数表、算法说明、文档模板）先落地为项目文档，不等待 ClawHub。

## When login is available
按顺序执行：
1. `clawhub login --token <TOKEN> --no-browser`
2. `clawhub whoami`
3. `clawhub update --all --no-input --force`
4. 按需安装新增 skill（逐项验证）。

## Suggested first additions (if you want me to local-create now)
- `rail-inspection-fps`：轨面/螺栓帧率与触发参数计算模板
- `rail-doc-packager`：将算法结果自动整理为 Word 定稿格式
- `rail-sync-diagnostics`：Frame ID/里程脉冲一致性检查流程
