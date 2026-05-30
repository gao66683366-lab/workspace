#!/usr/bin/env python3
"""生成专利说明书附图：系统架构、三键索引、融合算法、EKF架构、几何参数检测原理"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# 配置中文字体
font_path_regular = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font_path_bold = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
fm.fontManager.addfont(font_path_regular)
fm.fontManager.addfont(font_path_bold)

prop_regular = fm.FontProperties(fname=font_path_regular)
prop_bold = fm.FontProperties(fname=font_path_bold)

plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = '/root/.openclaw/workspace/铁路线路智能综合检测机器人/08-专利资料/'

def save_fig(fig, filename):
    path = OUTPUT_DIR + filename
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f'Saved: {path}')
    plt.close(fig)

def draw_box(ax, x, y, w, h, text, color='#E3F2FD', edgecolor='#1565C0', fontsize=9, bold=False, fp=None):
    box = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05',
                          facecolor=color, edgecolor=edgecolor, linewidth=1.5)
    ax.add_patch(box)
    fontprop = fp if fp else prop_regular
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, fontweight=weight, fontproperties=fontprop)

def draw_arrow(ax, x1, y1, x2, y2, color='black'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))


# ========== 图1：系统总体架构图 ==========
def gen_fig1():
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('图1 铁路线路综合检测系统总体架构图', fontsize=14, fontweight='bold', pad=15, fontproperties=prop_bold)

    train_body = FancyBboxPatch((6.5, 3.5), 3, 3, boxstyle='round,pad=0.1',
                                facecolor='#F5F5F5', edgecolor='#424242', linewidth=2)
    ax.add_patch(train_body)
    ax.text(8, 6.8, '检测小车车体', ha='center', va='center', fontsize=11, fontweight='bold', fontproperties=prop_bold)
    ax.text(8, 6.3, '工控机 (IP54)', ha='center', va='center', fontsize=9, fontproperties=prop_regular)
    ax.text(8, 5.8, '三网物理隔离架构', ha='center', va='center', fontsize=8, fontproperties=prop_regular)

    sensors_left = [
        (3.0, 8.2, '2D工业相机×6', '2448×2048\n20fps'),
        (0.5, 6.5, '3D线激光×2', '20000Hz\n3200点/轮廓'),
        (1.5, 4.8, 'HWT905\n姿态传感器', '200Hz\n三轴0.05°'),
    ]
    for x, y, name, spec in sensors_left:
        draw_box(ax, x-1.2, y-0.6, 2.4, 1.2, name + '\n' + spec, '#E8F5E9', '#2E7D32', 8)

    sensors_right = [
        (12.0, 8.2, '单点测距\n传感器×2', '2000Hz\n±0.15mm'),
        (14.0, 6.5, '测距传感器\n矩阵', '~1000Hz\n±0.1mm'),
        (12.0, 4.8, '编码器', '里程测量\n帧触发'),
    ]
    for x, y, name, spec in sensors_right:
        draw_box(ax, x-0.1, y-0.6, 2.2, 1.2, name + '\n' + spec, '#E3F2FD', '#1565C0', 8)

    for (x, y, _, _) in sensors_left:
        draw_arrow(ax, x+1.2, y, 6.5, 5.5)
    for (x, y, _, _) in sensors_right:
        draw_arrow(ax, x+0.1, y, 9.5, 5.5)

    draw_box(ax, 0.3, 1.5, 2.5, 1.0, '48V蓄电池组\n智能电源管理', '#FFF3E0', '#E65100', 8)
    draw_arrow(ax, 1.55, 2.5, 1.55, 3.5)
    draw_arrow(ax, 1.55, 3.5, 5.0, 5.5)

    draw_box(ax, 13.0, 1.5, 2.5, 1.0, '4G/5G无线传输\n数据远程上传', '#F3E5F5', '#6A1B9A', 8)
    draw_arrow(ax, 14.25, 2.5, 14.25, 3.5)
    draw_arrow(ax, 14.25, 3.5, 11.5, 4.5)

    draw_box(ax, 5.5, 0.8, 5.0, 1.5, '融合判定单元\n八通道数据融合 + 缺陷识别 + 几何参数计算',
              '#E8EAF6', '#283593', 9, bold=True)
    draw_arrow(ax, 6.5, 3.5, 8, 2.3)
    draw_arrow(ax, 9.5, 3.5, 8, 2.3)

    ax.text(8, 9.6, 'EtherCAT硬实时总线（控制）｜ 千兆以太网（采集）｜ 4G/5G（传输）',
            ha='center', va='center', fontsize=9, color='#424242', fontproperties=prop_regular,
            bbox=dict(boxstyle='round', facecolor='#FFF9C4', edgecolor='#F9A825', linewidth=1))

    ax.text(0.3, 9.8, '图中：1—检测小车车体；2—2D工业相机；3—3D线激光传感器；\n'
            '4—HWT905姿态传感器；5—单点测距传感器；6—测距传感器矩阵；\n'
            '7—工控机；8—通信模块；9—编码器；10—供电模块',
            ha='left', va='center', fontsize=8, color='#616161', fontproperties=prop_regular)

    fig.tight_layout()
    save_fig(fig, '图1_系统总体架构图.png')


# ========== 图2：三键索引时空对齐机制示意图 ==========
def gen_fig2():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title('图2 三键索引时空对齐机制示意图', fontsize=14, fontweight='bold', pad=15, fontproperties=prop_bold)

    ax.annotate('', xy=(13, 7.2), xytext=(0.5, 7.2),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.text(7, 7.5, '时间轴 (t)', ha='center', va='center', fontsize=11, fontweight='bold', fontproperties=prop_bold)
    for i in range(5):
        x = 1.5 + i * 2.5
        ax.plot([x, x], [7.1, 6.9], 'k-', lw=1.5)
        ax.text(x, 6.7, f't{i}', ha='center', va='center', fontsize=9, fontproperties=prop_regular)

    ax.annotate('', xy=(13, 6.2), xytext=(0.5, 6.2),
                arrowprops=dict(arrowstyle='->', color='#1565C0', lw=1.5))
    ax.text(7, 6.45, '帧编号 (FID)', ha='center', va='center', fontsize=10, color='#1565C0', fontproperties=prop_regular)
    for i in range(5):
        x = 1.5 + i * 2.5
        ax.plot([x, x], [6.1, 5.9], color='#1565C0', lw=1.5)
        ax.text(x, 5.7, f'FID_{i}', ha='center', va='center', fontsize=9, color='#1565C0', fontproperties=prop_regular)

    ax.annotate('', xy=(13, 5.2), xytext=(0.5, 5.2),
                arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=1.5))
    ax.text(7, 5.45, '里程坐标 (s_k, m)', ha='center', va='center', fontsize=10, color='#2E7D32', fontproperties=prop_regular)
    里程_labels = ['0.000', '0.005', '0.010', '0.015', '0.020']
    for i in range(5):
        x = 1.5 + i * 2.5
        ax.text(x, 5.1, 里程_labels[i], ha='center', va='center', fontsize=9, color='#2E7D32', fontproperties=prop_regular)

    sensor_y = [4.0, 3.0, 2.0, 1.0]
    sensor_names = ['2D工业相机 (20fps)', '3D线激光 (20000Hz)', 'HWT905姿态 (200Hz)', '单点测距 (2000Hz)']
    sensor_colors = ['#E3F2FD', '#E8F5E9', '#FFF3E0', '#F3E5F5']
    sensor_edge = ['#1565C0', '#2E7D32', '#E65100', '#6A1B9A']

    for idx, (y, name, col, edge) in enumerate(zip(sensor_y, sensor_names, sensor_colors, sensor_edge)):
        draw_box(ax, 0.8, y-0.35, 12.5, 0.7, name, col, edge, 9)
        for i in range(5):
            x = 1.5 + i * 2.5
            ax.plot([x, x], [y+0.35, y-0.35], color=edge, lw=1, linestyle='--', alpha=0.5)

    ax.text(7, 0.3, '三键索引元组：D(FID_k, s_k, t_k)\n帧边界严格对齐 → 多传感器硬件级同步',
            ha='center', va='center', fontsize=11, fontproperties=prop_regular,
            bbox=dict(boxstyle='round', facecolor='#E8EAF6', edgecolor='#283593', linewidth=2))

    fig.tight_layout()
    save_fig(fig, '图2_三键索引时空对齐机制示意图.png')


# ========== 图3：自适应动态加权融合算法流程图 ==========
def gen_fig3():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('图3 自适应动态加权融合算法流程图', fontsize=14, fontweight='bold', pad=15, fontproperties=prop_bold)

    draw_box(ax, 0.5, 7.5, 3.0, 1.0, '2D图像特征\n(置信度C₁)', '#E3F2FD', '#1565C0', 10)
    draw_box(ax, 0.5, 6.2, 3.0, 1.0, '3D点云几何\n(置信度C₂)', '#E8F5E9', '#2E7D32', 10)
    draw_box(ax, 0.5, 4.9, 3.0, 1.0, 'IMU振动信号\n(置信度C₃)', '#FFF3E0', '#E65100', 10)
    draw_box(ax, 0.5, 3.6, 3.0, 1.0, '测距几何参数\n(置信度C₄)', '#F3E5F5', '#6A1B9A', 10)

    for y in [8.0, 6.7, 5.4, 4.1]:
        draw_arrow(ax, 3.5, y, 4.8, 6.5)
    draw_arrow(ax, 3.5, 4.1, 4.8, 6.5)

    draw_box(ax, 5.0, 5.5, 3.5, 2.0, '可靠性因子计算\n\nr_d(t) = C_d(t) / σ_d(t)\n\nC_d: 维度置信度\nσ_d: 滑动标准差',
              '#FFF9C4', '#F9A825', 10)

    draw_arrow(ax, 8.5, 6.5, 9.8, 6.5)

    draw_box(ax, 10.0, 5.5, 3.5, 2.0, '权重归一化\n\nw_d(t) = r_d(t) / Σr_d(t)\n\nΣw_d = 1', '#E8EAF6', '#283593', 10)

    draw_arrow(ax, 11.75, 5.5, 11.75, 4.0)

    draw_box(ax, 9.5, 2.5, 4.5, 1.5, '加权几何平均融合\n\nC_fuse = ∏ C_d(t)^{w_d(t)}',
              '#E8EAF6', '#283593', 11, bold=True)

    draw_box(ax, 10.0, 0.5, 3.5, 1.5, '融合置信度 C_fuse\n\n>0.7 → 最终判定输出\n0.5~0.7 → 人工复核队列\n<0.5 → 丢弃',
              '#FFEBEE', '#C62828', 10)

    draw_arrow(ax, 11.75, 2.5, 11.75, 2.0)
    draw_arrow(ax, 11.75, 2.0, 11.75, 1.0)

    ax.text(7, -0.2, '几何平均特性：单一低置信度放大效应——任一维度异常显著降低融合置信度，符合安全原则',
            ha='center', va='center', fontsize=9, color='#424242', fontproperties=prop_regular,
            bbox=dict(boxstyle='round', facecolor='#FAFAFA', edgecolor='#BDBDBD', linewidth=1))

    fig.tight_layout()
    save_fig(fig, '图3_自适应动态加权融合算法流程图.png')


# ========== 图4：快慢双速EKF融合架构图 ==========
def gen_fig4():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title('图4 快慢双速EKF融合架构图', fontsize=14, fontweight='bold', pad=15, fontproperties=prop_bold)

    draw_box(ax, 0.3, 5.8, 2.5, 1.2, '单点测距传感器\n2000Hz采样', '#E3F2FD', '#1565C0', 10)
    draw_box(ax, 0.3, 4.2, 2.5, 1.2, 'HWT905姿态传感器\n200Hz采样', '#E8F5E9', '#2E7D32', 10)

    draw_box(ax, 3.5, 3.8, 4.0, 2.0, '快回路 EKF\n200Hz\n\n状态估计：θ_veh(k)\n补偿车体高频振动\n响应时间：5ms',
              '#FFF3E0', '#E65100', 10, bold=True)
    ax.text(5.5, 6.3, '快回路', fontsize=11, fontweight='bold', color='#E65100', fontproperties=prop_bold,
            bbox=dict(boxstyle='round', facecolor='#FFF3E0', edgecolor='#E65100'))
    draw_arrow(ax, 2.8, 6.3, 3.5, 5.8)
    draw_arrow(ax, 2.8, 4.8, 3.5, 4.8)

    draw_box(ax, 8.5, 3.8, 4.0, 2.0, '慢回路 EKF\n10Hz\n\n状态向量：x_k=[h_track,\n  h_veh, v_veh]^T\n输出：轨道高程h_track',
              '#E8F5E9', '#2E7D32', 10, bold=True)
    ax.text(10.5, 6.3, '慢回路', fontsize=11, fontweight='bold', color='#2E7D32', fontproperties=prop_bold,
            bbox=dict(boxstyle='round', facecolor='#E8F5E9', edgecolor='#2E7D32'))
    draw_arrow(ax, 2.8, 5.8, 8.5, 5.0)

    draw_box(ax, 9.0, 1.0, 4.5, 1.5, '轨道高程输出 + 车体振动补偿\n\n10Hz轨道高程估计\n高低不平顺精度：±0.5mm',
              '#E8EAF6', '#283593', 11, bold=True)
    draw_arrow(ax, 10.5, 3.8, 11.25, 2.5)

    ax.text(7, 2.2, '频域完全解耦：中心频率比 20:1\n轨道高程(<1Hz) vs 车体振动(0~20Hz)',
            ha='center', va='center', fontsize=10, fontproperties=prop_regular,
            bbox=dict(boxstyle='round', facecolor='#FFF9C4', edgecolor='#F9A825', linewidth=1.5))

    ax.text(7, 0.4, '双速EKF：快回路(200Hz)实时补偿高频振动，慢回路(10Hz)输出平滑轨道高程\n'
                    '奈奎斯特采样：快回路200Hz > 40Hz(车体振动上限)，慢回路10Hz > 2Hz(高程变化上限)',
            ha='center', va='center', fontsize=9, color='#616161', fontproperties=prop_regular)

    fig.tight_layout()
    save_fig(fig, '图4_快慢双速EKF融合架构图.png')


# ========== 图5：几何参数检测原理图 ==========
def gen_fig5():
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    titles = ['轨距检测原理', '水平检测原理', '高低检测原理']

    for ax, title in zip(axes, titles):
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10, fontproperties=prop_bold)

    # 子图1：轨距检测
    ax1 = axes[0]
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 7)
    ax1.axis('off')

    rail1 = Rectangle((1, 3.5), 1.5, 3, facecolor='#78909C', edgecolor='#37474F', linewidth=2)
    rail2 = Rectangle((7.5, 3.5), 1.5, 3, facecolor='#78909C', edgecolor='#37474F', linewidth=2)
    ax1.add_patch(rail1)
    ax1.add_patch(rail2)

    ax1.annotate('', xy=(7.5, 5.5), xytext=(2.5, 5.5),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax1.text(5, 5.8, '轨距G = d_left + d_right', ha='center', va='center', fontsize=10, color='red', fontproperties=prop_bold)

    ax1.add_patch(Rectangle((4.2, 1.0), 0.6, 1.5, facecolor='#29B6F6', edgecolor='#0277BD', linewidth=1.5))
    ax1.add_patch(Rectangle((5.2, 1.0), 0.6, 1.5, facecolor='#29B6F6', edgecolor='#0277BD', linewidth=1.5))
    ax1.text(4.5, 0.5, '测距矩阵', ha='center', va='center', fontsize=8, fontproperties=prop_regular)
    ax1.text(5.5, 0.5, '测距矩阵', ha='center', va='center', fontsize=8, fontproperties=prop_regular)

    ax1.annotate('', xy=(2.5, 5.5), xytext=(4.5, 2.0), arrowprops=dict(arrowstyle='-', color='#0288D1', lw=1, ls='--'))
    ax1.annotate('', xy=(7.5, 5.5), xytext=(5.5, 2.0), arrowprops=dict(arrowstyle='-', color='#0288D1', lw=1, ls='--'))
    ax1.text(4.0, 2.5, 'd_left', ha='center', fontsize=9, color='#0288D1', fontproperties=prop_regular)
    ax1.text(5.9, 2.5, 'd_right', ha='center', fontsize=9, color='#0288D1', fontproperties=prop_regular)
    ax1.text(5, 1.7, '姿态无关测量\n横滚角解耦', ha='center', va='center', fontsize=8, fontproperties=prop_regular,
            bbox=dict(boxstyle='round', facecolor='#E3F2FD'))

    # 子图2：水平检测
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 7)
    ax2.axis('off')

    ax2.plot([1, 9], [5.0, 5.0], 'k-', lw=2)
    ax2.plot([1, 9], [3.8, 4.4], 'k-', lw=2)
    ax2.fill_between([1, 9], [5.0, 5.0], [3.8, 4.4], alpha=0.3, color='#90CAF9')

    ax2.annotate('', xy=(9.2, 5.0), xytext=(9.2, 4.4),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax2.text(9.5, 4.7, 'Δh', ha='center', va='center', fontsize=12, color='red', fontweight='bold', fontproperties=prop_bold)

    ax2.add_patch(Rectangle((4.0, 1.0), 2.0, 1.5, facecolor='#66BB6A', edgecolor='#2E7D32', linewidth=1.5))
    ax2.text(5, 0.5, 'HWT905姿态传感器', ha='center', va='center', fontsize=8, fontproperties=prop_regular)
    ax2.annotate('', xy=(5, 2.5), xytext=(5, 5.0), arrowprops=dict(arrowstyle='-', color='#2E7D32', lw=1, ls='--'))
    ax2.text(5.3, 3.5, '横滚角θ_r', ha='center', va='center', fontsize=9, color='#2E7D32', fontproperties=prop_regular)

    ax2.text(5, 1.7, 'Δh = 1435×sin(θ_r)\n精度<0.4mm', ha='center', va='center', fontsize=8, fontproperties=prop_regular,
            bbox=dict(boxstyle='round', facecolor='#E8F5E9'))

    # 子图3：高低检测
    ax3 = axes[2]
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 7)
    ax3.axis('off')

    x = np.linspace(0, 10, 200)
    y_base = 4.5 + 0.3 * np.sin(2 * np.pi * x / 3)
    ax3.plot(x, y_base, 'k-', lw=2, label='轨道高程')

    y_veh = y_base + 0.15 * np.sin(2 * np.pi * x / 0.5)
    ax3.plot(x, y_veh, 'b--', lw=1.5, alpha=0.7, label='车体振动')

    for xi in [2, 5, 8]:
        yi = 4.5 + 0.3 * np.sin(2 * np.pi * xi / 3)
        ax3.plot([xi, xi], [yi+1.5, yi], 'g-', lw=1)
        ax3.plot([xi-0.1, xi+0.1], [yi+1.5, yi+1.5], 'g-', lw=1.5)

    ax3.text(5, 6.5, '单点测距传感器\n(2000Hz)', ha='center', va='center', fontsize=8, fontproperties=prop_regular)
    ax3.annotate('', xy=(5, 5.6), xytext=(5, 6.3), arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=1.5))
    ax3.text(1.5, 6.0, 'D = H - h_track + h_veh', ha='center', va='center', fontsize=8, fontproperties=prop_regular,
            bbox=dict(boxstyle='round', facecolor='#F3E5F5', edgecolor='#6A1B9A'))

    ax3.text(5, 0.5, '双速EKF融合\n快(200Hz)补偿振动 | 慢(10Hz)输出高程\n精度: ±0.5mm', ha='center', va='center', fontsize=8, fontproperties=prop_regular,
            bbox=dict(boxstyle='round', facecolor='#FFF3E0', edgecolor='#E65100'))
    ax3.legend(loc='upper right', fontsize=8)

    fig.suptitle('图5 几何参数检测原理图（轨距/水平/高低）', fontsize=14, fontweight='bold', y=1.02, fontproperties=prop_bold)
    fig.tight_layout()
    save_fig(fig, '图5_几何参数检测原理图.png')


if __name__ == '__main__':
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    gen_fig1()
    gen_fig2()
    gen_fig3()
    gen_fig4()
    gen_fig5()
    print('All 5 figures generated successfully!')