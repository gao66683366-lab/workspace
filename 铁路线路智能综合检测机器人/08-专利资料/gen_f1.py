#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
plt.rcParams['axes.unicode_minus'] = False

OUT = '/root/.openclaw/media/tool-image-generation/'

def save(fig, name):
    fig.savefig(f'{OUT}{name}', dpi=180, bbox_inches='tight', facecolor='white', pad_inches=0.25)
    plt.close(fig)
    print(f'Saved: {name}')

def box(ax, x, y, w, h, fc, ec, lw=1.5, r=0.06):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad={r}',facecolor=fc,edgecolor=ec,lw=lw))

def L(ax, x, y, t, fs=9, fw='bold', c='#1a1a1a', ha='center', va='center'):
    ax.text(x, y, t, ha=ha, va=va, fontsize=fs, fontweight=fw, color=c, linespacing=1.4)

def S(ax, x, y, t, fs=7, c='#555', ha='center'):
    ax.text(x, y, t, ha=ha, va=va, fontsize=fs, color=c, linespacing=1.25)

def arr(ax, x1,y1,x2,y2, c='#555', lw=1.2):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='->',color=c,lw=lw,shrinkA=3,shrinkB=3))

# ===== 图1：系统总体架构 =====
def fig1():
    fig,ax=plt.subplots(figsize=(18,11)); ax.set_xlim(0,18); ax.set_ylim(0,11); ax.axis('off'); fig.patch.set_facecolor('white')
    L(ax,9,10.5,'铁路线路智能视觉与多模态感知融合综合检测系统',fs=15); ax.axhline(10.1,xmin=.02,xmax=.98,c='#ccc',lw=1)
    # 感知层
    box(ax,0.3,6.5,17.4,3.0,'#EBF5FB','#7FA9B8',1.2); L(ax,0.7,9.2,'感知层',fs=9,fw='bold',c='#555',va='top')
    items=[
        ('6路2D工业相机','2448×2048 20fps\n千兆以太网\n轨面缺陷×2·道钉螺栓×2·焊缝×2',0.5,'#D6EAF8','#1A6FA8'),
        ('3D线激光×2','20000Hz 3200点/轮廓\nIP67防护等级\n左右钢轨轨头轮廓扫描',3.6,'#D6EAF8','#1A6FA8'),
        ('HWT905姿态传感器','200Hz 三轴0.05°\nIEEE 1588 PTP同步',6.7,'#D6EAF8','#1A6FA8'),
        ('单点测距传感器×2','2000Hz 精度±0.15mm\n仅用于高低检测',9.8,'#D6EAF8','#1A6FA8'),
        ('测距传感器矩阵','直接测轨距\nG=dL+dR 与横滚角解耦\n±0.3mm',12.9,'#B8D4ED','#0D4A8A'),
        ('编码器','100脉冲/帧\n分辨率≈5mm',15.8,'#E8F6EC','#1E7A3C'),
    ]
    for nm,dt,x,fc,ec in items:
        box(ax,x,6.6,2.8,2.7,fc,ec,1.3); L(ax,x+1.4,9.05,nm,fs=8.5); S(ax,x+1.4,7.35,dt,fs=6.5,c='#333')
    for xb in [1.9,5.0,8.1,11.2,14.3,17.1]: arr(ax,xb,6.5,xb,5.8,'#7FA9B8',1)
    # 计算层
    box(ax,0.3,4.0,17.4,1.7,'#E8F6EC','#7FA9B8',1.2); L(ax,0.7,5.4,'计算层',fs=9,fw='bold',c='#555',va='top')
    calcs=[
        ('工控机 IP54','Jetson AGX Orin',0.5,'#C8EDD5','#1E7A3C'),
        ('融合判定单元\n三级融合','时间对齐→空间关联→\n判级融合·自适应动态加权',5.0,'#A8D5B5','#155C28'),
        ('环形缓冲区\n帧边界对齐','三键索引元组\nD(FID,s,t)',10.0,'#A8D5B5','#155C28'),
        ('通信模块 4G/5G','远程监控\n数据上传',14.0,'#FFE4B5','#B86A00'),
    ]
    for nm,dt,x,fc,ec in calcs:
        box(ax,x,4.15,3.8,1.4,fc,ec,1.2); L(ax,x+1.9,5.05,nm,fs=8.5); S(ax,x+1.9,4.4,dt,fs=6.5,c='#555')
    for xb in [2.4,6.4,11.9,15.9]: arr(ax,xb,4.0,xb,3.5,'#7FA9B8',1)
    # 供电层
    box(ax,0.3,2.0,17.4,1.1,'#F3E8F8','#7FA9B8',1.2); L(ax,0.7,2.85,'供电层',fs=9,fw='bold',c='#555',va='top')
    box(ax,0.5,2.15,17.0,0.75,'#D8B8E0','#7A1A9A',1.2)
    L(ax,9,2.53,'供电模块 48V大容量蓄电池组 智能电源管理 BMS板/管理板温度三级保护',fs=9,fw='bold',c='#5A0A7A')
    # 底部指标
    box(ax,0.3,0.35,17.4,1.4,'#F9F9F9','#CCC',0.8)
    L(ax,9,1.5,'核心性能指标（济南铁路局120km以上实际线路验证）',fs=9,fw='bold',c='#333')
    L(ax,1.8,1.05,'融合判定准确率97.5%',fs=8,c='#1E7A3C'); L(ax,5.0,1.05,'传感器退化场景96.1%',fs=8,c='#1E7A3C')
    L(ax,8.2,1.05,'空间对齐精度3.2mm（降低74.7%）',fs=8,c='#1A6FA8'); L(ax,11.8,1.05,'轨面缺陷mAP@0.5=92.5%',fs=8,c='#1A6FA8')
    L(ax,15.0,1.05,'振动噪声降低53.7%',fs=8,c='#B86A00')
    L(ax,9,0.55,'检测速度：0.5m/s（精细检测）/1m/s（常规检测） | 三网物理隔离：EtherCAT控制网+千兆采集网+无线传输网',fs=7.5,c='#666')
    save(fig,'fig1_final_v2.png')

fig1()
print("Done")