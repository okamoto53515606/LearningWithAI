import pygame
import sys
import math
import asyncio
import os
from claude_draw import draw_claude

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("なにかな？クイズ！")

# フォント（web版: font.ttf を優先）
font_path = "font.ttf"
if not os.path.exists(font_path):
    for p in ["C:/Windows/Fonts/msgothic.ttc", "C:/Windows/Fonts/meiryo.ttc"]:
        if os.path.exists(p):
            font_path = p
            break

font_big   = pygame.font.Font(font_path, 52)
font_mid   = pygame.font.Font(font_path, 36)
font_small = pygame.font.Font(font_path, 28)
font_tiny  = pygame.font.Font(font_path, 20)

# 色
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
BG     = (255, 248, 220)
RED    = (220, 60, 60)
GREEN  = (60, 180, 80)
BLUE   = (60, 120, 220)
YELLOW = (255, 210, 0)
ORANGE = (255, 140, 0)
GRAY   = (180, 180, 180)
PINK   = (255, 182, 193)
PURPLE = (150, 80, 200)
BROWN  = (139, 90, 43)
LIGHT_BLUE = (173, 216, 230)

# サウンドなし（web版）
sound_correct = None
sound_wrong   = None

# ─────────── 画像描画関数 ───────────

def draw_train_handkerchief(surf, cx, cy, size=180):
    s = size
    hx, hy = cx - s//2, cy - s//2
    pygame.draw.rect(surf, WHITE, (hx, hy, s, s), border_radius=10)
    pygame.draw.rect(surf, (180, 180, 220), (hx, hy, s, s), 4, border_radius=10)
    pygame.draw.line(surf, (200, 200, 230), (hx+10, hy+10), (hx+s-10, hy+10), 2)
    tw = int(s * 0.7)
    th = int(s * 0.28)
    tx = cx - tw//2
    ty = cy - th//2 + 10
    pygame.draw.rect(surf, (80, 130, 200), (tx, ty, tw, th), border_radius=8)
    ww, wh = int(tw*0.16), int(th*0.45)
    for i in range(3):
        wx = tx + int(tw*0.1) + i * int(tw*0.28)
        wy = ty + int(th*0.15)
        pygame.draw.rect(surf, LIGHT_BLUE, (wx, wy, ww, wh), border_radius=3)
        pygame.draw.rect(surf, BLACK, (wx, wy, ww, wh), 2, border_radius=3)
    for i in range(2):
        wx = tx + int(tw*0.18) + i * int(tw*0.52)
        pygame.draw.circle(surf, BLACK, (wx, ty+th+5), 10)
        pygame.draw.circle(surf, GRAY, (wx, ty+th+5), 6)

def draw_kirby(surf, cx, cy, size=150):
    r = size // 2
    pygame.draw.circle(surf, PINK, (cx, cy), r)
    pygame.draw.circle(surf, (200, 100, 130), (cx, cy), r, 3)
    for dx in [-r//3, r//3]:
        pygame.draw.ellipse(surf, BLACK, (cx+dx-10, cy-r//4-8, 20, 24))
        pygame.draw.circle(surf, WHITE, (cx+dx-3, cy-r//4-2), 5)
    for dx in [-r//2, r//2]:
        pygame.draw.circle(surf, (255, 120, 120), (cx+dx, cy+r//6), r//5)
    pygame.draw.arc(surf, RED, (cx-12, cy+r//6, 24, 14), math.pi, 0, 3)
    for dx in [-r//3, r//3]:
        pygame.draw.ellipse(surf, (200, 80, 100), (cx+dx-14, cy+r-16, 28, 20))

def draw_timer_30(surf, cx, cy, size=160):
    r = size // 2
    pygame.draw.circle(surf, WHITE, (cx, cy), r)
    pygame.draw.circle(surf, BLACK, (cx, cy), r, 5)
    for i in range(60):
        angle = math.radians(i * 6 - 90)
        if i % 5 == 0:
            r1, r2, w = r - 22, r - 4, 3
        else:
            r1, r2, w = r - 14, r - 4, 1
        x1 = cx + int(r1 * math.cos(angle))
        y1 = cy + int(r1 * math.sin(angle))
        x2 = cx + int(r2 * math.cos(angle))
        y2 = cy + int(r2 * math.sin(angle))
        pygame.draw.line(surf, BLACK, (x1, y1), (x2, y2), w)
    for num, angle_deg in [(12, -90), (3, 0), (6, 90), (9, 180)]:
        angle = math.radians(angle_deg)
        nx = cx + int((r - 38) * math.cos(angle))
        ny = cy + int((r - 38) * math.sin(angle))
        t = font_small.render(str(num), True, BLACK)
        surf.blit(t, (nx - t.get_width()//2, ny - t.get_height()//2))
    pygame.draw.line(surf, BLACK, (cx, cy), (cx, cy - int(r*0.72)), 5)
    pygame.draw.line(surf, RED, (cx, cy), (cx, cy + int(r*0.52)), 6)
    pygame.draw.circle(surf, BLACK, (cx, cy), 8)
    pygame.draw.circle(surf, RED, (cx, cy), 5)
    pygame.draw.rect(surf, (100, 100, 100), (cx-8, cy-r-14, 16, 18), border_radius=4)

def draw_ring(surf, cx, cy, size=150):
    r = size // 2
    bw, bh = r, r // 2
    pygame.draw.ellipse(surf, YELLOW, (cx - bw, cy - bh//2, bw*2, bh), 0)
    pygame.draw.ellipse(surf, (255, 240, 100), (cx - bw + 6, cy - bh//2 + 4, bw*2 - 12, bh - 8), 0)
    pygame.draw.rect(surf, YELLOW, (cx-20, cy-bh//2-18, 40, 22), border_radius=4)
    pts = [(cx, cy-bh//2-36), (cx+18, cy-bh//2-20), (cx, cy-bh//2-4), (cx-18, cy-bh//2-20)]
    pygame.draw.polygon(surf, (100, 200, 255), pts)
    pygame.draw.polygon(surf, (60, 160, 220), pts, 3)
    pygame.draw.line(surf, WHITE, (cx-6, cy-bh//2-30), (cx+6, cy-bh//2-22), 3)
    pygame.draw.ellipse(surf, ORANGE, (cx - bw, cy - bh//2, bw*2, bh), 4)

def draw_stamp(surf, cx, cy, size=160):
    sw, sh = int(size * 0.8), size
    sx, sy = cx - sw//2, cy - sh//2
    notch = 12
    pygame.draw.rect(surf, WHITE, (sx, sy, sw, sh))
    for i in range(0, sw, notch):
        pygame.draw.circle(surf, BG, (sx + i + notch//2, sy), notch//2 + 1)
        pygame.draw.circle(surf, BG, (sx + i + notch//2, sy + sh), notch//2 + 1)
    for i in range(0, sh, notch):
        pygame.draw.circle(surf, BG, (sx, sy + i + notch//2), notch//2 + 1)
        pygame.draw.circle(surf, BG, (sx + sw, sy + i + notch//2), notch//2 + 1)
    inner = 12
    pygame.draw.rect(surf, RED, (sx+inner, sy+inner, sw-inner*2, sh-inner*2), 3)
    fmx = cx
    fbase_y = sy + sh - inner - 20
    ftop_y = sy + inner + 18
    fpts = [(fmx, ftop_y), (fmx - 45, fbase_y), (fmx + 45, fbase_y)]
    pygame.draw.polygon(surf, (100, 140, 200), fpts)
    spts = [(fmx, ftop_y), (fmx - 16, ftop_y + 22), (fmx + 16, ftop_y + 22)]
    pygame.draw.polygon(surf, WHITE, spts)
    val = font_small.render("84", True, RED)
    surf.blit(val, (cx - val.get_width()//2, sy + sh - inner - 26))

# ─────────── もんだいデータ ───────────

QUESTIONS = [
    {
        "draw": draw_train_handkerchief,
        "question": "これはなんでしょう？",
        "choices": ["ふろしき", "でんしゃのハンカチ", "タオル"],
        "answer": 1,
    },
    {
        "draw": draw_kirby,
        "question": "このキャラクターはだれ？",
        "choices": ["マリオ", "カービィ", "プーさん"],
        "answer": 1,
    },
    {
        "draw": draw_timer_30,
        "question": "このとけいはなんぷん？",
        "choices": ["15ふん", "30ふん", "60ふん"],
        "answer": 1,
    },
    {
        "draw": draw_ring,
        "question": "これはなんでしょう？",
        "choices": ["ゆびわ", "ネックレス", "おもちゃ"],
        "answer": 0,
    },
    {
        "draw": draw_stamp,
        "question": "これはなんでしょう？",
        "choices": ["シール", "きって", "カード"],
        "answer": 1,
    },
    {
        "draw": None,
        "question": "カレンダーで日にちが\nいちばん すくない月は\n何日でしょう？",
        "choices": ["28にち", "30にち", "31にち"],
        "answer": 0,
    },
    {
        "draw": None,
        "question": "マリオのぼうしに\nかかれている\nもじはなに？",
        "choices": ["A", "M", "N"],
        "answer": 1,
    },
    {
        "draw": None,
        "question": "ゴミばこは\nなにいろが\nおおいでしょう？",
        "choices": ["あか", "みどり", "しろ"],
        "answer": 1,
    },
    {
        "draw": None,
        "question": "マリオは\n何さいでしょう？",
        "choices": ["16さい", "24さい", "35さい"],
        "answer": 1,
    },
    {
        "draw": None,
        "question": "むかしの\nゲームで一番\nすごいといわれたゲームは？",
        "choices": ["テトリス", "パックマン", "マリオブラザーズ"],
        "answer": 2,
    },
]

# ─────────── ボタン ───────────

def draw_button(surf, rect, text, color, hover=False):
    col = tuple(min(255, c + 30) for c in color) if hover else color
    pygame.draw.rect(surf, col, rect, border_radius=14)
    pygame.draw.rect(surf, BLACK, rect, 3, border_radius=14)
    t = font_mid.render(text, True, WHITE)
    if t.get_width() > rect[2] - 10:
        t = font_small.render(text, True, WHITE)
    if t.get_width() > rect[2] - 10:
        t = font_tiny.render(text, True, WHITE)
    surf.blit(t, (rect[0] + rect[2]//2 - t.get_width()//2,
                   rect[1] + rect[3]//2 - t.get_height()//2))

CHOICE_COLORS = [(60, 140, 220), (60, 180, 100), (220, 140, 40)]

# ─────────── フィードバック ───────────

async def show_feedback(correct):
    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 1200:
        screen.fill(BG)
        if correct:
            col, msg = GREEN, "せいかい！！"
            pygame.draw.circle(screen, col, (WIDTH//2, HEIGHT//2), 100, 16)
        else:
            col, msg = RED, "ちがったよ…"
            pygame.draw.line(screen, col, (WIDTH//2-80, HEIGHT//2-80), (WIDTH//2+80, HEIGHT//2+80), 18)
            pygame.draw.line(screen, col, (WIDTH//2+80, HEIGHT//2-80), (WIDTH//2-80, HEIGHT//2+80), 18)
        t = font_big.render(msg, True, col)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 + 120))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        clock.tick(60)
        await asyncio.sleep(0)

# ─────────── タイトル画面 ───────────

async def title_screen():
    clock = pygame.time.Clock()
    btn_new = pygame.Rect(WIDTH//2 - 180, 380, 360, 64)
    while True:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)
        t1 = font_big.render("なにかな？クイズ！", True, ORANGE)
        screen.blit(t1, (WIDTH//2 - t1.get_width()//2, 120))
        t2 = font_small.render("え を みて こたえよう！", True, BROWN)
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, 220))
        t3 = font_small.render(f"ぜんぶで {len(QUESTIONS)} もん", True, BROWN)
        screen.blit(t3, (WIDTH//2 - t3.get_width()//2, 270))
        draw_button(screen, btn_new, "はじめる！", BLUE, btn_new.collidepoint(mx, my))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_new.collidepoint(mx, my):
                    return
        clock.tick(60)
        await asyncio.sleep(0)

# ─────────── クリア画面 ───────────

async def clear_screen(score):
    clock = pygame.time.Clock()
    btn = pygame.Rect(WIDTH//2 - 160, 490, 320, 60)
    t_start = pygame.time.get_ticks()
    while True:
        mx, my = pygame.mouse.get_pos()
        elapsed = (pygame.time.get_ticks() - t_start) / 1000.0
        screen.fill(BG)
        for i in range(8):
            angle = elapsed * 1.5 + i * math.pi / 4
            sx = int(WIDTH//2 + math.cos(angle) * 180)
            sy = int(HEIGHT//2 - 80 + math.sin(angle) * 60)
            pygame.draw.circle(screen, YELLOW, (sx, sy), 10)
        # くろーどちゃん（右下）
        draw_claude(screen, 690, 430, scale=0.2, t=elapsed)
        t1 = font_big.render("おつかれさま！", True, ORANGE)
        screen.blit(t1, (WIDTH//2 - t1.get_width()//2, 80))
        t2 = font_big.render(f"{score} / {len(QUESTIONS)} もんせいかい！", True, GREEN if score >= 4 else BLUE)
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, 180))
        msg = "すごい！！かんぺき！" if score == len(QUESTIONS) else "よくできました！" if score >= 3 else "またちょうせんしてね！"
        t3 = font_mid.render(msg, True, BROWN)
        screen.blit(t3, (WIDTH//2 - t3.get_width()//2, 280))
        msg2 = "くろーどちゃんも うれしいよ！" if score == len(QUESTIONS) else "また いっしょにあそぼうね！"
        t4 = font_small.render(msg2, True, PURPLE)
        screen.blit(t4, (WIDTH//2 - t4.get_width()//2, 370))
        draw_button(screen, btn, "もういちどあそぶ", BLUE, btn.collidepoint(mx, my))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn.collidepoint(mx, my):
                    return
        clock.tick(60)
        await asyncio.sleep(0)

# ─────────── メインゲームループ ───────────

async def game_loop():
    clock = pygame.time.Clock()
    current_q = 0
    score = 0
    selected = None
    answered = False

    while current_q < len(QUESTIONS):
        q = QUESTIONS[current_q]
        mx, my = pygame.mouse.get_pos()
        bw, bh = 240, 60
        total_w = bw * 3 + 16 * 2
        start_x = WIDTH//2 - total_w//2
        btn_y = 450 if q["draw"] is not None else 390
        btn_rects = [pygame.Rect(start_x + i*(bw+16), btn_y, bw, bh) for i in range(3)]
        next_btn = pygame.Rect(WIDTH//2 - 140, btn_y + 80, 280, 52)

        screen.fill(BG)
        t_num = font_small.render(f"{current_q+1} / {len(QUESTIONS)} もん", True, BROWN)
        screen.blit(t_num, (30, 20))
        t_sc = font_small.render(f"せいかい: {score}", True, GREEN)
        screen.blit(t_sc, (WIDTH - t_sc.get_width() - 30, 20))
        if q["draw"] is not None:
            q["draw"](screen, WIDTH//2, 200, 170)
            q_y = 360
        else:
            q_y = 120
        lines = q["question"].split("\n")
        for li, line in enumerate(lines):
            t_q = font_mid.render(line, True, BLACK)
            screen.blit(t_q, (WIDTH//2 - t_q.get_width()//2, q_y + li * 48))
        for i, (rect, choice) in enumerate(zip(btn_rects, q["choices"])):
            hover = rect.collidepoint(mx, my) and not answered
            col = CHOICE_COLORS[i]
            if answered:
                if i == q["answer"]:
                    col = GREEN
                elif i == selected:
                    col = RED
                else:
                    col = GRAY
            draw_button(screen, rect, choice, col, hover)
        if answered:
            draw_button(screen, next_btn, "つぎへ →", ORANGE, next_btn.collidepoint(mx, my))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not answered:
                    for i, rect in enumerate(btn_rects):
                        if rect.collidepoint(mx, my):
                            selected = i
                            answered = True
                            correct = (i == q["answer"])
                            if correct:
                                score += 1
                            await show_feedback(correct)
                elif next_btn.collidepoint(mx, my):
                    current_q += 1
                    selected = None
                    answered = False
        clock.tick(60)
        await asyncio.sleep(0)

    await clear_screen(score)

# ─────────── エントリポイント ───────────

async def main():
    while True:
        await title_screen()
        await game_loop()

asyncio.run(main())
