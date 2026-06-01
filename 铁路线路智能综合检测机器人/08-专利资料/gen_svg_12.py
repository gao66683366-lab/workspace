#!/usr/bin/env python3
# gen_figs_svg.py - 用SVG生成5张专利附图，转PNG
import cairosvg
import os

OUT = '/root/.openclaw/media/tool-image-generation/'
SVG_DIR = '/tmp/patent_figs/'
os.makedirs(SVG_DIR, exist_ok=True)

def render(name):
    svg_path = f'{SVG_DIR}{name}.svg'
    png_path = f'{OUT}{name}.png'
    cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=180)
    print(f'Rendered: {name}.png')
    return png_path

# ============================================================
# 图1：系统总体架构
# ============================================================
svg1 = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1200">
<rect width="2000" height="1200" fill="white"/>
<!-- 主标题 -->
<text x="1000" y="90" font-family="Noto Sans CJK JP, sans-serif" font-size="36" font-weight="bold" text-anchor="middle" fill="#1a1a1a">铁路线路智能视觉与多模态感知融合综合检测系统</text>
<line x1="40" y1="115" x2="1960" y2="115" stroke="#ccc" stroke-width="2"/>
<!-- 感知层 -->
<rect x="40" y="160" width="1920" height="360" rx="12" fill="#EBF5FB" stroke="#6A9BBF" stroke-width="3"/>
<text x="80" y="200" font-family="Noto Sans CJK JP, sans-serif" font-size="26" font-weight="bold" fill="#2A5A8A">感知层</text>
<!-- 感知层6个模块 -->
<g>
<rect x="80" y="250" width="280" height="250" rx="10" fill="#D0E8F8" stroke="#1A6FA8" stroke-width="3"/>
<text x="220" y="310" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">6路2D工业相机</text>
<text x="220" y="350" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">2448×2048  20fps</text>
<text x="220" y="380" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">千兆以太网</text>
<text x="220" y="410" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">轨面缺陷×2</text>
<text x="220" y="435" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">道钉螺栓×2·焊缝×2</text>
</g>
<g>
<rect x="380" y="250" width="280" height="250" rx="10" fill="#D0E8F8" stroke="#1A6FA8" stroke-width="3"/>
<text x="520" y="310" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">3D线激光×2</text>
<text x="520" y="350" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">20000Hz  3200点/轮廓</text>
<text x="520" y="380" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">IP67防护等级</text>
<text x="520" y="410" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">左右钢轨轨头轮廓扫描</text>
</g>
<g>
<rect x="680" y="250" width="280" height="250" rx="10" fill="#D0E8F8" stroke="#1A6FA8" stroke-width="3"/>
<text x="820" y="310" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">HWT905姿态传感器</text>
<text x="820" y="355" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">200Hz  三轴0.05°</text>
<text x="820" y="385" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">IEEE 1588 PTP同步</text>
</g>
<g>
<rect x="980" y="250" width="280" height="250" rx="10" fill="#D0E8F8" stroke="#1A6FA8" stroke-width="3"/>
<text x="1120" y="310" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">单点测距传感器×2</text>
<text x="1120" y="355" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">2000Hz  精度±0.15mm</text>
<text x="1120" y="385" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">仅用于高低检测</text>
</g>
<g>
<rect x="1280" y="250" width="280" height="250" rx="10" fill="#A8CCE8" stroke="#0D4A8A" stroke-width="3"/>
<text x="1420" y="310" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">测距传感器矩阵</text>
<text x="1420" y="355" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">直接测轨距</text>
<text x="1420" y="385" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">G=dL+dR 与横滚角解耦</text>
<text x="1420" y="410" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">±0.3mm</text>
</g>
<g>
<rect x="1580" y="250" width="280" height="250" rx="10" fill="#D8F0E0" stroke="#1E7A3C" stroke-width="3"/>
<text x="1720" y="310" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">编码器</text>
<text x="1720" y="355" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">100脉冲/帧</text>
<text x="1720" y="385" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">分辨率≈5mm</text>
</g>
<!-- 连接线 -->
<line x1="220" y1="160" x2="220" y2="200" stroke="#6A9BBF" stroke-width="2" stroke-dasharray="8,4"/>
<line x1="520" y1="160" x2="520" y2="200" stroke="#6A9BBF" stroke-width="2" stroke-dasharray="8,4"/>
<line x1="820" y1="160" x2="820" y2="200" stroke="#6A9BBF" stroke-width="2" stroke-dasharray="8,4"/>
<line x1="1120" y1="160" x2="1120" y2="200" stroke="#6A9BBF" stroke-width="2" stroke-dasharray="8,4"/>
<line x1="1420" y1="160" x2="1420" y2="200" stroke="#6A9BBF" stroke-width="2" stroke-dasharray="8,4"/>
<line x1="1720" y1="160" x2="1720" y2="200" stroke="#6A9BBF" stroke-width="2" stroke-dasharray="8,4"/>
<!-- 计算层 -->
<rect x="40" y="540" width="1920" height="240" rx="12" fill="#D8F0E0" stroke="#6A9BBF" stroke-width="3"/>
<text x="80" y="580" font-family="Noto Sans CJK JP, sans-serif" font-size="26" font-weight="bold" fill="#2A6A3A">计算层</text>
<g>
<rect x="80" y="610" width="400" height="155" rx="10" fill="#B8E0C8" stroke="#1E7A3C" stroke-width="3"/>
<text x="280" y="655" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">工控机 IP54</text>
<text x="280" y="695" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">Jetson AGX Orin</text>
<text x="280" y="725" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">融合判定单元</text>
</g>
<g>
<rect x="500" y="610" width="450" height="155" rx="10" fill="#98D0A8" stroke="#155C28" stroke-width="3"/>
<text x="725" y="655" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">融合判定单元 三级融合</text>
<text x="725" y="700" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">时间对齐→空间关联→判级融合</text>
<text x="725" y="730" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">自适应动态加权几何平均</text>
</g>
<g>
<rect x="970" y="610" width="450" height="155" rx="10" fill="#98D0A8" stroke="#155C28" stroke-width="3"/>
<text x="1195" y="655" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">环形缓冲区 帧边界对齐</text>
<text x="1195" y="700" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">三键索引元组</text>
<text x="1195" y="730" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">D(FID, s, t)</text>
</g>
<g>
<rect x="1440" y="610" width="400" height="155" rx="10" fill="#FFE8C0" stroke="#B86A00" stroke-width="3"/>
<text x="1640" y="655" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">通信模块 4G/5G</text>
<text x="1640" y="700" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">远程监控</text>
<text x="1640" y="730" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#333">数据上传</text>
</g>
<!-- 供电层 -->
<rect x="40" y="800" width="1920" height="130" rx="12" fill="#EDE0F5" stroke="#6A9BBF" stroke-width="3"/>
<text x="80" y="845" font-family="Noto Sans CJK JP, sans-serif" font-size="26" font-weight="bold" fill="#6A2A8A">供电层</text>
<rect x="80" y="860" width="1840" height="80" rx="8" fill="#D0B8E8" stroke="#7A1A9A" stroke-width="3"/>
<text x="1000" y="910" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#5A0A7A">供电模块  48V大容量蓄电池组  智能电源管理  BMS板/管理板温度三级保护</text>
<!-- 底部指标 -->
<rect x="40" y="960" width="1920" height="190" rx="10" fill="#F8F8F8" stroke="#BBB" stroke-width="2"/>
<text x="1000" y="1005" font-family="Noto Sans CJK JP, sans-serif" font-size="24" font-weight="bold" text-anchor="middle" fill="#222">核心性能指标（济南铁路局120km以上实际线路验证）</text>
<text x="300" y="1060" font-family="Noto Sans CJK JP, sans-serif" font-size="22" fill="#1E7A3C">融合判定准确率97.5%</text>
<text x="680" y="1060" font-family="Noto Sans CJK JP, sans-serif" font-size="22" fill="#1E7A3C">传感器退化场景96.1%</text>
<text x="1080" y="1060" font-family="Noto Sans CJK JP, sans-serif" font-size="22" fill="#1A6FA8">空间对齐精度3.2mm（降低74.7%）</text>
<text x="1500" y="1060" font-family="Noto Sans CJK JP, sans-serif" font-size="22" fill="#1A6FA8">轨面缺陷mAP@0.5=92.5%</text>
<text x="1850" y="1060" font-family="Noto Sans CJK JP, sans-serif" font-size="22" fill="#B86A00">振动噪声降低53.7%</text>
<text x="1000" y="1105" font-family="Noto Sans CJK JP, sans-serif" font-size="18" text-anchor="middle" fill="#666">检测速度：0.5m/s（精细检测）/1m/s（常规检测） | 三网物理隔离：EtherCAT控制网+千兆采集网+无线传输网</text>
</svg>"""

svg2 = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1800 1100">
<rect width="1800" height="1100" fill="white"/>
<text x="900" y="85" font-family="Noto Sans CJK JP, sans-serif" font-size="34" font-weight="bold" text-anchor="middle" fill="#1a1a1a">三键索引时空对齐机制示意图</text>
<line x1="40" y1="110" x2="1760" y2="110" stroke="#ccc" stroke-width="2"/>
<!-- 三键索引输入 -->
<g>
<rect x="50" y="150" width="480" height="300" rx="12" fill="#D0E8F8" stroke="#1A6FA8" stroke-width="3"/>
<text x="290" y="210" font-family="Noto Sans CJK JP, sans-serif" font-size="26" font-weight="bold" text-anchor="middle" fill="#1a1a1a">编码器</text>
<text x="290" y="260" font-family="Noto Sans CJK JP, sans-serif" font-size="18" text-anchor="middle" fill="#333">100脉冲/帧</text>
<text x="290" y="295" font-family="Noto Sans CJK JP, sans-serif" font-size="18" text-anchor="middle" fill="#333">生成帧编号FIDk</text>
<text x="290" y="330" font-family="Noto Sans CJK JP, sans-serif" font-size="18" text-anchor="middle" fill="#333">分辨率≈5mm/帧</text>
<line x1="290" y1="450" x2="290" y2="500" stroke="#888" stroke-width="3" marker-end="url(#arr)"/>
</g>
<g>
<rect x="630" y="150" width="480" height="300" rx="12" fill="#D8F0E0" stroke="#1E7A3C" stroke-width="3"/>
<text x="870" y="210" font-family="Noto Sans CJK JP, sans-serif" font-size="26" font-weight="bold" text-anchor="middle" fill="#1a1a1a">PTP时钟同步 IEEE 1588</text>
<text x="870" y="265" font-family="Noto Sans CJK JP, sans-serif" font-size="18" text-anchor="middle" fill="#333">UTC时间戳</text>
<text x="870" y="300" font-family="Noto Sans CJK JP, sans-serif" font-size="18" text-anchor="middle" fill="#333">精度优于1μs</text>
<text x="870" y="335" font-family="Noto Sans CJK JP, sans-serif" font-size="18" text-anchor="middle" fill="#333">跨传感器时间统一</text>
<line x1="870" y1="450" x2="870" y2="500" stroke="#888" stroke-width="3"/>
</g>
<g>
<rect x="1210" y="150" width="480" height="300" rx="12" fill="#FFF0D8" stroke="#B86A00" stroke-width="3"/>
<text x="1450" y="210" font-family="Noto Sans CJK JP, sans-serif" font-size="26" font-weight="bold" text-anchor="middle" fill="#1a1a1a">里程标定（标准轨段）</text>
<text x="1450" y="265" font-family="Noto Sans CJK JP, sans-serif" font-size="18" text-anchor="middle" fill="#333">消除轮径磨损误差</text>
<text x="1450" y="300" font-family="Noto Sans CJK JP, sans-serif" font-size="18" text-anchor="middle" fill="#333">消除打滑引入误差</text>
<text x="1450" y="335" font-family="Noto Sans CJK JP, sans-serif" font-size="18" text-anchor="middle" fill="#333">帧号→里程映射</text>
<line x1="1450" y1="450" x2="1450" y2="500" stroke="#888" stroke-width="3"/>
</g>
<!-- 三键索引元组核心 -->
<rect x="350" y="510" width="1100" height="320" rx="15" fill="#FFF0D8" stroke="#B86A00" stroke-width="4"/>
<text x="900" y="575" font-family="Noto Sans CJK JP, sans-serif" font-size="32" font-weight="bold" text-anchor="middle" fill="#B86A00">三键索引元组  D(FIDk, sk, tk)</text>
<text x="900" y="640" font-family="Noto Sans CJK JP, sans-serif" font-size="22" text-anchor="middle" fill="#555">帧编号 FIDk  ·  里程坐标 sk  ·  UTC时间戳 tk</text>
<text x="900" y="705" font-family="Noto Sans CJK JP, sans-serif" font-size="20" text-anchor="middle" fill="#777">帧边界精确对齐 → 多传感器硬件级时空统一</text>
<line x1="900" y1="830" x2="900" y2="890" stroke="#B86A00" stroke-width="4"/>
<!-- 输出 -->
<g>
<rect x="50" y="910" width="310" height="110" rx="8" fill="#B8E0C8" stroke="#1E7A3C" stroke-width="3"/>
<text x="205" y="955" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">2D工业相机×6</text>
<text x="205" y="990" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#555">20fps  帧触发曝光</text>
</g>
<g>
<rect x="380" y="910" width="310" height="110" rx="8" fill="#B8E0C8" stroke="#1E7A3C" stroke-width="3"/>
<text x="535" y="955" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">3D线激光×2</text>
<text x="535" y="990" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#555">20000Hz  帧中心采样</text>
</g>
<g>
<rect x="710" y="910" width="310" height="110" rx="8" fill="#A8CCE8" stroke="#0D4A8A" stroke-width="3"/>
<text x="865" y="955" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">HWT905</text>
<text x="865" y="990" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#555">200Hz  帧边界对齐</text>
</g>
<g>
<rect x="1040" y="910" width="310" height="110" rx="8" fill="#A8CCE8" stroke="#0D4A8A" stroke-width="3"/>
<text x="1195" y="955" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">单点测距×2</text>
<text x="1195" y="990" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#555">2000Hz  最近值采样</text>
</g>
<g>
<rect x="1370" y="910" width="320" height="110" rx="8" fill="#D0B8E8" stroke="#7A1A9A" stroke-width="3"/>
<text x="1530" y="955" font-family="Noto Sans CJK JP, sans-serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#1a1a1a">测距矩阵</text>
<text x="1530" y="990" font-family="Noto Sans CJK JP, sans-serif" font-size="17" text-anchor="middle" fill="#555">约1000Hz  帧边界同步</text>
</g>
<text x="900" y="1065" font-family="Noto Sans CJK JP, sans-serif" font-size="18" text-anchor="middle" fill="#666">8种传感器数据帧边界精确对齐 · 空间对齐精度亚毫米级（平均偏差3.2mm，降低74.7%）· 济南铁路局120km以上验证</text>
</svg>"""

with open(f'{SVG_DIR}fig1.svg', 'w') as f:
    f.write(svg1)
with open(f'{SVG_DIR}fig2.svg', 'w') as f:
    f.write(svg2)
print(f"Wrote SVG files to {SVG_DIR}")
render("fig1")
render("fig2")
print("Done fig1-2")