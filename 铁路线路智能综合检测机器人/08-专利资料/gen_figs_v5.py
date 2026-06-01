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

def S(ax, x, y, t, fs=7, c='#555', ha='center', va='center'):
    ax.text(x, y, t, ha=ha, va=va, fontsize=fs, color=c, linespacing=1.25)

def arr(ax, x1,y1,x2,y2, c='#555', lw=1.2):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='->',color=c,lw=lw,shrinkA=3,shrinkB=3))

def fig1():
    fig,ax=plt.subplots(figsize=(18,11)); ax.set_xlim(0,18); ax.set_ylim(0,11); ax.axis('off'); fig.patch.set_facecolor('white')
    L(ax,9,10.5,'铁路线路智能视觉与多模态感知融合综合检测系统',fs=15); ax.axhline(10.1,xmin=.02,xmax=.98,c='#ccc',lw=1)
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
    box(ax,0.3,2.0,17.4,1.1,'#F3E8F8','#7FA9B8',1.2); L(ax,0.7,2.85,'供电层',fs=9,fw='bold',c='#555',va='top')
    box(ax,0.5,2.15,17.0,0.75,'#D8B8E0','#7A1A9A',1.2)
    L(ax,9,2.53,'供电模块 48V大容量蓄电池组 智能电源管理 BMS板/管理板温度三级保护',fs=9,fw='bold',c='#5A0A7A')
    box(ax,0.3,0.35,17.4,1.4,'#F9F9F9','#CCC',0.8)
    L(ax,9,1.5,'核心性能指标（济南铁路局120km以上实际线路验证）',fs=9,fw='bold',c='#333')
    L(ax,1.8,1.05,'融合判定准确率97.5%',fs=8,c='#1E7A3C'); L(ax,5.0,1.05,'传感器退化场景96.1%',fs=8,c='#1E7A3C')
    L(ax,8.2,1.05,'空间对齐精度3.2mm（降低74.7%）',fs=8,c='#1A6FA8'); L(ax,11.8,1.05,'轨面缺陷mAP@0.5=92.5%',fs=8,c='#1A6FA8')
    L(ax,15.0,1.05,'振动噪声降低53.7%',fs=8,c='#B86A00')
    L(ax,9,0.55,'检测速度：0.5m/s（精细检测）/1m/s（常规检测） | 三网物理隔离：EtherCAT控制网+千兆采集网+无线传输网',fs=7.5,c='#666')
    save(fig,'fig1_final_v2.png')

def fig2():
    fig,ax=plt.subplots(figsize=(16,10)); ax.set_xlim(0,16); ax.set_ylim(0,10); ax.axis('off'); fig.patch.set_facecolor('white')
    L(ax,8,9.6,'三键索引时空对齐机制示意图',fs=14); ax.axhline(9.2,xmin=.02,xmax=.98,c='#ccc',lw=1)
    ins=[('编码器','100脉冲/帧\n生成帧编号FIDk\n分辨率≈5mm/帧',0.4,'#D6EAF8','#1A6FA8'),
         ('PTP时钟同步\nIEEE 1588','UTC时间戳\n精度优于1μs\n跨传感器时间统一',5.7,'#E8F6EC','#1E7A3C'),
         ('里程标定\n（标准轨段）','消除轮径磨损误差\n消除打滑引入误差\n帧号→里程映射',11.0,'#FFF3E0','#B86A00')]
    for nm,dt,x,fc,ec in ins:
        box(ax,x,6.3,4.3,3.0,fc,ec,1.5); L(ax,x+2.15,9.1,nm,fs=10); S(ax,x+2.15,7.35,dt,fs=7.5,c='#333')
    for xb in [2.5,7.85,13.15]: arr(ax,xb,6.3,xb,5.2,'#888',1.5)
    box(ax,3.0,1.8,10.0,3.1,'#FFF3E0','#B86A00',2.5,0.12)
    L(ax,8,4.45,'三键索引元组  D(FIDk, sk, tk)',fs=13,fw='bold',c='#B86A00')
    L(ax,8,3.65,'帧编号 FIDk  ·  里程坐标 sk  ·  UTC时间戳 tk',fs=10,c='#555')
    L(ax,8,2.9,'帧边界精确对齐 → 多传感器硬件级时空统一',fs=9,c='#777')
    arr(ax,8,1.8,8,1.0,'#B86A00',2)
    ax.annotate('',xy=(1.5,1.0),xytext=(5.0,1.8),arrowprops=dict(arrowstyle='->',color='#B86A00',lw=1,linestyle='dashed'))
    ax.annotate('',xy=(14.5,1.0),xytext=(11.0,1.8),arrowprops=dict(arrowstyle='->',color='#B86A00',lw=1,linestyle='dashed'))
    outs=[('2D工业相机×6','20fps帧触发曝光',0.4,0.15,'#C8EDD5','#1E7A3C'),
          ('3D线激光×2','20000Hz帧中心采样',3.55,0.15,'#C8EDD5','#1E7A3C'),
          ('HWT905','200Hz帧边界对齐',6.7,0.15,'#B8D4ED','#0D4A8A'),
          ('单点测距×2','2000Hz最近值采样',9.85,0.15,'#B8D4ED','#0D4A8A'),
          ('测距矩阵','约1000Hz帧边界同步',13.0,0.15,'#D8B8E0','#7A1A9A')]
    for nm,dt,x,y,fc,ec in outs:
        box(ax,x,y,2.6,0.85,fc,ec,1.2); L(ax,x+1.3,y+0.65,nm,fs=8); S(ax,x+1.3,y+0.15,dt,fs=6.5,c='#555')
    L(ax,8,-0.3,'8种传感器数据帧边界精确对齐 · 空间对齐精度亚毫米级（平均偏差3.2mm，降低74.7%）· 济南铁路局120km以上验证',fs=8.5,c='#666')
    save(fig,'fig2_final_v2.png')

def fig3():
    fig,ax=plt.subplots(figsize=(16,11)); ax.set_xlim(0,16); ax.set_ylim(0,11); ax.axis('off'); fig.patch.set_facecolor('white')
    L(ax,8,10.5,'自适应动态加权几何平均融合算法流程图',fs=14); ax.axhline(10.1,xmin=.02,xmax=.98,c='#ccc',lw=1)
    ins=[('维度置信度C₁(t)','轨面缺陷视觉检测',0.4,8.5,3.0,'#D6EAF8','#1A6FA8'),
         ('维度置信度C₂(t)','几何参数检测',5.7,8.5,3.0,'#E8F6EC','#1E7A3C'),
         ('维度置信度C₃(t)','钢轨廓形/波磨检测',11.0,8.5,3.0,'#F3E8F8','#7A1A9A')]
    for nm,dt,x,y,w,fc,ec in ins:
        box(ax,x,y,w,1.4,fc,ec,1.5); L(ax,x+w/2,y+1.1,nm,fs=10); S(ax,x+w/2,y+0.25,dt,fs=7.5,c='#555')
    for xb in [1.9,7.2,12.5]: arr(ax,xb,8.5,xb,7.5,'#888',1.5)
    box(ax,0.4,6.3,15.2,0.8,'#FFF8E0','#B8860A',1.3)
    L(ax,8,6.7,'滑动标准差计算  σ₁(t)  σ₂(t)  σ₃(t)',fs=10,fw='bold',c='#333')
    arr(ax,8,6.3,8,5.5,'#888',1.5)
    box(ax,0.4,4.5,15.2,0.8,'#FFF8E0','#B8860A',1.3)
    L(ax,8,4.9,'可靠性因子  rd(t)=Cd(t)/σd(t)  →  归一化权重  wd(t)=rd(t)/Σrd(t)  且  w₁+w₂+w₃=1',fs=9.5,fw='bold',c='#333')
    for xb in [1.9,7.2,12.5]: ax.annotate('',xy=(xb,4.5),xytext=(xb,5.5),arrowprops=dict(arrowstyle='->',color='#AAA',lw=.8))
    arr(ax,8,4.5,8,3.5,'#B86A00',2)
    box(ax,3.0,2.5,10.0,0.95,'#FFE066','#B86A00',2.5,0.1)
    L(ax,8,3.0,'加权几何平均融合  Cfuse = ∏Cd(t)^wd(t)',fs=12,fw='bold',c='#B86A00')
    L(ax,8,2.6,'几何平均乘积特性：任一维度异常 → 融合置信度显著降低，防止误判传播',fs=8,c='#555')
    arr(ax,8,2.5,8,1.8,'#B86A00',2)
    outs=[('Cfuse < 0.5','检测结果丢弃',0.4,0.3,4.0,'#FFCDD2','#A82020'),
          ('0.5 ≤ Cfuse < 0.7','进入人工复核队列',5.7,0.3,4.0,'#FFF8E0','#B8860A'),
          ('Cfuse ≥ 0.7','最终判定输出',11.0,0.3,4.0,'#C8EDD5','#1E7A3C')]
    for nm,dt,x,y,w,fc,ec in outs:
        arr(ax,8,1.8,x+w/2,1.8,'#888',1); box(ax,x,y,w,1.3,fc,ec,1.5)
        L(ax,x+w/2,y+1.0,nm,fs=9); S(ax,x+w/2,y+0.25,dt,fs=8,c='#333')
    L(ax,8,-0.3,'融合判定准确率97.5% · 传感器退化场景下（20%噪声）仍保持96.1%（仅下降1.4个百分点）',fs=8.5,c='#666')
    save(fig,'fig3_final_v2.png')

def fig4():
    fig,ax=plt.subplots(figsize=(16,10)); ax.set_xlim(0,16); ax.set_ylim(0,10); ax.axis('off'); fig.patch.set_facecolor('white')
    L(ax,8,9.6,'快慢双速EKF融合架构图',fs=14); ax.axhline(9.2,xmin=.02,xmax=.98,c='#ccc',lw=1)
    # 快回路
    box(ax,0.3,4.0,5.7,5.0,'#D6EAF8','#1A6FA8',1.5); L(ax,3.15,8.75,'快回路（200Hz）',fs=11,fw='bold',c='#1A6FA8'); S(ax,3.15,8.35,'高频振动实时估计',fs=9,c='#555')
    box(ax,0.55,6.2,5.2,1.5,'#B8D4ED','#0D4A8A',1.2); L(ax,3.15,7.0,'HWT905姿态传感器',fs=10,fw='bold'); S(ax,3.15,6.5,'200Hz采样 三轴0.05° PTP同步',fs=8,c='#333')
    arr(ax,3.15,6.2,3.15,5.4,'#1A6FA8',2)
    box(ax,0.55,4.2,5.2,1.1,'#1A6FA8','#0A3A6A',1.2); L(ax,3.15,4.75,'快回路EKF状态估计',fs=9.5,fw='bold',c='white'); S(ax,3.15,4.35,'实时补偿车体振动 响应时间5ms',fs=8,c='#CCC')
    arr(ax,3.15,4.2,3.15,3.5,'#1A6FA8',2); box(ax,0.55,2.7,5.2,0.75,'#C8EDD5','#1E7A3C',1.5)
    L(ax,3.15,3.08,'车体振动补偿量 hveh → 中央融合',fs=9,fw='bold')
    # 中央
    box(ax,6.1,2.6,3.8,3.8,'#FFE066','#B86A00',2.5,0.1)
    L(ax,8,6.0,'中央融合单元',fs=11,fw='bold',c='#B86A00'); L(ax,8,5.35,'快慢双速\n解耦核心',fs=9,c='#555')
    L(ax,8,4.5,'频域完全解耦\n无混叠效应',fs=8.5,c='#777'); L(ax,8,3.55,'输出：高低\n不平顺结果',fs=8,c='#555')
    arr(ax,3.15,2.7,6.1,4.5,'#B86A00',1.5); arr(ax,9.9,4.5,12.45,2.7,'#B86A00',1.5)
    # 慢回路
    box(ax,10.0,4.0,5.7,5.0,'#E8F6EC','#1E7A3C',1.5); L(ax,12.85,8.75,'慢回路（10Hz）',fs=11,fw='bold',c='#1E7A3C'); S(ax,12.85,8.35,'轨道高程估计',fs=9,c='#555')
    box(ax,10.25,6.2,5.2,1.5,'#C8EDD5','#1E7A3C',1.2); L(ax,12.85,7.0,'单点测距传感器×2（主测）',fs=10,fw='bold'); S(ax,12.85,6.5,'2000Hz 精度±0.15mm 安装高度约180mm',fs=8,c='#333')
    arr(ax,12.85,6.2,12.85,5.4,'#1E7A3C',2)
    box(ax,10.25,4.2,5.2,1.1,'#1E7A3C','#0A5520',1.2); L(ax,12.85,4.75,'慢回路EKF状态估计',fs=9.5,fw='bold',c='white'); S(ax,12.85,4.35,'状态向量 xk=[htrack,hveh,vveh]',fs=8,c='#CCC')
    arr(ax,12.85,4.2,12.85,3.5,'#1E7A3C',2); box(ax,10.25,2.7,5.2,0.75,'#B8D4ED','#0D4A8A',1.5)
    L(ax,12.85,3.08,'轨道高程真值 htrack → 中央融合',fs=9,fw='bold')
    # 输出
    box(ax,4.8,0.5,6.4,1.0,'#A8D5B5','#155C28',2,0.1); L(ax,8,1.0,'高低不平顺测量结果  精度优于±0.5mm',fs=10,fw='bold')
    arr(ax,8,2.6,8,1.5,'#155C28',2)
    L(ax,8,0.15,'频率比20:1（快200Hz/慢10Hz） · 振动噪声降低53.7% · 轨道高程变化频带<1Hz · 车体振动频带0~20Hz',fs=8.5,c='#666')
    save(fig,'fig4_final_v2.png')

def fig5():
    fig,ax=plt.subplots(figsize=(18,10)); ax.set_xlim(0,18); ax.set_ylim(0,10); ax.axis('off'); fig.patch.set_facecolor('white')
    L(ax,9,9.6,'几何参数检测原理图（轨距/水平/高低）',fs=14); ax.axhline(9.2,xmin=.02,xmax=.98,c='#ccc',lw=1)
    panels=[{'title':'轨距检测','view':'俯视图','x':0.3,'fc':'#D6EAF8','ec':'#1A6FA8'},
           {'title':'水平检测','view':'侧视图','x':6.4,'fc':'#E8F6EC','ec':'#1E7A3C'},
           {'title':'高低检测','view':'侧视图','x':12.5,'fc':'#FFF3E0','ec':'#B86A00'}]
    for p in panels:
        x=p['x']; box(ax,x,0.5,5.8,8.5,p['fc'],p['ec'],1.5); L(ax,x+2.9,8.75,p['title'],fs=12,fw='bold',c=p['ec']); S(ax,x+2.9,8.25,p['view'],fs=9,c='#888')
        if p['title']=='轨距检测':
            ax.add_patch(Rectangle((x+0.3,6.0),0.6,1.4,facecolor='#795548',edgecolor='#4E342E',lw=2))
            ax.add_patch(Rectangle((x+4.9,6.0),0.6,1.4,facecolor='#795548',edgecolor='#4E342E',lw=2))
            ax.annotate('',xy=(x+0.9,7.5),xytext=(x+4.9,7.5),arrowprops=dict(arrowstyle='<->',color='#1A6FA8',lw=2))
            L(ax,x+2.9,7.7,'G',fs=12,fw='bold',c='#1A6FA8')
            S(ax,x+0.05,7.4,'dL',fs=8,va='top',c='#1A6FA8'); S(ax,x+5.7,7.4,'dR',fs=8,va='top',c='#1A6FA8')
            ax.add_patch(Rectangle((x+1.0,5.8),3.8,1.8,facecolor='#90A4AE',edgecolor='#546E7A',lw=2,zorder=3))
            L(ax,x+2.9,6.7,'检测小车',fs=9,c='#37474F')
            S(ax,x+2.9,4.5,'测距传感器矩阵\n直接测量左右轨内侧距',fs=8.5,c='#333')
            box(ax,x+0.2,3.0,5.4,0.85,'white',p['ec'],1.5); L(ax,x+2.9,3.43,'G = dL + dR',fs=11,fw='bold',c=p['ec'])
            S(ax,x+2.9,2.15,'与横滚角完全解耦\n精度优于±0.3mm\n采样率约1000Hz',fs=8,c='#555')
        elif p['title']=='水平检测':
            ax.plot([x+0.5,x+4.8], [6.2,6.2], color='#795548',lw=6,solid_capstyle='round')
            ax.plot([x+0.5,x+4.8], [5.0,5.0], color='#795548',lw=6,solid_capstyle='round')
            ax.plot([x+0.5,x+0.5],[6.2,5.0],color='#795548',lw=2,linestyle='--')
            ax.plot([x+4.8,x+4.8],[6.2,5.0],color='#795548',lw=2,linestyle='--')
            ax.annotate('',xy=(x+0.5,5.85),xytext=(x+0.5,6.2),arrowprops=dict(arrowstyle='<->',color='#1E7A3C',lw=1.8))
            S(ax,x+0.3,5.75,'Δh',fs=9,c='#1E7A3C')
            ax.add_patch(Rectangle((x+1.5,4.7),2.5,0.6,facecolor='#90A4AE',edgecolor='#546E7A',lw=2))
            L(ax,x+2.9,5.0,'HWT905',fs=9,c='#37474F')
            S(ax,x+2.9,3.8,'横滚角θr测量\n超高差计算',fs=8.5,c='#333')
            box(ax,x+0.2,3.0,5.4,0.85,'white',p['ec'],1.5); L(ax,x+2.9,3.43,'Δh = 1435 × sin(θr)',fs=11,fw='bold',c=p['ec'])
            S(ax,x+2.9,2.15,'标准轨距1435mm\n误差小于0.4mm\n采样率200Hz',fs=8,c='#555')
        else:
            ax.plot([x+0.5,x+4.8],[6.5,6.5],color='#795548',lw=6,solid_capstyle='round')
            ax.plot([x+0.5,x+2.0],[6.1,6.1],color='#795548',lw=6,solid_capstyle='round')
            ax.plot([x+2.0,x+2.0],[6.5,6.1],color='#795548',lw=2,linestyle='--')
            ax.annotate('',xy=(x+1.0,6.9),xytext=(x+1.0,6.1),arrowprops=dict(arrowstyle='<->',color='#B86A00',lw=1.8))
            L(ax,x+0.85,6.55,'z',fs=9,c='#B86A00')
            ax.add_patch(Rectangle((x+0.8,6.25),1.2,0.45,facecolor='#90A4AE',edgecolor='#546E7A',lw=2))
            L(ax,x+1.4,6.47,'传感器',fs=7,c='#37474F')
            S(ax,x+2.9,4.5,'单点测距（主测）\n+HWT905（辅助）\n快慢双速EKF融合',fs=8.5,c='#333')
            box(ax,x+0.2,3.0,5.4,0.85,'white',p['ec'],1.5); L(ax,x+2.9,3.43,'z = H - D',fs=11,fw='bold',c=p['ec'])
            S(ax,x+2.9,2.15,'快慢双速EKF融合\n精度优于±0.5mm\n三键索引与视觉关联',fs=8,c='#555')
    L(ax,9,0.15,'所有检测值均通过三键索引与视觉检测数据关联',fs=8.5,c='#666')
    save(fig,'fig5_final_v2.png')

fig1(); fig2(); fig3(); fig4(); fig5()
print("All 5 figures saved.")