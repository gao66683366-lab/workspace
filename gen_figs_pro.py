#!/usr/bin/env python3
"""Draw 5 professional patent diagrams - pure cairo + cairo show_text for CJK."""
import math
import cairocffi as cairo
from PIL import Image
import numpy as np

OUT = "/root/.openclaw/media/tool-image-generation"
W, H = 1200, 900

def make_surface():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.paint()
    return surf, ctx

def save(surf, name):
    data = surf.get_data()
    arr = np.frombuffer(data, dtype=np.uint8).copy()
    # Cairo ARGB32 little-endian: [B,G,R,A] -> PIL RGBA: [R,G,B,A]
    swap = np.empty_like(arr)
    swap[0::4] = arr[2::4]
    swap[1::4] = arr[1::4]
    swap[2::4] = arr[0::4]
    swap[3::4] = arr[3::4]
    img = Image.frombuffer('RGBA', (W, H), swap.tobytes(), 'raw', 'RGBA', 0, 1)
    img = img.convert('RGB')
    img.save(f"{OUT}/{name}", 'PNG', quality=95)
    print(f"Saved {name}")

def set_font(ctx, size, weight=False):
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.set_font_size(size)
    try:
        ctx.select_font_face("Noto Sans CJK SC",
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_BOLD if weight else cairo.FONT_WEIGHT_NORMAL)
    except Exception:
        pass

def text_advance(ctx, text):
    """Return (width, height) for text at current font."""
    ext = ctx.text_extents(text)
    return ext[2], ext[3]  # width, height

def ctext_center(ctx, text, size, cx, cy, cw, ch, weight=False):
    set_font(ctx, size, weight)
    ext = ctx.text_extents(text)
    tw, th = ext[2], ext[3]
    fe = ctx.font_extents()
    th_total = fe[2]  # height from font_extents tuple
    tx = cx + (cw - tw) / 2
    ty = cy + (ch + th_total * 0.35) / 2
    ctx.move_to(tx, ty)
    ctx.show_text(text)

def pill(ctx, x, y, w, h, lw=2):
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.set_line_width(lw)
    ctx.rectangle(x, y, w, h)
    ctx.stroke()

def pill_fill(ctx, x, y, w, h, lw=2):
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.rectangle(x, y, w, h)
    ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.set_line_width(lw)
    ctx.rectangle(x, y, w, h)
    ctx.stroke()

def cline(ctx, x1, y1, x2, y2, lw=2):
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.set_line_width(lw)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()

def carrow(ctx, x1, y1, x2, y2, lw=2, head=12):
    cline(ctx, x1, y1, x2, y2, lw)
    angle = math.atan2(y2-y1, x2-x1)
    ctx.move_to(x2, y2)
    ctx.line_to(x2 - head*math.cos(angle - math.pi/6),
                y2 - head*math.sin(angle - math.pi/6))
    ctx.line_to(x2 - head*math.cos(angle + math.pi/6),
                y2 - head*math.sin(angle + math.pi/6))
    ctx.stroke()

def cello(ctx, cx, cy, rx, ry, lw=2):
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.set_line_width(lw)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2*math.pi)
    ctx.restore()
    ctx.stroke()

def cdashed(ctx, x1, y1, x2, y2, lw=2, dash=None):
    if dash is None: dash = (8, 6)
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.set_line_width(lw)
    ctx.set_dash(dash)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()
    ctx.set_dash([])

def ccirnum(ctx, cx, cy, r, num, size=28):
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.set_line_width(2.5)
    ctx.arc(cx, cy, r, 0, 2*math.pi)
    ctx.stroke()
    set_font(ctx, size, weight=True)
    ctx.move_to(cx - 8, cy + 7)
    ctx.show_text(str(num))


# ======= FIG 1 =======
def fig1():
    surf, ctx = make_surface()
    FS, FS2, FS3 = 22, 18, 14

    ctext_center(ctx, "铁路线路智能综合检测系统硬件架构图", 28, 0, 18, W, 40, weight=True)

    top_y, layer_h, gap = 70, 108, 8
    layer_names = ["供电层","运动层","传感层","计算层","交互层","输出报告"]
    layer_items = [
        ["48V大容量蓄电池组","三级保护","BMS板温度监控","管理板温度监控","全节点电流电压监控"],
        ["4轮行走机构","伺服驱动","运行速度1m/s","急停回路"],
        ["2D工业相机×6","3D线激光×2","HWT905姿态传感器","单点测距传感器矩阵","轮速编码器"],
        ["工控机IP54","融合判定单元","本地存储SSD","EtherCAT总线","4G/5G通信模块"],
        ["触摸屏","遥控器"],
        ["轨面缺陷报告","几何参数报告","廓形波磨报告"],
    ]
    box_x, box_w = 110, W-160

    for i,(name,items) in enumerate(zip(layer_names,layer_items)):
        y = top_y + i*(layer_h+gap)
        pill(ctx, box_x, y, box_w, layer_h, lw=2)
        tag_w = 130
        pill_fill(ctx, box_x, y, tag_w, layer_h, lw=2)
        set_font(ctx, FS+2, weight=True)
        ctx.move_to(box_x + 12, y + layer_h/2 + 6)
        ctx.show_text(name)
        cx = box_x+tag_w+10
        cw = box_w-tag_w-10
        rows = 2 if len(items)<=4 else 3
        cols = (len(items)+rows-1)//rows
        rh = layer_h/rows
        idx = 0
        for row in range(rows):
            for col in range(cols):
                if idx>=len(items): break
                iy = y+row*rh
                ix = cx+col*(cw/cols)
                set_font(ctx, FS2)
                ctx.move_to(ix+6, iy+rh/2+6)
                ctx.show_text(items[idx])
                if col>0: cline(ctx,ix,iy,ix,iy+rh,lw=1)
                idx+=1
            if row>0: cline(ctx,cx,iy,box_x+box_w,iy,lw=1)

    for i in range(6):
        y = top_y+i*(layer_h+gap)+layer_h//2
        ccirnum(ctx, 50, y, 22, i+1, 26)

    ctext_center(ctx, "三网物理隔离：EtherCAT（硬实时控制）+ 千兆以太网（高速采集）+ 4G/5G（远程传输）", FS3, 0, H-35, W, 30)
    save(surf,"fig1_pro.png")

# ======= FIG 2 =======
def fig2():
    surf, ctx = make_surface()
    FS, FS2, FS3 = 20, 17, 14

    ctext_center(ctx,"三键索引时空对齐机制示意图",26,0,18,W,40,weight=True)

    top_y, box_w, box_h = 75, 260, 80
    gap_x = 60
    sx = (W - (box_w*3+gap_x*2))//2
    top_boxes = ["编码器\nN=100脉冲/帧","PTP时钟\nIEEE 1588 UTC","里程标定\n标准轨段映射"]
    bpos = []
    for i,txt in enumerate(top_boxes):
        bx = sx+i*(box_w+gap_x)
        bpos.append((bx,top_y))
        pill_fill(ctx,bx,top_y,box_w,box_h,lw=2)
        lines=txt.split('\n')
        ty=top_y+(box_h-len(lines)*28)/2
        for ln in lines:
            set_font(ctx, FS)
            ctx.move_to(bx+12, ty+20)
            ctx.show_text(ln); ty+=28

    cx2=W//2; cy2=top_y+box_h+100; cr=85
    for bx,by in bpos:
        mx=bx+box_w//2; my=by+box_h
        carrow(ctx,mx,my,cx2,cy2-cr-10,lw=2,head=10)
    cello(ctx,cx2,cy2,cr,cr*0.8,lw=2.5)
    lines=["三键索引","FID_k, t_k, s_k"]; ty=cy2-30
    for ln in lines:
        set_font(ctx, FS+2, weight=True)
        ctx.move_to(cx2+12, ty+20)
        ctx.show_text(ln); ty+=28

    by2=cy2+int(cr*0.8)+20; bh=90
    pill_fill(ctx,cx2-300,by2,600,bh,lw=2)
    lines=["D(FID_k, s_k, t_k) 三键索引元组","→ 帧边界精确对齐 → 环形缓冲区"]; ty=by2+20
    for ln in lines:
        set_font(ctx, FS)
        ctx.move_to(cx2-280, ty+18)
        ctx.show_text(ln); ty+=30
    carrow(ctx,cx2,cy2+int(cr*0.8),cx2,by2,lw=2,head=10)

    bot_y=by2+bh+30
    bw=160; bg=(W-5*bw)//6
    items=["2D工业相机×6","3D线激光×2","HWT905","单点测距仪","测距矩阵"]
    for i,item in enumerate(items):
        bx=bg+i*(bw+bg)
        pill_fill(ctx,bx,bot_y,bw,70,lw=2)
        set_font(ctx, FS2)
        ctx.move_to(bx+8, bot_y+38)
        ctx.show_text(item)
        carrow(ctx,cx2,by2+bh,bx+bw//2,bot_y,lw=1.5,head=8)

    ctext_center(ctx,"帧分辨率≈5mm/帧  |  时间戳精度优于1μs  |  IEEE 1588 PTP",FS3,0,H-35,W,30)
    save(surf,"fig2_pro.png")

# ======= FIG 3 =======
def fig3():
    surf, ctx = make_surface()
    FS, FS2, FS3 = 20, 17, 14

    ctext_center(ctx,"自适应动态加权几何平均融合算法流程图",26,0,18,W,40,weight=True)

    top_y, in_w, in_h = 72, 280, 75
    gap = 40
    sx=(W-(in_w*3+gap*2))//2
    inputs=["视觉检测(轨面缺陷)","几何参数(轨距/水平/高低)","廓形波磨(3D激光)"]
    in_xs=[]
    for i,txt in enumerate(inputs):
        ix=sx+i*(in_w+gap); in_xs.append(ix)
        pill_fill(ctx,ix,top_y,in_w,in_h,lw=2)
        set_font(ctx, FS)
        ctx.move_to(ix+8, top_y+40)
        ctx.show_text(txt)

    chain_y=top_y+in_h+20; chain_h=68
    chain=["C_d(t)  维度置信度","σ_d(t)  滑动标准差","r_d(t)=C_d/σ  可靠性因子","w_d(t)  归一化权重"]
    cw=180; cg=18; ct=(W-(cw*4+cg*3))//2
    cx=ct
    for k,item in enumerate(chain):
        pill_fill(ctx,cx,chain_y,cw,chain_h,lw=2)
        set_font(ctx, FS2)
        ctx.move_to(cx+8, chain_y+38)
        ctx.show_text(item)
        if k>0:
            cline(ctx,cx-cg,chain_y+chain_h//2,cx,chain_y+chain_h//2,lw=2)
            carrow(ctx,cx-cg,chain_y+chain_h//2,cx,chain_y+chain_h//2,lw=2,head=8)
        cx+=cw+cg

    fc=ct+cw
    for ix in in_xs:
        ax=ix+in_w//2; ay=top_y+in_h
        cline(ctx,ax,ay,fc,chain_y,lw=1.5); carrow(ctx,ax,ay,fc,chain_y,lw=1.5,head=8)

    core_y=chain_y+chain_h+25; core_h=85
    core_x=W//2-270; core_w=540
    pill_fill(ctx,core_x,core_y,core_w,core_h,lw=3)
    lines=["C_fuse = ∏ C_d(t)^w_d(t)","加权几何平均融合"]; ty=core_y+22
    for ln in lines:
        set_font(ctx, FS+2, weight=True)
        ctx.move_to(core_x+12, ty+20)
        ctx.show_text(ln); ty+=30

    lc=ct+3*(cw+cg)
    cline(ctx,lc,chain_y+chain_h//2,core_x,core_y+core_h//2,lw=2)
    carrow(ctx,lc,chain_y+chain_h//2,core_x,core_y+core_h//2,lw=2,head=10)

    out_y=core_y+core_h+25; out_h=72; out_w=260
    og=(W-3*out_w)//4
    outs=[("C_fuse < 0.5","丢弃"),("0.5 ≤ C_fuse < 0.7","人工复核"),("C_fuse ≥ 0.7","最终判定")]
    for i,(cond,act) in enumerate(outs):
        ox=og+i*(out_w+og)
        pill_fill(ctx,ox,out_y,out_w,out_h,lw=2)
        lines=[cond,act]; ty=out_y+20
        for ln in lines:
            set_font(ctx, FS)
            ctx.move_to(ox+8, ty+20)
            ctx.show_text(ln); ty+=26
        ax=core_x+core_w//2
        cline(ctx,ax,core_y+core_h,ox+out_w//2,out_y,lw=2); carrow(ctx,ax,core_y+core_h,ox+out_w//2,out_y,lw=2,head=10)

    ctext_center(ctx,"融合准确率97.5%  |  传感器退化时96.1%",FS3,0,H-35,W,30)
    save(surf,"fig3_pro.png")

# ======= FIG 4 =======
def fig4():
    surf, ctx = make_surface()
    FS, FS2, FS3 = 19, 16, 14

    ctext_center(ctx,"快慢双速EKF融合架构图",26,0,18,W,40,weight=True)

    bw=360; top_y=70; bh=72
    lx=80; ly=top_y
    left=["HWT905姿态传感器","横滚角+俯仰角","车体振动估计 h_veh","振动补偿量输出(响应5ms)"]
    set_font(ctx, FS+3, weight=True)
    ctx.move_to(lx+8, ly+30)
    ctx.show_text("快回路 200Hz")
    ly+=36
    for k,item in enumerate(left):
        pill_fill(ctx,lx,ly,bw,bh,lw=2)
        set_font(ctx, FS)
        ctx.move_to(lx+8, ly+bh/2+6)
        ctx.show_text(item)
        if k<len(left)-1: carrow(ctx,lx+bw//2,ly+bh,lx+bw//2,ly+bh+20,lw=2,head=8)
        ly+=bh+20

    rx=W-80-bw; ry=top_y
    right=["单点测距传感器×2","2000Hz采样累积","EKF状态估计","x_k=[h_track,h_veh,v_veh]^T","轨道高程真值 h_track"]
    set_font(ctx, FS+3, weight=True)
    ctx.move_to(rx+8, ry+30)
    ctx.show_text("慢回路 10Hz")
    ry+=36
    for k,item in enumerate(right):
        pill_fill(ctx,rx,ry,bw,bh,lw=2)
        set_font(ctx, FS)
        ctx.move_to(rx+8, ry+bh/2+6)
        ctx.show_text(item)
        if k<len(right)-1: carrow(ctx,rx+bw//2,ry+bh,rx+bw//2,ry+bh+20,lw=2,head=8)
        ry+=bh+20

    cy_mid=(ly+ry)//2
    lines=["频域完全解耦","（20:1）","无混叠效应"]; ty=cy_mid-40
    for ln in lines:
        set_font(ctx, FS+2, weight=True)
        ctx.move_to(W//2+12, ty+20)
        ctx.show_text(ln); ty+=26

    cdashed(ctx,lx+bw,top_y+40,W//2-20,cy_mid,lw=1.5,dash=(6,6))
    cdashed(ctx,rx,top_y+40,W//2+20,cy_mid,lw=1.5,dash=(6,6))

    out_y=max(ly,ry)+15; out_x=W//2-260; out_w=520; out_h=80
    pill_fill(ctx,out_x,out_y,out_w,out_h,lw=2.5)
    set_font(ctx, FS+2, weight=True)
    ctx.move_to(out_x+12, out_y+45)
    ctx.show_text("高低不平顺值输出  →  精度±0.5mm")
    carrow(ctx,lx+bw//2,ly,W//2,out_y,lw=2,head=10)
    carrow(ctx,rx+bw//2,ry,W//2,out_y,lw=2,head=10)

    ctext_center(ctx,"振动噪声降低53.7%",FS3,0,H-35,W,30)
    save(surf,"fig4_pro.png")

# ======= FIG 5 =======
def fig5():
    surf, ctx = make_surface()
    FS, FS2, FS3 = 19, 16, 14

    ctext_center(ctx,"几何参数检测原理图（轨距/水平/高低）",26,0,18,W,40,weight=True)

    n=3; mg=50
    cw=(W-2*mg-2*30)//3
    cols=[
        {"title":"轨距检测","formula":"G = d_L + d_R","principle":"直接测距与横滚角完全解耦","precision":"±0.3mm","sensor":"测距传感器矩阵"},
        {"title":"水平检测","formula":"Δh = 1435×sin(θ_r)","principle":"纯横滚角几何推导","precision":"<0.4mm","sensor":"HWT905姿态传感器"},
        {"title":"高低检测","formula":"z = H - D","principle":"EKF校正姿态补偿","precision":"±0.5mm","sensor":"单点测距仪+HWT905"},
    ]
    sy=70
    for i,col in enumerate(cols):
        x=mg+i*(cw+30)
        pill_fill(ctx,x,sy,cw,52,lw=2)
        set_font(ctx, FS+4, weight=True)
        ctx.move_to(x+12, sy+34)
        ctx.show_text(col["title"])
        sections=[("检测原理",col["principle"]),("计算公式",col["formula"]),("精度指标",col["precision"]),("传感器",col["sensor"])]
        sec_y=sy+56; sec_h=130
        for sl,sv in sections:
            pill(ctx,x,sec_y,cw,sec_h,lw=2)
            pill_fill(ctx,x,sec_y,120,sec_h,lw=1.5)
            set_font(ctx, FS2)
            ctx.move_to(x+8, sec_y+sec_h/2+6)
            ctx.show_text(sl)
            ctx.move_to(x+128, sec_y+sec_h/2+6)
            ctx.show_text(sv)
            sec_y+=sec_h+6
    save(surf,"fig5_pro.png")

fig1()
fig2()
fig3()
fig4()
fig5()
print("All done!")
