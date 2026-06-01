#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
plt.rcParams['axes.unicode_minus'] = False

OUT = '/root/.openclaw/media/tool-image-generation/'

def save(fig, name):
    fig.savefig(f'{OUT}{name}', dpi=180, bbox_inches='tight', facecolor='white', pad_inches=0.4)
    plt.close(fig)
    print(f'Saved: {name}')

def box(ax, x, y, w, h, fc, ec, lw=1.5, r=0.08):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad={r}',facecolor=fc,edgecolor=ec,lw=lw))

def L(ax, x, y, t, fs=10, fw='bold', c='#1a1a1a', ha='center', va='center'):
    ax.text(x, y, t, ha=ha, va=va, fontsize=fs, fontweight=fw, color=c, linespacing=1.5)

def S(ax, x, y, t, fs=8, c='#444', ha='center', va='center'):
    ax.text(x, y, t, ha=ha, va=va, fontsize=fs, color=c, linespacing=1.3)

def arr(ax, x1,y1,x2,y2, c='#666', lw=1.5):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='->',color=c,lw=lw,shrinkA=5,shrinkB=5))

# ============================================================
# 图1：系统总体架构
# ============================================================
def fig1():
    fig,ax=plt.subplots(figsize=(20,12)); ax.set_xlim(0,20); ax.set_ylim(0,12); ax.axis('off'); fig.patch.set_facecolor('white')
    L(ax,10,11.4,'铁路线路智能视觉与多模态感知融合综合检测系统',fs=16); ax.axhline(11.0,xmin=.02,xmax=.98,c='#ccc',lw=1.2)

    # 感知层
    box(ax,0.4,7.2,19.2,3.6,'#EBF5FB','#6A9BBF',1.5)
    L(ax,0.9,10.55,'感知层',fs=11,fw='bold',c='#2A5A8A',va='top')

    items=[
        ('6路2D工业相机','2448×2048  20fps\n千兆以太网\n轨面缺陷×2·道钉螺栓×2·焊缝×2',0.7,'#D0E8F8','#1A6FA8'),
        ('3D线激光×2','20000Hz  3200点/轮廓\nIP67防护等级\n左右钢轨轨头轮廓扫描',4.2,'#D0E8F8','#1A6FA8'),
        ('HWT905姿态传感器','200Hz  三轴0.05°\nIEEE 1588 PTP同步',7.7,'#D0E8F8','#1A6FA8'),
        ('单点测距传感器×2','2000Hz  精度±0.15mm\n仅用于高低检测',10.8,'#D0E8F8','#1A6FA8'),
        ('测距传感器矩阵','直接测轨距\nG=dL+dR 与横滚角解耦\n±0.3mm',13.9,'#A8CCE8','#0D4A8A'),
        ('编码器','100脉冲/帧\n分辨率≈5mm',17.2,'#D8F0E0','#1E7A3C'),
    ]
    for nm,dt,x,fc,ec in items:
        box(ax,x,7.4,3.2,3.2,fc,ec,1.5); L(ax,x+1.6,10.35,nm,fs=9.5); S(ax,x+1.6,8.1,dt,fs=7.5,c='#333')
    for xb in [2.3,5.8,9.3,12.4,15.5,18.8]: arr(ax,xb,7.2,xb,6.5,'#6A9BBF',1.2)

    # 计算层
    box(ax,0.4,4.3,19.2,2.0,'#D8F0E0','#6A9BBF',1.5)
    L(ax,0.9,6.05,'计算层',fs=11,fw='bold',c='#2A6A3A',va='top')
    calcs=[
        ('工控机 IP54','Jetson AGX Orin\n融合判定单元',0.7,'#B8E0C8','#1E7A3C'),
        ('融合判定单元\n三级融合','时间对齐→空间关联→\n判级融合·自适应动态加权',5.5,'#98D0A8','#155C28'),
        ('环形缓冲区\n帧边界对齐','三键索引元组\nD(FID,s,t)',10.5,'#98D0A8','#155C28'),
        ('通信模块 4G/5G','远程监控\n数据上传',15.2,'#FFE8C0','#B86A00'),
    ]
    for nm,dt,x,fc,ec in calcs:
        box(ax,x,4.5,4.3,1.7,fc,ec,1.3); L(ax,x+2.15,5.85,nm,fs=9.5); S(ax,x+2.15,4.85,dt,fs=7.5,c='#555')
    for xb in [2.85,7.65,12.65,17.35]: arr(ax,xb,4.3,xb,3.9,'#6A9BBF',1.2)

    # 供电层
    box(ax,0.4,2.4,19.2,1.2,'#EDE0F5','#6A9BBF',1.5); L(ax,0.9,3.35,'供电层',fs=11,fw='bold',c='#6A2A8A',va='top')
    box(ax,0.6,2.55,19.0,0.85,'#D0B8E8','#7A1A9A',1.3)
    L(ax,10,3.0,'供电模块  48V大容量蓄电池组  智能电源管理  BMS板/管理板温度三级保护',fs=10,fw='bold',c='#5A0A7A')

    # 底部指标
    box(ax,0.4,0.4,19.2,1.7,'#F8F8F8','#BBB',1)
    L(ax,10,1.85,'核心性能指标（济南铁路局120km以上实际线路验证）',fs=10,fw='bold',c='#222')
    L(ax,2.2,1.3,'融合判定准确率97.5%',fs=9,c='#1E7A3C'); L(ax,6.5,1.3,'传感器退化场景96.1%',fs=9,c='#1E7A3C')
    L(ax,10.5,1.3,'空间对齐精度3.2mm（降低74.7%）',fs=9,c='#1A6FA8'); L(ax,15.0,1.3,'轨面缺陷mAP@0.5=92.5%',fs=9,c='#1A6FA8')
    L(ax,18.5,1.3,'振动噪声降低53.7%',fs=9,c='#B86A00')
    L(ax,10,0.7,'检测速度：0.5m/s（精细检测）/1m/s（常规检测） | 三网物理隔离：EtherCAT控制网+千兆采集网+无线传输网',fs=8.5,c='#666')
    save(fig,'fig1_v3.png')

# ============================================================
# 图2：三键索引时空对齐机制
# ============================================================
def fig2():
    fig,ax=plt.subplots(figsize=(18,11)); ax.set_xlim(0,18); ax.set_ylim(0,11); ax.axis('off'); fig.patch.set_facecolor('white')
    L(ax,9,10.4,'三键索引时空对齐机制示意图',fs=15); ax.axhline(9.9,xmin=.02,xmax=.98,c='#ccc',lw=1.2)

    ins=[('编码器','100脉冲/帧\n生成帧编号FIDk\n分辨率≈5mm/帧',0.5,'#D0E8F8','#1A6FA8'),
         ('PTP时钟同步\nIEEE 1588','UTC时间戳\n精度优于1μs\n跨传感器时间统一',6.3,'#D8F0E0','#1E7A3C'),
         ('里程标定\n（标准轨段）','消除轮径磨损误差\n消除打滑引入误差\n帧号→里程映射',12.1,'#FFF0D8','#B86A00')]
    for nm,dt,x,fc,ec in ins:
        box(ax,x,6.8,4.8,3.3,fc,ec,1.5); L(ax,x+2.4,9.85,nm,fs=11); S(ax,x+2.4,7.95,dt,fs=8.5,c='#333')
    for xb in [2.9,8.7,14.5]: arr(ax,xb,6.8,xb,5.5,'#888',1.5)

    box(ax,3.5,2.0,11.0,3.2,'#FFF0D8','#B86A00',2.5,0.12)
    L(ax,9,4.75,'三键索引元组  D(FIDk, sk, tk)',fs=14,fw='bold',c='#B86A00')
    L(ax,9,3.85,'帧编号 FIDk  ·  里程坐标 sk  ·  UTC时间戳 tk',fs=10,c='#555')
    L(ax,9,3.0,'帧边界精确对齐 → 多传感器硬件级时空统一',fs=9.5,c='#777')
    arr(ax,9,2.0,9,1.2,'#B86A00',2)
    ax.annotate('',xy=(2.0,1.2),xytext=(5.0,2.0),arrowprops=dict(arrowstyle='->',color='#B86A00',lw=1.2,linestyle='dashed'))
    ax.annotate('',xy=(16.0,1.2),xytext=(13.0,2.0),arrowprops=dict(arrowstyle='->',color='#B86A00',lw=1.2,linestyle='dashed'))

    outs=[('2D工业相机×6','20fps 帧触发曝光',0.5,0.2,'#B8E0C8','#1E7A3C'),
          ('3D线激光×2','20000Hz 帧中心采样',4.1,0.2,'#B8E0C8','#1E7A3C'),
          ('HWT905','200Hz 帧边界对齐',7.7,0.2,'#A8CCE8','#0D4A8A'),
          ('单点测距×2','2000Hz 最近值采样',11.3,0.2,'#A8CCE8','#0D4A8A'),
          ('测距矩阵','约1000Hz 帧边界同步',14.9,0.2,'#D0B8E8','#7A1A9A')]
    for nm,dt,x,y,fc,ec in outs:
        box(ax,x,y,3.0,1.0,fc,ec,1.3); L(ax,x+1.5,y+0.75,nm,fs=9); S(ax,x+1.5,y+0.2,dt,fs=7.5,c='#555')
    L(ax,9,-0.2,'8种传感器数据帧边界精确对齐 · 空间对齐精度亚毫米级（平均偏差3.2mm，降低74.7%）· 济南铁路局120km以上验证',fs=9,c='#666')
    save(fig,'fig2_v3.png')

# ============================================================
# 图3：自适应动态加权几何平均融合算法流程图
# ============================================================
def fig3():
    fig,ax=plt.subplots(figsize=(18,12)); ax.set_xlim(0,18); ax.set_ylim(0,12); ax.axis('off'); fig.patch.set_facecolor('white')
    L(ax,9,11.4,'自适应动态加权几何平均融合算法流程图',fs=15); ax.axhline(10.9,xmin=.02,xmax=.98,c='#ccc',lw=1.2)

    ins=[('维度置信度C1(t)','轨面缺陷视觉检测',0.5,9.3,3.3,'#D0E8F8','#1A6FA8'),
         ('维度置信度C2(t)','几何参数检测',6.6,9.3,3.3,'#D8F0E0','#1E7A3C'),
         ('维度置信度C3(t)','钢轨廓形/波磨检测',12.7,9.3,3.3,'#EDE0F5','#7A1A9A')]
    for nm,dt,x,y,w,fc,ec in ins:
        box(ax,x,y,w,1.6,fc,ec,1.5); L(ax,x+w/2,y+1.25,nm,fs=11); S(ax,x+w/2,y+0.25,dt,fs=8.5,c='#555')
    for xb in [2.15,8.25,14.35]: arr(ax,xb,9.3,xb,8.1,'#888',1.5)

    box(ax,0.5,6.8,17.0,0.9,'#FFF8D8','#B8860A',1.5)
    L(ax,9,7.25,'滑动标准差计算  σ1(t)  σ2(t)  σ3(t)',fs=11,fw='bold',c='#333')
    arr(ax,9,6.8,9,5.8,'#888',1.5)

    box(ax,0.5,4.7,17.0,0.9,'#FFF8D8','#B8860A',1.5)
    L(ax,9,5.15,'可靠性因子  rd(t)=Cd(t)/σd(t)  →  归一化权重  wd(t)=rd(t)/Σrd(t)  且  w1+w2+w3=1',fs=10,fw='bold',c='#333')
    for xb in [2.15,8.25,14.35]: ax.annotate('',xy=(xb,4.7),xytext=(xb,5.8),arrowprops=dict(arrowstyle='->',color='#AAA',lw=1))

    arr(ax,9,4.7,9,3.6,'#B86A00',2)
    box(ax,3.5,2.5,11.0,1.0,'#FFE066','#B86A00',2.5,0.1)
    L(ax,9,3.05,'加权几何平均融合  Cfuse = ∏Cd(t)^wd(t)',fs=13,fw='bold',c='#B86A00')
    L(ax,9,2.6,'几何平均乘积特性：任一维度异常 → 融合置信度显著降低，防止误判传播',fs=9,c='#555')
    arr(ax,9,2.5,9,1.8,'#B86A00',2)

    outs=[('Cfuse < 0.5','检测结果丢弃',0.5,0.35,4.5,'#FFCDD2','#A82020'),
          ('0.5 ≤ Cfuse < 0.7','进入人工复核队列',6.75,0.35,4.5,'#FFF8D8','#B8860A'),
          ('Cfuse ≥ 0.7','最终判定输出',13.0,0.35,4.5,'#B8E0C8','#1E7A3C')]
    for nm,dt,x,y,w,fc,ec in outs:
        arr(ax,9,1.8,x+w/2,1.8,'#888',1); box(ax,x,y,w,1.4,fc,ec,1.5)
        L(ax,x+w/2,y+1.1,nm,fs=10); S(ax,x+w/2,y+0.25,dt,fs=9,c='#333')
    L(ax,9,-0.2,'融合判定准确率97.5% · 传感器退化场景下（20%噪声）仍保持96.1%（仅下降1.4个百分点）',fs=9.5,c='#666')
    save(fig,'fig3_v3.png')

# ============================================================
# 图4：快慢双速EKF融合架构图
# ============================================================
def fig4():
    fig,ax=plt.subplots(figsize=(18,11)); ax.set_xlim(0,18); ax.set_ylim(0,11); ax.axis('off'); fig.patch.set_facecolor('white')
    L(ax,9,10.4,'快慢双速EKF融合架构图',fs=15); ax.axhline(9.9,xmin=.02,xmax=.98,c='#ccc',lw=1.2)

    # 快回路
    box(ax,0.4,4.3,6.0,5.3,'#D0E8F8','#1A6FA8',1.5); L(ax,3.4,9.3,'快回路（200Hz）',fs=12,fw='bold',c='#1A6FA8'); S(ax,3.4,8.85,'高频振动实时估计',fs=9.5,c='#555')
    box(ax,0.7,6.8,5.4,1.6,'#A8CCE8','#0D4A8A',1.3); L(ax,3.4,7.7,'HWT905姿态传感器',fs=10.5,fw='bold'); S(ax,3.4,7.15,'200Hz采样 三轴0.05° PTP同步',fs=8.5,c='#333')
    arr(ax,3.4,6.8,3.4,5.8,'#1A6FA8',2.5)
    box(ax,0.7,4.5,5.4,1.2,'#1A6FA8','#0A3A6A',1.3); L(ax,3.4,5.15,'快回路EKF状态估计',fs=10,fw='bold',c='white'); S(ax,3.4,4.65,'实时补偿车体振动 响应时间5ms',fs=8.5,c='#CCC')
    arr(ax,3.4,4.5,3.4,3.7,'#1A6FA8',2.5); box(ax,0.7,2.9,5.4,0.8,'#B8E0C8','#1E7A3C',1.5)
    L(ax,3.4,3.3,'车体振动补偿量 hveh → 中央融合',fs=10,fw='bold')

    # 中央
    box(ax,6.5,2.8,5.0,4.0,'#FFE066','#B86A00',2.5,0.12)
    L(ax,9,6.4,'中央融合单元',fs=12,fw='bold',c='#B86A00'); L(ax,9,5.65,'快慢双速\n解耦核心',fs=10,c='#555')
    L(ax,9,4.7,'频域完全解耦\n无混叠效应',fs=9.5,c='#777'); L(ax,9,3.65,'输出：高低\n不平顺结果',fs=9.5,c='#555')
    arr(ax,3.4,2.9,6.5,4.6,'#B86A00',1.8); arr(ax,11.5,4.6,14.6,2.8,'#B86A00',1.8)

    # 慢回路
    box(ax,11.6,4.3,6.0,5.3,'#D8F0E0','#1E7A3C',1.5); L(ax,14.6,9.3,'慢回路（10Hz）',fs=12,fw='bold',c='#1E7A3C'); S(ax,14.6,8.85,'轨道高程估计',fs=9.5,c='#555')
    box(ax,11.9,6.8,5.4,1.6,'#B8E0C8','#1E7A3C',1.3); L(ax,14.6,7.7,'单点测距传感器×2（主测）',fs=10.5,fw='bold'); S(ax,14.6,7.15,'2000Hz 精度±0.15mm 安装高度约180mm',fs=8.5,c='#333')
    arr(ax,14.6,6.8,14.6,5.8,'#1E7A3C',2.5)
    box(ax,11.9,4.5,5.4,1.2,'#1E7A3C','#0A5520',1.3); L(ax,14.6,5.15,'慢回路EKF状态估计',fs=10,fw='bold',c='white'); S(ax,14.6,4.65,'状态向量 xk=[htrack,hveh,vveh]',fs=8.5,c='#CCC')
    arr(ax,14.6,4.5,14.6,3.7,'#1E7A3C',2.5); box(ax,11.9,2.9,5.4,0.8,'#A8CCE8','#0D4A8A',1.5)
    L(ax,14.6,3.3,'轨道高程真值 htrack → 中央融合',fs=10,fw='bold')

    # 输出
    box(ax,5.2,0.5,7.6,1.1,'#98D0A8','#155C28',2,0.1); L(ax,9,1.05,'高低不平顺测量结果  精度优于±0.5mm',fs=11,fw='bold')
    arr(ax,9,2.8,9,1.6,'#155C28',2.5)
    L(ax,9,0.15,'频率比20:1（快200Hz/慢10Hz） · 振动噪声降低53.7% · 轨道高程变化频带<1Hz · 车体振动频带0~20Hz',fs=9,c='#666')
    save(fig,'fig4_v3.png')

# ============================================================
# 图5：几何参数检测原理图
# ============================================================
def fig5():
    fig,ax=plt.subplots(figsize=(20,11)); ax.set_xlim(0,20); ax.set_ylim(0,11); ax.axis('off'); fig.patch.set_facecolor('white')
    L(ax,10,10.4,'几何参数检测原理图（轨距/水平/高低）',fs=15); ax.axhline(9.9,xmin=.02,xmax=.98,c='#ccc',lw=1.2)

    panels=[{'title':'轨距检测','view':'俯视图','x':0.4,'fc':'#D0E8F8','ec':'#1A6FA8'},
           {'title':'水平检测','view':'侧视图','x':7.1,'fc':'#D8F0E0','ec':'#1E7A3C'},
           {'title':'高低检测','view':'侧视图','x':13.8,'fc':'#FFF0D8','ec':'#B86A00'}]

    for p in panels:
        x=p['x']; box(ax,x,0.5,6.3,9.0,p['fc'],p['ec'],1.5); L(ax,x+3.15,9.15,p['title'],fs=13,fw='bold',c=p['ec']); S(ax,x+3.15,8.6,p['view'],fs=10,c='#888')

        if p['title']=='轨距检测':
            ax.add_patch(Rectangle((x+0.4,6.5),0.7,1.6,facecolor='#795548',edgecolor='#4E342E',lw=2.5))
            ax.add_patch(Rectangle((x+5.2,6.5),0.7,1.6,facecolor='#795548',edgecolor='#4E342E',lw=2.5))
            ax.annotate('',xy=(x+1.1,8.2),xytext=(x+5.2,8.2),arrowprops=dict(arrowstyle='<->',color='#1A6FA8',lw=2.5))
            L(ax,x+3.15,8.5,'G',fs=14,fw='bold',c='#1A6FA8')
            S(ax,x+0.05,8.05,'dL',fs=10,va='top',c='#1A6FA8'); S(ax,x+6.3,8.05,'dR',fs=10,va='top',c='#1A6FA8')
            ax.add_patch(Rectangle((x+1.2,6.3),4.0,2.0,facecolor='#90A4AE',edgecolor='#546E7A',lw=2.5,zorder=3))
            L(ax,x+3.15,7.35,'检测小车',fs=10,c='#37474F')
            S(ax,x+3.15,5.0,'测距传感器矩阵\n直接测量左右轨内侧距',fs=9.5,c='#333')
            box(ax,x+0.3,3.3,5.7,1.0,'white',p['ec'],1.8); L(ax,x+3.15,3.8,'G = dL + dR',fs=13,fw='bold',c=p['ec'])
            S(ax,x+3.15,2.5,'与横滚角完全解耦\n精度优于±0.3mm\n采样率约1000Hz',fs=9,c='#555')

        elif p['title']=='水平检测':
            ax.plot([x+0.6,x+5.3],[6.8,6.8],color='#795548',lw=8,solid_capstyle='round')
            ax.plot([x+0.6,x+5.3],[5.2,5.2],color='#795548',lw=8,solid_capstyle='round')
            ax.plot([x+0.6,x+0.6],[6.8,5.2],color='#795548',lw=2.5,linestyle='--')
            ax.plot([x+5.3,x+5.3],[6.8,5.2],color='#795548',lw=2.5,linestyle='--')
            ax.annotate('',xy=(x+0.6,6.45),xytext=(x+0.6,6.8),arrowprops=dict(arrowstyle='<->',color='#1E7A3C',lw=2))
            S(ax,x+0.35,6.3,'Δh',fs=10,c='#1E7A3C')
            ax.add_patch(Rectangle((x+1.7,4.9),3.0,0.7,facecolor='#90A4AE',edgecolor='#546E7A',lw=2.5))
            L(ax,x+3.15,5.25,'HWT905',fs=10,c='#37474F')
            S(ax,x+3.15,3.9,'横滚角θr测量\n超高差计算',fs=9.5,c='#333')
            box(ax,x+0.3,3.3,5.7,1.0,'white',p['ec'],1.8); L(ax,x+3.15,3.8,'Δh = 1435 × sin(θr)',fs=13,fw='bold',c=p['ec'])
            S(ax,x+3.15,2.5,'标准轨距1435mm\n误差小于0.4mm\n采样率200Hz',fs=9,c='#555')

        else:
            ax.plot([x+0.6,x+5.3],[7.2,7.2],color='#795548',lw=8,solid_capstyle='round')
            ax.plot([x+0.6,x+2.5],[6.7,6.7],color='#795548',lw=8,solid_capstyle='round')
            ax.plot([x+2.5,x+2.5],[7.2,6.7],color='#795548',lw=2.5,linestyle='--')
            ax.annotate('',xy=(x+1.2,8.1),xytext=(x+1.2,6.7),arrowprops=dict(arrowstyle='<->',color='#B86A00',lw=2))
            L(ax,x+1.0,7.45,'z',fs=10,c='#B86A00')
            ax.add_patch(Rectangle((x+0.9,6.9),1.4,0.55,facecolor='#90A4AE',edgecolor='#546E7A',lw=2.5))
            L(ax,x+1.6,7.17,'传感器',fs=8.5,c='#37474F')
            S(ax,x+3.15,5.0,'单点测距（主测）\n+HWT905（辅助）\n快慢双速EKF融合',fs=9.5,c='#333')
            box(ax,x+0.3,3.3,5.7,1.0,'white',p['ec'],1.8); L(ax,x+3.15,3.8,'z = H - D',fs=13,fw='bold',c=p['ec'])
            S(ax,x+3.15,2.5,'快慢双速EKF融合\n精度优于±0.5mm\n三键索引与视觉关联',fs=9,c='#555')

    L(ax,10,0.15,'所有检测值均通过三键索引与视觉检测数据关联',fs=9.5,c='#666')
    save(fig,'fig5_v3.png')

fig1(); fig2(); fig3(); fig4(); fig5()
print("All 5 figures saved.")