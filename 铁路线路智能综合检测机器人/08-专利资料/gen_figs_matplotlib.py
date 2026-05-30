#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'SimHei', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = '/root/.openclaw/media/tool-image-generation/'

def save(fig, name):
    fig.savefig(f'{OUTPUT_DIR}{name}', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved: {name}')

# ===== 图1：系统总体架构图 =====
fig, ax = plt.subplots(1, 1, figsize=(14, 8))
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis('off')
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

ax.text(7, 7.6, '铁路线路智能视觉与多模态感知融合综合检测系统', 
        ha='center', va='center', fontsize=13, fontweight='bold',
        fontfamily='Noto Sans CJK SC')

# 分层背景
layers = [
    (0.3, 5.4, 13.4, 1.5, '#E3F2FD', '感知层'),
    (0.3, 3.8, 13.4, 1.3, '#E8F5E9', '计算层'),
    (0.3, 2.5, 13.4, 1.1, '#FFF3E0', '通信层'),
    (0.3, 1.4, 13.4, 0.9, '#F3E5F5', '供电层'),
]

for x, y, w, h, c, label in layers:
    rect = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05',
                          facecolor=c, edgecolor='#90A4AE', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + 0.2, y + h - 0.15, label, fontsize=8, color='#555', va='top', fontfamily='Noto Sans CJK SC')

# 感知层内容
感知层_items = [
    ('6路2D工业相机', '2448×2048\n20fps\n千兆以太网', 1.0, 5.55),
    ('HWT905\n姿态传感器', '200Hz采样\n三轴0.05°\nPTP同步', 4.5, 5.55),
    ('3D线激光\n传感器×2', '20000Hz\n3200点/轮廓\nIP67', 6.8, 5.55),
    ('单点测距\n传感器×2', '2000Hz\n±0.15mm', 9.0, 5.55),
    ('测距传感器\n矩阵', '直接测轨距\n与横滚角解耦', 11.2, 5.55),
]

for label, detail, x, y in 感知层_items:
    box = FancyBboxPatch((x, y), 2.1, 1.15, boxstyle='round,pad=0.1',
                         facecolor='#BBDEFB', edgecolor='#1976D2', linewidth=1.2)
    ax.add_patch(box)
    ax.text(x + 1.05, y + 0.95, label, ha='center', va='top', fontsize=7.5, 
            fontweight='bold', fontfamily='Noto Sans CJK SC')
    ax.text(x + 1.05, y + 0.35, detail, ha='center', va='center', fontsize=6.5, 
            color='#333', fontfamily='Noto Sans CJK SC')

# 感知层上方标签
ax.text(2.05, 6.72, '轨面缺陷×2\n道钉螺栓×2\n焊缝×2', ha='center', va='top', fontsize=6, color='#555', fontfamily='Noto Sans CJK SC')

# 计算层
calc_items = [
    ('工控机\nIP54防护', 1.5, 4.05),
    ('融合判定单元\n三级融合', 5.5, 4.05),
    ('环形缓冲区\n帧边界对齐', 9.5, 4.05),
]
for label, x, y in calc_items:
    box = FancyBboxPatch((x, y), 3.0, 0.95, boxstyle='round,pad=0.1',
                         facecolor='#C8E6C9', edgecolor='#388E3C', linewidth=1.2)
    ax.add_patch(box)
    ax.text(x + 1.5, y + 0.5, label, ha='center', va='center', fontsize=7.5,
            fontweight='bold', fontfamily='Noto Sans CJK SC')

# 通信层
comm_items = [
    ('通信模块\n4G/5G无线', 1.5, 2.6),
    ('编码器\n帧触发+里程', 5.5, 2.6),
]
for label, x, y in comm_items:
    box = FancyBboxPatch((x, y), 3.0, 0.85, boxstyle='round,pad=0.1',
                         facecolor='#FFE0B2', edgecolor='#F57C00', linewidth=1.2)
    ax.add_patch(box)
    ax.text(x + 1.5, y + 0.43, label, ha='center', va='center', fontsize=7.5,
            fontweight='bold', fontfamily='Noto Sans CJK SC')

# 供电层
power_items = [
    ('供电模块\n48V大容量蓄电池组\n智能电源管理', 1.5, 1.45),
]
for label, x, y in power_items:
    box = FancyBboxPatch((x, y), 10.5, 0.75, boxstyle='round,pad=0.1',
                         facecolor='#E1BEE7', edgecolor='#7B1FA2', linewidth=1.2)
    ax.add_patch(box)
    ax.text(x + 5.25, y + 0.38, label, ha='center', va='center', fontsize=7.5,
            fontweight='bold', fontfamily='Noto Sans CJK SC')

# 右侧标注
ax.text(13.5, 6.2, '检测速度\n0.5m/s(精细)\n1m/s(常规)', ha='right', va='top', fontsize=7, color='#555', fontfamily='Noto Sans CJK SC')
ax.text(13.5, 4.5, '覆盖8项\n检测功能', ha='right', va='top', fontsize=7, color='#555', fontfamily='Noto Sans CJK SC')

# 底部备注
ax.text(7, 0.6, '三网物理隔离：EtherCAT控制网 + 千兆采集网 + 无线传输网', 
        ha='center', va='center', fontsize=8, color='#666', style='italic', fontfamily='Noto Sans CJK SC')
ax.text(7, 0.25, '融合判定准确率97.5%  ·  传感器退化场景下96.1%  ·  空间对齐精度亚毫米级(平均偏差3.2mm，降低74.7%)', 
        ha='center', va='center', fontsize=7.5, color='#888', fontfamily='Noto Sans CJK SC')

save(fig, 'fig1_system_architecture_20260529.png')