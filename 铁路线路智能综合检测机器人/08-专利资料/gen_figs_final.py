#!/usr/bin/env python3
# gen_figs_matplotlib.py - 生成5张专利附图
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch
import matplotlib.patheffects as pe
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
def fig1():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    ax.text(7, 7.5, '铁路线路智能视觉与多模态感知融合综合检测系统',
            ha='center', va='center', fontsize=12, fontweight='bold')

    rect = FancyBboxPatch((0.3, 5.2), 13.4, 1.5, boxstyle='round,pad=0.05',
                          facecolor='#E3F2FD', edgecolor='#90A4AE', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(0.5, 6.55, '感知层', fontsize=8, color='#555', va='top')

    items = [
        ('6路2D工业相机', '2448×2048  20fps\n千兆以太网\n轨面缺陷×2 道钉螺栓×2 焊缝×2', 1.0, 5.35),
        ('HWT905姿态传感器', '200Hz  三轴0.05°\nIEEE 1588 PTP同步', 4.3, 5.35),
        ('3D线激光传感器×2', '20000Hz  3200点/轮廓\nIP67  左右钢轨轮廓扫描', 7.4, 5.35),
        ('单点测距传感器×2', '2000Hz  精度±0.15mm', 10.5, 5.35),
        ('测距传感器矩阵', '直接测量轨距\n与横滚角完全解耦', 12.4, 5.35),
    ]
    for label, detail, x, y in items:
        box = FancyBboxPatch((x, y), 2.0, 1.2, boxstyle='round,pad=0.08',
                             facecolor='#BBDEFB', edgecolor='#1976D2', linewidth=1.2)
        ax.add_patch(box)
        ax.text(x+1.0, y+1.05, label, ha='center', va='top', fontsize=7.5, fontweight='bold')
        ax.text(x+1.0, y+0.35, detail, ha='center', va='center', fontsize=6.5, color='#333')

    rect2 = FancyBboxPatch((0.3, 3.6), 13.4, 1.4, boxstyle='round,pad=0.05',
                          facecolor='#E8F5E9', edgecolor='#90A4AE', linewidth=1.5)
    ax.add_patch(rect2)
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

    rect3 = FancyBboxPatch((0.3, 2.1), 13.4, 1.2, boxstyle='round,pad=0.05',
                          facecolor='#F3E5F5', edgecolor='#90A4AE', linewidth=1.5)
    ax.add_patch(rect3)
    ax.text(0.5, 3.1, '供电层', fontsize=8, color='#555', va='top')
    box = FancyBboxPatch((0.5, 2.2), 13.0, 0.9, boxstyle='round,pad=0.08',
                         facecolor='#E1BEE7', edgecolor='#7B1FA2', linewidth=1.2)
    ax.add_patch(box)
    ax.text(7, 2.65, '供电模块  48V大容量蓄电池组  智能电源管理',
            ha='center', va='center', fontsize=8, fontweight='bold')

    ax.text(7, 1.4, '三网物理隔离：EtherCAT控制网 + 千兆采集网 + 无线传输网',
            ha='center', va='center', fontsize=8, color='#666')
    ax.text(7, 1.05, '检测速度：0.5m/s（精细检测）/ 1m/s（常规检测）  |  覆盖8项检测功能',
            ha='center', va='center', fontsize=7.5, color='#888')
    ax.text(7, 0.65, '融合判定准确率97.5%  ·  传感器退化场景下仍保持96.1%  ·  空间对齐精度亚毫米级（平均偏差3.2mm，降低74.7%）',
            ha='center', va='center', fontsize=7.5, color='#888')

    save(fig, 'fig1_system_architecture_20260529.png')

# ============================================================
# 图2：三键索引时空对齐机制示意图
# ============================================================
def fig2():
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    ax.text(6.5, 6.6, '三键索引时空对齐机制示意图',
            ha='center', va='center', fontsize=12, fontweight='bold')

    # 三个输入模块
    inputs = [
        ('编码器', '每100脉冲=1帧\n生成帧编号FID_k\n约5mm里程分辨率', 0.8),
        ('PTP时钟同步', 'IEEE 1588 PTP协议\nUTC时间戳精度\n优于1微秒', 4.5),
        ('里程标定', '标准轨段标定\n消除轮径磨损误差\n消除打滑引入误差', 8.2),
    ]
    for label, detail, x in inputs:
        box = FancyBboxPatch((x, 4.2), 3.0, 1.6, boxstyle='round,pad=0.1',
                             facecolor='#BBDEFB', edgecolor='#1976D2', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x+1.5, 5.55, label, ha='center', va='center', fontsize=9, fontweight='bold')
        ax.text(x+1.5, 4.7, detail, ha='center', va='center', fontsize=7.5, color='#333')

    # 箭头向下
    for x in [2.3, 6.0, 9.7]:
        ax.annotate('', xy=(x, 3.9), xytext=(x, 3.9),
                   arrowprops=dict(arrowstyle='->', color='#666', lw=1.5))

    # 三键索引元组大方框
    box = FancyBboxPatch((3.5, 2.0), 6.0, 1.7, boxstyle='round,pad=0.15',
                         facecolor='#FFF9C4', edgecolor='#F57F17', linewidth=2)
    ax.add_patch(box)
    ax.text(6.5, 3.45, '三键索引元组 D(FID_k, s_k, t_k)',
            ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(6.5, 2.95, '帧编号 FID_k  ·  里程坐标 s_k  ·  UTC时间戳 t_k',
            ha='center', va='center', fontsize=9, color='#555')

    # 四个输出分支
    outputs = [
        ('2D工业相机', '帧触发曝光\n20fps', 0.8, 0.3),
        ('3D线激光传感器', '帧中心时刻采样\n20000Hz', 3.8, 0.3),
        ('HWT905姿态传感器', '帧边界对齐\n200Hz 三轴姿态角', 6.8, 0.3),
        ('单点测距传感器', '2000Hz\n帧中心最近值采样', 9.8, 0.3),
    ]
    for label, detail, x, y in outputs:
        box = FancyBboxPatch((x, y), 2.8, 1.0, boxstyle='round,pad=0.08',
                             facecolor='#E8F5E9', edgecolor='#388E3C', linewidth=1.2)
        ax.add_patch(box)
        ax.text(x+1.4, y+0.85, label, ha='center', va='top', fontsize=7.5, fontweight='bold')
        ax.text(x+1.4, y+0.3, detail, ha='center', va='center', fontsize=7, color='#333')

    # 箭头从大方框到输出
    for x in [2.2, 5.2, 8.2, 11.2]:
        ax.annotate('', xy=(x+1.4, 2.0), xytext=(x+1.4, 2.0),
                   arrowprops=dict(arrowstyle='->', color='#666', lw=1.5))

    # 底部说明
    ax.text(6.5, 0.1, '8种传感器数据在帧边界精确对齐  ·  多传感器空间对齐精度亚毫米级  ·  平均偏差3.2mm，降低74.7%',
            ha='center', va='center', fontsize=8, color='#888')

    save(fig, 'fig2_three_key_index_20260529.png')

# ============================================================
# 图3：自适应动态加权几何平均融合算法流程图
# ============================================================
def fig3():
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    ax.text(6.5, 7.6, '自适应动态加权几何平均融合算法流程图',
            ha='center', va='center', fontsize=12, fontweight='bold')

    # 第一行：输入
    inputs = [
        ('维度置信度C₁(t)', '来源：轨面缺陷视觉检测', 0.8, '#E3F2FD', '#1565C0'),
        ('维度置信度C₂(t)', '来源：几何参数检测', 4.8, '#E8F5E9', '#2E7D32'),
        ('维度置信度C₃(t)', '来源：钢轨廓形波磨检测', 8.8, '#F3E5F5', '#7B1FA2'),
    ]
    for label, detail, x, fc, ec in inputs:
        box = FancyBboxPatch((x, 6.2), 3.2, 1.1, boxstyle='round,pad=0.1',
                             facecolor=fc, edgecolor=ec, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x+1.6, 6.95, label, ha='center', va='center', fontsize=9, fontweight='bold')
        ax.text(x+1.6, 6.45, detail, ha='center', va='center', fontsize=7.5, color='#555')

    # 向下箭头
    for x in [2.4, 6.4, 10.4]:
        ax.annotate('', xy=(x, 5.9), xytext=(x, 6.2),
                   arrowprops=dict(arrowstyle='->', color='#888', lw=1.5))

    # 第二行：滑动标准差
    box = FancyBboxPatch((0.5, 5.0), 12.0, 0.7, boxstyle='round,pad=0.08',
                         facecolor='#FFF8E1', edgecolor='#F9A825', linewidth=1.2)
    ax.add_patch(box)
    ax.text(6.5, 5.35, '滑动标准差计算  σ₁(t)  σ₂(t)  σ₃(t)',
            ha='center', va='center', fontsize=9, fontweight='bold')

    # 向下箭头
    for x in [2.4, 6.4, 10.4]:
        ax.annotate('', xy=(x, 4.6), xytext=(x, 5.0),
                   arrowprops=dict(arrowstyle='->', color='#888', lw=1.5))

    # 第三行：可靠性因子
    box = FancyBboxPatch((0.5, 3.9), 12.0, 0.7, boxstyle='round,pad=0.08',
                         facecolor='#FFF8E1', edgecolor='#F9A825', linewidth=1.2)
    ax.add_patch(box)
    ax.text(6.5, 4.25, '可靠性因子计算  r₁=C₁/σ₁  r₂=C₂/σ₂  r₃=C₃/σ₃',
            ha='center', va='center', fontsize=9, fontweight='bold')

    # 向下箭头
    for x in [2.4, 6.4, 10.4]:
        ax.annotate('', xy=(x, 3.55), xytext=(x, 3.9),
                   arrowprops=dict(arrowstyle='->', color='#888', lw=1.5))

    # 第四行：权重归一化
    box = FancyBboxPatch((0.5, 2.9), 12.0, 0.65, boxstyle='round,pad=0.08',
                         facecolor='#E1F5FE', edgecolor='#0277BD', linewidth=1.5)
    ax.add_patch(box)
    ax.text(6.5, 3.22, '权重归一化  w₁+w₂+w₃=1  w_d(t)=r_d(t)/Σr_d(t)',
            ha='center', va='center', fontsize=9, fontweight='bold')

    # 向下箭头
    for x in [2.4, 6.4, 10.4]:
        ax.annotate('', xy=(6.5, 2.6), xytext=(x, 2.9),
                   arrowprops=dict(arrowstyle='->', color='#888', lw=1.5))

    # 核心融合模块
    box = FancyBboxPatch((4.0, 1.4), 5.0, 1.1, boxstyle='round,pad=0.15',
                         facecolor='#FFEB3B', edgecolor='#F57F17', linewidth=2.5)
    ax.add_patch(box)
    ax.text(6.5, 2.2, '加权几何平均融合', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(6.5, 1.65, 'C_fuse = C₁^w₁ × C₂^w₂ × C₃^w₃', ha='center', va='center', fontsize=9, color='#555')

    # 三档输出
    outputs = [
        ('C_fuse < 0.5', '检测结果丢弃', 0.5, '#FFCDD2', '#C62828'),
        ('0.5 ≤ C_fuse < 0.7', '进入人工复核队列', 4.8, '#FFF9C4', '#F57F17'),
        ('C_fuse ≥ 0.7', '最终判定输出', 9.1, '#C8E6C9', '#2E7D32'),
    ]
    for label, detail, x, fc, ec in outputs:
        ax.annotate('', xy=(x+1.6, 0.75), xytext=(6.5, 1.4),
                   arrowprops=dict(arrowstyle='->', color='#888', lw=1.2))
        box = FancyBboxPatch((x, 0.1), 3.2, 0.7, boxstyle='round,pad=0.08',
                             facecolor=fc, edgecolor=ec, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x+1.6, 0.65, label, ha='center', va='center', fontsize=8, fontweight='bold')
        ax.text(x+1.6, 0.3, detail, ha='center', va='center', fontsize=7.5, color='#333')

    ax.text(6.5, -0.15, '融合判定准确率97.5%  ·  传感器退化场景下仍保持96.1%',
            ha='center', va='center', fontsize=8, color='#888')

    save(fig, 'fig3_fusion_algorithm_20260529.png')

# ============================================================
# 图4：快慢双速EKF融合架构图
# ============================================================
def fig4():
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    ax.text(6, 6.6, '快慢双速EKF融合架构图',
            ha='center', va='center', fontsize=12, fontweight='bold')

    # 左侧快回路
    rect = FancyBboxPatch((0.3, 3.8), 4.5, 2.4, boxstyle='round,pad=0.1',
                          facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(2.55, 5.95, '快回路（200Hz）', ha='center', va='center', fontsize=10, fontweight='bold', color='#1565C0')
    ax.text(2.55, 5.55, '高频振动实时估计', ha='center', va='center', fontsize=8, color='#555')

    box = FancyBboxPatch((0.5, 4.3), 4.1, 0.9, boxstyle='round,pad=0.08',
                         facecolor='#BBDEFB', edgecolor='#1565C0', linewidth=1.2)
    ax.add_patch(box)
    ax.text(2.55, 4.75, 'HWT905姿态传感器', ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(2.55, 4.4, '200Hz  三轴0.05°  PTP同步', ha='center', va='center', fontsize=7.5, color='#555')

    ax.annotate('', xy=(2.55, 3.9), xytext=(2.55, 4.3),
               arrowprops=dict(arrowstyle='->', color='#1565C0', lw=2))

    box2 = FancyBboxPatch((0.5, 3.15), 4.1, 0.7, boxstyle='round,pad=0.08',
                         facecolor='#1565C0', edgecolor='#0D47A1', linewidth=1.2)
    ax.add_patch(box2)
    ax.text(2.55, 3.5, '快回路EKF处理  响应5ms', ha='center', va='center', fontsize=8.5, fontweight='bold', color='white')

    ax.annotate('', xy=(2.55, 2.8), xytext=(2.55, 3.15),
               arrowprops=dict(arrowstyle='->', color='#1565C0', lw=2))

    out1 = FancyBboxPatch((0.5, 2.05), 4.1, 0.7, boxstyle='round,pad=0.08',
                          facecolor='#E8F5E9', edgecolor='#388E3C', linewidth=1.5)
    ax.add_patch(out1)
    ax.text(2.55, 2.4, '车体振动补偿量 h_veh', ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(2.55, 2.1, '输出至中央融合单元', ha='center', va='center', fontsize=7, color='#555')

    # 右侧慢回路
    rect2 = FancyBboxPatch((7.2, 3.8), 4.5, 2.4, boxstyle='round,pad=0.1',
                           facecolor='#E8F5E9', edgecolor='#388E3C', linewidth=1.5)
    ax.add_patch(rect2)
    ax.text(9.45, 5.95, '慢回路（10Hz）', ha='center', va='center', fontsize=10, fontweight='bold', color='#2E7D32')
    ax.text(9.45, 5.55, '轨道高程估计', ha='center', va='center', fontsize=8, color='#555')

    box = FancyBboxPatch((7.4, 4.3), 4.1, 0.9, boxstyle='round,pad=0.08',
                         facecolor='#C8E6C9', edgecolor='#388E3C', linewidth=1.2)
    ax.add_patch(box)
    ax.text(9.45, 4.75, '单点测距传感器', ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(9.45, 4.4, '2000Hz  精度±0.15mm  安装高度约180mm', ha='center', va='center', fontsize=7, color='#555')

    ax.annotate('', xy=(9.45, 3.9), xytext=(9.45, 4.3),
               arrowprops=dict(arrowstyle='->', color='#388E3C', lw=2))

    box2 = FancyBboxPatch((7.4, 3.15), 4.1, 0.7, boxstyle='round,pad=0.08',
                          facecolor='#388E3C', edgecolor='#1B5E20', linewidth=1.2)
    ax.add_patch(box2)
    ax.text(9.45, 3.5, '慢回路EKF处理  状态向量[h_track,h_veh,v_veh]', ha='center', va='center', fontsize=8, fontweight='bold', color='white')

    ax.annotate('', xy=(9.45, 2.8), xytext=(9.45, 3.15),
               arrowprops=dict(arrowstyle='->', color='#388E3C', lw=2))

    out2 = FancyBboxPatch((7.4, 2.05), 4.1, 0.7, boxstyle='round,pad=0.08',
                          facecolor='#BBDEFB', edgecolor='#1976D2', linewidth=1.5)
    ax.add_patch(out2)
    ax.text(9.45, 2.4, '轨道高程真值 h_track', ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(9.45, 2.1, '输出至中央融合单元', ha='center', va='center', fontsize=7, color='#555')

    # 中央融合单元
    center_box = FancyBboxPatch((4.0, 1.3), 4.0, 0.75, boxstyle='round,pad=0.15',
                               facecolor='#FFEB3B', edgecolor='#F57F17', linewidth=2.5)
    ax.add_patch(center_box)
    ax.text(6, 1.67, '中央融合单元', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(6, 1.35, '快慢双速解耦核心  频域完全解耦', ha='center', va='center', fontsize=8, color='#555')

    # 箭头到中央
    ax.annotate('', xy=(5.5, 1.3), xytext=(2.55, 2.05),
               arrowprops=dict(arrowstyle='->', color='#F57F17', lw=2))
    ax.annotate('', xy=(6.5, 1.3), xytext=(9.45, 2.05),
               arrowprops=dict(arrowstyle='->', color='#F57F17', lw=2))

    # 输出
    out_final = FancyBboxPatch((3.5, 0.3), 5.0, 0.7, boxstyle='round,pad=0.1',
                              facecolor='#A5D6A7', edgecolor='#1B5E20', linewidth=2)
    ax.add_patch(out_final)
    ax.text(6, 0.65, '高低不平顺测量结果  精度优于±0.5mm',
            ha='center', va='center', fontsize=9, fontweight='bold')

    # 底部备注
    ax.text(6, 0.05, '频率比20:1（快回路200Hz / 慢回路10Hz）  ·  振动噪声降低53.7%  ·  轨道高程变化频带<1Hz  ·  车体振动频带0~20Hz',
            ha='center', va='center', fontsize=7.5, color='#888')

    save(fig, 'fig4_dual_speed_ekf_20260529.png')

# ============================================================
# 图5：几何参数检测原理图（轨距/水平/高低）
# ============================================================
def fig5():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    ax.text(7, 6.7, '几何参数检测原理图（轨距/水平/高低）',
            ha='center', va='center', fontsize=12, fontweight='bold')

    # 三栏
    panels = [
        {
            'title': '轨距检测',
            'subtitle': '俯视图',
            'label1': 'd_left',
            'label2': 'd_right',
            'formula': 'G = d_left + d_right',
            'note': '与横滚角完全解耦\n精度优于±0.3mm\n采样率约1000Hz',
            'x': 0.5,
            'fc': '#E3F2FD',
            'ec': '#1565C0',
        },
        {
            'title': '水平检测',
            'subtitle': '侧视图',
            'label1': 'θ_r',
            'label2': '',
            'formula': 'Δh = 1435 × sin(θ_r)',
            'note': 'HWT905横滚角\n标准轨距1435mm\n误差小于0.4mm',
            'x': 4.9,
            'fc': '#E8F5E9',
            'ec': '#2E7D32',
        },
        {
            'title': '高低检测',
            'subtitle': '侧视图',
            'label1': 'z = H - D',
            'label2': '',
            'formula': '快慢双速EKF融合\n精度优于±0.5mm',
            'note': '单点测距传感器主测\nHWT905辅助校正\n三键索引与视觉关联',
            'x': 9.3,
            'fc': '#FFF9C4',
            'ec': '#F57F17',
        },
    ]

    for p in panels:
        x = p['x']
        # 大框
        rect = FancyBboxPatch((x, 0.8), 4.3, 5.6, boxstyle='round,pad=0.1',
                             facecolor=p['fc'], edgecolor=p['ec'], linewidth=1.5)
        ax.add_patch(rect)

        # 标题
        ax.text(x+2.15, 6.2, p['title'], ha='center', va='center', fontsize=11, fontweight='bold', color=p['ec'])

        # 俯视图示意（轨+小车）
        if p['subtitle'] == '俯视图':
            # 画两根钢轨（俯视）
            ax.add_patch(Rectangle((x+0.3, 4.8), 0.3, 0.8, facecolor='#795548', edgecolor='#4E342E', linewidth=1))
            ax.add_patch(Rectangle((x+3.7, 4.8), 0.3, 0.8, facecolor='#795548', edgecolor='#4E342E', linewidth=1))
            # 左右标注
            ax.text(x+0.45, 5.2, p['label1'], ha='center', va='center', fontsize=8, fontweight='bold', color='#1565C0')
            ax.text(x+3.85, 5.2, p['label2'], ha='center', va='center', fontsize=8, fontweight='bold', color='#1565C0')
            # 中间画小车
            ax.add_patch(Rectangle((x+0.8, 4.7), 2.7, 1.0, facecolor='#90A4AE', edgecolor='#546E7A', linewidth=1.5))
            ax.text(x+2.15, 5.2, '检测小车', ha='center', va='center', fontsize=7.5, color='#37474F')
            # 轨距标注
            ax.text(x+2.15, 4.55, '轨距G', ha='center', va='center', fontsize=8, color='#333')
        else:
            # 侧视图示意
            # 画轨道
            ax.plot([x+0.5, x+4.0], [4.5, 4.5], color='#795548', linewidth=3)
            ax.plot([x+0.5, x+4.0], [4.2, 4.2], color='#795548', linewidth=3)
            # 画小车
            ax.add_patch(Rectangle((x+1.5, 4.05), 1.5, 0.35, facecolor='#90A4AE', edgecolor='#546E7A', linewidth=1.5))
            # 标注
            if 'HWT905' in p['note']:
                ax.text(x+2.25, 4.22, 'HWT905姿态传感器', ha='center', va='center', fontsize=7, color='#2E7D32')
                ax.text(x+2.25, 4.55, '横滚角θ_r', ha='center', va='top', fontsize=7.5, color='#333')
            else:
                ax.text(x+2.25, 4.6, 'z = H - D', ha='center', va='top', fontsize=7.5, color='#333')
                ax.text(x+2.25, 4.3, '单点测距传感器', ha='center', va='top', fontsize=7, color='#F57F17')

        # 公式框
        box = FancyBboxPatch((x+0.2, 2.5), 3.9, 0.7, boxstyle='round,pad=0.08',
                            facecolor='white', edgecolor=p['ec'], linewidth=1.5)
        ax.add_patch(box)
        ax.text(x+2.15, 2.85, p['formula'], ha='center', va='center', fontsize=9, fontweight='bold')

        # 说明文字
        ax.text(x+2.15, 2.1, p['note'], ha='center', va='center', fontsize=7.5, color='#555')

    # 底部说明
    ax.text(7, 0.2, '所有检测值均通过三键索引与视觉检测数据关联  ·  实现跨维度联合判定',
            ha='center', va='center', fontsize=8, color='#888')

    save(fig, 'fig5_geometry_parameters_20260529.png')

# 执行
fig1()
fig2()
fig3()
fig4()
fig5()
print('All 5 figures saved.')