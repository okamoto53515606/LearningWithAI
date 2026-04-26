"""げきムズ タイムアタック - 30びょうで10もん ノーミス！
1ねんふくしゅう x2、2ねんふくしゅう x2、まちがいさがし x4、きせつ x2
"""
import pygame, random, math, numpy as np, os
from claude_draw import draw_claude

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)

WIDTH, HEIGHT = 1280, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("げきムズ タイムアタック！")
clock = pygame.time.Clock()

def load_font(size):
    for p in ["C:/Windows/Fonts/meiryo.ttc","C:/Windows/Fonts/YuGothM.ttc","C:/Windows/Fonts/msgothic.ttc"]:
        if os.path.exists(p): return pygame.font.Font(p,size)
    return pygame.font.SysFont(None,size)

FONT_KANJI=load_font(200); FONT_HUGE=load_font(100); FONT_BIG=load_font(60)
FONT_MID=load_font(38); FONT_SMALL=load_font(26); FONT_TIMER=load_font(80)

WHITE=(255,255,255); BLACK=(20,20,20); BLUE=(100,180,255); GREEN=(100,220,120)
RED=(240,80,80); YELLOW=(255,220,80); PURPLE=(200,130,230); ORANGE=(255,160,80)
BG=(255,240,210); PINK=(255,180,200); SKY=(180,230,255); BROWN=(140,90,50)

def make_tone(f,d,v=0.4):
    sr=22050; n=int(sr*d); t=np.linspace(0,d,n,False)
    w=np.sin(2*np.pi*f*t)*v*np.linspace(1,0,n)
    a=(w*32767).astype(np.int16); return pygame.sndarray.make_sound(np.column_stack((a,a)))
def make_chord(fs,d,v=0.3):
    sr=22050; n=int(sr*d); t=np.linspace(0,d,n,False)
    w=sum(np.sin(2*np.pi*f*t) for f in fs)/len(fs)*v*np.linspace(1,0,n)
    a=(w*32767).astype(np.int16); return pygame.sndarray.make_sound(np.column_stack((a,a)))
SND_OK=make_chord([523,659,784],0.25,0.3)
SND_NG=make_tone(180,0.4,0.4)
SND_WIN=make_chord([523,659,784,1046,1318],1.0,0.3)
SND_LOSE=make_chord([200,150,100],0.8,0.3)
SND_TICK=make_tone(1200,0.04,0.2)

# ---------- えがき：まちがいさがし ようイラスト ----------
def draw_ringo(surf, cx, cy, size, wrong=False):
    """りんご：wrong だと みどりいろ"""
    col=(80,180,80) if wrong else (220,50,50)
    r=int(size*0.45)
    pygame.draw.circle(surf,col,(cx,cy+10),r)
    pygame.draw.circle(surf,BLACK,(cx,cy+10),r,3)
    # は
    pygame.draw.ellipse(surf,(80,180,80),(cx,cy-r-5,30,20))
    pygame.draw.ellipse(surf,BLACK,(cx,cy-r-5,30,20),2)
    # ハイライト
    pygame.draw.circle(surf,WHITE,(cx-15,cy-10),8)

def draw_kasa(surf, cx, cy, size, wrong=False):
    """かさ：wrong だと ほねが3ぼん（ふつうは6ぼん）"""
    r=int(size*0.5)
    pygame.draw.arc(surf,BLUE,(cx-r,cy-r//2,2*r,r),math.pi,2*math.pi,0)
    # かさのおおうサーク埋める
    pts=[]
    for a in range(180,361,5):
        pts.append((cx+r*math.cos(math.radians(a)),cy+r*math.sin(math.radians(a))))
    pts.append((cx,cy))
    pygame.draw.polygon(surf,(100,160,230),pts)
    pygame.draw.polygon(surf,BLACK,pts,3)
    # ほね
    bones = 3 if wrong else 6
    for i in range(bones+1):
        ang = math.pi + math.pi*i/bones
        pygame.draw.line(surf,BLACK,(cx,cy),(cx+r*math.cos(ang),cy+r*math.sin(ang)),2)
    # え
    pygame.draw.line(surf,BROWN,(cx,cy),(cx,cy+r+30),5)
    pygame.draw.arc(surf,BROWN,(cx-15,cy+r+10,30,30),0,math.pi,5)

def draw_denwa(surf, cx, cy, size, wrong=False):
    """でんわ：wrong だと じゅわきが あおいろ"""
    base=pygame.Rect(cx-size//2,cy,size,size//2)
    pygame.draw.rect(surf,(200,200,200),base,border_radius=10)
    pygame.draw.rect(surf,BLACK,base,3,border_radius=10)
    # ボタン
    for r in range(3):
        for c in range(3):
            pygame.draw.rect(surf,WHITE,(base.x+15+c*30,base.y+10+r*22,22,18),border_radius=3)
            pygame.draw.rect(surf,BLACK,(base.x+15+c*30,base.y+10+r*22,22,18),1,border_radius=3)
    # じゅわき
    col = BLUE if wrong else (50,50,50)
    pygame.draw.rect(surf,col,(cx-size//2-10,cy-30,size+20,30),border_radius=15)
    pygame.draw.rect(surf,BLACK,(cx-size//2-10,cy-30,size+20,30),3,border_radius=15)

def draw_hana(surf, cx, cy, size, wrong=False):
    """おはな：wrong だと はなびらが 4まい（ふつうは5まい）"""
    petals = 4 if wrong else 5
    r=int(size*0.18)
    for i in range(petals):
        ang = 2*math.pi*i/petals - math.pi/2
        px=cx+int(45*math.cos(ang)); py=cy+int(45*math.sin(ang))
        pygame.draw.circle(surf,(255,150,200),(px,py),r)
        pygame.draw.circle(surf,BLACK,(px,py),r,2)
    pygame.draw.circle(surf,YELLOW,(cx,cy),20)
    pygame.draw.circle(surf,BLACK,(cx,cy),20,2)
    # くき
    pygame.draw.line(surf,(80,180,80),(cx,cy+20),(cx,cy+size//2+30),5)
    pygame.draw.ellipse(surf,(80,180,80),(cx,cy+size//4,40,20))

# ---------- きせつ ようイラスト ----------
def draw_yago(surf, cx, cy, size):
    body_w=int(size*0.7); body_h=int(size*0.32)
    pygame.draw.ellipse(surf,(110,140,90),(cx-body_w//2,cy-body_h//2,body_w,body_h))
    pygame.draw.ellipse(surf,BLACK,(cx-body_w//2,cy-body_h//2,body_w,body_h),3)
    for i in range(3):
        pygame.draw.line(surf,(80,110,60),(cx+body_w//2,cy),(cx+body_w//2+30,cy-15+i*15),4)
    head_r=int(size*0.18)
    pygame.draw.circle(surf,(100,130,80),(cx-body_w//2-head_r//2,cy),head_r)
    pygame.draw.circle(surf,BLACK,(cx-body_w//2-head_r//2,cy),head_r,3)
    pygame.draw.circle(surf,BLACK,(cx-body_w//2-head_r//2-8,cy-head_r//2),8)
    pygame.draw.circle(surf,BLACK,(cx-body_w//2-head_r//2+8,cy-head_r//2),8)

def draw_kaki(surf, cx, cy, size):
    r=int(size*0.4)
    pygame.draw.circle(surf,ORANGE,(cx,cy+10),r)
    pygame.draw.circle(surf,BLACK,(cx,cy+10),r,3)
    # へた
    pygame.draw.polygon(surf,(80,140,60),[(cx-30,cy-r+20),(cx+30,cy-r+20),(cx+15,cy-r+5),(cx-15,cy-r+5)])
    pygame.draw.polygon(surf,BLACK,[(cx-30,cy-r+20),(cx+30,cy-r+20),(cx+15,cy-r+5),(cx-15,cy-r+5)],2)

# ---------- もんだい ----------
# image: えをかく かんすう（あれば）。choice: 2たく
PROBLEMS = [
    {"label":"1ねん さんすう","question":"7 + 8 は？","choices":["15","14"],"correct_idx":0},
    {"label":"1ねん こくご","question":"「ひと」 はどっち？","choices":["人","入"],"correct_idx":0,"kanji":True},
    {"label":"2ねん さんすう","question":"9 × 6 は？","choices":["54","56"],"correct_idx":0},
    {"label":"2ねん こくご","question":"「あき」 はどっち？","choices":["秋","秒"],"correct_idx":0,"kanji":True},
    {"label":"まちがいさがし","question":"おかしい りんご はどっち？","draw":"ringo","choices":["A","B"]},
    {"label":"まちがいさがし","question":"おかしい かさ はどっち？","draw":"kasa","choices":["A","B"]},
    {"label":"まちがいさがし","question":"おかしい でんわ はどっち？","draw":"denwa","choices":["A","B"]},
    {"label":"まちがいさがし","question":"おかしい おはな はどっち？","draw":"hana","choices":["A","B"]},
    {"label":"きせつ","question":"ヤゴ はどのきせつ？","draw_kisetsu":"yago","choices":["はる","ふゆ"],"correct_idx":0},
    {"label":"きせつ","question":"カキ はどのきせつ？","draw_kisetsu":"kaki","choices":["なつ","あき"],"correct_idx":1},
]

# まちがいさがしの correct_idx は ゲームかいしじにランダムで きめる
DRAW_FUNCS={"ringo":draw_ringo,"kasa":draw_kasa,"denwa":draw_denwa,"hana":draw_hana}
KISETSU_FUNCS={"yago":draw_yago,"kaki":draw_kaki}

TIME_LIMIT=20.0

def bg():
    screen.fill(BG)
    for i in range(40):
        pygame.draw.circle(screen,(255,225,170),((i*53)%WIDTH,(i*31)%HEIGHT),3)

class Game:
    def __init__(self):
        self.state="title"; self.idx=0; self.start_ticks=None
        self.feedback=None; self.tick_last=0
        # まちがいさがしの correct_idx を ランダム
        self.problems=[dict(p) for p in PROBLEMS]
        for p in self.problems:
            if "draw" in p:
                p["correct_idx"]=random.randint(0,1)  # どっちが wrong か

    def start(self):
        self.state="playing"; self.start_ticks=pygame.time.get_ticks()
        self.idx=0; self.feedback=None

    def remaining(self):
        if self.start_ticks is None: return TIME_LIMIT
        e=(pygame.time.get_ticks()-self.start_ticks)/1000.0
        return max(0.0, TIME_LIMIT-e)

    def click_choice(self,i):
        p=self.problems[self.idx]
        if i==p["correct_idx"]:
            SND_OK.play(); self.feedback=["ok",12]
        else:
            SND_NG.play(); self.state="lose"

    def update(self):
        if self.state=="playing":
            if self.remaining()<=0:
                SND_LOSE.play(); self.state="lose"; return
            sec=int(self.remaining())
            if sec<=5 and sec!=self.tick_last:
                SND_TICK.play(); self.tick_last=sec
            if self.feedback:
                self.feedback[1]-=1
                if self.feedback[1]<=0:
                    self.feedback=None; self.idx+=1
                    if self.idx>=len(self.problems):
                        SND_WIN.play(); self.state="win"

def draw_title():
    bg()
    t=FONT_HUGE.render("げきムズ！",True,RED); screen.blit(t,t.get_rect(center=(WIDTH//2,130)))
    t=FONT_HUGE.render("タイムアタック",True,BLUE); screen.blit(t,t.get_rect(center=(WIDTH//2,250)))
    t=FONT_BIG.render("20びょう で 10もん ノーミス！",True,BLACK)
    screen.blit(t,t.get_rect(center=(WIDTH//2,380)))
    t=FONT_MID.render("1ねん・2ねん・まちがいさがし・きせつ ぜんぶでる！",True,(80,80,80))
    screen.blit(t,t.get_rect(center=(WIDTH//2,450)))
    btn=pygame.Rect(WIDTH//2-220,500,440,140)
    pygame.draw.rect(screen,YELLOW,btn,border_radius=30); pygame.draw.rect(screen,BLACK,btn,6,border_radius=30)
    t=FONT_BIG.render("スタート！",True,BLACK); screen.blit(t,t.get_rect(center=btn.center))
    t=FONT_MID.render("1もんでも まちがえたら ゲームオーバー！",True,(150,80,80))
    screen.blit(t,t.get_rect(center=(WIDTH//2,690)))
    return btn

def draw_timer(g):
    rem=g.remaining()
    bar=pygame.Rect(40,30,WIDTH-80,30)
    pygame.draw.rect(screen,(220,220,220),bar,border_radius=15)
    fill_w=int((WIDTH-80)*rem/TIME_LIMIT)
    bcol = GREEN if rem>10 else (YELLOW if rem>5 else RED)
    pygame.draw.rect(screen,bcol,(40,30,fill_w,30),border_radius=15)
    pygame.draw.rect(screen,BLACK,bar,3,border_radius=15)
    tcol = RED if rem<=5 else BLACK
    t=FONT_TIMER.render(f"{rem:.1f}",True,tcol); screen.blit(t,t.get_rect(center=(WIDTH//2,105)))

def draw_playing(g):
    bg(); draw_timer(g)
    p=g.problems[g.idx]
    t=FONT_MID.render(f"{g.idx+1}/10  {p['label']}",True,(80,80,80))
    screen.blit(t,(40,165))
    # しつもん
    qbox=pygame.Rect(WIDTH//2-450,200,900,110)
    pygame.draw.rect(screen,WHITE,qbox,border_radius=20); pygame.draw.rect(screen,BLACK,qbox,5,border_radius=20)
    t=FONT_BIG.render(p["question"],True,BLACK); screen.blit(t,t.get_rect(center=qbox.center))

    # 2たく
    L=pygame.Rect(120,360,440,360); R=pygame.Rect(WIDTH-120-440,360,440,360)
    for i,r in enumerate([L,R]):
        col = PINK if i==0 else SKY
        pygame.draw.rect(screen,col,r,border_radius=20); pygame.draw.rect(screen,BLACK,r,5,border_radius=20)
        if "draw" in p:
            # まちがいさがし：correct_idx が wrong（おかしいほう）
            wrong = (i == p["correct_idx"])
            DRAW_FUNCS[p["draw"]](screen, r.centerx, r.centery, 280, wrong=wrong)
            # ラベル
            tt=FONT_BIG.render(p["choices"][i],True,BLACK)
            screen.blit(tt,tt.get_rect(midtop=(r.centerx,r.bottom-70)))
        elif "draw_kisetsu" in p:
            # 季節：i=0 ならイラスト＋label, i=1 もlabel。実際はイラストは1つ、両方は文字
            tt=FONT_HUGE.render(p["choices"][i],True,BLACK)
            screen.blit(tt,tt.get_rect(center=r.center))
        else:
            ch=p["choices"][i]
            if p.get("kanji"):
                tt=FONT_KANJI.render(ch,True,BLACK)
            else:
                tt=FONT_HUGE.render(ch,True,BLACK)
            screen.blit(tt,tt.get_rect(center=r.center))

    # きせつもんだいは うえに イラスト（小）も
    if "draw_kisetsu" in p:
        # しつもんのうえあたりにイラストを表示
        ibox=pygame.Rect(WIDTH//2-100,200,200,110)
        # 上書き
        pygame.draw.rect(screen,WHITE,ibox); pygame.draw.rect(screen,BLACK,ibox,3)
        KISETSU_FUNCS[p["draw_kisetsu"]](screen, ibox.centerx, ibox.centery+10, 100)

    if g.feedback:
        cx,cy=WIDTH//2,HEIGHT//2+60
        pygame.draw.circle(screen,GREEN,(cx,cy),100,16)
    return L,R

def draw_end(g):
    bg()
    if g.state=="win":
        rem=g.remaining()
        t=FONT_HUGE.render("クリア！！",True,RED)
        screen.blit(t,t.get_rect(center=(WIDTH//2,90)))
        t2=FONT_BIG.render(f"のこり {rem:.1f} びょう",True,PURPLE)
        screen.blit(t2,t2.get_rect(center=(WIDTH//2,180)))
        t3=FONT_BIG.render("たろうくん てんさい〜！！",True,PURPLE)
        screen.blit(t3,t3.get_rect(center=(WIDTH//2,260)))
        t4=FONT_MID.render("げきムズ クリア おめでとう！",True,ORANGE)
        screen.blit(t4,t4.get_rect(center=(WIDTH//2,320)))
        tt = pygame.time.get_ticks()/1000.0
        draw_claude(screen, WIDTH//2, 470, scale=0.45, t=tt)
        msg=FONT_MID.render("くろーどちゃんより：さいこうだよ〜！",True,(180,80,140))
        screen.blit(msg,msg.get_rect(center=(WIDTH//2,540)))
    else:
        t=FONT_HUGE.render("ゲームオーバー...",True,RED)
        screen.blit(t,t.get_rect(center=(WIDTH//2,200)))
        if g.remaining()<=0:
            t2=FONT_BIG.render("じかんぎれ！",True,(150,80,80))
        else:
            t2=FONT_BIG.render(f"{g.idx+1}もんめで まちがえちゃった！",True,(150,80,80))
        screen.blit(t2,t2.get_rect(center=(WIDTH//2,340)))
        t3=FONT_MID.render("もういっかい ちょうせん！",True,BLACK)
        screen.blit(t3,t3.get_rect(center=(WIDTH//2,440)))
    btn=pygame.Rect(WIDTH//2-200,580,400,120)
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
                if g.state=="title" and tbtn and tbtn.collidepoint(mx,my): g.start()
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
        if g.state=="title": tbtn=draw_title()
        elif g.state=="playing": prects=draw_playing(g)
        else: ebtn=draw_end(g)
        pygame.display.flip(); clock.tick(60)
    pygame.quit()

if __name__=="__main__":
    main()
