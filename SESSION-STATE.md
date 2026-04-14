# SESSION-STATE.md

> 当前主动工作记忆（WAL 主入口）。任何关键纠正、明确决策、具体数值、当前主线，都应先写这里，再回复。

## 当前状态
- 状态：active
- 最后更新时间：2026-03-11 19:46 GMT+8

## 当前主线
1. 已建立并接入本地记忆系统（SQLite + 本地向量索引）。
2. 已安装并接入 self-improving-agent。
3. 已安装 proactive-agent，当前正在做全接入。
4. 后续需要按 proactive-agent 的 WAL / Working Buffer / Recovery 机制维护连续性。

## 当前关键约束
- 中文沟通。
- 不能失忆，不能前后口径打架，不能说胡话。
- 先对齐资料和参数，再继续推演。
- 边处理边展示过程。

## 最近明确决策
- 记忆系统采用：向量数据库 + SQLite 双层方案。
- 已安装技能：self-improving-agent、desearch-web-search、proactive-agent。
- proactive-agent 要求按“全接入”执行，而不是只安装。

## 下一步
- 把 proactive-agent 的工作流文件和脚本接齐。
- 把这些入口并入当前记忆体系。
- 后续有新的关键纠正/决策，优先写入这里。

### [2026/3/11 19:48:35] integration
- proactive-agent 已按全接入方式补齐 SESSION-STATE、working-buffer 与恢复入口
