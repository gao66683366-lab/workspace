---
name: rail-inspection-fps
description: 铁路检测机器人2D工业相机与3D线激光采样节拍/帧率计算。用于按速度、视场、重叠率、里程触发间隔快速给出可执行参数表。
---

# Rail Inspection FPS

## Inputs
- 速度范围 v_min, v_nom, v_max (m/s)
- 轨向视场长度 L (m)
- 重叠率 r (0~1)
- 里程触发间隔 d (m)
- 允许模糊 b (mm)

## Core equations
1. 连续采样下限：
\[
f_{cont}=\frac{v}{(1-r)L}
\]

2. 位置触发频率：
\[
f_{pos}=\frac{v}{d}
\]

3. 曝光约束（运动模糊）：
\[
t_{exp} \le \frac{b}{v}
\]

4. 工程建议：
\[
f_{set}=\max(f_{cont}, f_{pos}, f_{biz})\times k_{margin}
\]
其中 `k_margin` 建议 1.2~2.0。

## Project defaults (current)
- v_max = 1.0 m/s（3.6 km/h）
- 轨头轨面宽度：70.8 mm（工程可取 72 mm）
- 建议先验：轨面相机 20 fps，螺栓相机 25 fps

## Output template
- CAM编号
- 触发模式（连续/里程触发/混合）
- 目标帧率（fps）
- 曝光上限（us）
- 验收条件（ResultingFrameRateAbs、丢帧率、拖影）
