"""タイムアタッククイズ - 25びょうで4もんノーミスクリア！
1. 1ねんさんすう: 10 + 30
2. 1ねんこくご: 「字」のかんじ どっち？
3. 2ねんさんすう: ひっさん
4. 2ねんこくご: くろーどちゃんがきめる
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
pygame.display.set_caption("タイムアタッククイズ")
clock = pygame.time.Clock()

def load_font(size):
    for p in ["C:/Windows/Fonts/meiryo.ttc","C:/Windows/Fonts/YuGothM.ttc","C:/Windows/Fonts/msgothic.ttc"]:
        if os.path.exists(p): return pygame.font.Font(p,size)
    return pygame.font.SysFont(None,size)

FONT_KANJI=load_font(220)
FONT_HUGE=load_font(110); FONT_BIG=load_font(64); FONT_MID=load_font(40); FONT_SMALL=load_font(28)
FONT_TIMER=load_font(80)

WHITE=(255,255,255); BLACK=(20,20,20); BLUE=(100,180,255); GREEN=(100,220,120)
RED=(240,80,80); YELLOW=(255,220,80); PURPLE=(200,130,230); ORANGE=(255,160,80)
BG=(255,245,220); PINK=(255,180,200); SKY=(180,230,255)

def make_tone(f,d,v=0.4):
    sr=22050; n=int(sr*d); t=np.linspace(0,d,n,False)
    w=np.sin(2*np.pi*f*t)*v*np.linspace(1,0,n)
    a=(w*32767).astype(np.int16); return pygame.sndarray.make_sound(np.column_stack((a,a)))
def make_chord(fs,d,v=0.3):
    sr=22050; n=int(sr*d); t=np.linspace(0,d,n,False)
    w=sum(np.sin(2*np.pi*f*t) for f in fs)/len(fs)*v*np.linspace(1,0,n)
    a=(w*32767).astype(np.int16); return pygame.sndarray.make_sound(np.column_stack((a,a)))
SND_OK=make_chord([523,659,784],0.3,0.3)
SND_NG=make_tone(180,0.4,0.4)
SND_WIN=make_chord([523,659,784,1046],0.8,0.3)
SND_LOSE=make_chord([200,150,100],0.8,0.3)
SND_TICK=make_tone(1000,0.04,0.2)

# ---------- もんだいデータ ----------
# type: "choice2" 2たく / "input" すうじにゅうりょく
PROBLEMS = [
    {
        "type":"choice2",
        "label":"1ねん さんすう",
        "question":"10 + 30 は？",
        "choices":["40","30"],
        "correct_idx":0,
    },
    {
        "type":"choice2",
        "label":"1ねん こくご",
        "question":"「じ」 はどっち？",
        "choices":["字","宇"],
        "correct_idx":0,
        "kanji":True,
    },
    {
        "type":"choice2",
        "label":"2ねん さんすう（ひっさん）",
        "question":"  25\n+ 18",
        "choices":["43","33"],
        "correct_idx":0,
        "vertical":True,
    },
    {
        "type":"choice2",
        "label":"2ねん こくご",
        "question":"「はる」 はどっち？",
        "choices":["春","夏"],
        "correct_idx":0,
        "kanji":True,
    },
]
TIME_LIMIT = 25.0

def bg():
    screen.fill(BG)
    for i in range(40):
        pygame.draw.circle(screen,(255,230,180),((i*53)%WIDTH,(i*31)%HEIGHT),3)

class Game:
    def __init__(self):
        self.state="title"  # title / playing / win / lose
        self.idx=0
        self.start_ticks=None
        self.feedback=None
        self.tick_last=0

    def start(self):
        self.state="playing"
        self.start_ticks=pygame.time.get_ticks()
        self.idx=0
        self.feedback=None

    def remaining(self):
        if self.start_ticks is None: return TIME_LIMIT
        elapsed=(pygame.time.get_ticks()-self.start_ticks)/1000.0
        return max(0.0, TIME_LIMIT-elapsed)

    def click_choice(self, i):
        p=PROBLEMS[self.idx]
        if i==p["correct_idx"]:
            SND_OK.play()
            self.feedback=["ok",20]
        else:
            # ノーミス：いっぱつアウト
            SND_NG.play()
            self.state="lose"

    def update(self):
        if self.state=="playing":
            if self.remaining()<=0:
                SND_LOSE.play(); self.state="lose"; return
            # チクタクおと
            sec=int(self.remaining())
            if sec<=5 and sec!=self.tick_last:
                SND_TICK.play(); self.tick_last=sec
            if self.feedback:
                self.feedback[1]-=1
                if self.feedback[1]<=0:
                    self.feedback=None
                    self.idx+=1
                    if self.idx>=len(PROBLEMS):
                        SND_WIN.play(); self.state="win"

def draw_title(g):
    bg()
    t=FONT_HUGE.render("タイムアタック",True,RED); screen.blit(t,t.get_rect(center=(WIDTH//2,150)))
    t=FONT_HUGE.render("クイズ！",True,BLUE); screen.blit(t,t.get_rect(center=(WIDTH//2,270)))
    t=FONT_BIG.render("25びょう で 4もん ノーミス！",True,BLACK)
    screen.blit(t,t.get_rect(center=(WIDTH//2,400)))
    btn=pygame.Rect(WIDTH//2-220,470,440,150)
    pygame.draw.rect(screen,YELLOW,btn,border_radius=30); pygame.draw.rect(screen,BLACK,btn,6,border_radius=30)
    t=FONT_BIG.render("スタート！",True,BLACK); screen.blit(t,t.get_rect(center=btn.center))
    t=FONT_MID.render("1もんでも まちがえたら ゲームオーバー！",True,(150,80,80))
    screen.blit(t,t.get_rect(center=(WIDTH//2,680)))
    return btn

def draw_timer(g):
    rem=g.remaining()
    # タイマーバー
    bar=pygame.Rect(40,30,WIDTH-80,30)
    pygame.draw.rect(screen,(220,220,220),bar,border_radius=15)
    fill_w=int((WIDTH-80)*rem/TIME_LIMIT)
    bcol = GREEN if rem>10 else (YELLOW if rem>5 else RED)
    pygame.draw.rect(screen,bcol,(40,30,fill_w,30),border_radius=15)
    pygame.draw.rect(screen,BLACK,bar,3,border_radius=15)
    # すうじ
    tcol = RED if rem<=5 else BLACK
    t=FONT_TIMER.render(f"{rem:.1f}",True,tcol); screen.blit(t,t.get_rect(center=(WIDTH//2,110)))

def draw_playing(g):
    bg()
    draw_timer(g)
    p=PROBLEMS[g.idx]
    # ラベル
    t=FONT_MID.render(f"{g.idx+1}/4  {p['label']}",True,(80,80,80))
    screen.blit(t,(40,170))

    # しつもん
    qbox=pygame.Rect(WIDTH//2-400,220,800,180)
    pygame.draw.rect(screen,WHITE,qbox,border_radius=20); pygame.draw.rect(screen,BLACK,qbox,5,border_radius=20)
    if p.get("vertical"):
        # ひっさんを2ぎょうで
        lines=p["question"].split("\n")
        for i,line in enumerate(lines):
            t=FONT_BIG.render(line,True,BLACK)
            screen.blit(t,t.get_rect(center=(qbox.centerx, qbox.y+50+i*70)))
        pygame.draw.line(screen,BLACK,(qbox.centerx-100,qbox.y+150),(qbox.centerx+150,qbox.y+150),4)
    else:
        t=FONT_BIG.render(p["question"],True,BLACK)
        screen.blit(t,t.get_rect(center=qbox.center))

    # 2たくボタン
    L=pygame.Rect(120,460,440,260); R=pygame.Rect(WIDTH-120-440,460,440,260)
    for i,r in enumerate([L,R]):
        col = PINK if i==0 else SKY
        pygame.draw.rect(screen,col,r,border_radius=20); pygame.draw.rect(screen,BLACK,r,5,border_radius=20)
        ch=p["choices"][i]
        if p.get("kanji"):
            t=FONT_KANJI.render(ch,True,BLACK)
        else:
            t=FONT_HUGE.render(ch,True,BLACK)
        screen.blit(t,t.get_rect(center=r.center))

    # フィードバック○
    if g.feedback:
        cx,cy=WIDTH//2,HEIGHT//2+50
        pygame.draw.circle(screen,GREEN,(cx,cy),120,18)
        tt=FONT_BIG.render("せいかい！",True,GREEN); screen.blit(tt,tt.get_rect(center=(cx,cy)))
    return L,R

def draw_end(g):
    bg()
    if g.state=="win":
        rem=g.remaining()
        t=FONT_HUGE.render("クリア！！",True,RED)
        screen.blit(t,t.get_rect(center=(WIDTH//2,100)))
        t2=FONT_BIG.render(f"のこり {rem:.1f} びょう",True,PURPLE)
        screen.blit(t2,t2.get_rect(center=(WIDTH//2,200)))
        t3=FONT_BIG.render("すごい〜！たろうくんてんさい！",True,PURPLE)
        screen.blit(t3,t3.get_rect(center=(WIDTH//2,290)))
        tt = pygame.time.get_ticks()/1000.0
        draw_claude(screen, WIDTH//2, 450, scale=0.45, t=tt)
        msg=FONT_MID.render("くろーどちゃんより：ものすごいスピードだね〜！",True,(180,80,140))
        screen.blit(msg,msg.get_rect(center=(WIDTH//2,520)))
    else:
        t=FONT_HUGE.render("ゲームオーバー...",True,RED)
        screen.blit(t,t.get_rect(center=(WIDTH//2,200)))
        if g.remaining()<=0:
            t2=FONT_BIG.render("じかんぎれ！",True,(150,80,80))
        else:
            t2=FONT_BIG.render("まちがえちゃった！",True,(150,80,80))
        screen.blit(t2,t2.get_rect(center=(WIDTH//2,340)))
    btn=pygame.Rect(WIDTH//2-200,560,400,120)
    pygame.draw.rect(screen,BLUE,btn,border_radius=20); pygame.draw.rect(screen,BLACK,btn,4,border_radius=20)
    t=FONT_BIG.render("もういちど！",True,WHITE); screen.blit(t,t.get_rect(center=btn.center))
    return btn

def main():
    g=Game(); running=True; tbtn=None; prects=None; ebtn=None
    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                mx,my=e.pos
                if g.state=="title" and tbtn and tbtn.collidepoint(mx,my):
                    g.start()
                elif g.state=="playing" and not g.feedback and prects:
                    L,R=prects
                    if L.collidepoint(mx,my): g.click_choice(0)
                    elif R.collidepoint(mx,my): g.click_choice(1)
                elif g.state in ("win","lose") and ebtn and ebtn.collidepoint(mx,my):
                    g=Game()
            elif e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: running=False
                elif e.key==pygame.K_SPACE and g.state=="title": g.start()
        g.update()
        if g.state=="title": tbtn=draw_title(g)
        elif g.state=="playing": prects=draw_playing(g)
        else: ebtn=draw_end(g)
        pygame.display.flip(); clock.tick(60)
    pygame.quit()

if __name__=="__main__":
    main()
