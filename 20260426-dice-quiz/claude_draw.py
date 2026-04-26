"""くろーどちゃん イラスト（共通モジュール）"""
import pygame, math, time

SKIN=(255,225,200); HAIR=(80,60,140); HAIR_LIGHT=(120,90,180)
WHITE=(255,255,255); BLACK=(30,30,30); PINK=(255,160,180)
RED=(220,80,100); CHEEK=(255,180,190); EYE=(90,60,160)
DRESS=(255,200,220); RIBBON=(255,120,150)

def draw_claude(screen, cx, cy, scale=1.0, t=0.0):
    """くろーどちゃんを (cx,cy) に描画。scale=1.0 で約500px縦"""
    s = scale
    sway = math.sin(t*1.5)*3*s

    def S(v): return int(v*s)

    # ドレス
    dress_pts=[(cx-S(160),cy+S(130)),(cx+S(160),cy+S(130)),(cx+S(220),cy+S(360)),(cx-S(220),cy+S(360))]
    pygame.draw.polygon(screen,DRESS,dress_pts)
    pygame.draw.polygon(screen,BLACK,dress_pts,max(2,int(3*s)))
    # リボン
    pygame.draw.polygon(screen,RIBBON,[(cx-S(60),cy+S(135)),(cx-S(15),cy+S(115)),(cx-S(15),cy+S(155)),(cx-S(60),cy+S(155))])
    pygame.draw.polygon(screen,RIBBON,[(cx+S(60),cy+S(135)),(cx+S(15),cy+S(115)),(cx+S(15),cy+S(155)),(cx+S(60),cy+S(155))])
    pygame.draw.rect(screen,RED,(cx-S(15),cy+S(115),S(30),S(40)))
    # うで
    pygame.draw.line(screen,SKIN,(cx-S(150),cy+S(150)),(cx-S(200)+int(sway),cy+S(260)),max(8,int(28*s)))
    pygame.draw.line(screen,SKIN,(cx+S(150),cy+S(150)),(cx+S(200)-int(sway),cy+S(260)),max(8,int(28*s)))
    pygame.draw.circle(screen,SKIN,(cx-S(200)+int(sway),cy+S(260)),max(8,int(22*s)))
    pygame.draw.circle(screen,SKIN,(cx+S(200)-int(sway),cy+S(260)),max(8,int(22*s)))
    # くび
    pygame.draw.rect(screen,SKIN,(cx-S(25),cy+S(90),S(50),S(40)))
    # かみ うしろ
    pygame.draw.ellipse(screen,HAIR,(cx-S(220),cy-S(180),S(440),S(440)))
    pygame.draw.ellipse(screen,HAIR_LIGHT,(cx-S(200),cy-S(160),S(400),S(200)))
    # かお
    face=pygame.Rect(cx-S(130),cy-S(100),S(260),S(290))
    pygame.draw.ellipse(screen,SKIN,face)
    pygame.draw.ellipse(screen,BLACK,face,max(2,int(3*s)))
    # まえがみ
    pygame.draw.ellipse(screen,HAIR,(cx-S(140),cy-S(150),S(280),S(140)))
    pygame.draw.polygon(screen,SKIN,[(cx-S(30),cy-S(40)),(cx+S(30),cy-S(40)),(cx+S(10),cy-S(90)),(cx-S(10),cy-S(90))])
    # サイドかみ
    pygame.draw.polygon(screen,HAIR,[(cx-S(130),cy-S(50)),(cx-S(180),cy+S(30)),(cx-S(150),cy+S(180)),(cx-S(110),cy+S(150)),(cx-S(110),cy-S(30))])
    pygame.draw.polygon(screen,HAIR,[(cx+S(130),cy-S(50)),(cx+S(180),cy+S(30)),(cx+S(150),cy+S(180)),(cx+S(110),cy+S(150)),(cx+S(110),cy-S(30))])
    # ヘアリボン
    rx, ry = cx-S(90), cy-S(130)
    pygame.draw.polygon(screen,RED,[(rx,ry),(rx-S(50),ry-S(30)),(rx-S(50),ry+S(30))])
    pygame.draw.polygon(screen,RED,[(rx,ry),(rx+S(50),ry-S(30)),(rx+S(50),ry+S(30))])
    pygame.draw.circle(screen,RED,(rx,ry),max(4,int(12*s)))
    # ほっぺ
    pygame.draw.circle(screen,CHEEK,(cx-S(70),cy+S(50)),max(6,int(22*s)))
    pygame.draw.circle(screen,CHEEK,(cx+S(70),cy+S(50)),max(6,int(22*s)))
    # め（笑顔）
    pygame.draw.arc(screen,BLACK,(cx-S(80),cy-S(15),S(60),S(55)),math.pi,2*math.pi,max(2,int(5*s)))
    pygame.draw.arc(screen,BLACK,(cx+S(20),cy-S(15),S(60),S(55)),math.pi,2*math.pi,max(2,int(5*s)))
    pygame.draw.ellipse(screen,EYE,(cx-S(72),cy+S(5),S(44),S(46)))
    pygame.draw.ellipse(screen,EYE,(cx+S(28),cy+S(5),S(44),S(46)))
    pygame.draw.circle(screen,WHITE,(cx-S(55),cy+S(15)),max(3,int(10*s)))
    pygame.draw.circle(screen,WHITE,(cx+S(45),cy+S(15)),max(3,int(10*s)))
    # まゆ
    pygame.draw.arc(screen,(70,50,110),(cx-S(78),cy-S(30),S(55),S(25)),0,math.pi,max(2,int(4*s)))
    pygame.draw.arc(screen,(70,50,110),(cx+S(23),cy-S(30),S(55),S(25)),0,math.pi,max(2,int(4*s)))
    # おはな
    pygame.draw.line(screen,(200,160,140),(cx,cy+S(45)),(cx,cy+S(62)),max(2,int(3*s)))
    # おくち
    mouth_y = cy+S(95)
    pygame.draw.arc(screen,RED,(cx-S(30),mouth_y-S(10),S(60),S(40)),math.pi,2*math.pi,max(2,int(5*s)))
    pygame.draw.arc(screen,PINK,(cx-S(25),mouth_y-S(5),S(50),S(30)),math.pi,2*math.pi,max(4,int(12*s)))
