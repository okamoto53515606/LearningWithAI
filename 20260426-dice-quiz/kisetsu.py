"""きせつクイズ - たろうくん の 3かいめ
えがでてきて、どのきせつかを 2たくで あてる！
はる=ヤゴ、なつ=カブトムシ、あき=カキ、ふゆ=ゆきうさぎ
"""
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
pygame.display.set_caption("きせつクイズ")
clock = pygame.time.Clock()

def load_font(size):
    for p in ["C:/Windows/Fonts/meiryo.ttc","C:/Windows/Fonts/YuGothM.ttc","C:/Windows/Fonts/msgothic.ttc"]:
        if os.path.exists(p): return pygame.font.Font(p,size)
    return pygame.font.SysFont(None,size)

FONT_HUGE=load_font(110); FONT_BIG=load_font(64); FONT_MID=load_font(40); FONT_SMALL=load_font(28)

WHITE=(255,255,255); BLACK=(20,20,20); BLUE=(100,180,255); GREEN=(100,220,120)
RED=(240,80,80); YELLOW=(255,220,80); PURPLE=(200,130,230); ORANGE=(255,160,80)
BG=(255,245,220); PINK=(255,180,200); BROWN=(140,90,50); SKY=(180,230,255)

def make_tone(f,d,v=0.4):
    sr=22050; n=int(sr*d); t=np.linspace(0,d,n,False)
    w=np.sin(2*np.pi*f*t)*v*np.linspace(1,0,n)
    a=(w*32767).astype(np.int16); return pygame.sndarray.make_sound(np.column_stack((a,a)))
def make_chord(fs,d,v=0.3):
    sr=22050; n=int(sr*d); t=np.linspace(0,d,n,False)
    w=sum(np.sin(2*np.pi*f*t) for f in fs)/len(fs)*v*np.linspace(1,0,n)
    a=(w*32767).astype(np.int16); return pygame.sndarray.make_sound(np.column_stack((a,a)))
SND_OK=make_chord([523,659,784],0.5,0.3)
SND_NG=make_tone(180,0.4,0.4)
SND_FIN=make_chord([523,659,784,1046],0.8,0.3)

# ---------- えがき ----------
def draw_yago(surf,cx,cy,size):
    """ヤゴ：トンボのよう虫。みず のなか にいる"""
    # からだ（だえん、ちゃいろっぽい）
    body_w=int(size*0.7); body_h=int(size*0.32)
    pygame.draw.ellipse(surf,(110,140,90),(cx-body_w//2,cy-body_h//2,body_w,body_h))
    pygame.draw.ellipse(surf,BLACK,(cx-body_w//2,cy-body_h//2,body_w,body_h),3)
    # しっぽ
    for i in range(3):
        pygame.draw.line(surf,(80,110,60),(cx+body_w//2,cy),(cx+body_w//2+30,cy-15+i*15),4)
    # あたま
    head_r=int(size*0.18)
    pygame.draw.circle(surf,(100,130,80),(cx-body_w//2-head_r//2,cy),head_r)
    pygame.draw.circle(surf,BLACK,(cx-body_w//2-head_r//2,cy),head_r,3)
    # おおきな め
    pygame.draw.circle(surf,BLACK,(cx-body_w//2-head_r//2-8,cy-head_r//2),8)
    pygame.draw.circle(surf,BLACK,(cx-body_w//2-head_r//2+8,cy-head_r//2),8)
    pygame.draw.circle(surf,WHITE,(cx-body_w//2-head_r//2-6,cy-head_r//2-2),3)
    pygame.draw.circle(surf,WHITE,(cx-body_w//2-head_r//2+10,cy-head_r//2-2),3)
    # あし
    for i in range(3):
        x=cx-30+i*30
        pygame.draw.line(surf,BLACK,(x,cy+body_h//2-2),(x-10,cy+body_h//2+25),3)
        pygame.draw.line(surf,BLACK,(x,cy+body_h//2-2),(x+10,cy+body_h//2+25),3)
    # みず（あおいせん）
    for i in range(3):
        y=cy+size//2+i*15
        pygame.draw.arc(surf,BLUE,(cx-100,y-10,200,20),0,math.pi,3)

def draw_kabuto(surf,cx,cy,size):
    """カブトムシ"""
    # からだ（くろい）
    body_w=int(size*0.55); body_h=int(size*0.55)
    body=pygame.Rect(cx-body_w//2,cy-body_h//2,body_w,body_h)
    pygame.draw.ellipse(surf,(50,30,20),body)
    pygame.draw.ellipse(surf,BLACK,body,3)
    # まんなかのせん
    pygame.draw.line(surf,BLACK,(cx,cy-body_h//2+10),(cx,cy+body_h//2-10),3)
    # あたま
    head_w=int(size*0.35); head_h=int(size*0.22)
    head=pygame.Rect(cx-head_w//2,cy-body_h//2-head_h+5,head_w,head_h)
    pygame.draw.ellipse(surf,(40,25,15),head)
    pygame.draw.ellipse(surf,BLACK,head,3)
    # つの（おおきい）
    horn_top=(cx,cy-body_h//2-head_h-60)
    pygame.draw.line(surf,(40,25,15),(cx,head.y+5),horn_top,12)
    # つの の さき（Yじがた）
    pygame.draw.line(surf,(40,25,15),horn_top,(cx-25,horn_top[1]-25),10)
    pygame.draw.line(surf,(40,25,15),horn_top,(cx+25,horn_top[1]-25),10)
    pygame.draw.line(surf,BLACK,(cx,head.y+5),horn_top,3)
    pygame.draw.line(surf,BLACK,horn_top,(cx-25,horn_top[1]-25),2)
    pygame.draw.line(surf,BLACK,horn_top,(cx+25,horn_top[1]-25),2)
    # め
    pygame.draw.circle(surf,WHITE,(head.centerx-12,head.centery),5)
    pygame.draw.circle(surf,WHITE,(head.centerx+12,head.centery),5)
    pygame.draw.circle(surf,BLACK,(head.centerx-12,head.centery),3)
    pygame.draw.circle(surf,BLACK,(head.centerx+12,head.centery),3)
    # あし
    for i in range(3):
        y=cy-body_h//2+15+i*30
        pygame.draw.line(surf,BLACK,(cx-body_w//2+5,y),(cx-body_w//2-25,y+10),4)
        pygame.draw.line(surf,BLACK,(cx+body_w//2-5,y),(cx+body_w//2+25,y+10),4)

def draw_kaki(surf,cx,cy,size):
    """カキ（かき の み）"""
    # み（だいだいいろ）
    r=int(size*0.35)
    pygame.draw.circle(surf,(255,140,50),(cx,cy),r)
    pygame.draw.circle(surf,(220,100,30),(cx,cy),r,4)
    # たて の すじ
    for ang in [-0.4,0,0.4]:
        x1=cx+int(math.sin(ang)*r*0.9); x2=cx+int(math.sin(ang)*r*0.9)
        pygame.draw.arc(surf,(220,100,30),(cx-r+10,cy-r,2*r-20,2*r),math.pi/2-0.3+ang,math.pi/2+0.3+ang,3)
    # ハイライト
    pygame.draw.ellipse(surf,(255,200,150),(cx-r+15,cy-r+10,30,40))
    # へた（みどり、はっぱ4まい）
    for i in range(4):
        a=-math.pi/2+i*(math.pi/2)
        x=cx+int(math.cos(a)*15); y=cy-r+5+int(math.sin(a)*10)
        leaf=[(cx,cy-r+5),(x+int(math.cos(a)*15),y+int(math.sin(a)*10)),(cx+int(math.cos(a+0.5)*8),cy-r+10)]
        pygame.draw.polygon(surf,(80,160,80),leaf)
        pygame.draw.polygon(surf,BLACK,leaf,2)
    # えだ
    pygame.draw.line(surf,BROWN,(cx,cy-r+5),(cx,cy-r-25),5)
    pygame.draw.line(surf,BLACK,(cx,cy-r+5),(cx,cy-r-25),1)

def draw_yukiusagi(surf,cx,cy,size):
    """ゆきうさぎ：しろいやまのうさぎ。なんてんのみとはっぱでつくる"""
    # ゆきのやま（しろ）
    base_w=int(size*0.85); base_h=int(size*0.55)
    pygame.draw.ellipse(surf,WHITE,(cx-base_w//2,cy-10,base_w,base_h))
    pygame.draw.ellipse(surf,(180,200,220),(cx-base_w//2,cy-10,base_w,base_h),3)
    # あたま（しろいまる）
    head_r=int(size*0.22)
    pygame.draw.circle(surf,WHITE,(cx,cy-head_r+10),head_r)
    pygame.draw.circle(surf,(180,200,220),(cx,cy-head_r+10),head_r,3)
    # みみ（はっぱ：みどり）
    for side in [-1,1]:
        ear=[(cx+side*15,cy-head_r-5),(cx+side*30,cy-head_r-50),(cx+side*5,cy-head_r-10)]
        pygame.draw.polygon(surf,(80,160,80),ear)
        pygame.draw.polygon(surf,BLACK,ear,2)
    # め（あかいなんてんのみ）
    pygame.draw.circle(surf,RED,(cx-15,cy-head_r+5),7)
    pygame.draw.circle(surf,RED,(cx+15,cy-head_r+5),7)
    pygame.draw.circle(surf,BLACK,(cx-15,cy-head_r+5),7,2)
    pygame.draw.circle(surf,BLACK,(cx+15,cy-head_r+5),7,2)

PROBLEMS = [
    {"draw":draw_yago,      "name":"ヤゴ",       "answer":"はる"},
    {"draw":draw_kabuto,    "name":"カブトムシ", "answer":"なつ"},
    {"draw":draw_kaki,      "name":"カキ",       "answer":"あき"},
    {"draw":draw_yukiusagi, "name":"ゆきうさぎ", "answer":"ふゆ"},
]
SEASON_COLORS={"はる":PINK,"なつ":(120,200,100),"あき":ORANGE,"ふゆ":SKY}

def draw_heart(surf,cx,cy,size=30,color=RED):
    pts=[]
    for a in range(0,360,5):
        t=math.radians(a)
        x=16*math.sin(t)**3
        y=-(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))
        pts.append((cx+x*size/16,cy+y*size/16))
    pygame.draw.polygon(surf,color,pts); pygame.draw.polygon(surf,BLACK,pts,2)

def bg():
    screen.fill(BG)
    for i in range(40):
        pygame.draw.circle(screen,(255,230,180),((i*53)%WIDTH,(i*31)%HEIGHT),3)

class Game:
    def __init__(self):
        self.state="playing"
        self.hearts=3; self.score=0
        self.order=list(range(len(PROBLEMS))); random.shuffle(self.order)
        self.idx=0
        self.feedback=None
        self.setup_problem()

    def setup_problem(self):
        self.current=PROBLEMS[self.order[self.idx]]
        # 2たく：せいかいと、ちがうきせつ1つ
        ans=self.current["answer"]
        others=[s for s in ["はる","なつ","あき","ふゆ"] if s!=ans]
        wrong=random.choice(others)
        self.choices=[ans,wrong]
        random.shuffle(self.choices)
        self.correct_side="L" if self.choices[0]==ans else "R"

    def click(self,side):
        if side==self.correct_side:
            self.score+=1; self.feedback=["correct",70]; SND_OK.play()
        else:
            self.hearts-=1; self.feedback=["wrong",70]; SND_NG.play()

    def update(self):
        if self.feedback:
            self.feedback[1]-=1
            if self.feedback[1]<=0:
                fb=self.feedback[0]; self.feedback=None
                if fb=="correct":
                    self.idx+=1
                    if self.idx>=len(PROBLEMS) or self.hearts<=0:
                        self.state="finish"; SND_FIN.play()
                    else:
                        self.setup_problem()
                else:
                    if self.hearts<=0: self.state="finish"

def draw_playing(g):
    bg()
    p=g.current
    # うえのバー
    t=FONT_BIG.render(f"だい {g.idx+1} もん / {len(PROBLEMS)}",True,BLACK); screen.blit(t,(40,30))
    for i in range(3):
        col=RED if i<g.hearts else (200,200,200)
        draw_heart(screen,WIDTH-60-i*70,60,30,col)

    # しつもん
    box=pygame.Rect(WIDTH//2-360,120,720,90)
    pygame.draw.rect(screen,YELLOW,box,border_radius=20); pygame.draw.rect(screen,BLACK,box,4,border_radius=20)
    t=FONT_BIG.render("これは どの きせつ？",True,BLACK); screen.blit(t,t.get_rect(center=box.center))

    # え
    img_box=pygame.Rect(WIDTH//2-260,240,520,340)
    pygame.draw.rect(screen,WHITE,img_box,border_radius=20); pygame.draw.rect(screen,BLACK,img_box,5,border_radius=20)
    p["draw"](screen,img_box.centerx,img_box.centery,300)
    # なまえはひょうじしない（ヒントになっちゃうから）

    # 2たくボタン
    L=pygame.Rect(120,620,440,140)
    R=pygame.Rect(WIDTH-120-440,620,440,140)
    for i,r in enumerate([L,R]):
        ch=g.choices[i]
        col=SEASON_COLORS[ch]
        pygame.draw.rect(screen,col,r,border_radius=20); pygame.draw.rect(screen,BLACK,r,5,border_radius=20)
        t=FONT_HUGE.render(ch,True,BLACK); screen.blit(t,t.get_rect(center=r.center))

    if g.feedback:
        fb=g.feedback[0]; cx,cy=WIDTH//2,HEIGHT//2
        if fb=="correct":
            pygame.draw.circle(screen,GREEN,(cx,cy),200,25)
            tt=FONT_HUGE.render("せいかい！",True,GREEN); screen.blit(tt,tt.get_rect(center=(cx,cy)))
        else:
            pygame.draw.line(screen,RED,(cx-150,cy-150),(cx+150,cy+150),25)
            pygame.draw.line(screen,RED,(cx+150,cy-150),(cx-150,cy+150),25)
            tt=FONT_BIG.render(f"こたえは 「{p['answer']}」 だよ！",True,RED)
            screen.blit(tt,tt.get_rect(center=(cx,cy+220)))
    return L,R

def draw_finish(g):
    bg()
    if g.score==len(PROBLEMS):
        t=FONT_HUGE.render("ぜんもん せいかい！",True,RED)
    elif g.hearts<=0:
        t=FONT_HUGE.render("ゲームオーバー...",True,RED)
    else:
        t=FONT_HUGE.render("おわり！",True,RED)
    screen.blit(t,t.get_rect(center=(WIDTH//2,120)))
    if g.score==len(PROBLEMS):
        t2=FONT_BIG.render("すごい〜！たろうくんてんさい！",True,PURPLE)
        screen.blit(t2,t2.get_rect(center=(WIDTH//2,220)))
    s=FONT_BIG.render(f"せいかい: {g.score} / {len(PROBLEMS)}",True,BLACK)
    screen.blit(s,s.get_rect(center=(WIDTH//2,300)))
    tt = pygame.time.get_ticks()/1000.0
    draw_claude(screen, WIDTH//2, 470, scale=0.45, t=tt)
    msg=FONT_MID.render("くろーどちゃんより：あそんでくれてありがとう〜！",True,(180,80,140))
    screen.blit(msg,msg.get_rect(center=(WIDTH//2,540)))
    btn=pygame.Rect(WIDTH//2-180,580,360,100)
    pygame.draw.rect(screen,BLUE,btn,border_radius=20); pygame.draw.rect(screen,BLACK,btn,4,border_radius=20)
    t=FONT_MID.render("もういちど あそぶ",True,WHITE); screen.blit(t,t.get_rect(center=btn.center))
    return btn

def main():
    g=Game(); running=True; prects=None; fbtn=None
    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                mx,my=e.pos
                if g.state=="playing" and not g.feedback and prects:
                    L,R=prects
                    if L.collidepoint(mx,my): g.click("L")
                    elif R.collidepoint(mx,my): g.click("R")
                elif g.state=="finish" and fbtn and fbtn.collidepoint(mx,my):
                    g=Game()
            elif e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: running=False
        g.update()
        if g.state=="playing": prects=draw_playing(g)
        elif g.state=="finish": fbtn=draw_finish(g)
        pygame.display.flip(); clock.tick(60)
    pygame.quit()

if __name__=="__main__":
    main()
