#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
plt.rcParams['axes.unicode_minus'] = False

OUT = '/root/.openclaw/media/tool-image-generation/'

def save(fig, name):
    fig.savefig(f'{OUT}{name}', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved: {name}')

def box(ax, x, y, w, h, fc, ec, lw=1.2):
    p = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.06', facecolor=fc, edgecolor=ec, linewidth=lw)
    ax.add_patch(p)

def txt(ax, x, y, text, ha='center', va='center', fs=8, fw='normal', color='#333'):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, fontweight=fw, color=color)

def arr(ax, x1, y1, x2, y2, c='#555', lw=1.5):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', color=c, lw=lw))

# ============================================================
# 图1：系统总体架构图（论文参数版）
# ============================================================
def fig1():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis('off'); fig.patch.set_facecolor('white')
    txt(ax, 8, 8.7, '铁路线路智能视觉与多模态感知融合综合检测系统', fs=13, fw='bold')

    # 感知层
    box(ax, 0.3, 5.5, 15.4, 2.3, '#E3F2FD', '#90A4AE', 1.5)
    txt(ax, 0.6, 7.6, '感知层', fs=8.5, fw='bold', color='#555')

    items = [
        (0.6, 6.3, 2.8, 1.3, '#BBDEFB', '#1565C0', '6路2D工业相机', '2448×2048px  20fps  千兆以太网\n轨面缺陷检测×2  道钉螺栓×2  焊缝×2'),
        (3.9, 6.3, 2.5, 1.3, '#BBDEFB', '#1565C0', '3D线激光×2', '20000Hz  3200点/轮廓  IP67\n左右钢轨轨头轮廓扫描'),
        (6.9, 6.3, 2.5, 1.3, '#BBDEFB', '#1565C0', 'HWT905姿态传感器', '200Hz  三轴0.05°  PTP同步\n轨道坐标系基准'),
        (9.9, 6.3, 2.4, 1.3, '#BBDEFB', '#1565C0', '单点测距传感器×2', '2000Hz  精度±0.15mm\n仅用于高低检测'),
        (12.8, 6.3, 2.7, 1.3, '#90CAF9', '#0D47A1', '测距传感器矩阵', '直接测轨距G=d_left+d_right\n与横滚角完全解耦  ±0.3mm'),
    ]
    for x, y, w, h, fc, ec, label, detail in items:
        box(ax, x, y, w, h, fc, ec, 1.3)
        txt(ax, x+w/2, y+h*0.78, label, fs=8, fw='bold')
        txt(ax, x+w/2, y+h*0.35, detail, fs=6.5, color='#333')

    # 计算层
    box(ax, 0.3, 3.5, 15.4, 1.8, '#E8F5E9', '#90A4AE', 1.5)
    txt(ax, 0.6, 5.1, '计算层', fs=8.5, fw='bold', color='#555')
    calc = [
        (0.6, 3.8, 2.8, 1.2, '#C8E6C9', '#2E7D32', '工控机\nIP54防护', 'Jetson AGX Orin\n融合判定单元'),
        (4.0, 3.8, 3.2, 1.2, '#A5D6A7', '#1B5E20', '融合判定单元\n三级融合', '时间对齐→空间关联→判级融合\n自适应动态加权几何平均'),
        (7.8, 3.8, 3.0, 1.2, '#A5D6A7', '#1B5E20', '环形缓冲区\n帧边界对齐', '三键索引元组\nD(FID_k,s_k,t_k)'),
        (11.4, 3.8, 2.5, 1.2, '#C8E6C9', '#2E7D32', '编码器', '帧触发+里程测量\n100脉冲/帧≈5mm'),
        (14.4, 3.8, 1.1, 1.2, '#FFE0B2', '#E65100', '通信\n4G/5G', '远程监控\n数据上传'),
    ]
    for x, y, w, h, fc, ec, label, detail in calc:
        box(ax, x, y, w, h, fc, ec, 1.2)
        txt(ax, x+w/2, y+h*0.68, label, fs=8, fw='bold')
        txt(ax, x+w/2, y+h*0.28, detail, fs=6.5, color='#333')

    # 供电层
    box(ax, 0.3, 2.2, 15.4, 1.0, '#F3E5F5', '#90A4AE', 1.5)
    txt(ax, 0.6, 3.0, '供电层', fs=8.5, fw='bold', color='#555')
    box(ax, 0.5, 2.35, 15.0, 0.7, '#E1BEE7', '#7B1FA2', 1.2)
    txt(ax, 8, 2.72, '供电模块  48V大容量蓄电池组  智能电源管理  BMS板/管理板温度三级保护', fs=8, fw='bold', color='#4A148C')

    # 底部指标
    box(ax, 0.3, 0.6, 15.4, 1.35, '#FAFAFA', '#BDBDBD', 1)
    txt(ax, 8, 1.75, '核心性能指标（基于济南铁路局120km以上实际线路验证）', fs=8.5, fw='bold', color='#333')
    txt(ax, 1.5, 1.3, '融合判定准确率97.5%', fs=7.5, color='#2E7D32')
    txt(ax, 4.5, 1.3, '传感器退化场景96.1%', fs=7.5, color='#2E7D32')
    txt(ax, 7.5, 1.3, '空间对齐精度3.2mm（降低74.7%）', fs=7.5, color='#1565C0')
    txt(ax, 11.0, 1.3, '轨面缺陷mAP@0.5=92.5%', fs=7.5, color='#1565C0')
    txt(ax, 13.8, 1.3, '振动噪声降低53.7%', fs=7.5, color='#F57F17')
    txt(ax, 8, 0.75, '检测速度：0.5m/s（精细检测）/ 1m/s（常规检测）  |  三网物理隔离：EtherCAT控制网 + 千兆采集网 + 无线传输网', fs=7.5, color='#666')
    txt(ax, 14.8, 7.6, '8项检测功能\n轨面缺陷 · 道钉螺栓\n焊缝质量 · 钢轨廓形\n波磨 · 轨距 · 水平 · 高低', fs=7, color='#555', va='top')

    for xb in [2.0, 5.2, 8.2, 11.1, 14.1]:
        arr(ax, xb, 5.5, xb, 5.0, '#90A4AE', 1)

    save(fig, 'fig1_paper_based.png')

# ============================================================
# 图2：三键索引时空对齐机制
# ============================================================
def fig2():
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_xlim(0, 15); ax.set_ylim(0, 8); ax.axis('off'); fig.patch.set_facecolor('white')
    txt(ax, 7.5, 7.6, '三键索引时空对齐机制示意图', fs=12, fw='bold')

    sources = [
        ('编码器', '100脉冲/帧\n生成FID_k\n分辨率≈5mm/帧', 0.8, '#E3F2FD', '#1565C0'),
        ('PTP时钟\n(IEEE 1588)', 'UTC时间戳\n精度优于1μs\n跨传感器同步', 5.5, '#E8F5E9', '#2E7D32'),
        ('里程标定\n(标准轨段)', '消除轮径磨损\n和打滑误差\n帧号→里程映射', 10.2, '#FFF9C4', '#F57F17'),
    ]
    for label, detail, x, fc, ec in sources:
        box(ax, x, 5.5, 3.8, 1.7, fc, ec, 1.5)
        txt(ax, x+1.9, 7.15, label, fs=9, fw='bold')
        txt(ax, x+1.9, 6.05, detail, fs=7.5, color='#333')

    for xb in [2.7, 7.4, 12.1]:
        arr(ax, xb, 5.5, xb, 4.6, '#888', 1.5)

    box(ax, 3.5, 2.5, 8.0, 2.0, '#FFF9C4', '#F57F17', 2.5)
    txt(ax, 7.5, 4.15, '三键索引元组  D(FID_k, s_k, t_k)', fs=11, fw='bold', color='#E65100')
    txt(ax, 7.5, 3.55, '帧编号 FID_k  ·  里程坐标 s_k  ·  UTC时间戳 t_k', fs=9, color='#555')
    txt(ax, 7.5, 3.0, '帧边界精确对齐 → 多传感器硬件级时空统一', fs=8, color='#888')

    arr(ax, 7.5, 2.5, 7.5, 1.7, '#F57F17', 2)
    arr(ax, 5.0, 2.5, 2.5, 1.7, '#F57F17', 1.2)
    arr(ax, 10.0, 2.5, 12.5, 1.7, '#F57F17', 1.2)

    sensors = [
        ('2D工业相机×6', '20fps\n帧触发曝光', 0.5, '#C8E6C9', '#2E7D32'),
        ('3D线激光×2', '20000Hz\n帧中心时刻采样', 3.2, '#C8E6C9', '#2E7D32'),
        ('HWT905', '200Hz\n帧边界对齐', 5.9, '#BBDEFB', '#1565C0'),
        ('单点测距×2', '2000Hz\n最近值采样', 8.6, '#BBDEFB', '#1565C0'),
        ('测距矩阵', '约1000Hz\n帧边界同步', 11.3, '#E1BEE7', '#7B1FA2'),
    ]
    for label, detail, x, fc, ec in sensors:
        box(ax, x, 0.3, 2.8, 1.3, fc, ec, 1.2)
        txt(ax, x+1.4, 1.45, label, fs=7.5, fw='bold')
        txt(ax, x+1.4, 0.75, detail, fs=7, color='#333')

    txt(ax, 7.5, -0.05, '8种传感器数据帧边界精确对齐  ·  空间对齐精度亚毫米级（平均偏差3.2mm，降低74.7%）', fs=8, color='#666')
    save(fig, 'fig2_paper_based.png')

# ============================================================
# 图3：自适应动态加权融合算法流程图
# ============================================================
def fig3():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14); ax.set_ylim(0, 9); ax.axis('off'); fig.patch.set_facecolor('white')
    txt(ax, 7, 8.7, '自适应动态加权几何平均融合算法流程图', fs=12, fw='bold')

    inputs = [
        ('维度置信度C₁(t)', '轨面缺陷\n视觉检测', 0.5, 7.0, 3.0, '#E3F2FD', '#1565C0'),
        ('维度置信度C₂(t)', '几何参数\n检测', 4.8, 7.0, 3.0, '#E8F5E9', '#2E7D32'),
        ('维度置信度C₃(t)', '钢轨廓形\n波磨检测', 9.1, 7.0, 3.0, '#F3E5F5', '#7B1FA2'),
    ]
    for label, detail, x, y, w, fc, ec in inputs:
        box(ax, x, y, w, 1.4, fc, ec, 1.5)
        txt(ax, x+w/2, y+1.15, label, fs=9, fw='bold')
        txt(ax, x+w/2, y+0.45, detail, fs=8, color='#333')

    for xb in [2.0, 6.3, 10.6]:
        arr(ax, xb, 7.0, xb, 6.3, '#888', 1.5)

    box(ax, 0.5, 5.5, 12.0, 0.7, '#FFF8E1', '#F9A825', 1.2)
    txt(ax, 7, 5.85, '滑动标准差计算  σ₁(t)  σ₂(t)  σ₃(t)', fs=9, fw='bold')
    arr(ax, 7, 5.5, 7, 4.8, '#888', 1.5)

    box(ax, 0.5, 4.0, 12.0, 0.7, '#FFF8E1', '#F9A825', 1.2)
    txt(ax, 7, 4.35, '可靠性因子  r_d(t) = C_d(t)/σ_d(t)  →  归一化权重  w_d(t)=r_d(t)/Σr_d(t)', fs=9, fw='bold')
    for xb in [2.0, 6.3, 10.6]:
        arr(ax, xb, 5.5, xb, 4.7, '#888', 1)

    arr(ax, 7, 4.0, 7, 2.9, '#F57F17', 2)
    box(ax, 3.5, 2.0, 7.0, 1.0, '#FFEB3B', '#F57F17', 2.5)
    txt(ax, 7, 2.65, '加权几何平均融合  C_fuse = ∏ C_d(t)^w_d(t)', fs=10, fw='bold')
    txt(ax, 7, 2.2, '几何平均乘积特性：任一维度异常 → 融合置信度显著降低', fs=7.5, color='#555')

    arr(ax, 7, 2.0, 7, 1.35, '#F57F17', 1.5)
    outputs = [
        ('C_fuse < 0.5', '检测结果丢弃', 0.5, '#FFCDD2', '#C62828'),
        ('0.5 ≤ C_fuse < 0.7', '进入人工复核队列', 5.0, '#FFF9C4', '#F57F17'),
        ('C_fuse ≥ 0.7', '最终判定输出', 9.5, '#C8E6C9', '#2E7D32'),
    ]
    for label, detail, x, fc, ec in outputs:
        w = 3.8
        arr(ax, 7, 1.35, x+w/2, 1.35, '#888', 1)
        box(ax, x, 0.3, w, 1.0, fc, ec, 1.5)
        txt(ax, x+w/2, 1.05, label, fs=8, fw='bold')
        txt(ax, x+w/2, 0.6, detail, fs=7.5, color='#333')

    txt(ax, 7, -0.05, '融合判定准确率97.5%  ·  传感器退化场景下（20%噪声）仍保持96.1%（仅下降1.4个百分点）', fs=8, color='#666')
    save(fig, 'fig3_paper_based.png')

# ============================================================
# 图4：快慢双速EKF融合架构图
# ============================================================
def fig4():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 8); ax.axis('off'); fig.patch.set_facecolor('white')
    txt(ax, 7, 7.6, '快慢双速EKF融合架构图', fs=12, fw='bold')

    box(ax, 0.3, 3.8, 5.5, 3.5, '#E3F2FD', '#1565C0', 1.5)
    txt(ax, 3.05, 7.05, '快回路（200Hz）  高频振动实时估计', fs=9, fw='bold', color='#1565C0')
    box(ax, 0.5, 5.6, 5.1, 1.2, '#BBDEFB', '#1565C0', 1.2)
    txt(ax, 3.05, 6.2, 'HWT905姿态传感器', fs=9, fw='bold')
    txt(ax, 3.05, 5.75, '200Hz采样  三轴0.05°  PTP时间同步', fs=7.5, color='#333')
    arr(ax, 3.05, 5.6, 3.05, 5.0, '#1565C0', 2)
    box(ax, 0.5, 4.0, 5.1, 0.95, '#1565C0', '#0D47A1', 1.2)
    txt(ax, 3.05, 4.47, '快回路EKF状态估计', fs=8.5, fw='bold', color='white')
    txt(ax, 3.05, 4.1, '实时补偿车体高频振动  响应时间5ms', fs=7.5, color='#CCC')
    arr(ax, 3.05, 4.0, 3.05, 3.3, '#1565C0', 2)
    box(ax, 0.5, 2.5, 5.1, 0.75, '#E8F5E9', '#2E7D32', 1.5)
    txt(ax, 3.05, 2.87, '车体振动补偿量 h_veh  →  中央融合', fs=8.5, fw='bold')

    box(ax, 5.9, 2.2, 2.2, 3.0, '#FFEB3B', '#F57F17', 2.5)
    txt(ax, 7, 4.8, '中央融合单元', fs=9, fw='bold')
    txt(ax, 7, 4.35, '快慢双速\n解耦核心', fs=8, color='#555')
    txt(ax, 7, 3.7, '频域完全解耦\n无混叠效应', fs=7.5, color='#666')
    arr(ax, 3.05, 2.5, 5.9, 3.5, '#F57F17', 1.5)
    arr(ax, 8.1, 3.5, 10.9, 2.5, '#F57F17', 1.5)

    box(ax, 8.2, 3.8, 5.5, 3.5, '#E8F5E9', '#2E7D32', 1.5)
    txt(ax, 10.95, 7.05, '慢回路（10Hz）  轨道高程估计', fs=9, fw='bold', color='#2E7D32')
    box(ax, 8.4, 5.6, 5.1, 1.2, '#C8E6C9', '#388E3C', 1.2)
    txt(ax, 10.95, 6.2, '单点测距传感器×2（主测）', fs=9, fw='bold')
    txt(ax, 10.95, 5.75, '2000Hz  精度±0.15mm  安装高度约180mm', fs=7.5, color='#333')
    arr(ax, 10.95, 5.6, 10.95, 5.0, '#388E3C', 2)
    box(ax, 8.4, 4.0, 5.1, 0.95, '#388E3C', '#1B5E20', 1.2)
    txt(ax, 10.95, 4.47, '慢回路EKF状态估计', fs=8.5, fw='bold', color='white')
    txt(ax, 10.95, 4.1, '状态向量x_k=[h_track, h_veh, v_veh]ᵀ', fs=7.5, color='#CCC')
    arr(ax, 10.95, 4.0, 10.95, 3.3, '#388E3C', 2)
    box(ax, 8.4, 2.5, 5.1, 0.75, '#BBDEFB', '#1976D2', 1.5)
    txt(ax, 10.95, 2.87, '轨道高程真值 h_track  →  中央融合', fs=8.5, fw='bold')

    box(ax, 4.5, 0.8, 5.0, 0.9, '#A5D6A7', '#1B5E20', 2)
    txt(ax, 7, 1.25, '高低不平顺测量结果  精度优于±0.5mm', fs=9, fw='bold')
    arr(ax, 7, 2.2, 7, 1.7, '#1B5E20', 2)

    txt(ax, 7, 0.25, '频率比20:1（快200Hz / 慢10Hz）  ·  振动噪声降低53.7%  ·  轨道高程变化频带<1Hz  ·  车体振动频带0~20Hz', fs=8, color='#666')
    save(fig, 'fig4_paper_based.png')

# ============================================================
# 图5：几何参数检测原理图
# ============================================================
def fig5():
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_xlim(0, 15); ax.set_ylim(0, 8); ax.axis('off'); fig.patch.set_facecolor('white')
    txt(ax, 7.5, 7.7, '几何参数检测原理图（轨距/水平/高低）', fs=12, fw='bold')

    panels = [
        {'title': '轨距检测', 'view': '俯视图', 'x': 0.4, 'fc': '#E3F2FD', 'ec': '#1565C0'},
        {'title': '水平检测', 'view': '侧视图', 'x': 5.2, 'fc': '#E8F5E9', 'ec': '#2E7D32'},
        {'title': '高低检测', 'view': '侧视图', 'x': 10.0, 'fc': '#FFF9C4', 'ec': '#F57F17'},
    ]

    for p in panels:
        x = p['x']
        box(ax, x, 0.8, 4.5, 6.5, p['fc'], p['ec'], 1.5)
        txt(ax, x+2.25, 7.1, p['title'], fs=11, fw='bold', color=p['ec'])
        txt(ax, x+2.25, 6.7, p['view'], fs=8, color='#888')

        if p['title'] == '轨距检测':
            ax.add_patch(Rectangle((x+0.3, 4.6), 0.4, 1.0, facecolor='#795548', edgecolor='#4E342E', lw=1))
            ax.add_patch(Rectangle((x+3.8, 4.6), 0.4, 1.0, facecolor='#795548', edgecolor='#4E342E', lw=1))
            ax.annotate('', xy=(x+0.7, 5.5), xytext=(x+3.8, 5.5), arrowprops=dict(arrowstyle='<->', color='#1565C0', lw=1.5))
            txt(ax, x+2.25, 5.7, 'G', fs=10, fw='bold', color='#1565C0')
            txt(ax, x+0.1, 5.9, 'd_left', fs=7.5, va='top')
            txt(ax, x+4.1, 5.9, 'd_right', fs=7.5, va='top')
            ax.add_patch(Rectangle((x+0.9, 4.5), 2.7, 1.2, facecolor='#90A4AE', edgecolor='#546E7A', lw=1.5))
            txt(ax, x+2.25, 5.1, '检测小车', fs=7.5, color='#37474F')
            txt(ax, x+2.25, 3.5, '测距传感器矩阵\n直接测量左右轨内侧距', fs=8, color='#333')
            box(ax, x+0.2, 2.3, 4.1, 0.75, 'white', p['ec'], 1.5)
            txt(ax, x+2.25, 2.67, 'G = d_left + d_right', fs=9.5, fw='bold', color=p['ec'])
            txt(ax, x+2.25, 1.6, '与横滚角完全解耦\n精度优于±0.3mm\n采样率约1000Hz', fs=7.5, color='#555')

        elif p['title'] == '水平检测':
            ax.plot([x+0.5, x+3.0], [4.8, 4.8], color='#795548', lw=4)
            ax.plot([x+0.5, x+3.0], [4.35, 4.35], color='#795548', lw=4)
            ax.plot([x+0.5, x+0.5], [4.8, 4.35], color='#795548', lw=1.5, linestyle='--')
            ax.plot([x+3.0, x+3.0], [4.8, 4.35], color='#795548', lw=1.5, linestyle='--')
            ax.annotate('', xy=(x+0.5, 4.65), xytext=(x+0.5, 4.8), arrowprops=dict(arrowstyle='<->', color='#2E7D32', lw=1.5))
            txt(ax, x+0.35, 4.58, 'Δh', fs=8, color='#2E7D32')
            ax.add_patch(Rectangle((x+1.2, 4.1), 1.6, 0.45, facecolor='#90A4AE', edgecolor='#546E7A', lw=1.5))
            txt(ax, x+2.0, 4.32, 'HWT905', fs=7.5, color='#37474F')
            txt(ax, x+2.0, 3.5, '横滚角θ_r测量\n超高差计算', fs=8, color='#333')
            box(ax, x+0.2, 2.3, 4.1, 0.75, 'white', p['ec'], 1.5)
            txt(ax, x+2.25, 2.67, 'Δh = 1435 × sin(θ_r)', fs=9.5, fw='bold', color=p['ec'])
            txt(ax, x+2.25, 1.6, '标准轨距1435mm\n误差小于0.4mm\n采样率200Hz', fs=7.5, color='#555')

        else:
            ax.plot([x+0.5, x+3.5], [4.6, 4.6], color='#795548', lw=4)
            ax.plot([x+0.5, x+1.5], [4.3, 4.3], color='#795548', lw=4)
            ax.plot([x+1.5, x+1.5], [4.6, 4.3], color='#795548', lw=1.5, linestyle='--')
            ax.plot([x+0.5, x+1.5], [4.6, 4.6], color='#795548', lw=1, linestyle=':')
            ax.annotate('', xy=(x+0.8, 4.85), xytext=(x+0.8, 4.5), arrowprops=dict(arrowstyle='<->', color='#F57F17', lw=1.5))
            txt(ax, x+0.65, 4.68, 'z', fs=8, color='#F57F17')
            ax.add_patch(Rectangle((x+0.7, 4.55), 1.0, 0.35, facecolor='#90A4AE', edgecolor='#546E7A', lw=1.5))
            txt(ax, x+1.2, 4.72, '传感器', fs=6.5, color='#37474F')
            txt(ax, x+2.0, 3.5, '单点测距（主测）+HWT905（辅助）\n快慢双速EKF融合', fs=8, color='#333')
            box(ax, x+0.2, 2.3, 4.1, 0.75, 'white', p['ec'], 1.5)
            txt(ax, x+2.25, 2.67, 'z = H - D', fs=9.5, fw='bold', color=p['ec'])
            txt(ax, x+2.25, 1.6, '快慢双速EKF融合\n精度优于±0.5mm\n三键索引与视觉关联', fs=7.5, color='#555')

    txt(ax, 7.5, 0.2, '所有检测值均通过三键索引与视觉检测数据关联  ·  实现跨维度联合判定', fs=8, color='#666')
    save(fig, 'fig5_paper_based.png')

fig1(); fig2(); fig3(); fig4(); fig5()
print('All 5 paper-based figures saved.')