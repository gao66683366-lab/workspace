#!/usr/bin/env python3
# gen_figs_matplotlib.py - 生成5张专利附图（matplotlib版）
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
plt.rcParams['axes.unicode_minus'] = False

OUT = '/root/.openclaw/media/tool-image-generation/'

def save(fig, name):
    fig.savefig(f'{OUT}{name}', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved: {name}')

# ============================================================
# 图1：系统总体架构图
# ============================================================
def make_fig1():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # 标题
    ax.text(7, 7.5, '铁路线路智能视觉与多模态感知融合综合检测系统',
            ha='center', va='center', fontsize=12, fontweight='bold')

    # ---- 感知层 ----
    rect = FancyBboxPatch((0.3, 5.2), 13.4, 1.5, boxstyle='round,pad=0.05',
                          facecolor='#E3F2FD', edgecolor='#90A4AE', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(0.5, 6.55, '感知层', fontsize=8, color='#555', va='top')

   感知_items = [
        ('6路2D工业相机', '2448×2048  20fps\n千兆以太网\n轨面缺陷×2 道钉螺栓×2 焊缝×2', 1.0, 5.35),
        ('HWT905姿态传感器', '200Hz  三轴0.05°\nIEEE 1588 PTP同步', 4.3, 5.35),
        ('3D线激光传感器×2', '20000Hz  3200点/轮廓\nIP67  左右钢轨轮廓扫描', 7.4, 5.35),
        ('单点测距传感器×2', '2000Hz  精度±0.15mm', 10.5, 5.35),
        ('测距传感器矩阵', '直接测量轨距\n与横滚角完全解耦', 12.4, 5.35),
    ]
    for label, detail, x, y in 感知_items:
        box = FancyBboxPatch((x, y), 2.0, 1.2, boxstyle='round,pad=0.08',
                             facecolor='#BBDEFB', edgecolor='#1976D2', linewidth=1.2)
        ax.add_patch(box)
        ax.text(x+1.0, y+1.05, label, ha='center', va='top', fontsize=7.5, fontweight='bold')
        ax.text(x+1.0, y+0.35, detail, ha='center', va='center', fontsize=6.5, color='#333')

    # ---- 计算层 ----
    rect = FancyBboxPatch((0.3, 3.6), 13.4, 1.4, boxstyle='round,pad=0.05',
                          facecolor='#E8F5E9', edgecolor='#90A4AE', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(0.5, 4.8, '计算层', fontsize=8, color='#555', va='top')
    calc = [
        ('工控机\nIP54防护', 1.0, 3.75),
        ('融合判定单元\n三级融合\n自适应动态加权', 5.2, 3.75),
        ('环形缓冲区\n帧边界对齐', 9.4, 3.75),
        ('通信模块\n4G/5G无线', 12.4, 3.75),
    ]
    for label, x, y in calc:
        box = FancyBboxPatch((x, y), 2.8, 1.1, boxstyle='round,pad=0.08',
                             facecolor='#C8E6C9', edgecolor='#388E3C', linewidth=1.2)
        ax.add_patch(box)
        ax.text(x+1.4, y+0.55, label, ha='center', va='center', fontsize=7.5, fontweight='bold')

    # ---- 供电层 ----
    rect = FancyBboxPatch((0.3, 2.1), 13.4, 1.2, boxstyle='round,pad=0.05',
                          facecolor='#F3E5F5', edgecolor='#90A4AE', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(0.5, 3.1, '供电层', fontsize=8, color='#555', va='top')
    box = FancyBboxPatch((0.5, 2.2), 13.0, 0.9, boxstyle='round,pad=0.08',
                         facecolor='#E1BEE7', edgecolor='#7B1FA2', linewidth=1.2)
    ax.add_patch(box)
    ax.text(7, 2.65, '供电模块  48V大容量蓄电池组  智能电源管理',
            ha='center', va='center', fontsize=8, fontweight='bold')

    # 底部备注
    ax.text(7, 1.4, '三网物理隔离：EtherCAT控制网 + 千兆采集网 + 无线传输网',
            ha='center', va='center', fontsize=8, color='#666')
    ax.text(7, 1.05, '检测速度：0.5m/s（精细检测）/ 1m/s（常规检测）  |  覆盖8项检测功能',
            ha='center', va='center', fontsize=7.5, color='#888')
    ax.text(7, 0.65, '融合判定准确率97.5%  ·  传感器退化场景下仍保持96.1%  ·  空间对齐精度亚毫米级（平均偏差3.2mm，降低74.7%）',
            ha='center', va='center', fontsize=7.5, color='#888')

    save(fig, 'fig1_system_architecture_20260529.png')

make_fig1()