import pygame
import sys
import math
import random
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# 画面設定
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("まちがいさがし！")

# 色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
LIGHT_BLUE = (200, 220, 255)
YELLOW = (255, 255, 0)
PINK = (255, 180, 200)

# フォント
font_big = pygame.font.SysFont("yugothicuisemibold", 40)
font_huge = pygame.font.SysFont("yugothicuisemibold", 80)
font_medium = pygame.font.SysFont("yugothicuisemibold", 30)
font_small = pygame.font.SysFont("yugothicuisemibold", 24)

# 効果音を生成
def make_pinpon_sound():
    """ピンポーン音を作る"""
    sr = 44100
    duration = 0.6
    t = np.linspace(0, duration, int(sr * duration), False)
    # 高い音2つ（ピンポン）
    tone1 = np.sin(2 * np.pi * 880 * t) * 0.4
    tone2 = np.sin(2 * np.pi * 1100 * t) * 0.4
    # 前半はピン、後半はポン
    half = len(t) // 2
    sound = np.zeros_like(t)
    sound[:half] = tone1[:half]
    sound[half:] = tone2[half:]
    # フェードアウト
    fade = np.linspace(1, 0, len(t))
    sound = sound * fade
    sound = (sound * 32767).astype(np.int16)
    stereo = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo)

def make_buzzer_sound():
    """ブッブー音を作る"""
    sr = 44100
    duration = 0.6
    t = np.linspace(0, duration, int(sr * duration), False)
    # 低い音（ブッブー）
    tone = np.sin(2 * np.pi * 200 * t) * 0.4
    # ブッ・ブー（途中で区切る）
    third = len(t) // 3
    sound = np.zeros_like(t)
    sound[:third] = tone[:third]
    sound[third:third+int(sr*0.05)] = 0  # 隙間
    sound[third+int(sr*0.05):] = tone[third+int(sr*0.05):]
    # フェードアウト
    fade = np.linspace(1, 0, len(t))
    sound = sound * fade
    sound = (sound * 32767).astype(np.int16)
    stereo = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo)

sound_pinpon = make_pinpon_sound()
sound_buzzer = make_buzzer_sound()

# ゲーム状態
lives = 3
current_question = 0
score = 0
message = ""
message_timer = 0
game_over = False
game_clear = False

# ワンワンを描く関数（くさりの大きさ・歯の大きさを変えられる）
def draw_chain_chomp(surface, x, y, chain_sizes=None, scale=1.0, tooth_scale=1.0):
    """
    ワンワンを描く
    chain_sizes: くさりの各リンクの大きさ [link1, link2, link3, link4]
    """
    if chain_sizes is None:
        chain_sizes = [12, 12, 12, 12]  # デフォルト

    # くさり（左から右へ）
    chain_start_x = x - 80 * scale
    chain_y = y + 30 * scale
    for i, size in enumerate(chain_sizes):
        link_x = chain_start_x + i * 25 * scale
        link_size = int(size * scale)
        # くさりのリンク（しかく）
        rect = pygame.Rect(
            int(link_x - link_size),
            int(chain_y - link_size),
            int(link_size * 2),
            int(link_size * 2)
        )
        pygame.draw.rect(surface, DARK_GRAY, rect, 0, border_radius=3)
        pygame.draw.rect(surface, GRAY, rect, 2, border_radius=3)

    # くい（地面にささってる棒）
    stake_x = int(chain_start_x - 15 * scale)
    stake_y = int(chain_y - 20 * scale)
    pygame.draw.rect(surface, GRAY, (stake_x, stake_y, int(12 * scale), int(50 * scale)))
    pygame.draw.polygon(surface, GRAY, [
        (stake_x, stake_y),
        (stake_x + int(6 * scale), stake_y - int(15 * scale)),
        (stake_x + int(12 * scale), stake_y)
    ])

    # からだ（大きい黒い丸）
    body_x = int(x + 20 * scale)
    body_y = int(y)
    body_r = int(55 * scale)
    pygame.draw.circle(surface, BLACK, (body_x, body_y), body_r)

    # ひかり（左上の白い丸）
    highlight_x = int(body_x - 20 * scale)
    highlight_y = int(body_y - 25 * scale)
    pygame.draw.circle(surface, WHITE, (highlight_x, highlight_y), int(12 * scale))

    # 目（白い丸 + 黒い丸）
    eye_l_x = int(body_x - 12 * scale)
    eye_r_x = int(body_x + 15 * scale)
    eye_y = int(body_y - 10 * scale)
    # 白目
    pygame.draw.circle(surface, WHITE, (eye_l_x, eye_y), int(14 * scale))
    pygame.draw.circle(surface, WHITE, (eye_r_x, eye_y), int(14 * scale))
    # 黒目
    pygame.draw.circle(surface, BLACK, (eye_l_x + int(3 * scale), eye_y), int(6 * scale))
    pygame.draw.circle(surface, BLACK, (eye_r_x + int(3 * scale), eye_y), int(6 * scale))

    # 口（大きく開いた口）
    mouth_x = int(body_x + 10 * scale)
    mouth_y = int(body_y + 15 * scale)
    # 口の中（赤）
    pygame.draw.ellipse(surface, RED, (
        mouth_x - int(30 * scale), mouth_y - int(12 * scale),
        int(50 * scale), int(30 * scale)
    ))
    # 歯（上）
    for i in range(4):
        tooth_x = mouth_x - int(25 * scale) + i * int(14 * scale)
        tw = int(7 * scale * tooth_scale)
        th = int(12 * scale * tooth_scale)
        pygame.draw.polygon(surface, WHITE, [
            (tooth_x, mouth_y - int(12 * scale)),
            (tooth_x + tw, mouth_y - int(12 * scale)),
            (tooth_x + int(3 * scale), mouth_y - int(12 * scale) + th)
        ])
    # 歯（下）
    for i in range(3):
        tooth_x = mouth_x - int(18 * scale) + i * int(14 * scale)
        tw = int(7 * scale * tooth_scale)
        th = int(13 * scale * tooth_scale)
        pygame.draw.polygon(surface, WHITE, [
            (tooth_x, mouth_y + int(18 * scale)),
            (tooth_x + tw, mouth_y + int(18 * scale)),
            (tooth_x + int(3 * scale), mouth_y + int(18 * scale) - th)
        ])


# キノピオを描く関数（あたまの大きさを変えられる）
TOAD_RED = (220, 30, 30)
TOAD_SKIN = (255, 220, 180)
TOAD_WHITE = (255, 255, 255)
TOAD_BLUE = (50, 80, 200)
TOAD_BROWN = (139, 90, 43)

def draw_toad(surface, x, y, head_scale=1.0, scale=1.0):
    """
    キノピオを描く
    head_scale: あたま（きのこのぼうし）の大きさ。1.0がふつう
    """
    s = scale

    # からだ（青いベスト）
    body_w = int(40 * s)
    body_h = int(35 * s)
    body_rect = pygame.Rect(x - body_w, y + int(10 * s), body_w * 2, body_h)
    pygame.draw.ellipse(surface, TOAD_BLUE, body_rect)

    # おなか（白い丸）
    belly_rect = pygame.Rect(x - int(18 * s), y + int(15 * s), int(36 * s), int(25 * s))
    pygame.draw.ellipse(surface, TOAD_WHITE, belly_rect)

    # あたま（肌色の顔）
    face_r = int(30 * s)
    face_y = y - int(5 * s)
    pygame.draw.circle(surface, TOAD_SKIN, (x, face_y), face_r)

    # きのこのぼうし（赤い帽子）- head_scaleで大きさが変わる
    hat_w = int(60 * s * head_scale)
    hat_h = int(40 * s * head_scale)
    hat_y = face_y - int(30 * s * head_scale)
    hat_rect = pygame.Rect(x - hat_w, hat_y, hat_w * 2, hat_h)
    pygame.draw.ellipse(surface, TOAD_RED, hat_rect)

    # ぼうしの白い丸もよう
    spot_r = int(12 * s * head_scale)
    pygame.draw.circle(surface, TOAD_WHITE, (x - int(25 * s * head_scale), hat_y + int(18 * s * head_scale)), spot_r)
    pygame.draw.circle(surface, TOAD_WHITE, (x + int(25 * s * head_scale), hat_y + int(18 * s * head_scale)), spot_r)
    pygame.draw.circle(surface, TOAD_WHITE, (x, hat_y + int(8 * s * head_scale)), spot_r)

    # 目（大きい黒い目）
    eye_l_x = x - int(12 * s)
    eye_r_x = x + int(12 * s)
    eye_y = face_y - int(2 * s)
    pygame.draw.circle(surface, BLACK, (eye_l_x, eye_y), int(7 * s))
    pygame.draw.circle(surface, BLACK, (eye_r_x, eye_y), int(7 * s))
    # ひかり
    pygame.draw.circle(surface, WHITE, (eye_l_x - int(2 * s), eye_y - int(2 * s)), int(2 * s))
    pygame.draw.circle(surface, WHITE, (eye_r_x - int(2 * s), eye_y - int(2 * s)), int(2 * s))

    # 口（ちいさいニコニコ）
    mouth_y = face_y + int(12 * s)
    pygame.draw.arc(surface, BLACK, (x - int(8 * s), mouth_y - int(4 * s), int(16 * s), int(10 * s)), 3.14, 6.28, int(2 * s))

    # 足（茶色のくつ）
    shoe_y = y + int(42 * s)
    pygame.draw.ellipse(surface, TOAD_BROWN, (x - int(30 * s), shoe_y, int(25 * s), int(12 * s)))
    pygame.draw.ellipse(surface, TOAD_BROWN, (x + int(5 * s), shoe_y, int(25 * s), int(12 * s)))


# ドラえもんを描く関数（タケコプターのはねの角度が変えられる）
DORA_BLUE = (0, 120, 215)
DORA_SKIN = (255, 255, 255)
DORA_NOSE_RED = (220, 30, 30)
DORA_YELLOW = (255, 210, 0)

def draw_doraemon(surface, x, y, copter_angle=30, scale=1.0):
    """
    ドラえもんを描く
    copter_angle: タケコプターのはねの角度（デフォルト30度）
    """
    s = scale

    # からだ（青い丸）
    body_y = y + int(25 * s)
    pygame.draw.circle(surface, DORA_BLUE, (x, body_y), int(40 * s))
    # おなかの白い丸
    pygame.draw.circle(surface, WHITE, (x, body_y + int(5 * s)), int(28 * s))

    # ポケット（半円）
    pocket_rect = pygame.Rect(x - int(20 * s), body_y + int(2 * s), int(40 * s), int(30 * s))
    pygame.draw.arc(surface, BLACK, pocket_rect, 3.14, 6.28, int(2 * s))
    pygame.draw.line(surface, BLACK, (x - int(20 * s), body_y + int(17 * s)), (x + int(20 * s), body_y + int(17 * s)), int(2 * s))

    # あたま（青い丸）
    head_y = y - int(15 * s)
    pygame.draw.circle(surface, DORA_BLUE, (x, head_y), int(45 * s))

    # かお（白い丸）
    face_y = head_y + int(8 * s)
    pygame.draw.circle(surface, WHITE, (x, face_y), int(35 * s))

    # 目（白い楕円 + 黒い丸）
    eye_y = head_y - int(5 * s)
    # 左目
    pygame.draw.ellipse(surface, WHITE, (x - int(16 * s), eye_y - int(12 * s), int(16 * s), int(20 * s)))
    pygame.draw.circle(surface, BLACK, (x - int(5 * s), eye_y - int(3 * s)), int(4 * s))
    # 右目
    pygame.draw.ellipse(surface, WHITE, (x, eye_y - int(12 * s), int(16 * s), int(20 * s)))
    pygame.draw.circle(surface, BLACK, (x + int(5 * s), eye_y - int(3 * s)), int(4 * s))

    # はな（赤い丸）
    nose_y = face_y - int(5 * s)
    pygame.draw.circle(surface, DORA_NOSE_RED, (x, nose_y), int(7 * s))
    # はなのひかり
    pygame.draw.circle(surface, WHITE, (x - int(2 * s), nose_y - int(2 * s)), int(2 * s))

    # はなからの線
    pygame.draw.line(surface, BLACK, (x, nose_y + int(7 * s)), (x, face_y + int(18 * s)), int(2 * s))

    # 口（にっこり曲線）
    mouth_rect = pygame.Rect(x - int(25 * s), face_y - int(5 * s), int(50 * s), int(40 * s))
    pygame.draw.arc(surface, BLACK, mouth_rect, 3.5, 5.9, int(2 * s))

    # ひげ（左3本、右3本）
    whisker_x = int(30 * s)
    whisker_len = int(22 * s)
    for i, dy in enumerate([-8, 0, 8]):
        wy = face_y + int(dy * s)
        # 左ひげ
        pygame.draw.line(surface, BLACK, (x - int(15 * s), wy), (x - int(15 * s) - whisker_len, wy - int(3 * s) + i * int(3 * s)), int(2 * s))
        # 右ひげ
        pygame.draw.line(surface, BLACK, (x + int(15 * s), wy), (x + int(15 * s) + whisker_len, wy - int(3 * s) + i * int(3 * s)), int(2 * s))

    # すず（首に黄色い鈴）
    bell_y = y + int(2 * s)
    # 首輪（赤い帯）
    pygame.draw.rect(surface, DORA_NOSE_RED, (x - int(25 * s), bell_y - int(5 * s), int(50 * s), int(8 * s)))
    # すず本体
    pygame.draw.circle(surface, DORA_YELLOW, (x, bell_y + int(6 * s)), int(8 * s))
    pygame.draw.circle(surface, BLACK, (x, bell_y + int(6 * s)), int(8 * s), int(1 * s))
    pygame.draw.line(surface, BLACK, (x - int(5 * s), bell_y + int(6 * s)), (x + int(5 * s), bell_y + int(6 * s)), int(1 * s))
    pygame.draw.circle(surface, BLACK, (x, bell_y + int(9 * s)), int(2 * s))

    # タケコプター
    copter_y = head_y - int(45 * s)
    # 棒
    pygame.draw.rect(surface, DORA_YELLOW, (x - int(2 * s), copter_y, int(4 * s), int(12 * s)))
    # はね（角度で変わる！）
    angle_rad = math.radians(copter_angle)
    blade_len = int(30 * s)
    # 左のはね
    lx = x - int(blade_len * math.cos(angle_rad))
    ly = copter_y - int(blade_len * math.sin(angle_rad)) + int(3 * s)
    pygame.draw.line(surface, (100, 180, 255), (x, copter_y + int(3 * s)), (lx, ly), int(5 * s))
    # 右のはね
    rx = x + int(blade_len * math.cos(angle_rad))
    ry = copter_y - int(blade_len * math.sin(angle_rad)) + int(3 * s)
    pygame.draw.line(surface, (100, 180, 255), (x, copter_y + int(3 * s)), (rx, ry), int(5 * s))

    # 足
    foot_y = y + int(58 * s)
    pygame.draw.ellipse(surface, WHITE, (x - int(28 * s), foot_y, int(24 * s), int(12 * s)))
    pygame.draw.ellipse(surface, WHITE, (x + int(4 * s), foot_y, int(24 * s), int(12 * s)))


# たいこのたつじんのかっちゃん（みずいろの顔）を描く関数
TAIKO_LIGHT_BLUE = (120, 200, 255)
TAIKO_DARK_BLUE = (60, 140, 220)
TAIKO_FACE_WHITE = (255, 255, 255)

def draw_kacchan(surface, x, y, eye_glow=False, scale=1.0):
    """
    たいこのたつじんのかっちゃん（みずいろ）を描く
    eye_glow: めがひかるかどうか
    """
    s = scale

    # たいこのふち（みずいろの丸）
    drum_r = int(55 * s)
    pygame.draw.circle(surface, TAIKO_LIGHT_BLUE, (x, y), drum_r)
    # たいこの内側（もうすこし暗いみずいろ）
    pygame.draw.circle(surface, TAIKO_DARK_BLUE, (x, y), int(45 * s))
    # かお（白い丸）
    pygame.draw.circle(surface, TAIKO_FACE_WHITE, (x, y), int(38 * s))

    # ほっぺ（うすピンク）
    cheek_y = y + int(8 * s)
    pygame.draw.circle(surface, (255, 200, 200), (x - int(25 * s), cheek_y), int(8 * s))
    pygame.draw.circle(surface, (255, 200, 200), (x + int(25 * s), cheek_y), int(8 * s))

    # め（黒い丸）
    eye_y = y - int(5 * s)
    eye_l_x = x - int(14 * s)
    eye_r_x = x + int(14 * s)
    pygame.draw.circle(surface, BLACK, (eye_l_x, eye_y), int(8 * s))
    pygame.draw.circle(surface, BLACK, (eye_r_x, eye_y), int(8 * s))

    # めのひかり（まちがいバージョンはひかりがちょっと大きい）
    if eye_glow:
        # まちがい：ひかりがすこしだけ大きい
        pygame.draw.circle(surface, WHITE, (eye_l_x - int(2 * s), eye_y - int(2 * s)), int(4 * s))
        pygame.draw.circle(surface, WHITE, (eye_r_x - int(2 * s), eye_y - int(2 * s)), int(4 * s))
    else:
        # おてほん：ひかりはちいさい
        pygame.draw.circle(surface, WHITE, (eye_l_x - int(2 * s), eye_y - int(2 * s)), int(2 * s))
        pygame.draw.circle(surface, WHITE, (eye_r_x - int(2 * s), eye_y - int(2 * s)), int(2 * s))

    # くち（にっこり）
    mouth_y = y + int(10 * s)
    pygame.draw.arc(surface, BLACK, (x - int(15 * s), mouth_y - int(8 * s), int(30 * s), int(20 * s)), 3.4, 6.0, int(3 * s))

    # バチ（左右に持ってる）
    bachi_y = y + int(20 * s)
    # 左バチ
    pygame.draw.line(surface, (200, 160, 80), (x - int(45 * s), bachi_y + int(20 * s)), (x - int(20 * s), bachi_y - int(10 * s)), int(4 * s))
    pygame.draw.circle(surface, (200, 160, 80), (x - int(45 * s), bachi_y + int(20 * s)), int(5 * s))
    # 右バチ
    pygame.draw.line(surface, (200, 160, 80), (x + int(45 * s), bachi_y + int(20 * s)), (x + int(20 * s), bachi_y - int(10 * s)), int(4 * s))
    pygame.draw.circle(surface, (200, 160, 80), (x + int(45 * s), bachi_y + int(20 * s)), int(5 * s))


# テレサ（Boo）を描く関数
def draw_teresa(surface, x, y, scale=1.0):
    """テレサを描く"""
    s = scale

    # からだ（白い丸）
    body_r = int(40 * s)
    pygame.draw.circle(surface, WHITE, (x, y), body_r)

    # しっぽ（左下にとんがり）
    tail_points = [
        (x - int(30 * s), y + int(15 * s)),
        (x - int(55 * s), y + int(30 * s)),
        (x - int(25 * s), y + int(30 * s)),
    ]
    pygame.draw.polygon(surface, WHITE, tail_points)

    # 手（左右の小さい三角）
    # 左手
    pygame.draw.polygon(surface, WHITE, [
        (x - int(35 * s), y - int(5 * s)),
        (x - int(50 * s), y + int(5 * s)),
        (x - int(35 * s), y + int(15 * s)),
    ])
    # 右手
    pygame.draw.polygon(surface, WHITE, [
        (x + int(35 * s), y - int(5 * s)),
        (x + int(50 * s), y + int(5 * s)),
        (x + int(35 * s), y + int(15 * s)),
    ])

    # 目（大きい黒い丸）
    eye_y = y - int(8 * s)
    pygame.draw.circle(surface, BLACK, (x - int(12 * s), eye_y), int(8 * s))
    pygame.draw.circle(surface, BLACK, (x + int(12 * s), eye_y), int(8 * s))

    # 口（大きく開いた口）
    mouth_y = y + int(10 * s)
    pygame.draw.ellipse(surface, BLACK, (x - int(18 * s), mouth_y, int(36 * s), int(18 * s)))
    # 歯（上の2本）
    pygame.draw.polygon(surface, WHITE, [
        (x - int(8 * s), mouth_y),
        (x - int(3 * s), mouth_y),
        (x - int(5 * s), mouth_y + int(8 * s))
    ])
    pygame.draw.polygon(surface, WHITE, [
        (x + int(3 * s), mouth_y),
        (x + int(8 * s), mouth_y),
        (x + int(5 * s), mouth_y + int(8 * s))
    ])

    # したベロ（赤）
    pygame.draw.ellipse(surface, (220, 50, 80), (x - int(8 * s), mouth_y + int(8 * s), int(16 * s), int(10 * s)))


# カービィを描く関数（ほっぺたの大きさを変えられる）
KIRBY_PINK = (255, 150, 180)
KIRBY_DARK_PINK = (230, 100, 140)
KIRBY_SHOE_RED = (200, 30, 30)

def draw_kirby(surface, x, y, cheek_scale=1.0, scale=1.0):
    """
    カービィを描く
    cheek_scale: ほっぺたの大きさ。1.0がふつう
    """
    s = scale

    # からだ（ピンクの丸）
    body_r = int(40 * s)
    pygame.draw.circle(surface, KIRBY_PINK, (x, y), body_r)

    # 足（赤いくつ）
    foot_y = y + int(30 * s)
    pygame.draw.ellipse(surface, KIRBY_SHOE_RED, (x - int(32 * s), foot_y, int(28 * s), int(15 * s)))
    pygame.draw.ellipse(surface, KIRBY_SHOE_RED, (x + int(4 * s), foot_y, int(28 * s), int(15 * s)))

    # 手（ピンクの楕円）
    pygame.draw.ellipse(surface, KIRBY_PINK, (x - int(45 * s), y - int(5 * s), int(20 * s), int(18 * s)))
    pygame.draw.ellipse(surface, KIRBY_PINK, (x + int(25 * s), y - int(5 * s), int(20 * s), int(18 * s)))

    # 目（大きい楕円の黒い目）
    eye_y = y - int(8 * s)
    # 左目
    pygame.draw.ellipse(surface, BLACK, (x - int(18 * s), eye_y - int(12 * s), int(12 * s), int(18 * s)))
    # 右目
    pygame.draw.ellipse(surface, BLACK, (x + int(6 * s), eye_y - int(12 * s), int(12 * s), int(18 * s)))
    # 目のひかり
    pygame.draw.circle(surface, WHITE, (x - int(14 * s), eye_y - int(6 * s)), int(3 * s))
    pygame.draw.circle(surface, WHITE, (x + int(10 * s), eye_y - int(6 * s)), int(3 * s))

    # ほっぺた（cheek_scaleで大きさが変わる！）
    cheek_r = int(10 * s * cheek_scale)
    cheek_y = y + int(5 * s)
    pygame.draw.circle(surface, KIRBY_DARK_PINK, (x - int(25 * s), cheek_y), cheek_r)
    pygame.draw.circle(surface, KIRBY_DARK_PINK, (x + int(25 * s), cheek_y), cheek_r)

    # 口（ちいさいニコニコ）
    mouth_y = y + int(5 * s)
    pygame.draw.arc(surface, BLACK, (x - int(8 * s), mouth_y, int(16 * s), int(10 * s)), 3.4, 6.0, int(2 * s))


# 3キャラを並べて描く関数（だい5もん用）
def draw_triple(surface, x, y, teresa_ok=True, kirby_cheek=1.0, chomp_tooth=1.0, scale=1.0):
    """テレサ・カービィ・ワンワンを3つ並べて描く"""
    spacing = int(110 * scale)
    small = scale * 0.6
    # テレサ（左）
    draw_teresa(surface, x - spacing, y, small)
    # カービィ（真ん中）
    draw_kirby(surface, x, y + int(10 * small), kirby_cheek, small)
    # ワンワン（右）
    draw_chain_chomp(surface, x + spacing, y, [12, 12, 12, 12], small, chomp_tooth)


# 問題データ：おてほん vs まちがい
questions = [
    {
        "type": "chain_chomp",
        "title": "だい1もん：ワンワンの くさり",
        "hint": "くさりの おおきさを よーくみてね！",
        "correct_params": {"chain_sizes": [12, 12, 12, 12]},
        "wrong_params": {"chain_sizes": [12, 15, 12, 12]},
        "wrong_side": None,
    },
    {
        "type": "toad",
        "title": "だい2もん：キノピオの あたま",
        "hint": "あたまの おおきさを よーくみてね！",
        "correct_params": {"head_scale": 1.0},
        "wrong_params": {"head_scale": 0.85},
        "wrong_side": None,
    },
    {
        "type": "doraemon",
        "title": "だい3もん：ドラえもんの タケコプター",
        "hint": "タケコプターの はねを よーくみてね！",
        "correct_params": {"copter_angle": 30},
        "wrong_params": {"copter_angle": 22},
        "wrong_side": None,
    },
    {
        "type": "kacchan",
        "title": "だい4もん：たいこの たつじん",
        "hint": "めを よーくみてね！",
        "correct_params": {"eye_glow": False},
        "wrong_params": {"eye_glow": True},
        "wrong_side": None,
    },
    {
        "type": "triple",
        "title": "だい5もん：ちょう むずかしい！",
        "hint": "3キャラ ぜんぶ よーくみてね！",
        "correct_params": {"kirby_cheek": 1.0, "chomp_tooth": 1.0},
        "wrong_params": {"kirby_cheek": 1.15, "chomp_tooth": 0.85},
        "wrong_side": None,
    },
]

# 各問題のまちがいの位置をランダムに決める
for q in questions:
    q["wrong_side"] = random.choice(["left", "right"])


def draw_question_character(surface, x, y, q_type, params, scale=1.0):
    """問題のタイプに応じたキャラクターを描く"""
    if q_type == "chain_chomp":
        draw_chain_chomp(surface, x, y, params.get("chain_sizes"), scale, params.get("tooth_scale", 1.0))
    elif q_type == "toad":
        draw_toad(surface, x, y, params.get("head_scale", 1.0), scale)
    elif q_type == "doraemon":
        draw_doraemon(surface, x, y, params.get("copter_angle", 30), scale)
    elif q_type == "kacchan":
        draw_kacchan(surface, x, y, params.get("eye_glow", False), scale)
    elif q_type == "triple":
        draw_triple(surface, x, y, True, params.get("kirby_cheek", 1.0), params.get("chomp_tooth", 1.0), scale)


def draw_heart(surface, x, y, filled=True):
    """ハートを描く"""
    color = RED if filled else GRAY
    # ハートの形をポリゴンで
    points = []
    for t in range(100):
        angle = t / 100 * 2 * math.pi
        hx = 16 * (math.sin(angle) ** 3)
        hy = -(13 * math.cos(angle) - 5 * math.cos(2*angle) - 2 * math.cos(3*angle) - math.cos(4*angle))
        points.append((x + hx * 1.2, y + hy * 1.2))
    if len(points) > 2:
        pygame.draw.polygon(surface, color, points)


def draw_game():
    screen.fill(LIGHT_BLUE)

    if game_over:
        text = font_big.render("ゲームオーバー！", True, RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))
        text2 = font_medium.render(f"スコア：{score} もん せいかい！", True, BLACK)
        screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 10))
        text3 = font_small.render("クリックで もういちど あそぶ", True, DARK_GRAY)
        screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 60))
        pygame.display.flip()
        return

    if game_clear:
        if score == len(questions):
            text = font_big.render("ぜんもん せいかい！すごい！！", True, GREEN)
        else:
            text = font_big.render("おわり！がんばったね！", True, GREEN)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))
        text2 = font_medium.render(f"スコア：{score} / {len(questions)} もん せいかい！", True, BLACK)
        screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 10))
        text3 = font_small.render("クリックで もういちど あそぶ", True, DARK_GRAY)
        screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 60))
        pygame.display.flip()
        return

    q = questions[current_question]

    # タイトル
    title_text = font_big.render(q["title"], True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 10))

    # ヒント
    hint_text = font_small.render(q["hint"], True, DARK_GRAY)
    screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, 55))

    # おてほん（上の真ん中）
    otehon_text = font_medium.render("★ おてほん ★", True, RED)
    screen.blit(otehon_text, (WIDTH // 2 - otehon_text.get_width() // 2, 90))

    # おてほんの枠（tripleは大きくする）
    if q["type"] == "triple":
        otehon_rect = pygame.Rect(WIDTH // 2 - 300, 120, 600, 180)
    else:
        otehon_rect = pygame.Rect(WIDTH // 2 - 150, 120, 300, 180)
    pygame.draw.rect(screen, WHITE, otehon_rect, border_radius=10)
    pygame.draw.rect(screen, RED, otehon_rect, 3, border_radius=10)
    draw_question_character(screen, WIDTH // 2, 220, q["type"], q["correct_params"], scale=0.9)

    # 下の2つの選択肢
    left_rect = pygame.Rect(50, 380, 420, 300)
    right_rect = pygame.Rect(530, 380, 420, 300)

    # 枠
    pygame.draw.rect(screen, WHITE, left_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, left_rect, 3, border_radius=10)
    pygame.draw.rect(screen, WHITE, right_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, right_rect, 3, border_radius=10)

    # ラベル
    label_a = font_medium.render("A", True, BLACK)
    label_b = font_medium.render("B", True, BLACK)
    screen.blit(label_a, (left_rect.centerx - label_a.get_width() // 2, 385))
    screen.blit(label_b, (right_rect.centerx - label_b.get_width() // 2, 385))

    # ワンワン/キノピオを描く（どっちかが間違い）
    if q["wrong_side"] == "left":
        draw_question_character(screen, left_rect.centerx, 510, q["type"], q["wrong_params"], scale=1.0)
        draw_question_character(screen, right_rect.centerx, 510, q["type"], q["correct_params"], scale=1.0)
    else:
        draw_question_character(screen, left_rect.centerx, 510, q["type"], q["correct_params"], scale=1.0)
        draw_question_character(screen, right_rect.centerx, 510, q["type"], q["wrong_params"], scale=1.0)

    # ハート（ライフ）
    for i in range(3):
        draw_heart(screen, 60 + i * 45, 730, filled=(i < lives))

    # スコア
    score_text = font_small.render(f"せいかい：{score}", True, BLACK)
    screen.blit(score_text, (WIDTH - 170, 715))

    # メッセージ（正解・不正解）おおきく！
    if message and message_timer > 0:
        # 背景を半透明にする
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 150))
        screen.blit(overlay, (0, 0))

        if message == "せいかい！":
            # おおきな ○（マル）
            pygame.draw.circle(screen, GREEN, (WIDTH // 2, HEIGHT // 2 - 30), 150, 20)
            msg_color = GREEN
        else:
            # おおきな ×（バツ）
            cx, cy = WIDTH // 2, HEIGHT // 2 - 30
            pygame.draw.line(screen, RED, (cx - 120, cy - 120), (cx + 120, cy + 120), 20)
            pygame.draw.line(screen, RED, (cx + 120, cy - 120), (cx - 120, cy + 120), 20)
            msg_color = RED

        msg_text = font_huge.render(message, True, msg_color)
        screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, HEIGHT // 2 + 140))

    pygame.display.flip()


def check_click(pos):
    global lives, current_question, score, message, message_timer, game_over, game_clear

    if game_over or game_clear:
        # リスタート
        reset_game()
        return

    if message_timer > 0:
        return

    x, y = pos
    q = questions[current_question]

    left_rect = pygame.Rect(50, 380, 420, 300)
    right_rect = pygame.Rect(530, 380, 420, 300)

    clicked_wrong = False

    if left_rect.collidepoint(x, y):
        if q["wrong_side"] == "left":
            clicked_wrong = True
        else:
            clicked_wrong = False
    elif right_rect.collidepoint(x, y):
        if q["wrong_side"] == "right":
            clicked_wrong = True
        else:
            clicked_wrong = False
    else:
        return  # 枠の外

    if clicked_wrong:
        # 正解！（間違いを見つけた）
        score += 1
        message = "せいかい！"
        message_timer = 60
        sound_pinpon.play()
    else:
        # 不正解
        lives -= 1
        message = "ふせいかい！"
        message_timer = 60
        sound_buzzer.play()
        if lives <= 0:
            game_over = True


def reset_game():
    global lives, current_question, score, message, message_timer, game_over, game_clear
    lives = 3
    current_question = 0
    score = 0
    message = ""
    message_timer = 0
    game_over = False
    game_clear = False
    for q in questions:
        q["wrong_side"] = random.choice(["left", "right"])


# メインループ
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            check_click(event.pos)

    # メッセージタイマー
    if message_timer > 0:
        message_timer -= 1
        if message_timer == 0:
            message = ""
            if not game_over:
                current_question += 1
                if current_question >= len(questions):
                    game_clear = True

    draw_game()
    clock.tick(30)

pygame.quit()
sys.exit()
