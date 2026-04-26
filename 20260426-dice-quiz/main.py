"""サイコロまちがいさがし - たろうくんとくろーどちゃんのクイズ"""
import pygame
import random
import math
import numpy as np
import os
from claude_draw import draw_claude

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)

WIDTH, HEIGHT = 1280, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("サイコロまちがいさがし")
clock = pygame.time.Clock()

def load_font(size):
    for p in ["C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/YuGothM.ttc", "C:/Windows/Fonts/msgothic.ttc"]:
        if os.path.exists(p):
            return pygame.font.Font(p, size)
    return pygame.font.SysFont(None, size)

FONT_HUGE = load_font(120)
FONT_BIG = load_font(64)
FONT_MID = load_font(40)
FONT_SMALL = load_font(28)

WHITE=(255,255,255); BLACK=(20,20,20); PINK=(255,180,200); BLUE=(100,180,255)
GREEN=(100,220,120); RED=(240,80,80); YELLOW=(255,220,80); PURPLE=(200,130,230)
ORANGE=(255,160,80); BG=(255,245,220)

def make_tone(freq, duration, volume=0.4):
    sr=22050; n=int(sr*duration); t=np.linspace(0,duration,n,False)
    wave=np.sin(2*np.pi*freq*t)*volume*np.linspace(1,0,n)
    a=(wave*32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((a,a)))

def make_chord(freqs, duration, volume=0.3):
    sr=22050; n=int(sr*duration); t=np.linspace(0,duration,n,False)
    wave=sum(np.sin(2*np.pi*f*t) for f in freqs)/len(freqs)*volume*np.linspace(1,0,n)
    a=(wave*32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((a,a)))

SND_CORRECT = make_chord([523,659,784], 0.5, 0.3)
SND_WRONG = make_tone(180, 0.4, 0.4)
SND_DICE = make_tone(800, 0.05, 0.3)
SND_FINISH = make_chord([523,659,784,1046], 0.8, 0.3)

# ---------- えがく ----------
def draw_ramen(surf, cx, cy, size, diff=False):
    bw=int(size*0.85); bh=int(size*0.55)
    pygame.draw.ellipse(surf,(200,60,60),(cx-bw//2,cy,bw,bh))
    pygame.draw.ellipse(surf,BLACK,(cx-bw//2,cy,bw,bh),4)
    pygame.draw.ellipse(surf,(220,180,100),(cx-int(size*0.36),cy-8,int(size*0.72),int(size*0.18)))
    for i in range(6):
        a=i*0.6; pygame.draw.circle(surf,(255,230,150),(cx+int(math.cos(a)*50),cy+5+int(math.sin(a)*8)),6)
    pygame.draw.circle(surf,(200,130,90),(cx-50,cy+5),18); pygame.draw.circle(surf,BLACK,(cx-50,cy+5),18,2)
    for i in range(5): pygame.draw.rect(surf,(120,200,120),(cx-60+i*30,cy-5,8,8))
    pygame.draw.circle(surf,WHITE,(cx+50,cy+5),22); pygame.draw.circle(surf,BLACK,(cx+50,cy+5),22,2)
    pygame.draw.circle(surf,(255,180,60),(cx+50,cy+5),12)
    if diff:
        pygame.draw.circle(surf,WHITE,(cx+95,cy+18),18); pygame.draw.circle(surf,BLACK,(cx+95,cy+18),18,2)
        pygame.draw.circle(surf,(255,180,60),(cx+95,cy+18),9)
    for x in [cx-30,cx,cx+30]:
        pygame.draw.arc(surf,(180,180,180),(x-10,cy-80,20,50),0,math.pi,3)

def draw_calendar(surf, cx, cy, size, diff=False):
    w=int(size*0.8); h=int(size*0.85)
    r=pygame.Rect(cx-w//2,cy-h//2,w,h)
    pygame.draw.rect(surf,WHITE,r,border_radius=8); pygame.draw.rect(surf,BLACK,r,4,border_radius=8)
    pygame.draw.rect(surf,RED,(r.x,r.y,r.w,50),border_top_left_radius=8,border_top_right_radius=8)
    t=FONT_SMALL.render("4 がつ",True,WHITE); surf.blit(t,t.get_rect(center=(cx,r.y+25)))
    cw=w//7; ch=(h-50)//5; day=1
    for ro in range(5):
        for c in range(7):
            x=r.x+c*cw; y=r.y+50+ro*ch
            if day<=30:
                num=18 if (diff and day==15) else day
                col=RED if c==0 else (BLUE if c==6 else BLACK)
                tt=FONT_SMALL.render(str(num),True,col)
                surf.blit(tt,tt.get_rect(center=(x+cw//2,y+ch//2)))
                day+=1

def draw_phone(surf, cx, cy, size, diff=False):
    bw=int(size*0.75); bh=int(size*0.85)
    body=pygame.Rect(cx-bw//2,cy-bh//2+30,bw,bh-30)
    pygame.draw.rect(surf,(240,220,180),body,border_radius=20); pygame.draw.rect(surf,BLACK,body,4,border_radius=20)
    rc=BLUE if diff else BLACK
    rec=pygame.Rect(cx-bw//2+10,cy-bh//2-10,bw-20,60)
    pygame.draw.ellipse(surf,rc,rec)
    pygame.draw.circle(surf,rc,(rec.x-5,rec.y+35),25); pygame.draw.circle(surf,rc,(rec.right+5,rec.y+35),25)
    for ro in range(4):
        for c in range(3):
            bx=body.x+30+c*60; by=body.y+60+ro*50
            pygame.draw.circle(surf,WHITE,(bx+20,by+20),18); pygame.draw.circle(surf,BLACK,(bx+20,by+20),18,2)
            lbl=["1","2","3","4","5","6","7","8","9","*","0","#"][ro*3+c]
            t=FONT_SMALL.render(lbl,True,BLACK); surf.blit(t,t.get_rect(center=(bx+20,by+20)))

def draw_kusuri(surf, cx, cy, size, diff=False):
    bw=int(size*0.55); bh=int(size*0.85)
    body=pygame.Rect(cx-bw//2,cy-bh//2+40,bw,bh-40)
    pygame.draw.rect(surf,(200,240,220),body,border_radius=15); pygame.draw.rect(surf,BLACK,body,4,border_radius=15)
    cap_color = BLUE if diff else RED
    cap=pygame.Rect(cx-bw//2-8,cy-bh//2,bw+16,60)
    pygame.draw.rect(surf,cap_color,cap,border_radius=8); pygame.draw.rect(surf,BLACK,cap,4,border_radius=8)
    label=pygame.Rect(body.x+10,body.y+30,body.w-20,100)
    pygame.draw.rect(surf,WHITE,label); pygame.draw.rect(surf,BLACK,label,2)
    t=FONT_SMALL.render("くすり",True,BLACK); surf.blit(t,t.get_rect(center=(label.centerx,label.y+30)))
    pygame.draw.rect(surf,RED,(label.centerx-4,label.y+55,8,30))
    pygame.draw.rect(surf,RED,(label.x+30,label.y+65,label.w-60,8))

def draw_pikmin(surf, cx, cy, size, diff=False):
    bw=int(size*0.4); bh=int(size*0.55)
    pygame.draw.ellipse(surf,RED,(cx-bw//2,cy-bh//2,bw,bh))
    pygame.draw.ellipse(surf,BLACK,(cx-bw//2,cy-bh//2,bw,bh),3)
    ey=cy-30
    pygame.draw.ellipse(surf,WHITE,(cx-30,ey,22,32)); pygame.draw.ellipse(surf,WHITE,(cx+8,ey,22,32))
    pygame.draw.ellipse(surf,BLACK,(cx-25,ey+8,12,18)); pygame.draw.ellipse(surf,BLACK,(cx+13,ey+8,12,18))
    pygame.draw.arc(surf,BLACK,(cx-12,cy-5,24,18),math.pi,2*math.pi,3)
    st=cy-bh//2-50
    pygame.draw.line(surf,(80,160,80),(cx,cy-bh//2+5),(cx,st),5)
    if not diff:
        for i in range(5):
            a=-math.pi/2+i*(2*math.pi/5)
            px=cx+int(math.cos(a)*18); py=st+int(math.sin(a)*18)
            pygame.draw.circle(surf,PINK,(px,py),12); pygame.draw.circle(surf,BLACK,(px,py),12,2)
        pygame.draw.circle(surf,YELLOW,(cx,st),8); pygame.draw.circle(surf,BLACK,(cx,st),8,2)
    else:
        leaf=[(cx,st-25),(cx-22,st+5),(cx+22,st+5)]
        pygame.draw.polygon(surf,(100,200,100),leaf); pygame.draw.polygon(surf,BLACK,leaf,3)
    pygame.draw.line(surf,RED,(cx-bw//2+5,cy),(cx-bw//2-15,cy+20),6)
    pygame.draw.line(surf,RED,(cx+bw//2-5,cy),(cx+bw//2+15,cy+20),6)
    pygame.draw.ellipse(surf,BLACK,(cx-25,cy+bh//2-5,18,14)); pygame.draw.ellipse(surf,BLACK,(cx+7,cy+bh//2-5,18,14))

def draw_patapata(surf, cx, cy, size, diff=False):
    for side in [-1,1]:
        wx=cx+side*80; wy=cy-40
        pts=[(wx,wy),(wx+side*40,wy-30),(wx+side*60,wy+10),(wx+side*30,wy+25)]
        pygame.draw.polygon(surf,WHITE,pts); pygame.draw.polygon(surf,BLACK,pts,3)
    sw=int(size*0.6); sh=int(size*0.5)
    if diff: sw=int(sw*1.18); sh=int(sh*1.18)
    shell=pygame.Rect(cx-sw//2,cy-sh//2+10,sw,sh)
    pygame.draw.ellipse(surf,RED,shell); pygame.draw.ellipse(surf,BLACK,shell,4)
    inner=shell.inflate(-30,-25)
    pygame.draw.ellipse(surf,(255,200,200),inner); pygame.draw.ellipse(surf,BLACK,inner,3)
    hr=45; hy=cy-sh//2-20
    pygame.draw.circle(surf,(100,200,100),(cx,hy),hr); pygame.draw.circle(surf,BLACK,(cx,hy),hr,3)
    pygame.draw.ellipse(surf,WHITE,(cx-25,hy-18,18,28)); pygame.draw.ellipse(surf,WHITE,(cx+7,hy-18,18,28))
    pygame.draw.ellipse(surf,BLACK,(cx-20,hy-10,10,16)); pygame.draw.ellipse(surf,BLACK,(cx+12,hy-10,10,16))
    beak=[(cx-12,hy+18),(cx+12,hy+18),(cx,hy+32)]
    pygame.draw.polygon(surf,ORANGE,beak); pygame.draw.polygon(surf,BLACK,beak,2)
    pygame.draw.ellipse(surf,ORANGE,(cx-35,cy+sh//2,30,18)); pygame.draw.ellipse(surf,ORANGE,(cx+5,cy+sh//2,30,18))
    pygame.draw.ellipse(surf,BLACK,(cx-35,cy+sh//2,30,18),2); pygame.draw.ellipse(surf,BLACK,(cx+5,cy+sh//2,30,18),2)

PROBLEMS = [
    {"name":"ラーメン",  "draw":draw_ramen,    "hint":"たまごの かずを よくみて！"},
    {"name":"カレンダー","draw":draw_calendar, "hint":"すうじを よくみて！"},
    {"name":"でんわ",    "draw":draw_phone,    "hint":"じゅわきの いろを よくみて！"},
    {"name":"くすり",    "draw":draw_kusuri,   "hint":"ふたの いろを よくみて！"},
    {"name":"ピクミン",  "draw":draw_pikmin,   "hint":"あたまの うえを よくみて！"},
    {"name":"パタパタ",  "draw":draw_patapata, "hint":"コウラの おおきさを よくみて！"},
]
DLABEL=["","とってもかんたん","かんたん","ふつう","ちょいムズ","むずかしい","げきムズ"]
DCOLOR=[WHITE,GREEN,GREEN,YELLOW,ORANGE,RED,PURPLE]

def draw_dice(surf,cx,cy,num,sz=140):
    r=pygame.Rect(cx-sz//2,cy-sz//2,sz,sz)
    pygame.draw.rect(surf,WHITE,r,border_radius=20); pygame.draw.rect(surf,BLACK,r,5,border_radius=20)
    L=cx-sz//4; R=cx+sz//4; T=cy-sz//4; B=cy+sz//4
    pips={1:[(cx,cy)],2:[(L,T),(R,B)],3:[(L,T),(cx,cy),(R,B)],
          4:[(L,T),(R,T),(L,B),(R,B)],5:[(L,T),(R,T),(cx,cy),(L,B),(R,B)],
          6:[(L,T),(R,T),(L,cy),(R,cy),(L,B),(R,B)]}
    for p in pips.get(num,[]): pygame.draw.circle(surf,BLACK,p,12)

def draw_heart(surf,cx,cy,size=30,color=RED):
    pts=[]
    for a in range(0,360,5):
        t=math.radians(a)
        x=16*math.sin(t)**3
        y=-(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))
        pts.append((cx+x*size/16,cy+y*size/16))
    pygame.draw.polygon(surf,color,pts); pygame.draw.polygon(surf,BLACK,pts,2)

# ---------- ステート ----------
class Game:
    def __init__(self):
        self.state="title"; self.hearts=3; self.score=0
        self.solved=set(); self.dice_value=1; self.dice_anim_t=0
        self.current_problem=None; self.diff_side="L"
        self.feedback=None; self.message=""

    def roll(self):
        self.state="rolling"; self.dice_anim_t=0; SND_DICE.play()

    def click(self,side):
        if side==self.diff_side:
            self.score+=1; self.solved.add(self.current_problem)
            self.feedback=["correct",60]; SND_CORRECT.play()
        else:
            self.hearts-=1; self.feedback=["wrong",60]; SND_WRONG.play()

    def update(self):
        if self.state=="rolling":
            self.dice_anim_t+=1
            if self.dice_anim_t%5==0: self.dice_value=random.randint(1,6)
            if self.dice_anim_t>60:
                self.dice_value=random.randint(1,6)
                self.state="result_dice"; self.dice_anim_t=0
        elif self.state=="result_dice":
            self.dice_anim_t+=1
            if self.dice_anim_t>90:
                if self.dice_value in self.solved:
                    self.message=f"{self.dice_value} ばんは もうやったよ〜 もういちどふってね！"
                    self.state="title"
                else:
                    self.current_problem=self.dice_value
                    self.diff_side=random.choice(["L","R"])
                    self.state="playing"
        if self.feedback:
            self.feedback[1]-=1
            if self.feedback[1]<=0:
                fb=self.feedback[0]; self.feedback=None
                if fb=="correct":
                    if len(self.solved)>=6:
                        self.state="finish"; SND_FINISH.play()
                    elif self.hearts<=0:
                        self.state="finish"
                    else:
                        self.message="つぎも サイコロ ふってね！"
                        self.state="title"
                else:
                    if self.hearts<=0: self.state="finish"

# ---------- えがき ----------
def bg():
    screen.fill(BG)
    for i in range(40):
        pygame.draw.circle(screen,(255,230,180),((i*53)%WIDTH,(i*31)%HEIGHT),3)

def draw_title(g):
    bg()
    t=FONT_HUGE.render("サイコロ",True,RED); screen.blit(t,t.get_rect(center=(WIDTH//2,110)))
    t=FONT_HUGE.render("まちがいさがし",True,BLUE); screen.blit(t,t.get_rect(center=(WIDTH//2,230)))
    btn=pygame.Rect(WIDTH//2-220,360,440,180)
    pygame.draw.rect(screen,YELLOW,btn,border_radius=30); pygame.draw.rect(screen,BLACK,btn,6,border_radius=30)
    t=FONT_BIG.render("サイコロをふる！",True,BLACK); screen.blit(t,t.get_rect(center=btn.center))
    if g.message:
        m=FONT_MID.render(g.message,True,BLACK); screen.blit(m,m.get_rect(center=(WIDTH//2,580)))
    c=FONT_MID.render(f"クリア: {len(g.solved)} / 6",True,BLACK); screen.blit(c,(40,40))
    for i in range(3):
        col=RED if i<g.hearts else (200,200,200)
        draw_heart(screen,WIDTH-60-i*70,60,30,col)
    for n in range(1,7):
        x=200+(n-1)*140; y=HEIGHT-90
        if n in g.solved:
            pygame.draw.circle(screen,GREEN,(x,y),40); pygame.draw.circle(screen,BLACK,(x,y),40,3)
            ck=FONT_BIG.render("○",True,WHITE); screen.blit(ck,ck.get_rect(center=(x,y)))
        else:
            pygame.draw.circle(screen,WHITE,(x,y),40); pygame.draw.circle(screen,BLACK,(x,y),40,3)
            nm=FONT_BIG.render(str(n),True,BLACK); screen.blit(nm,nm.get_rect(center=(x,y)))
    return btn

def draw_rolling(g):
    bg()
    t=FONT_BIG.render("コロコロコロ...",True,BLACK); screen.blit(t,t.get_rect(center=(WIDTH//2,200)))
    draw_dice(screen,WIDTH//2+random.randint(-8,8),HEIGHT//2+random.randint(-8,8),g.dice_value,200)

def draw_result(g):
    bg()
    t=FONT_BIG.render(f"{g.dice_value} がでたよ！",True,BLACK); screen.blit(t,t.get_rect(center=(WIDTH//2,130)))
    draw_dice(screen,WIDTH//2,HEIGHT//2-50,g.dice_value,200)
    box=pygame.Rect(WIDTH//2-280,HEIGHT//2+130,560,100)
    pygame.draw.rect(screen,DCOLOR[g.dice_value],box,border_radius=20); pygame.draw.rect(screen,BLACK,box,4,border_radius=20)
    t=FONT_BIG.render(DLABEL[g.dice_value],True,BLACK); screen.blit(t,t.get_rect(center=box.center))
    pn=PROBLEMS[g.dice_value-1]["name"]
    t=FONT_MID.render(f"もんだい: {pn}",True,BLACK); screen.blit(t,t.get_rect(center=(WIDTH//2,HEIGHT//2+260)))

def draw_playing(g):
    bg()
    p=PROBLEMS[g.current_problem-1]
    t=FONT_BIG.render(f"{g.current_problem}: {p['name']}",True,BLACK); screen.blit(t,(40,30))
    for i in range(3):
        col=RED if i<g.hearts else (200,200,200)
        draw_heart(screen,WIDTH-60-i*70,60,30,col)
    h=FONT_MID.render(p["hint"],True,(100,80,80)); screen.blit(h,h.get_rect(center=(WIDTH//2,110)))
    msg=FONT_MID.render("ちがう ほうの えを クリックしてね！",True,(80,80,80))
    screen.blit(msg,msg.get_rect(center=(WIDTH//2,150)))
    bw=500; bh=500
    L=pygame.Rect(80,190,bw,bh); R=pygame.Rect(WIDTH-80-bw,190,bw,bh)
    for r in [L,R]:
        pygame.draw.rect(screen,WHITE,r,border_radius=20); pygame.draw.rect(screen,BLACK,r,5,border_radius=20)
    p["draw"](screen,L.centerx,L.centery,400,g.diff_side=="L")
    p["draw"](screen,R.centerx,R.centery,400,g.diff_side=="R")
    if g.feedback:
        fb=g.feedback[0]
        if fb=="correct":
            cx,cy=WIDTH//2,HEIGHT//2+50
            pygame.draw.circle(screen,GREEN,(cx,cy),200,25)
            tt=FONT_HUGE.render("せいかい！",True,GREEN); screen.blit(tt,tt.get_rect(center=(cx,cy)))
        else:
            cx,cy=WIDTH//2,HEIGHT//2+50
            pygame.draw.line(screen,RED,(cx-150,cy-150),(cx+150,cy+150),25)
            pygame.draw.line(screen,RED,(cx+150,cy-150),(cx-150,cy+150),25)
            tt=FONT_HUGE.render("ちがうよ！",True,RED); screen.blit(tt,tt.get_rect(center=(cx,cy+220)))
    return L,R

def draw_finish(g):
    bg()
    if g.hearts<=0 and len(g.solved)<6:
        t=FONT_HUGE.render("ゲームオーバー...",True,RED)
    else:
        t=FONT_HUGE.render("ぜんもんクリア！",True,RED)
    screen.blit(t,t.get_rect(center=(WIDTH//2,120)))
    if len(g.solved)>=6:
        t2=FONT_BIG.render("すごい〜！たろうくんてんさい！",True,PURPLE)
        screen.blit(t2,t2.get_rect(center=(WIDTH//2,220)))
    s=FONT_BIG.render(f"せいかい: {g.score} / 6",True,BLACK)
    screen.blit(s,s.get_rect(center=(WIDTH//2,300)))
    # くろーどちゃん
    tt = pygame.time.get_ticks()/1000.0
    draw_claude(screen, WIDTH//2, 470, scale=0.45, t=tt)
    msg=FONT_MID.render("くろーどちゃんより：あそんでくれてありがとう〜！",True,(180,80,140))
    screen.blit(msg,msg.get_rect(center=(WIDTH//2,540)))
    btn=pygame.Rect(WIDTH//2-180,580,360,100)
    pygame.draw.rect(screen,BLUE,btn,border_radius=20); pygame.draw.rect(screen,BLACK,btn,4,border_radius=20)
    t=FONT_MID.render("もういちどあそぶ",True,WHITE); screen.blit(t,t.get_rect(center=btn.center))
    return btn

def main():
    g=Game(); running=True; tbtn=None; prects=None; fbtn=None
    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                mx,my=e.pos
                if g.state=="title" and tbtn and tbtn.collidepoint(mx,my):
                    g.message=""; g.roll()
                elif g.state=="playing" and not g.feedback and prects:
                    L,R=prects
                    if L.collidepoint(mx,my): g.click("L")
                    elif R.collidepoint(mx,my): g.click("R")
                elif g.state=="finish" and fbtn and fbtn.collidepoint(mx,my):
                    g=Game()
            elif e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: running=False
                elif e.key==pygame.K_SPACE and g.state=="title":
                    g.message=""; g.roll()
        g.update()
        if g.state=="title": tbtn=draw_title(g)
        elif g.state=="rolling": draw_rolling(g)
        elif g.state=="result_dice": draw_result(g)
        elif g.state=="playing": prects=draw_playing(g)
        elif g.state=="finish": fbtn=draw_finish(g)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__=="__main__":
    main()
