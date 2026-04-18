"""
クイズたいけつ！ ほんと？うそ？
くろーどちゃんからたろうくんへの20もんクイズ

操作:
  ↑↓ キー: ほんと / うそ をえらぶ
  Enter キー: けってい
  ESC キー: おわる
"""

import sys
import os
import math
import random
import json
import numpy as np
import pygame

# quiz_data.py を同じフォルダから読み込む
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quiz_data import QUIZZES

# --- 定数 ---
FPS = 60
BG_COLOR = (30, 30, 60)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 50)
CYAN = (100, 220, 255)
GREEN = (50, 220, 100)
RED = (255, 80, 80)
PINK = (255, 150, 180)
ORANGE = (255, 165, 0)
DARK_BLUE = (20, 20, 50)
GRAY = (120, 120, 140)

# ゲーム別カラー
GAME_COLORS = {
    "マリオワンダー": (255, 50, 50),
    "ゼルダ ブレワイ": (50, 200, 50),
    "ルイージマンション": (100, 50, 200),
}


def generate_sound_pinpon(sample_rate=44100):
    """ピンポーン（正解音）"""
    duration = 0.6
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    # 2音の和音（ド・ミ）+ ディケイ
    freq1, freq2 = 523.25, 659.25  # C5, E5
    envelope = np.exp(-t * 3.0)
    wave = 0.4 * np.sin(2 * np.pi * freq1 * t) + 0.3 * np.sin(2 * np.pi * freq2 * t)
    wave = (wave * envelope * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


def generate_sound_buzzer(sample_rate=44100):
    """ブッブー（不正解音）"""
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    freq = 150
    envelope = np.exp(-t * 4.0)
    wave = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))  # 矩形波
    wave = (wave * envelope * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


def generate_sound_jajan(sample_rate=44100):
    """ジャジャーン（問題登場音）"""
    duration = 0.8
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    # 上昇する3音
    freq1, freq2, freq3 = 261.63, 329.63, 392.0  # C4, E4, G4
    env1 = np.where(t < 0.25, np.exp(-t * 2), 0)
    env2 = np.where((t >= 0.2) & (t < 0.5), np.exp(-(t - 0.2) * 2), 0)
    env3 = np.where(t >= 0.4, np.exp(-(t - 0.4) * 1.5), 0)
    wave = (
        0.3 * np.sin(2 * np.pi * freq1 * t) * env1
        + 0.3 * np.sin(2 * np.pi * freq2 * t) * env2
        + 0.4 * np.sin(2 * np.pi * freq3 * t) * env3
    )
    wave = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


def generate_sound_select(sample_rate=44100):
    """カーソル移動音"""
    duration = 0.08
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    wave = 0.3 * np.sin(2 * np.pi * 800 * t) * np.exp(-t * 30)
    wave = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


def generate_sound_decide(sample_rate=44100):
    """決定音"""
    duration = 0.15
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    wave = 0.4 * np.sin(2 * np.pi * 600 * t) * np.exp(-t * 15)
    wave = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


def generate_sound_drumroll(sample_rate=44100):
    """ドラムロール風"""
    duration = 1.2
    n = int(sample_rate * duration)
    t = np.linspace(0, duration, n, dtype=np.float32)
    wave = np.zeros(n, dtype=np.float32)
    # ランダムなパルス列（だんだん速く）
    interval_start = 0.08
    interval_end = 0.02
    time_pos = 0.0
    while time_pos < duration:
        progress = time_pos / duration
        interval = interval_start + (interval_end - interval_start) * progress
        idx = int(time_pos * sample_rate)
        pulse_len = min(int(0.01 * sample_rate), n - idx)
        if pulse_len > 0:
            pulse_t = np.linspace(0, 0.01, pulse_len, dtype=np.float32)
            amplitude = 0.3 + 0.4 * progress
            wave[idx : idx + pulse_len] += amplitude * np.sin(
                2 * np.pi * 200 * pulse_t
            ) * np.exp(-pulse_t * 200)
        time_pos += interval
    wave = np.clip(wave, -1.0, 1.0)
    wave = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


def generate_sound_fanfare(sample_rate=44100):
    """ファンファーレ（結果発表）"""
    duration = 1.5
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    notes = [
        (261.63, 0.0, 0.3),
        (329.63, 0.15, 0.3),
        (392.0, 0.3, 0.3),
        (523.25, 0.5, 1.0),
    ]
    wave = np.zeros_like(t)
    for freq, start, dur in notes:
        mask = (t >= start) & (t < start + dur)
        env = np.where(mask, np.exp(-((t - start)) * 2.0), 0)
        wave += 0.25 * np.sin(2 * np.pi * freq * t) * env
    wave = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


# --- ファンシーモード用の効果音 ---

def generate_fancy_pinpon(sample_rate=44100):
    """豪華な正解音（和音+スウィープ）"""
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    # 和音C-E-G-C（メジャーコード）
    freqs = [523.25, 659.25, 783.99, 1046.50]
    wave = np.zeros_like(t)
    for i, f in enumerate(freqs):
        delay = i * 0.05
        env = np.where(t >= delay, np.exp(-(t - delay) * 2.5), 0)
        wave += 0.2 * np.sin(2 * np.pi * f * t) * env
    # 上昇スウィープ
    sweep = np.sin(2 * np.pi * (400 + 600 * t) * t) * np.exp(-t * 5) * 0.15
    wave += sweep
    wave = np.clip(wave, -1.0, 1.0)
    wave = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


def generate_fancy_buzzer(sample_rate=44100):
    """コミカルな不正解音"""
    duration = 0.7
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    # 下降する音
    freq = 300 - 200 * t / duration
    envelope = np.exp(-t * 3.0)
    wave = 0.4 * np.sign(np.sin(2 * np.pi * np.cumsum(freq / sample_rate))) * envelope
    # トロンボーン風のワウワウ
    wave += 0.2 * np.sin(2 * np.pi * 100 * t) * np.sin(2 * np.pi * 8 * t) * envelope
    wave = np.clip(wave, -1.0, 1.0)
    wave = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


def generate_fancy_fanfare(sample_rate=44100):
    """豪華なファンファーレ（結果発表）"""
    duration = 2.5
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    # トランペット風のメロディ
    notes = [
        (392.0, 0.0, 0.2),   # G4
        (392.0, 0.2, 0.2),   # G4
        (392.0, 0.4, 0.2),   # G4
        (523.25, 0.6, 0.4),  # C5
        (659.25, 1.0, 0.3),  # E5
        (783.99, 1.3, 0.3),  # G5
        (1046.50, 1.6, 0.9), # C6
    ]
    wave = np.zeros_like(t)
    for freq, start, dur in notes:
        mask = (t >= start) & (t < start + dur)
        env = np.where(mask, np.exp(-((t - start)) * 1.5) * (1 - np.exp(-((t - start)) * 30)), 0)
        wave += 0.15 * np.sin(2 * np.pi * freq * t) * env
        wave += 0.08 * np.sin(2 * np.pi * freq * 2 * t) * env  # 倍音
    wave = np.clip(wave, -1.0, 1.0)
    wave = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


def generate_fancy_drumroll(sample_rate=44100):
    """豪華なドラムロール（シンバル付き）"""
    duration = 1.5
    n = int(sample_rate * duration)
    t = np.linspace(0, duration, n, dtype=np.float32)
    wave = np.zeros(n, dtype=np.float32)
    # ドラム（密度が増す）
    interval_start = 0.06
    interval_end = 0.015
    time_pos = 0.0
    while time_pos < duration:
        progress = time_pos / duration
        interval = interval_start + (interval_end - interval_start) * progress
        idx = int(time_pos * sample_rate)
        pulse_len = min(int(0.012 * sample_rate), n - idx)
        if pulse_len > 0:
            pulse_t = np.linspace(0, 0.012, pulse_len, dtype=np.float32)
            amplitude = 0.2 + 0.5 * progress
            wave[idx: idx + pulse_len] += amplitude * np.sin(
                2 * np.pi * 180 * pulse_t
            ) * np.exp(-pulse_t * 150)
        time_pos += interval
    # 最後にシンバル風ノイズ
    cymbal_start = int(0.9 * duration * sample_rate)
    cymbal_len = n - cymbal_start
    if cymbal_len > 0:
        noise = np.random.uniform(-0.3, 0.3, cymbal_len).astype(np.float32)
        cymbal_env = np.exp(-np.linspace(0, 3, cymbal_len, dtype=np.float32))
        wave[cymbal_start:] += noise * cymbal_env
    wave = np.clip(wave, -1.0, 1.0)
    wave = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


class Particle:
    """紙吹雪パーティクル"""
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-12, -3)
        self.gravity = 0.2
        self.life = random.randint(40, 80)
        self.age = 0
        self.size = random.randint(4, 10)
        self.color = random.choice([
            (255, 50, 80), (50, 200, 255), (255, 220, 50),
            (50, 255, 100), (255, 150, 50), (200, 100, 255),
        ])
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-10, 10)
        self.bounds_w = w
        self.bounds_h = h

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.age += 1
        self.rotation += self.rot_speed

    def draw(self, surface):
        if self.age >= self.life:
            return
        alpha = max(0, 1 - self.age / self.life)
        color = (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha),
        )
        # 回転する四角形
        s = self.size
        points = []
        for dx, dy in [(-s, -s), (s, -s), (s, s), (-s, s)]:
            rad = math.radians(self.rotation)
            rx = dx * math.cos(rad) - dy * math.sin(rad)
            ry = dx * math.sin(rad) + dy * math.cos(rad)
            points.append((int(self.x + rx), int(self.y + ry)))
        pygame.draw.polygon(surface, color, points)


class QuizGame:
    def __init__(self, fancy=False):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.fancy = fancy

        # ウィンドウモード（ドラッグで移動できる）
        info = pygame.display.Info()
        self.W = int(info.current_w * 0.6)
        self.H = int(info.current_h * 0.75)
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("クイズたいけつ！")

        self.clock = pygame.time.Clock()

        # フォント（日本語対応）
        font_candidates = [
            "C:/Windows/Fonts/meiryo.ttc",
            "C:/Windows/Fonts/msgothic.ttc",
            "C:/Windows/Fonts/YuGothM.ttc",
        ]
        self.font_path = None
        for fp in font_candidates:
            if os.path.exists(fp):
                self.font_path = fp
                break

        self.font_xl = pygame.font.Font(self.font_path, int(self.H * 0.12))
        self.font_large = pygame.font.Font(self.font_path, int(self.H * 0.07))
        self.font_medium = pygame.font.Font(self.font_path, int(self.H * 0.045))
        self.font_small = pygame.font.Font(self.font_path, int(self.H * 0.035))

        # 効果音を生成
        self.snd_pinpon = generate_sound_pinpon()
        self.snd_buzzer = generate_sound_buzzer()
        self.snd_jajan = generate_sound_jajan()
        self.snd_select = generate_sound_select()
        self.snd_decide = generate_sound_decide()
        self.snd_drumroll = generate_sound_drumroll()
        self.snd_fanfare = generate_sound_fanfare()

        # VoiceVox音声（事前生成済みなら読み込む）
        self.voices = {}
        sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
        if os.path.isdir(sounds_dir):
            for fname in os.listdir(sounds_dir):
                if fname.endswith(".wav"):
                    key = fname[:-4]  # 拡張子除去
                    try:
                        self.voices[key] = pygame.mixer.Sound(
                            os.path.join(sounds_dir, fname)
                        )
                    except Exception:
                        pass

        self.quizzes = QUIZZES
        self.current_q = 0
        self.score = 0
        self.selected = 0  # 0=ほんと, 1=うそ
        self.particles = []

        # ファンシーモード：効果音の差し替え + 画像読み込み
        if self.fancy:
            self.snd_pinpon = generate_fancy_pinpon()
            self.snd_buzzer = generate_fancy_buzzer()
            self.snd_fanfare = generate_fancy_fanfare()
            self.snd_drumroll = generate_fancy_drumroll()

            # ゲーム画像の読み込み
            self.game_images = {}
            images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
            image_map = {
                "マリオワンダー": "mario_wonder.jpg",
                "ゼルダ ブレワイ": "zelda_link.jpg",
                "ルイージマンション": "luigi_mansion.jpg",
            }
            for game_name, fname in image_map.items():
                path = os.path.join(images_dir, fname)
                if os.path.exists(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        # 画像サイズを調整（高さを画面の25%に）
                        target_h = int(self.H * 0.22)
                        ratio = target_h / img.get_height()
                        target_w = int(img.get_width() * ratio)
                        self.game_images[game_name] = pygame.transform.smoothscale(img, (target_w, target_h))
                    except Exception:
                        pass

        # 声マップ（voice_map.json）の読み込み
        self.voice_map = {}
        voice_map_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "sounds", "voice_map.json"
        )
        if os.path.exists(voice_map_path):
            try:
                with open(voice_map_path, "r", encoding="utf-8") as f:
                    self.voice_map = json.load(f)
            except Exception:
                pass

    def play_voice(self, key):
        """VoiceVox事前生成音声を再生（なければスキップ）"""
        if key in self.voices:
            self.voices[key].play()

    def draw_text_center(self, text, font, color, y, shadow=True):
        """テキストを中央揃えで描画（影つき）"""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if shadow:
                shadow_surf = font.render(line, True, (0, 0, 0))
                shadow_rect = shadow_surf.get_rect(
                    center=(self.W // 2 + 3, y + i * font.get_linesize() + 3)
                )
                self.screen.blit(shadow_surf, shadow_rect)
            surf = font.render(line, True, color)
            rect = surf.get_rect(center=(self.W // 2, y + i * font.get_linesize()))
            self.screen.blit(surf, rect)

    def draw_gradient_bg(self):
        """グラデーション背景"""
        for y in range(self.H):
            ratio = y / self.H
            r = int(20 + 20 * ratio)
            g = int(15 + 15 * ratio)
            b = int(50 + 30 * (1 - ratio))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.W, y))

    def draw_stars(self, frame):
        """背景の星"""
        random.seed(42)
        for _ in range(50):
            x = random.randint(0, self.W)
            y = random.randint(0, self.H)
            brightness = int(
                150 + 105 * math.sin((frame + random.randint(0, 100)) * 0.03)
            )
            brightness = max(50, min(255, brightness))
            size = random.choice([1, 1, 1, 2, 2, 3])
            star_b = min(255, brightness + 20)
            pygame.draw.circle(
                self.screen, (brightness, brightness, star_b), (x, y), size
            )

    def title_screen(self):
        """タイトル画面"""
        frame = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    if event.key == pygame.K_RETURN:
                        self.snd_decide.play()
                        return True

            self.draw_gradient_bg()
            self.draw_stars(frame)

            # タイトル（バウンスアニメーション）
            bounce = math.sin(frame * 0.05) * 10
            title_y = int(self.H * 0.25 + bounce)

            if self.fancy:
                # レインボータイトル
                title_text = "クイズたいけつ！"
                total_w = self.font_xl.size(title_text)[0]
                start_x = (self.W - total_w) // 2
                cx = start_x
                for ci, ch in enumerate(title_text):
                    hue = (frame * 3 + ci * 30) % 360
                    r = max(0, min(255, int(255 * max(0, min(1, abs((hue / 60) % 6 - 3) - 1)))))
                    g = max(0, min(255, int(255 * max(0, min(1, 2 - abs((hue / 60) % 6 - 2))))))
                    b = max(0, min(255, int(255 * max(0, min(1, 2 - abs((hue / 60) % 6 - 4))))))
                    ch_surf = self.font_xl.render(ch, True, (r, g, b))
                    self.screen.blit(ch_surf, (cx, title_y))
                    cx += ch_surf.get_width()

                # ファンシーモード表示
                self.draw_text_center(
                    "★ ファンシーモード ★",
                    self.font_small,
                    ORANGE,
                    int(self.H * 0.18),
                )
            else:
                self.draw_text_center("クイズたいけつ！", self.font_xl, YELLOW, title_y)

            # サブタイトル
            self.draw_text_center(
                "ほんと？ うそ？", self.font_large, CYAN, int(self.H * 0.45)
            )

            # ゲーム名
            self.draw_text_center(
                "マリオワンダー ・ ゼルダ ・ ルイージマンション",
                self.font_small,
                WHITE,
                int(self.H * 0.58),
            )

            # スタート指示（点滅）
            if (frame // 30) % 2 == 0:
                self.draw_text_center(
                    "Enter キーで スタート！",
                    self.font_medium,
                    GREEN,
                    int(self.H * 0.78),
                )

            # 問題数
            self.draw_text_center(
                f"ぜんぶで {len(self.quizzes)}もん",
                self.font_small,
                GRAY,
                int(self.H * 0.88),
            )

            pygame.display.flip()
            self.clock.tick(FPS)
            frame += 1

    def show_question_number(self, q_num):
        """「だい○もん！」をドーンと表示"""
        self.snd_drumroll.play()

        # ドラムロール中のアニメーション（1.2秒）
        for frame in range(int(FPS * 1.2)):
            self.draw_gradient_bg()
            self.draw_stars(frame)

            # 波打つ「？」マーク
            for i in range(5):
                wobble = math.sin(frame * 0.1 + i) * 30
                x = self.W // 2 + (i - 2) * 120
                y = int(self.H * 0.45 + wobble)
                alpha = int(100 + 50 * math.sin(frame * 0.05 + i))
                color = (alpha, alpha, alpha + 40)
                surf = self.font_xl.render("？", True, color)
                rect = surf.get_rect(center=(x, y))
                self.screen.blit(surf, rect)

            pygame.display.flip()
            self.clock.tick(FPS)

        # ジャジャーン！
        self.snd_jajan.play()
        text = f"だい{q_num}もん！"

        # ズームインアニメーション
        for frame in range(int(FPS * 1.0)):
            self.draw_gradient_bg()
            self.draw_stars(frame)

            progress = min(1.0, frame / (FPS * 0.3))
            scale = 0.3 + 0.7 * progress
            # イージング（バウンス）
            if progress >= 1.0:
                t = (frame - FPS * 0.3) / (FPS * 0.7)
                scale = 1.0 + 0.05 * math.sin(t * math.pi * 4) * math.exp(-t * 3)

            font_size = int(self.H * 0.14 * scale)
            font_size = max(10, min(font_size, int(self.H * 0.16)))
            font_q = pygame.font.Font(self.font_path, font_size)

            # 問題番号
            self.draw_text_center(text, font_q, YELLOW, int(self.H * 0.35))

            # ゲーム名表示（フェードイン）
            quiz = self.quizzes[self.current_q]
            game_color = GAME_COLORS.get(quiz["game"], WHITE)
            if frame > FPS * 0.4:
                self.draw_text_center(
                    f"【{quiz['game']}】",
                    self.font_medium,
                    game_color,
                    int(self.H * 0.58),
                )

            pygame.display.flip()
            self.clock.tick(FPS)

    def question_screen(self):
        """問題画面 → 回答選択"""
        quiz = self.quizzes[self.current_q]
        self.selected = 0
        decided = False

        # VoiceVox読み上げ
        voice_key = f"q{self.current_q + 1}_question"
        self.play_voice(voice_key)

        frame = 0
        while not decided:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        self.selected = 1 - self.selected
                        self.snd_select.play()
                    if event.key == pygame.K_RETURN:
                        self.snd_decide.play()
                        decided = True

            self.draw_gradient_bg()
            self.draw_stars(frame)

            # ヘッダー（問題番号 / スコア）
            header_text = f"だい{self.current_q + 1}もん / {len(self.quizzes)}もん"
            surf_h = self.font_small.render(header_text, True, GRAY)
            self.screen.blit(surf_h, (30, 20))

            score_text = f"スコア: {self.score}"
            surf_s = self.font_small.render(score_text, True, YELLOW)
            self.screen.blit(surf_s, (self.W - surf_s.get_width() - 30, 20))

            # 声の情報表示（voice_map があれば）
            q_key = str(self.current_q + 1)
            if q_key in self.voice_map:
                vi = self.voice_map[q_key]
                voice_text = f"こえ: [{vi['id']}] {vi['name']}"
                voice_surf = self.font_small.render(voice_text, True, PINK)
                self.screen.blit(voice_surf, (30, 50))

            # ゲーム名タグ
            game_color = GAME_COLORS.get(quiz["game"], WHITE)
            tag_surf = self.font_small.render(f"【{quiz['game']}】", True, game_color)
            tag_rect = tag_surf.get_rect(center=(self.W // 2, int(self.H * 0.12)))
            self.screen.blit(tag_surf, tag_rect)

            # ファンシーモード：ゲーム画像を右上に表示
            if self.fancy and hasattr(self, 'game_images') and quiz["game"] in self.game_images:
                img = self.game_images[quiz["game"]]
                img_x = self.W - img.get_width() - 15
                img_y = int(self.H * 0.08)
                # 画像に枠をつける
                border = 3
                pygame.draw.rect(self.screen, game_color,
                    (img_x - border, img_y - border,
                     img.get_width() + border * 2, img.get_height() + border * 2),
                    border, 8)
                self.screen.blit(img, (img_x, img_y))

            # 問題文
            self.draw_text_center(
                quiz["question"], self.font_large, WHITE, int(self.H * 0.25)
            )

            # 選択肢の区切り線
            line_y = int(self.H * 0.55)
            pygame.draw.line(
                self.screen,
                GRAY,
                (self.W * 0.15, line_y),
                (self.W * 0.85, line_y),
                2,
            )

            # 選択肢
            choices = ["ほんと！", "うそ！"]
            choice_colors = [GREEN, RED]
            for i, (choice, c_color) in enumerate(zip(choices, choice_colors)):
                y = int(self.H * 0.63 + i * self.H * 0.12)
                box_w = int(self.W * 0.5)
                box_h = int(self.H * 0.09)
                box_x = (self.W - box_w) // 2
                box_y = y - box_h // 2

                if i == self.selected:
                    # 選択中：明るい枠線 + 塗りつぶし
                    pulse = int(20 * math.sin(frame * 0.1))
                    fill_color = (
                        max(0, min(255, c_color[0] // 4 + pulse)),
                        max(0, min(255, c_color[1] // 4 + pulse)),
                        max(0, min(255, c_color[2] // 4 + pulse)),
                    )
                    pygame.draw.rect(
                        self.screen, fill_color, (box_x, box_y, box_w, box_h), 0, 15
                    )
                    pygame.draw.rect(
                        self.screen, c_color, (box_x, box_y, box_w, box_h), 4, 15
                    )
                    # 矢印
                    arrow_x = box_x - 50
                    arrow_surf = self.font_large.render("▶", True, c_color)
                    self.screen.blit(arrow_surf, (arrow_x, y - arrow_surf.get_height() // 2))
                else:
                    dark_c = (c_color[0] // 3, c_color[1] // 3, c_color[2] // 3)
                    pygame.draw.rect(
                        self.screen, dark_c, (box_x, box_y, box_w, box_h), 2, 15
                    )

                # テキスト
                text_color = WHITE if i == self.selected else GRAY
                surf = self.font_large.render(choice, True, text_color)
                rect = surf.get_rect(center=(self.W // 2, y))
                self.screen.blit(surf, rect)

            # 操作ガイド
            self.draw_text_center(
                "↑↓ えらぶ  Enter けってい",
                self.font_small,
                GRAY,
                int(self.H * 0.92),
            )

            pygame.display.flip()
            self.clock.tick(FPS)
            frame += 1

        # 回答を返す（True=ほんと, False=うそ）
        return self.selected == 0  # 0=ほんと選択→True

    def show_result(self, player_answer):
        """正解・不正解の演出"""
        quiz = self.quizzes[self.current_q]
        is_correct = player_answer == quiz["answer"]

        if is_correct:
            self.score += 1
            self.snd_pinpon.play()
            mark = "◯"
            mark_color = GREEN
            result_text = "せいかい！！"
            voice_key = f"q{self.current_q + 1}_correct"
        else:
            self.snd_buzzer.play()
            mark = "✕"
            mark_color = RED
            result_text = "ざんねん！"
            voice_key = f"q{self.current_q + 1}_wrong"

        # VoiceVoxの結果読み上げ
        self.play_voice(voice_key)

        # ファンシーモードで正解時は紙吹雪パーティクルを生成
        if self.fancy and is_correct:
            self.particles = []
            for _ in range(60):
                self.particles.append(Particle(
                    random.randint(int(self.W * 0.2), int(self.W * 0.8)),
                    random.randint(int(self.H * 0.3), int(self.H * 0.5)),
                    self.W, self.H
                ))
        else:
            self.particles = []

        # マーク表示アニメーション
        for frame in range(int(FPS * 3.0)):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    if event.key == pygame.K_RETURN and frame > FPS * 0.5:
                        return True

            self.draw_gradient_bg()
            self.draw_stars(frame)

            # 声の情報表示
            q_key = str(self.current_q + 1)
            if q_key in self.voice_map:
                vi = self.voice_map[q_key]
                voice_text = f"こえ: [{vi['id']}] {vi['name']}"
                voice_surf = self.font_small.render(voice_text, True, PINK)
                self.screen.blit(voice_surf, (30, 20))

            # 大きな◯or✕（ズームイン）
            progress = min(1.0, frame / (FPS * 0.3))
            scale = 0.2 + 0.8 * progress
            # バウンス
            if progress >= 1.0:
                t = (frame / FPS - 0.3) / 2.7
                scale = 1.0 + 0.08 * math.sin(t * math.pi * 3) * math.exp(-t * 3)

            mark_size = int(self.H * 0.25 * scale)
            mark_size = max(10, min(mark_size, int(self.H * 0.28)))

            if mark == "◯":
                # 丸を描画
                pygame.draw.circle(
                    self.screen,
                    mark_color,
                    (self.W // 2, int(self.H * 0.3)),
                    mark_size // 2,
                    max(8, mark_size // 8),
                )
            else:
                # バツを描画
                cx, cy = self.W // 2, int(self.H * 0.3)
                half = mark_size // 2
                thickness = max(8, mark_size // 8)
                pygame.draw.line(
                    self.screen,
                    mark_color,
                    (cx - half, cy - half),
                    (cx + half, cy + half),
                    thickness,
                )
                pygame.draw.line(
                    self.screen,
                    mark_color,
                    (cx + half, cy - half),
                    (cx - half, cy + half),
                    thickness,
                )

            # 結果テキスト
            if frame > FPS * 0.3:
                self.draw_text_center(
                    result_text, self.font_large, mark_color, int(self.H * 0.50)
                )

            # 解説
            if frame > FPS * 0.6:
                self.draw_text_center(
                    quiz["explanation"],
                    self.font_medium,
                    WHITE,
                    int(self.H * 0.63),
                )

            # 正解表示
            if frame > FPS * 0.5:
                answer_text = (
                    "こたえ：ほんと！" if quiz["answer"] else "こたえ：うそ！"
                )
                answer_color = GREEN if quiz["answer"] else RED
                self.draw_text_center(
                    answer_text, self.font_medium, answer_color, int(self.H * 0.55)
                )

            # スコア
            score_text = f"スコア: {self.score} / {self.current_q + 1}"
            surf_s = self.font_small.render(score_text, True, YELLOW)
            self.screen.blit(surf_s, (self.W - surf_s.get_width() - 30, 20))

            # ファンシーモード：紙吹雪パーティクル
            if self.fancy:
                for p in self.particles:
                    p.update()
                    p.draw(self.screen)
                self.particles = [p for p in self.particles if p.age < p.life]

            # 次へ指示（遅延表示）
            if frame > FPS * 1.0 and (frame // 25) % 2 == 0:
                self.draw_text_center(
                    "Enter キーで つぎへ",
                    self.font_small,
                    GRAY,
                    int(self.H * 0.92),
                )

            pygame.display.flip()
            self.clock.tick(FPS)

        # 3秒経過後も自動的に次へ
        return True

    def final_screen(self):
        """最終結果画面"""
        self.snd_fanfare.play()

        # ランク決定
        ratio = self.score / len(self.quizzes)
        if ratio >= 0.9:
            rank = "クイズマスター！！"
            rank_color = YELLOW
        elif ratio >= 0.7:
            rank = "すごい！クイズはかせ！"
            rank_color = GREEN
        elif ratio >= 0.5:
            rank = "なかなか！がんばったね！"
            rank_color = CYAN
        else:
            rank = "つぎは もっとがんばろう！"
            rank_color = PINK

        frame = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        return

            self.draw_gradient_bg()
            self.draw_stars(frame)

            # けっか はっぴょう！
            bounce = math.sin(frame * 0.04) * 8
            self.draw_text_center(
                "けっか はっぴょう！",
                self.font_xl,
                YELLOW,
                int(self.H * 0.12 + bounce),
            )

            # スコア（大きく）
            score_display = f"{self.score} / {len(self.quizzes)} もん せいかい！"
            self.draw_text_center(
                score_display, self.font_large, WHITE, int(self.H * 0.35)
            )

            # パーセンテージ
            pct = int(ratio * 100)
            self.draw_text_center(
                f"せいかいりつ {pct}%",
                self.font_medium,
                CYAN,
                int(self.H * 0.48),
            )

            # ランク
            self.draw_text_center(rank, self.font_large, rank_color, int(self.H * 0.62))

            # キラキラ演出
            if ratio >= 0.7:
                for i in range(8):
                    angle = frame * 0.02 + i * math.pi / 4
                    r = 150 + 50 * math.sin(frame * 0.03 + i)
                    x = int(self.W // 2 + r * math.cos(angle))
                    y = int(self.H * 0.62 + r * math.sin(angle))
                    star_color = (
                        min(255, max(0, int(200 + 55 * math.sin(frame * 0.05 + i)))),
                        min(255, max(0, int(200 + 55 * math.sin(frame * 0.05 + i + 2)))),
                        50,
                    )
                    pygame.draw.circle(self.screen, star_color, (x, y), 4)

            # 終了指示
            if (frame // 30) % 2 == 0:
                self.draw_text_center(
                    "Enter キーで おわり",
                    self.font_small,
                    GRAY,
                    int(self.H * 0.90),
                )

            pygame.display.flip()
            self.clock.tick(FPS)
            frame += 1

    def run(self):
        """メインループ"""
        # タイトル画面
        if not self.title_screen():
            pygame.quit()
            return

        # クイズループ
        for i in range(len(self.quizzes)):
            self.current_q = i

            # 問題番号表示
            self.show_question_number(i + 1)

            # 問題 → 回答
            answer = self.question_screen()
            if answer is None:
                pygame.quit()
                return

            # 正解・不正解演出
            cont = self.show_result(answer)
            if not cont:
                pygame.quit()
                return

        # 最終結果
        self.final_screen()
        pygame.quit()


if __name__ == "__main__":
    fancy = "--fancy" in sys.argv
    game = QuizGame(fancy=fancy)
    game.run()
