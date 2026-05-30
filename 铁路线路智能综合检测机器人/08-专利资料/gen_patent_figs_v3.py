#!/usr/bin/env python3
"""生成专利说明书附图 v3 - 布局优化版"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import numpy as np

font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font_path_b = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
fm.fontManager.addfont(font_path)
fm.fontManager.addfont(font_path_b)
fp_r = fm.FontProperties(fname=font_path)
fp_b = fm.FontProperties(fname=font_path_b)

plt.rcParams['axes.unicode_minus'] = False
OUTPUT_DIR = '/root/.openclaw/workspace/铁路线路智能综合检测机器人/08-专利资料/'

def save(fig, name):
    fig.savefig(OUTPUT_DIR + name, dpi=150, bbox_inches='tight', facecolor='white')
    print(f'Saved: {name}')
    plt.close(fig)

def box(ax, x, y, w, h, txt, fc='#E8F5E9', ec='#1565C0', fs=9, bold=False, txt2=''):
    p = FancyBboxPatch((x,y), w, h, boxstyle='round,pad=0.08', fc=fc, ec=ec, lw=1.5)
    ax.add_patch(p)
    fw = 'bold' if bold else 'normal'
    if txt2:
        ax.text(x+w/2, y+h/2+0.12, txt, ha='center', va='center', fontsize=fs, fontweight=fw, fontproperties=fp_r)
        ax.text(x+w/2, y+h/2-0.12, txt2, ha='center', va='center', fontsize=fs-1, fontweight="normal", fontproperties=fp_r, color='#555')
    else:
        ax.text(x+w/2, y+h/2, txt, ha='center', va='center', fontsize=fs, fontweight=fw, fontproperties=fp_r)

def arr(ax, x1,y1,x2,y2, c='black'):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle='->', color=c, lw=1.5))

def label(ax, x, y, txt, fs=9, color='black', bold=False, **kwargs):
    fw = 'bold' if bold else 'normal'
    ax.text(x, y, txt, ha='center', va='center', fontsize=fs, fontproperties=fp_r, color=color, fontweight=fw, **kwargs)


# ==================== 图1：系统总体架构 ====================
def fig1():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis('off')
    ax.set_title('图1 铁路线路综合检测系统总体架构图', fontsize=14, fontproperties=fp_b, pad=12)

    # 中央：检测小车
    p = FancyBboxPatch((6.2, 3.8), 3.6, 2.4, boxstyle='round,pad=0.1', fc='#ECEFF1', ec='#546E7A', lw=2)
    ax.add_patch(p)
    ax.text(8, 6.5, '检测小车车体', ha='center', va='center', fontsize=12, fontweight='bold', fontproperties=fp_b)
    ax.text(8, 5.9, '工控机 (IP54) / 三网物理隔离', ha='center', va='center', fontsize=9, fontproperties=fp_r)

    # 左侧传感器 - 箭头指向车体不同高度
    lsen = [
        (7.2,'2D工业相机×6','2448×2048 / 20fps / 千兆网','#E3F2FD','#1565C0'),
        (6.0,'3D线激光传感器×2','20000Hz / 3200点/轮廓 / IP67','#E8F5E9','#2E7D32'),
        (4.8,'姿态传感器','200Hz / 三轴0.05° / PTP同步','#FFF3E0','#E65100'),
    ]
    tgt_y = [6.2, 5.4, 4.3]
    for k,(y,txt,t2,fc,ec) in enumerate(lsen):
        box(ax, 0.3, y-0.4, 2.6, 0.9, txt, fc=fc, ec=ec, fs=9)
        arr(ax, 2.9, y+0.05, 6.2, tgt_y[k])

    # 右侧传感器 - 箭头指向车体不同高度
    rsen = [
        (7.2,'单点测距传感器×2','2000Hz / ±0.15mm','#E3F2FD','#1565C0'),
        (6.0,'测距传感器矩阵','~1000Hz / ±0.1mm / 直接测轨距','#E8F5E9','#2E7D32'),
        (4.8,'编码器','里程测量 / 帧触发','#F3E5F5','#6A1B9A'),
    ]
    for k,(y,txt,t2,fc,ec) in enumerate(rsen):
        box(ax, 13.1, y-0.4, 2.6, 0.9, txt, fc=fc, ec=ec, fs=9)
        arr(ax, 13.1, y+0.05, 9.8, tgt_y[k])

    # 底部输出
    box(ax, 5.5, 1.5, 5.0, 1.3, '融合判定单元', fc='#E8EAF6', ec='#283593', fs=11, bold=True, txt2='八通道数据融合 + 缺陷识别 + 几何参数计算')
    arr(ax, 8, 3.8, 8, 2.8)

    # 供电
    box(ax, 0.3, 1.2, 2.4, 0.9, '48V蓄电池组\n智能电源管理', fc='#FFF9C4', ec='#F9A825', fs=9)
    arr(ax, 1.5, 2.1, 1.5, 3.8)
    arr(ax, 1.5, 3.8, 5.5, 2.8)

    # 通信
    box(ax, 13.4, 1.2, 2.4, 0.9, '4G/5G无线传输\n数据远程上传', fc='#F3E5F5', ec='#6A1B9A', fs=9)
    arr(ax, 14.6, 2.1, 14.6, 3.8)
    arr(ax, 14.6, 3.8, 10.5, 2.8)

    ax.text(8, 8.7, 'EtherCAT硬实时总线（控制）  |  千兆以太网（采集）  |  4G/5G（传输）',
            ha='center', va='center', fontsize=9, fontproperties=fp_r,
            bbox=dict(boxstyle='round', fc='#FFF9C4', ec='#F9A825', lw=1))

    ax.text(0.2, 8.5, '图中：1—检测小车车体；2—2D工业相机；3—3D线激光传感器；4—姿态传感器；\n'
            '5—单点测距传感器；6—测距传感器矩阵；7—工控机；8—通信模块；9—编码器；10—供电模块',
            ha='left', va='top', fontsize=8, fontproperties=fp_r, color='#666')

    save(fig, '图1_系统总体架构图.png')


# ==================== 图2：三键索引时空对齐 ====================
def fig2():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('图2 三键索引时空对齐机制示意图', fontsize=14, fontproperties=fp_b, pad=12)

    # 三行轴
    for y,txt,c in [(6.3,'时间轴 (t)','#333'),(5.2,'帧编号 (FID)','#1565C0'),(4.1,'里程坐标 (s_k)','#2E7D32')]:
        ax.annotate('', xy=(13, y), xytext=(0.5, y), arrowprops=dict(arrowstyle='->', color=c, lw=2))
        ax.text(7, y+0.25, txt, ha='center', va='center', fontsize=10, fontweight='bold', fontproperties=fp_b, color=c)
        for i in range(5):
            x = 1.5 + i*2.5
            ax.plot([x,x],[y-0.08,y+0.08], color=c, lw=2)
            ax.text(x, y-0.25, f't{i}' if y==6.3 else f'FID_{i}' if y==5.2 else f'{i*5:.0f}m', ha='center', va='top', fontsize=8, fontproperties=fp_r, color=c)

    # 传感器带
    sensors = [
        (2.8, '2D工业相机 (20fps)', '#E3F2FD', '#1565C0'),
        (1.9, '3D线激光 (20000Hz)', '#E8F5E9', '#2E7D32'),
        (1.0, '姿态传感器 (200Hz)', '#FFF3E0', '#E65100'),
        (0.1, '单点测距 (2000Hz)', '#F3E5F5', '#6A1B9A'),
    ]
    for y,txt,fc,ec in sensors:
        box(ax, 0.5, y, 12.5, 0.6, txt, fc=fc, ec=ec, fs=9)
        for i in range(5):
            x = 1.5 + i*2.5
            ax.plot([x,x],[y,y+0.6], color=ec, lw=0.8, ls='--', alpha=0.4)

    ax.text(7, -0.2, '三键索引元组：D(FID_k, s_k, t_k)  —  帧边界严格对齐，多传感器硬件级同步',
            ha='center', va='center', fontsize=10, fontproperties=fp_b,
            bbox=dict(boxstyle='round', fc='#E8EAF6', ec='#283593', lw=2))

    save(fig, '图2_三键索引时空对齐机制示意图.png')


# ==================== 图3：自适应动态加权融合算法流程 ====================
def fig3():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14); ax.set_ylim(0, 9); ax.axis('off')
    ax.set_title('图3 自适应动态加权融合算法流程图', fontsize=14, fontproperties=fp_b, pad=12)

    # 输入4路
    inputs = [
        (7.5, '2D图像特征', '(C₁)', '#E3F2FD', '#1565C0'),
        (6.2, '3D点云几何', '(C₂)', '#E8F5E9', '#2E7D32'),
        (4.9, 'IMU振动信号', '(C₃)', '#FFF3E0', '#E65100'),
        (3.6, '测距几何参数', '(C₄)', '#F3E5F5', '#6A1B9A'),
    ]
    for y,txt,suff,fc,ec in inputs:
        box(ax, 0.3, y-0.4, 2.8, 0.8, txt, fc=fc, ec=ec, fs=10)
        ax.text(2.9+0.35, y, suff, fontsize=9, fontproperties=fp_r, color='#555')
        arr(ax, 3.1, y, 4.5, 5.5)

    # 可靠性因子
    box(ax, 4.5, 4.5, 3.2, 2.0, '可靠性因子计算\n\nr_d = C_d / σ_d\n\nC_d: 维度置信度\nσ_d: 滑动标准差',
        fc='#FFF9C4', ec='#F9A825', fs=10)
    arr(ax, 7.7, 5.5, 8.8, 5.5)

    # 权重归一化
    box(ax, 8.8, 4.5, 3.0, 2.0, '权重归一化\n\nw_d = r_d / Σr_d\n\nΣw_d = 1', fc='#E8EAF6', ec='#283593', fs=10)
    arr(ax, 11.8, 5.5, 11.8, 4.0)

    # 几何平均融合
    box(ax, 9.3, 2.7, 4.5, 1.3, '加权几何平均融合\nC_fuse = ∏ C_d^{w_d}',
        fc='#E8EAF6', ec='#283593', fs=11, bold=True)
    arr(ax, 11.8, 4.5, 11.8, 4.0)

    # 判定输出
    box(ax, 9.3, 1.0, 4.5, 1.3, '融合置信度 C_fuse\n>0.7 → 最终输出 | 0.5~0.7 → 人工复核 | <0.5 → 丢弃',
        fc='#FFEBEE', ec='#C62828', fs=10)
    arr(ax, 11.5, 2.7, 11.5, 2.3)

    ax.text(7, 0.3, '几何平均特性：单一低置信度放大——任一维度异常显著降低融合置信度，符合安全原则',
            ha='center', va='center', fontsize=9, fontproperties=fp_r, color='#555',
            bbox=dict(boxstyle='round', fc='#FAFAFA', ec='#BDBDBD', lw=1))

    save(fig, '图3_自适应动态加权融合算法流程图.png')


# ==================== 图4：快慢双速EKF融合架构 ====================
def fig4():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('图4 快慢双速EKF融合架构图', fontsize=14, fontproperties=fp_b, pad=12)

    # ===== 简洁三行布局 =====

    # --- 左侧输入 ---
    box(ax, 0.2, 5.5, 2.6, 0.9, '单点测距传感器\n2000Hz采样', fc='#E3F2FD', ec='#1565C0', fs=10)
    box(ax, 0.2, 4.0, 2.6, 0.9, '姿态传感器\n200Hz采样',     fc='#E8F5E9', ec='#2E7D32', fs=10)

    # --- 快回路 EKF（左侧）---
    box(ax, 3.0, 4.6, 3.8, 1.8, '快回路 EKF  — 200Hz\n\nθ_veh(k) 状态估计\n补偿车体高频振动\n响应时间：5ms',
        fc='#FFF3E0', ec='#E65100', fs=10, bold=True)
    arr(ax, 2.8, 5.95, 3.0, 6.2)
    arr(ax, 2.8, 4.45, 3.0, 4.8)

    # --- 慢回路 EKF（右侧，与快回路平齐）---
    box(ax, 8.0, 4.6, 3.8, 1.8, '慢回路 EKF  — 10Hz\n\nx_k = [h_track, h_veh, v_veh]^T\n输出轨道高程 h_track',
        fc='#E8F5E9', ec='#2E7D32', fs=10, bold=True)
    arr(ax, 6.8, 5.5, 8.0, 5.5)

    # --- 输出层（慢回路正下方）---
    box(ax, 5.5, 1.2, 5.0, 1.6, '轨道高程输出 + 车体振动补偿\n\n10Hz轨道高程估计  |  精度 ±0.5mm',
        fc='#E8EAF6', ec='#283593', fs=11, bold=True)
    arr(ax, 9.9, 4.6, 9.9, 2.8)

    ax.text(6.9, 6.6, '频域完全解耦：中心频率比 20:1', ha='center', va='center', fontsize=9,
            fontproperties=fp_b, bbox=dict(boxstyle='round', fc='#FFF9C4', ec='#F9A825', lw=1.5))

    ax.text(7, 0.3, '双速EKF：快回路200Hz补偿高频振动，慢回路10Hz输出轨道高程（精度 ±0.5mm）',
            ha='center', va='center', fontsize=9, fontproperties=fp_r, color='#666')

    save(fig, '图4_快慢双速EKF融合架构图.png')

# ==================== 图5：几何参数检测原理 ====================
def fig5():
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))

    # --- 轨距检测 ---
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('轨距检测原理', fontsize=12, fontproperties=fp_b, pad=8)

    # 钢轨
    ax.add_patch(Rectangle((1.2, 3.5), 1.5, 3, fc='#78909C', ec='#37474F', lw=2))
    ax.add_patch(Rectangle((7.3, 3.5), 1.5, 3, fc='#78909C', ec='#37474F', lw=2))
    # 轨距箭头
    ax.annotate('', xy=(7.3, 5.8), xytext=(2.7, 5.8), arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    label(ax, 5, 6.1, 'G = d_left + d_right', fs=10, color='red', bold=True)
    # 测距传感器
    ax.add_patch(Rectangle((4.0, 1.2), 0.6, 1.3, fc='#29B6F6', ec='#0277BD', lw=1.5))
    ax.add_patch(Rectangle((5.4, 1.2), 0.6, 1.3, fc='#29B6F6', ec='#0277BD', lw=1.5))
    label(ax, 4.3, 0.7, '测距', fs=8)
    label(ax, 5.7, 0.7, '测距', fs=8)
    ax.annotate('', xy=(2.7, 5.8), xytext=(4.0, 2.5), arrowprops=dict(arrowstyle='-', color='#0288D1', lw=1, ls='--'))
    ax.annotate('', xy=(7.3, 5.8), xytext=(5.4, 2.5), arrowprops=dict(arrowstyle='-', color='#0288D1', lw=1, ls='--'))
    label(ax, 4.0, 2.3, 'd_left', fs=8, color='#0288D1')
    label(ax, 5.9, 2.3, 'd_right', fs=8, color='#0288D1')
    label(ax, 5, 1.7, '姿态无关测量\n横滚角完全解耦', fs=8,
            bbox=dict(boxstyle='round', fc='#E3F2FD'))

    # --- 水平检测 ---
    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('水平检测原理', fontsize=12, fontproperties=fp_b, pad=8)

    ax.plot([1,9],[5.2,5.2],'k-',lw=2)
    ax.plot([1,9],[3.8,4.5],'k-',lw=2)
    ax.fill_between([1,9],[5.2,5.2],[3.8,4.5],alpha=0.3,color='#90CAF9')
    ax.annotate('', xy=(9.3, 5.2), xytext=(9.3, 4.5), arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    label(ax, 9.6, 4.85, 'Δh', fs=12, color='red', bold=True)
    ax.add_patch(Rectangle((4.0, 1.2), 2.0, 1.2, fc='#66BB6A', ec='#2E7D32', lw=1.5))
    label(ax, 5, 0.7, '姿态传感器', fs=8)
    ax.annotate('', xy=(5, 2.4), xytext=(5, 5.2), arrowprops=dict(arrowstyle='-', color='#2E7D32', lw=1, ls='--'))
    label(ax, 5.4, 3.5, '横滚角θ_r', fs=8, color='#2E7D32')
    label(ax, 5, 1.7, 'Δh = 1435×sin(θ_r)\n精度<0.4mm', fs=8,
            bbox=dict(boxstyle='round', fc='#E8F5E9'))

    # --- 高低检测 ---
    ax = axes[2]
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('高低检测原理', fontsize=12, fontproperties=fp_b, pad=8)

    x = np.linspace(0, 10, 300)
    y1 = 4.5 + 0.35*np.sin(2*np.pi*x/3.5)
    ax.plot(x, y1, 'k-', lw=2.5, label='轨道高程')
    y2 = y1 + 0.2*np.sin(2*np.pi*x/0.6)
    ax.plot(x, y2, 'b--', lw=1.5, alpha=0.7, label='车体振动')

    for xi in [2, 5, 8]:
        yi = 4.5 + 0.35*np.sin(2*np.pi*xi/3.5)
        ax.plot([xi,xi],[yi+1.2, yi], color='#2E7D32', lw=1.5)
        ax.plot([xi-0.15,xi+0.15],[yi+1.2,yi+1.2], color='#2E7D32', lw=2)

    label(ax, 5, 6.5, '单点测距传感器 (2000Hz)', fs=8)
    ax.annotate('', xy=(5, 5.6), xytext=(5, 6.3), arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=1.5))
    label(ax, 1.5, 6.0, 'D = H - h_track + h_veh', fs=8,
            bbox=dict(boxstyle='round', fc='#F3E5F5', ec='#6A1B9A'))
    label(ax, 5, 0.7, '双速EKF：快(200Hz)补偿振动\n慢(10Hz)输出高程 | ±0.5mm', fs=8,
            bbox=dict(boxstyle='round', fc='#FFF3E0', ec='#E65100'))
    ax.legend(loc='upper right', fontsize=8)

    fig.suptitle('图5 几何参数检测原理图', fontsize=14, fontproperties=fp_b, y=1.01)
    fig.tight_layout()
    save(fig, '图5_几何参数检测原理图.png')


if __name__ == '__main__':
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    print('All 5 figures done!')