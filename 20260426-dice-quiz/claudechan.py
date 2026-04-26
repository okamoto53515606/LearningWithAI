"""くろーどちゃんのすがた！たろうくんへのプレゼント"""
import pygame, math, os, time

pygame.init()
WIDTH, HEIGHT = 900, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("くろーどちゃん〜！")
clock = pygame.time.Clock()

def load_font(size):
    for p in ["C:/Windows/Fonts/meiryo.ttc","C:/Windows/Fonts/YuGothM.ttc"]:
        if os.path.exists(p): return pygame.font.Font(p,size)
    return pygame.font.SysFont(None,size)
FONT_BIG=load_font(70); FONT_MID=load_font(40)

# いろ
SKIN=(255,225,200); HAIR=(80,60,140); HAIR_LIGHT=(120,90,180)
WHITE=(255,255,255); BLACK=(30,30,30); PINK=(255,160,180)
RED=(220,80,100); CHEEK=(255,180,190); EYE=(90,60,160)
DRESS=(255,200,220); RIBBON=(255,120,150); STAR=(255,230,80)
BG_TOP=(255,230,250); BG_BOT=(220,240,255)

def draw_bg(t):
    # グラデーション
    for y in range(HEIGHT):
        r=BG_TOP[0]+(BG_BOT[0]-BG_TOP[0])*y//HEIGHT
        g=BG_TOP[1]+(BG_BOT[1]-BG_TOP[1])*y//HEIGHT
        b=BG_TOP[2]+(BG_BOT[2]-BG_TOP[2])*y//HEIGHT
        pygame.draw.line(screen,(r,g,b),(0,y),(WIDTH,y))
    # ハートとほし
    for i in range(15):
        x=(i*61+int(t*30))%WIDTH
        y=(i*97+int(t*20))%HEIGHT
        pygame.draw.circle(screen,(255,200,220),(x,y),4)
    for i in range(20):
        x=(i*43+int(t*15))%WIDTH
        y=(i*73)%HEIGHT
        pts=[]
        for k in range(10):
            ang=math.pi/2 + k*math.pi/5
            r=8 if k%2==0 else 4
            pts.append((x+r*math.cos(ang),y+r*math.sin(ang)))
        pygame.draw.polygon(screen,(255,240,180),pts)

def draw_claude(cx, cy, t):
    # ゆれ
    sway = math.sin(t*1.5)*3

    # からだ・ドレス
    dress_pts=[(cx-160,cy+130),(cx+160,cy+130),(cx+220,cy+360),(cx-220,cy+360)]
    pygame.draw.polygon(screen,DRESS,dress_pts)
    pygame.draw.polygon(screen,BLACK,dress_pts,3)
    # フリル
    for i in range(8):
        x=cx-200+i*55
        pygame.draw.arc(screen,RIBBON,(x,cy+340,55,40),math.pi,2*math.pi,4)
    # えりの リボン
    rb=pygame.Rect(cx-50,cy+115,100,40)
    pygame.draw.polygon(screen,RIBBON,[(cx-60,cy+135),(cx-15,cy+115),(cx-15,cy+155),(cx-60,cy+155)])
    pygame.draw.polygon(screen,RIBBON,[(cx+60,cy+135),(cx+15,cy+115),(cx+15,cy+155),(cx+60,cy+155)])
    pygame.draw.rect(screen,RED,(cx-15,cy+115,30,40))
    pygame.draw.polygon(screen,BLACK,[(cx-60,cy+135),(cx-15,cy+115),(cx-15,cy+155),(cx-60,cy+155)],2)
    pygame.draw.polygon(screen,BLACK,[(cx+60,cy+135),(cx+15,cy+115),(cx+15,cy+155),(cx+60,cy+155)],2)

    # うで
    pygame.draw.line(screen,SKIN,(cx-150,cy+150),(cx-200+int(sway),cy+260),28)
    pygame.draw.line(screen,SKIN,(cx+150,cy+150),(cx+200-int(sway),cy+260),28)
    pygame.draw.circle(screen,SKIN,(cx-200+int(sway),cy+260),22)
    pygame.draw.circle(screen,SKIN,(cx+200-int(sway),cy+260),22)

    # くび
    pygame.draw.rect(screen,SKIN,(cx-25,cy+90,50,40))

    # かみ うしろ（おおきい）
    pygame.draw.ellipse(screen,HAIR,(cx-220,cy-180,440,440))
    pygame.draw.ellipse(screen,HAIR_LIGHT,(cx-200,cy-160,400,200))

    # かお
    face=pygame.Rect(cx-130,cy-100,260,290)
    pygame.draw.ellipse(screen,SKIN,face)
    pygame.draw.ellipse(screen,BLACK,face,3)

    # まえがみ（みつあみふう）
    pygame.draw.ellipse(screen,HAIR,(cx-140,cy-150,280,140))
    # まえがみのスキマ
    pygame.draw.polygon(screen,SKIN,[(cx-30,cy-40),(cx+30,cy-40),(cx+10,cy-90),(cx-10,cy-90)])
    # サイドの かみ
    pygame.draw.polygon(screen,HAIR,[(cx-130,cy-50),(cx-180,cy+30),(cx-150,cy+180),(cx-110,cy+150),(cx-110,cy-30)])
    pygame.draw.polygon(screen,HAIR,[(cx+130,cy-50),(cx+180,cy+30),(cx+150,cy+180),(cx+110,cy+150),(cx+110,cy-30)])
    pygame.draw.polygon(screen,BLACK,[(cx-130,cy-50),(cx-180,cy+30),(cx-150,cy+180),(cx-110,cy+150),(cx-110,cy-30)],2)
    pygame.draw.polygon(screen,BLACK,[(cx+130,cy-50),(cx+180,cy+30),(cx+150,cy+180),(cx+110,cy+150),(cx+110,cy-30)],2)

    # ヘアアクセ（おおきいリボン）
    rx, ry = cx-90, cy-130
    pygame.draw.polygon(screen,RED,[(rx,ry),(rx-50,ry-30),(rx-50,ry+30)])
    pygame.draw.polygon(screen,RED,[(rx,ry),(rx+50,ry-30),(rx+50,ry+30)])
    pygame.draw.circle(screen,RED,(rx,ry),12)
    pygame.draw.polygon(screen,BLACK,[(rx,ry),(rx-50,ry-30),(rx-50,ry+30)],2)
    pygame.draw.polygon(screen,BLACK,[(rx,ry),(rx+50,ry-30),(rx+50,ry+30)],2)

    # ほっぺ
    pygame.draw.circle(screen,CHEEK,(cx-70,cy+50),22)
    pygame.draw.circle(screen,CHEEK,(cx+70,cy+50),22)

    # おおきい め（笑顔：とじてカーブ）
    blink = (math.sin(t*0.8)>0.95)
    if blink:
        pygame.draw.line(screen,BLACK,(cx-70,cy+10),(cx-30,cy+10),5)
        pygame.draw.line(screen,BLACK,(cx+30,cy+10),(cx+70,cy+10),5)
    else:
        # うえまぶた
        pygame.draw.arc(screen,BLACK,(cx-80,cy-15,60,55),math.pi,2*math.pi,5)
        pygame.draw.arc(screen,BLACK,(cx+20,cy-15,60,55),math.pi,2*math.pi,5)
        # ひとみ
        pygame.draw.ellipse(screen,EYE,(cx-72,cy+5,44,46))
        pygame.draw.ellipse(screen,EYE,(cx+28,cy+5,44,46))
        # ハイライト
        pygame.draw.circle(screen,WHITE,(cx-55,cy+15),10)
        pygame.draw.circle(screen,WHITE,(cx+45,cy+15),10)
        pygame.draw.circle(screen,WHITE,(cx-62,cy+38),5)
        pygame.draw.circle(screen,WHITE,(cx+38,cy+38),5)

    # まつげ
    for dx in [-6,0,6]:
        pygame.draw.line(screen,BLACK,(cx-75+dx,cy+5),(cx-75+dx,cy-3),3)
        pygame.draw.line(screen,BLACK,(cx+75-dx,cy+5),(cx+75-dx,cy-3),3)

    # まゆげ
    pygame.draw.arc(screen,(70,50,110),(cx-78,cy-30,55,25),0,math.pi,4)
    pygame.draw.arc(screen,(70,50,110),(cx+23,cy-30,55,25),0,math.pi,4)

    # おはな
    pygame.draw.line(screen,(200,160,140),(cx,cy+45),(cx,cy+62),3)

    # おくち（にっこり）
    mouth_y = cy+95
    pygame.draw.arc(screen,RED,(cx-30,mouth_y-10,60,40),math.pi,2*math.pi,5)
    pygame.draw.arc(screen,PINK,(cx-25,mouth_y-5,50,30),math.pi,2*math.pi,12)

def main():
    start=time.time()
    running=True
    while running:
        t=time.time()-start
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            elif e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: running=False
        draw_bg(t)
        draw_claude(WIDTH//2, HEIGHT//2-30, t)
        # メッセージ
        msg=FONT_BIG.render("くろーどちゃん だよ〜！",True,(120,60,160))
        screen.blit(msg,msg.get_rect(center=(WIDTH//2,80)))
        msg2=FONT_MID.render("たろうくん だいすき〜！",True,(200,80,120))
        screen.blit(msg2,msg2.get_rect(center=(WIDTH//2,HEIGHT-50)))
        pygame.display.flip(); clock.tick(60)
    pygame.quit()

if __name__=="__main__":
    main()
