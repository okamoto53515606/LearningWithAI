"""
무궁화 꽃이 피었습니다 アニメーション＋音楽デモ
Python 3.12 + pygame
"""

import pygame
import sys
import math
import numpy as np
import os

# ─── 初期化 ───
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()

W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("むくげの花が咲きました")
clock = pygame.time.Clock()

# ─── 色 ───
SKY       = (195, 225, 255)
GRASS     = ( 55, 155,  55)
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED_C     = (220,  30,  30)
GREEN_C   = ( 30, 200,  70)
YELLOW    = (255, 220,   0)
SKIN      = (255, 210, 160)
DARK_HAIR = ( 35,  18,   8)
JUMPSUIT  = (  0, 175,  75)
DARK_GREY = ( 80,  80,  80)
BG_PANEL  = ( 20,  20,  40)

# ─── フォント ───
def get_font(size):
    for name in ["Malgun Gothic", "BIZ UDGothic", "Meiryo", "Yu Gothic", "Arial"]:
        try:
            return pygame.font.SysFont(name, size)
        except Exception:
            pass
    return pygame.font.Font(None, size)

font_sm = get_font(22)
font_md = get_font(36)
font_lg = get_font(60)

# ─── 音声合成：むくげの花が咲きました のメロディー ───
SR = 44100

def tone(freq, dur, vol=0.35):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, False)
    wave = np.sin(2 * np.pi * freq * t)
    attack  = int(n * 0.05)
    release = int(n * 0.25)
    env = np.ones(n)
    env[:attack]    = np.linspace(0, 1, attack)
    env[n-release:] = np.linspace(1, 0, release)
    return (wave * env * vol * 32767).astype(np.int16)

def silence(dur):
    return np.zeros(int(SR * dur), dtype=np.int16)

def make_chant():
    # 무궁화 꽃이 피었습니다 の近似メロディー
    E4, G4, A4, D4 = 330, 392, 440, 294
    seq = [
        (E4, 0.18), (E4, 0.18), (G4, 0.32),   # 무-궁-화
        (E4, 0.18), (E4, 0.18), (G4, 0.32),   # 꽃-이-피
        (G4, 0.18), (A4, 0.18), (G4, 0.18), (E4, 0.32),  # 었-습-니-다
        (D4, 0.15), (E4, 0.50),
    ]
    parts = []
    for freq, dur in seq:
        parts.append(tone(freq, dur))
        parts.append(silence(0.04))
    mono   = np.concatenate(parts)
    stereo = np.column_stack([mono, mono])
    return pygame.sndarray.make_sound(stereo)

chant_sound = make_chant()
CHANT_LEN_MS = int(chant_sound.get_length() * 1000)

# ─── 画像読み込み ───
IMG_DIR = os.path.join(os.path.dirname(__file__), "images")

def load_img(name, size):
    path = os.path.join(IMG_DIR, name)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, size)
        except Exception:
            pass
    return None

doll_face_img = load_img("doll_face.jpg", (90, 90))

# ─── 人形描画 ───
def draw_doll(surface, x, y, turn_t):
    """
    turn_t: 0.0=後ろ向き  1.0=正面向き  (0〜1 でアニメ)
    x, y: 頭の中心
    """
    s = 1.0
    facing = turn_t > 0.5

    # ドレス（黄色台形）
    dress_pts = [
        (x - int(55*s), y + int(80*s)),
        (x + int(55*s), y + int(80*s)),
        (x + int(75*s), y + int(260*s)),
        (x - int(75*s), y + int(260*s)),
    ]
    pygame.draw.polygon(surface, YELLOW, dress_pts)
    pygame.draw.polygon(surface, (190, 160, 0), dress_pts, 2)

    # 首
    pygame.draw.rect(surface, SKIN, (x-12, y+62, 24, 22))

    # 頭・髪
    head_r  = 52
    head_cy = y + 50
    pygame.draw.circle(surface, SKIN,      (x, head_cy), head_r)
    pygame.draw.circle(surface, DARK_HAIR, (x, head_cy - 8), 48)

    if facing:
        # 正面顔（人形の顔画像 or 描画）
        if doll_face_img:
            fw = 84
            face = pygame.transform.smoothscale(doll_face_img, (fw, fw))
            surface.blit(face, (x - fw//2, head_cy - fw//2))
        else:
            pygame.draw.circle(surface, SKIN, (x, head_cy), 44)
            pygame.draw.circle(surface, BLACK, (x-14, head_cy-5), 7)
            pygame.draw.circle(surface, BLACK, (x+14, head_cy-5), 7)
            pygame.draw.arc(surface, RED_C,
                            (x-18, head_cy+12, 36, 16), math.pi, 0, 3)
        # 怖い眉
        pygame.draw.line(surface, DARK_HAIR, (x-30, head_cy-26), (x-12, head_cy-20), 3)
        pygame.draw.line(surface, DARK_HAIR, (x+30, head_cy-26), (x+12, head_cy-20), 3)
    else:
        # 後ろ向き：髪のみ
        pygame.draw.circle(surface, DARK_HAIR, (x, head_cy), 50)
        pygame.draw.circle(surface, DARK_HAIR, (x-33, head_cy+28), 16)
        pygame.draw.circle(surface, DARK_HAIR, (x+33, head_cy+28), 16)

    # 腕
    arm_y = y + 90
    pygame.draw.line(surface, SKIN, (x-55, arm_y), (x-82, arm_y+60), 10)
    pygame.draw.line(surface, SKIN, (x+55, arm_y), (x+82, arm_y+60), 10)

    # 足・靴
    leg_top = y + 255
    pygame.draw.rect(surface, SKIN, (x-30, leg_top, 24, 50))
    pygame.draw.rect(surface, SKIN, (x+ 6, leg_top, 24, 50))
    pygame.draw.ellipse(surface, BLACK, (x-38, leg_top+44, 38, 18))
    pygame.draw.ellipse(surface, BLACK, (x+ 0, leg_top+44, 38, 18))

# ─── 歩く人々（背景の参加者） ───
class Walker:
    def __init__(self, x, y, speed, number):
        self.x     = float(x)
        self.y     = float(y)
        self.speed = speed
        self.number = str(number)
        self.frame = float(x) / 30  # 位相ずらし

    def update(self, dt_ms, moving):
        if moving:
            self.x += self.speed * dt_ms / 1000
            self.frame += dt_ms / 110
        if self.x > W + 60:
            self.x = -60

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        swing = math.sin(self.frame) * 10
        pygame.draw.rect(surface, JUMPSUIT, (x-10, y-24, 20, 30))
        pygame.draw.circle(surface, SKIN, (x, y-34), 12)
        num = font_sm.render(self.number, True, WHITE)
        surface.blit(num, (x - num.get_width()//2, y-20))
        pygame.draw.line(surface, DARK_GREY, (x-5, y+6), (x-5+int(swing), y+26), 5)
        pygame.draw.line(surface, DARK_GREY, (x+5, y+6), (x+5-int(swing), y+26), 5)

walkers = [
    Walker( 80, 500, 90,  1),
    Walker(200, 510, 70,  2),
    Walker(330, 495, 110, 3),
    Walker(470, 505, 80,  4),
    Walker(600, 500, 95,  5),
    Walker(720, 510, 75,  6),
]

# ─── 背景描画 ───
def draw_bg():
    screen.fill(SKY)
    for cx, cy, r, c in [
        (150, 560, 190, (70, 150, 70)),
        (480, 575, 170, (65, 145, 65)),
        (820, 565, 210, (75, 155, 75)),
    ]:
        pygame.draw.circle(screen, c, (cx, cy), r)
    pygame.draw.rect(screen, GRASS, (0, 510, W, 90))
    pygame.draw.rect(screen, (45, 125, 45), (0, 525, W, 75))

# ─── 状態定数 ───
ST_GREEN = 0   # 進め（後ろ向き） 4秒
ST_TURN  = 1   # 振り返りアニメ  0.6秒
ST_RED   = 2   # 止まれ（正面向き）2.5秒

GREEN_DUR = 4000   # ms
TURN_DUR  =  600
RED_DUR   = 2500

state      = ST_GREEN
timer      = 0
turn_t     = 0.0   # 0=後ろ 1=正面
pulse      = 0.0   # ラベルの点滅用

# ─── メインループ ───
while True:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()

    # ── 状態更新 ──
    timer += dt
    pulse = (pulse + dt / 500) % (2 * math.pi)

    if state == ST_GREEN:
        turn_t = 0.0
        if timer >= GREEN_DUR:
            state = ST_TURN
            timer = 0
            chant_sound.play()

    elif state == ST_TURN:
        turn_t = min(1.0, timer / TURN_DUR)
        if timer >= TURN_DUR:
            state = ST_RED
            timer = 0

    elif state == ST_RED:
        turn_t = 1.0
        if timer >= RED_DUR:
            state = ST_GREEN
            timer = 0

    moving = (state == ST_GREEN)

    # ── 描画 ──
    draw_bg()

    # 歩く参加者
    for w in walkers:
        w.update(dt, moving)
        w.draw(screen)

    # 人形（中央奥）
    draw_doll(screen, W // 2, 140, turn_t)

    # ── 状態パネル ──
    if state == ST_GREEN:
        label     = "🟢  진めー！  進め！"
        label_col = GREEN_C
        sub       = "むくげの花が咲きました"
    elif state == ST_TURN:
        label     = "⚠️  振り返り中…"
        label_col = YELLOW
        sub       = "무궁화 꽃이 피었습니다♪"
    else:
        alpha     = int(abs(math.sin(pulse)) * 200 + 55)
        label     = "🔴  止まれ！  止まれ！"
        label_col = (255, max(0, int(55 - abs(math.sin(pulse))*55)), 0)
        sub       = "동작 그만！  動くな！"

    # パネル背景
    panel = pygame.Surface((W, 80), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 140))
    screen.blit(panel, (0, H - 80))

    lbl = font_lg.render(label, True, label_col)
    screen.blit(lbl, (W//2 - lbl.get_width()//2, H - 72))
    sub_t = font_sm.render(sub, True, (220, 220, 220))
    screen.blit(sub_t, (W//2 - sub_t.get_width()//2, H - 24))

    # ESCヒント
    screen.blit(font_sm.render("ESC で終了", True, (180, 180, 180)), (10, 10))

    pygame.display.flip()


import pygame
import sys
import random
import math
import numpy as np
import os

# ─────────────────────────────────────────
#  初期化
# ─────────────────────────────────────────
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()

W, H = 1100, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("무궁화 꽃이 피었습니다")
clock = pygame.time.Clock()

# ─────────────────────────────────────────
#  色定数
# ─────────────────────────────────────────
SKY       = (180, 220, 255)
GRASS     = ( 60, 160,  60)
GRASS2    = ( 45, 130,  45)
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED_C     = (220,  30,  30)
GREEN_C   = ( 30, 200,  60)
YELLOW    = (255, 220,   0)
SKIN      = (255, 210, 160)
DARK_HAIR = ( 40,  20,  10)
JUMPSUIT  = (  0, 180,  80)
DARK_GREY = ( 80,  80,  80)

# ─────────────────────────────────────────
#  フォント
# ─────────────────────────────────────────
def get_font(size):
    for name in ["Malgun Gothic", "BIZ UDGothic", "Meiryo", "Yu Gothic", "Arial"]:
        try:
            f = pygame.font.SysFont(name, size)
            return f
        except Exception:
            pass
    return pygame.font.Font(None, size)

font_sm = get_font(22)
font_md = get_font(32)
font_lg = get_font(48)
font_xl = get_font(80)

# ─────────────────────────────────────────
#  音声合成：무궁화 꽃이 피었습니다 のメロディー
# ─────────────────────────────────────────
SR = 44100

def tone(freq, dur, vol=0.35):
    n = int(SR * dur)
    t = np.linspace(0, dur, n, False)
    wave = np.sin(2 * np.pi * freq * t)
    attack  = int(n * 0.05)
    release = int(n * 0.25)
    env = np.ones(n)
    env[:attack]     = np.linspace(0, 1, attack)
    env[n-release:]  = np.linspace(1, 0, release)
    return (wave * env * vol * 32767).astype(np.int16)

def silence(dur):
    return np.zeros(int(SR * dur), dtype=np.int16)

def make_chant():
    E4, G4, A4, D4 = 330, 392, 440, 294
    seq = [
        (E4, 0.18), (E4, 0.18), (G4, 0.32),
        (E4, 0.18), (E4, 0.18), (G4, 0.32),
        (G4, 0.18), (A4, 0.18), (G4, 0.18), (E4, 0.32),
        (D4, 0.15), (E4, 0.50),
    ]
    parts = []
    for freq, dur in seq:
        parts.append(tone(freq, dur))
        parts.append(silence(0.04))
    mono = np.concatenate(parts)
    stereo = np.column_stack([mono, mono])
    return pygame.sndarray.make_sound(stereo)

chant_sound = make_chant()

# ─────────────────────────────────────────
#  画像読み込み
# ─────────────────────────────────────────
IMG_DIR = os.path.join(os.path.dirname(__file__), "images")

def load_img(name, size):
    path = os.path.join(IMG_DIR, name)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, size)
        except Exception:
            pass
    return None

doll_face_img = load_img("doll_face.jpg", (90, 90))

# ─────────────────────────────────────────
#  人形（ヨンヒ）描画
# ─────────────────────────────────────────
def draw_doll(surface, x, y, facing_front, scale=1.0):
    s = scale
    # ドレス（黄色）
    dress_pts = [
        (x - int(55*s), y + int(80*s)),
        (x + int(55*s), y + int(80*s)),
        (x + int(75*s), y + int(260*s)),
        (x - int(75*s), y + int(260*s)),
    ]
    pygame.draw.polygon(surface, YELLOW, dress_pts)
    pygame.draw.polygon(surface, (200, 170, 0), dress_pts, 2)

    # 首
    pygame.draw.rect(surface, SKIN,
                     (x - int(12*s), y + int(60*s), int(24*s), int(25*s)))

    # 頭
    head_r  = int(52 * s)
    head_cy = y + int(50 * s)
    pygame.draw.circle(surface, SKIN, (x, head_cy), head_r)
    pygame.draw.circle(surface, DARK_HAIR, (x, head_cy - int(8*s)), int(48*s))

    if facing_front:
        if doll_face_img:
            fw = int(84 * s)
            face = pygame.transform.smoothscale(doll_face_img, (fw, fw))
            surface.blit(face, (x - fw//2, head_cy - fw//2))
        else:
            pygame.draw.circle(surface, SKIN, (x, head_cy), int(44*s))
            pygame.draw.circle(surface, BLACK, (x - int(14*s), head_cy - int(5*s)), int(7*s))
            pygame.draw.circle(surface, BLACK, (x + int(14*s), head_cy - int(5*s)), int(7*s))
            pygame.draw.arc(surface, RED_C,
                            (x - int(18*s), head_cy + int(12*s), int(36*s), int(16*s)),
                            math.pi, 0, 3)
        # 眉（怖い）
        pygame.draw.line(surface, DARK_HAIR,
                         (x - int(30*s), head_cy - int(26*s)),
                         (x - int(12*s), head_cy - int(20*s)), int(3*s))
        pygame.draw.line(surface, DARK_HAIR,
                         (x + int(30*s), head_cy - int(26*s)),
                         (x + int(12*s), head_cy - int(20*s)), int(3*s))
    else:
        pygame.draw.circle(surface, DARK_HAIR, (x, head_cy), int(50*s))
        pygame.draw.circle(surface, DARK_HAIR, (x - int(33*s), head_cy + int(28*s)), int(16*s))
        pygame.draw.circle(surface, DARK_HAIR, (x + int(33*s), head_cy + int(28*s)), int(16*s))

    # 腕
    arm_y = y + int(90 * s)
    pygame.draw.line(surface, SKIN,
                     (x - int(55*s), arm_y), (x - int(82*s), arm_y + int(60*s)), int(10*s))
    pygame.draw.line(surface, SKIN,
                     (x + int(55*s), arm_y), (x + int(82*s), arm_y + int(60*s)), int(10*s))

    # 足・靴
    leg_top = y + int(255 * s)
    pygame.draw.rect(surface, SKIN, (x - int(30*s), leg_top, int(24*s), int(50*s)))
    pygame.draw.rect(surface, SKIN, (x + int( 6*s), leg_top, int(24*s), int(50*s)))
    pygame.draw.ellipse(surface, BLACK, (x - int(38*s), leg_top + int(44*s), int(38*s), int(18*s)))
    pygame.draw.ellipse(surface, BLACK, (x + int( 0*s), leg_top + int(44*s), int(38*s), int(18*s)))

# ─────────────────────────────────────────
#  プレイヤー
# ─────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        self.x    = float(x)
        self.y    = float(y)
        self.alive = True
        self.won   = False
        self.wframe = 0.0

    def update(self, dt_ms, is_red):
        if not self.alive or self.won:
            return
        keys = pygame.key.get_pressed()
        moving = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        if moving:
            self.x += 220 * dt_ms / 1000
            self.wframe += dt_ms / 110
            if is_red:
                self.alive = False

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        if not self.alive:
            pygame.draw.line(surface, RED_C, (x-18, y-18), (x+18, y+18), 4)
            pygame.draw.line(surface, RED_C, (x+18, y-18), (x-18, y+18), 4)
            t = font_sm.render("DEAD", True, RED_C)
            surface.blit(t, (x - t.get_width()//2, y + 22))
            return
        swing = math.sin(self.wframe) * 12
        # ジャンプスーツ
        pygame.draw.rect(surface, JUMPSUIT, (x-12, y-28, 24, 36))
        # 頭
        pygame.draw.circle(surface, SKIN, (x, y-40), 14)
        # 番号
        num = font_sm.render("456", True, WHITE)
        surface.blit(num, (x - num.get_width()//2, y-22))
        # 足
        pygame.draw.line(surface, DARK_GREY, (x-6, y+8), (x-6+int(swing), y+32), 6)
        pygame.draw.line(surface, DARK_GREY, (x+6, y+8), (x+6-int(swing), y+32), 6)

# ─────────────────────────────────────────
#  背景
# ─────────────────────────────────────────
def draw_bg(goal_x):
    screen.fill(SKY)
    for cx, cy, r, c in [(200,560,200,(80,160,80)), (500,580,180,(70,150,70)), (900,570,220,(85,165,85))]:
        pygame.draw.circle(screen, c, (cx, cy), r)
    pygame.draw.rect(screen, GRASS,  (0, 515, W, 135))
    pygame.draw.rect(screen, GRASS2, (0, 530, W, 120))
    pygame.draw.line(screen, WHITE, (goal_x, 0), (goal_x, H), 3)

# ─────────────────────────────────────────
#  オーバーレイ
# ─────────────────────────────────────────
def draw_overlay(text, sub, color):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 170))
    screen.blit(ov, (0, 0))
    t1 = font_xl.render(text, True, color)
    t2 = font_md.render(sub,  True, WHITE)
    screen.blit(t1, (W//2 - t1.get_width()//2, H//2 - 70))
    screen.blit(t2, (W//2 - t2.get_width()//2, H//2 + 30))

# ─────────────────────────────────────────
#  定数
# ─────────────────────────────────────────
GREEN_MIN    = 3000
GREEN_MAX    = 7000
RED_DURATION = 3200
GOAL_X       = W - 200
START_X      = 80

ST_GREEN = 0
ST_RED   = 1
ST_DEAD  = 2
ST_WIN   = 3

# ─────────────────────────────────────────
#  ゲームループ
# ─────────────────────────────────────────
def run_game():
    player    = Player(START_X, 490)
    state     = ST_GREEN
    timer     = 0
    green_dur = random.randint(GREEN_MIN, GREEN_MAX)
    doll_anim = 0.0  # 0=後ろ 1=正面

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r and state in (ST_DEAD, ST_WIN):
                    run_game(); return

        # ── 状態機械 ──
        if state == ST_GREEN:
            timer += dt
            player.update(dt, is_red=False)
            doll_anim = max(0.0, doll_anim - dt / 300)
            if player.x >= GOAL_X:
                state = ST_WIN
            elif timer >= green_dur:
                state = ST_RED
                timer = 0
                chant_sound.play()

        elif state == ST_RED:
            timer += dt
            player.update(dt, is_red=True)
            doll_anim = min(1.0, doll_anim + dt / 300)
            if not player.alive:
                state = ST_DEAD
            elif timer >= RED_DURATION:
                state     = ST_GREEN
                timer     = 0
                green_dur = random.randint(GREEN_MIN, GREEN_MAX)

        # ── 描画 ──
        is_red = (state == ST_RED)
        draw_bg(GOAL_X)

        # 人形
        draw_doll(screen, GOAL_X + 80, 230, facing_front=(doll_anim > 0.5))

        # プレイヤー
        player.draw(screen)

        # 進捗バー
        prog = max(0.0, min(1.0, (player.x - START_X) / (GOAL_X - START_X)))
        bar_w = 400
        pygame.draw.rect(screen, (80,80,80), (50, 18, bar_w, 20), border_radius=6)
        if prog > 0:
            pygame.draw.rect(screen, (GREEN_C if not is_red else RED_C),
                             (50, 18, int(bar_w*prog), 20), border_radius=6)
        pygame.draw.rect(screen, WHITE, (50, 18, bar_w, 20), 2, border_radius=6)
        screen.blit(font_sm.render(f"{int(prog*100)}%", True, WHITE), (460, 19))

        # カウントダウン（赤中）
        if is_red:
            remain = max(0, (RED_DURATION - timer) / 1000)
            screen.blit(font_md.render(f"⏱ {remain:.1f}s", True, YELLOW), (W-160, 18))

        # 信号ラベル
        if is_red:
            sig = font_lg.render("🔴 무궁화 꽃이 피었습니다！", True, RED_C)
        else:
            sig = font_lg.render("🟢 GREEN LIGHT  →  進め！", True, GREEN_C)
        screen.blit(sig, (W//2 - sig.get_width()//2, 560))

        # 操作ヒント
        screen.blit(font_sm.render("→ / D キーで移動    R:リスタート    ESC:終了", True, (220,220,220)),
                    (50, H-28))

        # 結果
        if state == ST_WIN:
            draw_overlay("통과！  WIN！", "Rキーでリスタート", GREEN_C)
        elif state == ST_DEAD:
            draw_overlay("탈락！  DEAD", "Rキーでリスタート", RED_C)

        pygame.display.flip()

if __name__ == "__main__":
    run_game()

