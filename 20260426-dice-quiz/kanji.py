"""かんじクイズ - たろうくん の 2かいめ の クイズ
1から6のかずをえらぶ。1がげきムズ、6がちょうかんたん。
ただしいかんじをえらぶ！
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
pygame.display.set_caption("かんじクイズ")
clock = pygame.time.Clock()

def load_font(size):
    for p in ["C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/YuGothM.ttc", "C:/Windows/Fonts/msgothic.ttc"]:
        if os.path.exists(p):
            return pygame.font.Font(p, size)
    return pygame.font.SysFont(None, size)

FONT_KANJI = load_font(280)
FONT_HUGE = load_font(110)
FONT_BIG = load_font(64)
FONT_MID = load_font(40)
FONT_SMALL = load_font(28)

WHITE=(255,255,255); BLACK=(20,20,20); BLUE=(100,180,255)
GREEN=(100,220,120); RED=(240,80,80); YELLOW=(255,220,80); PURPLE=(200,130,230)
ORANGE=(255,160,80); BG=(255,245,220); PINK=(255,180,200)

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
SND_FINISH = make_chord([523,659,784,1046], 0.8, 0.3)

# ---------- もんだいデータ ----------
# (なんばん, よみかた, ただしいかんじ, にてるけどちがうかんじ, ヒント)
# 1=げきムズ, 6=ちょうかんたん
# にてるかんじを えらんで、そっくりに！
PROBLEMS = {
    1: {"yomi":"よう",   "correct":"曜", "wrong":"耀", "hint":"なんようび の よう！"},
    2: {"yomi":"はる",   "correct":"春", "wrong":"奉", "hint":"はるなつあきふゆ の はる！"},
    3: {"yomi":"し",     "correct":"死", "wrong":"処", "hint":"しぬ の し！"},
    4: {"yomi":"うた",   "correct":"歌", "wrong":"歎", "hint":"うた を うたう！"},
    5: {"yomi":"もり",   "correct":"森", "wrong":"林", "hint":"きが いっぱい の もり！"},
    6: {"yomi":"じ",     "correct":"字", "wrong":"宇", "hint":"もじ の じ！"},
}
DCOLOR={1:YELLOW,2:YELLOW,3:YELLOW,4:YELLOW,5:YELLOW,6:YELLOW}

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
        self.state="select"  # select / playing / feedback / finish
        self.hearts=3
        self.score=0
        self.solved=set()
        self.current=None
        self.correct_side="L"
        self.feedback=None
        self.message=""
        self.number_btns={}

    def click_number(self, n):
        if n in self.solved:
            self.message=f"{n} ばんは もうやったよ〜！"
            return
        self.message=""
        self.current=n
        self.correct_side=random.choice(["L","R"])
        self.state="playing"

    def click_kanji(self, side):
        if side==self.correct_side:
            self.score+=1
            self.solved.add(self.current)
            self.feedback=["correct",70]
            SND_CORRECT.play()
        else:
            self.hearts-=1
            self.feedback=["wrong",70]
            SND_WRONG.play()

    def update(self):
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
                        self.message="つぎの かずを えらんでね！"
                        self.state="select"
                else:
                    if self.hearts<=0:
                        self.state="finish"

def draw_select(g):
    bg()
    t=FONT_HUGE.render("かんじクイズ",True,RED)
    screen.blit(t,t.get_rect(center=(WIDTH//2,90)))
    t=FONT_MID.render("すきな かずを えらんでね！",True,BLACK)
    screen.blit(t,t.get_rect(center=(WIDTH//2,180)))

    # ハート
    for i in range(3):
        col=RED if i<g.hearts else (200,200,200)
        draw_heart(screen,WIDTH-60-i*70,60,30,col)
    c=FONT_MID.render(f"クリア: {len(g.solved)} / 6",True,BLACK); screen.blit(c,(40,40))

    g.number_btns={}
    for n in range(1,7):
        col_idx = (n-1)%3
        row_idx = (n-1)//3
        x = 200 + col_idx*320
        y = 270 + row_idx*230
        rect = pygame.Rect(x, y, 280, 200)
        if n in g.solved:
            pygame.draw.rect(screen,(200,200,200),rect,border_radius=20)
            pygame.draw.rect(screen,BLACK,rect,4,border_radius=20)
            t=FONT_HUGE.render(str(n),True,WHITE); screen.blit(t,t.get_rect(center=(rect.centerx,rect.centery-20)))
            t=FONT_MID.render("クリア！",True,GREEN); screen.blit(t,t.get_rect(center=(rect.centerx,rect.centery+70)))
        else:
            pygame.draw.rect(screen,DCOLOR[n],rect,border_radius=20)
            pygame.draw.rect(screen,BLACK,rect,4,border_radius=20)
            t=FONT_HUGE.render(str(n),True,BLACK); screen.blit(t,t.get_rect(center=rect.center))
        g.number_btns[n]=rect

    if g.message:
        m=FONT_MID.render(g.message,True,BLACK); screen.blit(m,m.get_rect(center=(WIDTH//2,HEIGHT-40)))

def draw_playing(g):
    bg()
    p=PROBLEMS[g.current]
    # うえのバー
    t=FONT_BIG.render(f"だい {g.current} もん",True,BLACK)
    screen.blit(t,(40,30))
    for i in range(3):
        col=RED if i<g.hearts else (200,200,200)
        draw_heart(screen,WIDTH-60-i*70,60,30,col)

    # よみかた
    box=pygame.Rect(WIDTH//2-300,130,600,100)
    pygame.draw.rect(screen,YELLOW,box,border_radius=20); pygame.draw.rect(screen,BLACK,box,4,border_radius=20)
    t=FONT_BIG.render(f"「{p['yomi']}」 はどっち？",True,BLACK)
    screen.blit(t,t.get_rect(center=box.center))

    # ヒント
    h=FONT_MID.render(p["hint"],True,(100,80,80))
    screen.blit(h,h.get_rect(center=(WIDTH//2,260)))

    # 2まいの かんじ
    bw=440; bh=440
    L=pygame.Rect(120,330,bw,bh); R=pygame.Rect(WIDTH-120-bw,330,bw,bh)
    for r in [L,R]:
        pygame.draw.rect(screen,WHITE,r,border_radius=20)
        pygame.draw.rect(screen,BLACK,r,5,border_radius=20)
    if g.correct_side=="L":
        lk=p["correct"]; rk=p["wrong"]
    else:
        lk=p["wrong"]; rk=p["correct"]
    tl=FONT_KANJI.render(lk,True,BLACK); screen.blit(tl,tl.get_rect(center=L.center))
    tr=FONT_KANJI.render(rk,True,BLACK); screen.blit(tr,tr.get_rect(center=R.center))

    if g.feedback:
        fb=g.feedback[0]
        cx,cy=WIDTH//2,HEIGHT//2+50
        if fb=="correct":
            pygame.draw.circle(screen,GREEN,(cx,cy),200,25)
            tt=FONT_HUGE.render("せいかい！",True,GREEN); screen.blit(tt,tt.get_rect(center=(cx,cy)))
        else:
            pygame.draw.line(screen,RED,(cx-150,cy-150),(cx+150,cy+150),25)
            pygame.draw.line(screen,RED,(cx+150,cy-150),(cx-150,cy+150),25)
            # ただしいほうをおしえる
            tt=FONT_BIG.render(f"こたえは 「{p['correct']}」 だよ！",True,RED)
            screen.blit(tt,tt.get_rect(center=(cx,cy+220)))

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
                if g.state=="select":
                    for n,r in g.number_btns.items():
                        if r.collidepoint(mx,my):
                            g.click_number(n); break
                elif g.state=="playing" and not g.feedback and prects:
                    L,R=prects
                    if L.collidepoint(mx,my): g.click_kanji("L")
                    elif R.collidepoint(mx,my): g.click_kanji("R")
                elif g.state=="finish" and fbtn and fbtn.collidepoint(mx,my):
                    g=Game()
            elif e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: running=False
        g.update()
        if g.state=="select": draw_select(g)
        elif g.state=="playing": prects=draw_playing(g)
        elif g.state=="finish": fbtn=draw_finish(g)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__=="__main__":
    main()
