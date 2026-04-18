"""
たろうくんの がぞうクイズ！
くろーどちゃんと いっしょにつくるクイズゲーム

- たろうくんのオリジナルもんだい20問
- わなの がぞうで まどわす！
- VoiceVoxのこえで もんだいをだす

操作:
  ↑↓ キー: こたえを えらぶ
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
    "マリオカートワールド": (255, 100, 50),
    "ゼルダ ブレスオブザワイルド": (50, 200, 50),
    "ゼルダ ティアーズオブザキングダム": (50, 220, 100),
    "ルイージマンション3": (100, 50, 200),
    "マインクラフト": (100, 200, 50),
    "マリオパーティージャンボリー": (255, 150, 50),
    "マリオメーカー2": (255, 50, 50),
    "たいこのたつじん": (255, 100, 100),
    "ペーパーマリオRPG": (200, 50, 50),
    "マリオvsドンキーコング": (255, 200, 50),
    "スーパーマリオ3Dワールド": (50, 150, 255),
    "カービィディスカバリー": (255, 150, 200),
    "プリンセスピーチ ショータイム": (255, 180, 200),
}


def generate_sound_pinpon(sample_rate=44100):
    """ピンポーン（正解音）"""
    duration = 0.6
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    freq1, freq2 = 523.25, 659.25
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
    wave = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))
    wave = (wave * envelope * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)


def generate_sound_jajan(sample_rate=44100):
    """ジャジャーン（問題登場音）"""
    duration = 0.8
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    freq1, freq2, freq3 = 261.63, 329.63, 392.0
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
        color = tuple(int(c * alpha) for c in self.color)
        s = self.size
        points = []
        for dx, dy in [(-s, -s), (s, -s), (s, s), (-s, s)]:
            rad = math.radians(self.rotation)
            rx = dx * math.cos(rad) - dy * math.sin(rad)
            ry = dx * math.sin(rad) + dy * math.cos(rad)
            points.append((int(self.x + rx), int(self.y + ry)))
        pygame.draw.polygon(surface, color, points)


class QuizGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        info = pygame.display.Info()
        self.W = int(info.current_w * 0.65)
        self.H = int(info.current_h * 0.8)
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("たろうくんの がぞうクイズ！")

        self.clock = pygame.time.Clock()

        # フォント
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

        self.font_xl = pygame.font.Font(self.font_path, int(self.H * 0.10))
        self.font_large = pygame.font.Font(self.font_path, int(self.H * 0.065))
        self.font_medium = pygame.font.Font(self.font_path, int(self.H * 0.04))
        self.font_small = pygame.font.Font(self.font_path, int(self.H * 0.03))

        # 効果音
        self.snd_pinpon = generate_sound_pinpon()
        self.snd_buzzer = generate_sound_buzzer()
        self.snd_jajan = generate_sound_jajan()
        self.snd_select = generate_sound_select()
        self.snd_decide = generate_sound_decide()
        self.snd_drumroll = generate_sound_drumroll()
        self.snd_fanfare = generate_sound_fanfare()

        # VoiceVox事前生成音声
        self.voices = {}
        sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
        if os.path.isdir(sounds_dir):
            for fname in os.listdir(sounds_dir):
                if fname.endswith(".wav"):
                    key = fname[:-4]
                    try:
                        self.voices[key] = pygame.mixer.Sound(
                            os.path.join(sounds_dir, fname)
                        )
                    except Exception:
                        pass

        # 罠画像の読み込み（images/q1_trap.png, q2_trap.png, ...）
        self.trap_images = {}
        images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        if os.path.isdir(images_dir):
            for fname in os.listdir(images_dir):
                if fname.startswith("q") and "_trap" in fname:
                    key = fname.split("_trap")[0]  # "q1", "q2", ...
                    path = os.path.join(images_dir, fname)
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        # 画面の30%の高さに調整
                        target_h = int(self.H * 0.30)
                        ratio = target_h / img.get_height()
                        target_w = int(img.get_width() * ratio)
                        # 最大幅も制限
                        if target_w > int(self.W * 0.45):
                            target_w = int(self.W * 0.45)
                            ratio = target_w / img.get_width()
                            target_h = int(img.get_height() * ratio)
                        self.trap_images[key] = pygame.transform.smoothscale(
                            img, (target_w, target_h)
                        )
                    except Exception:
                        pass

        self.quizzes = QUIZZES
        self.current_q = 0
        self.score = 0
        self.selected = 0
        self.particles = []

    def play_voice(self, key):
        """VoiceVox事前生成音声を再生"""
        if key in self.voices:
            self.voices[key].play()

    def draw_text_center(self, text, font, color, y, shadow=True):
        """テキストを中央揃えで描画"""
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

    def draw_text_at(self, text, font, color, x, y, shadow=True):
        """テキストを指定位置に描画"""
        if shadow:
            shadow_surf = font.render(text, True, (0, 0, 0))
            self.screen.blit(shadow_surf, (x + 2, y + 2))
        surf = font.render(text, True, color)
        self.screen.blit(surf, (x, y))

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
            pygame.draw.circle(
                self.screen, (brightness, brightness, min(255, brightness + 20)),
                (x, y), size,
            )

    def draw_trap_image(self, q_num, frame):
        """罠画像を表示（あれば）"""
        key = f"q{q_num}"
        if key in self.trap_images:
            img = self.trap_images[key]
            # 画面右側に表示、少しゆらゆら
            bob = math.sin(frame * 0.03) * 5
            x = self.W - img.get_width() - int(self.W * 0.05)
            y = int(self.H * 0.20 + bob)
            # 枠を描画
            border_rect = pygame.Rect(x - 4, y - 4, img.get_width() + 8, img.get_height() + 8)
            pygame.draw.rect(self.screen, YELLOW, border_rect, 3, border_radius=8)
            self.screen.blit(img, (x, y))
            # 「ヒント？」ラベル
            self.draw_text_at("ヒント？🤔", self.font_small, YELLOW,
                            x, y - int(self.H * 0.04))

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

            bounce = math.sin(frame * 0.05) * 10
            title_y = int(self.H * 0.20 + bounce)

            # レインボータイトル
            title_text = "たろうくんの"
            total_w = self.font_large.size(title_text)[0]
            start_x = (self.W - total_w) // 2
            cx = start_x
            for ci, ch in enumerate(title_text):
                hue = (frame * 3 + ci * 25) % 360
                r = max(0, min(255, int(255 * max(0, min(1, abs((hue / 60) % 6 - 3) - 1)))))
                g = max(0, min(255, int(255 * max(0, min(1, 2 - abs((hue / 60) % 6 - 2))))))
                b = max(0, min(255, int(255 * max(0, min(1, 2 - abs((hue / 60) % 6 - 4))))))
                ch_surf = self.font_large.render(ch, True, (r, g, b))
                self.screen.blit(ch_surf, (cx, title_y))
                cx += ch_surf.get_width()

            self.draw_text_center(
                "がぞうクイズ！", self.font_xl, YELLOW, int(self.H * 0.33 + bounce)
            )
            self.draw_text_center(
                "わなの がぞうに だまされるな！",
                self.font_medium, CYAN, int(self.H * 0.50),
            )

            # スタート指示
            if (frame // 30) % 2 == 0:
                self.draw_text_center(
                    "Enter キーで スタート！",
                    self.font_medium, GREEN, int(self.H * 0.72),
                )

            self.draw_text_center(
                f"ぜんぶで {len(self.quizzes)}もん",
                self.font_small, GRAY, int(self.H * 0.85),
            )

            pygame.display.flip()
            self.clock.tick(FPS)
            frame += 1

    def show_question_number(self, q_num):
        """「だい○もん！」ズームイン"""
        self.snd_drumroll.play()
        for frame in range(90):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            self.draw_gradient_bg()
            self.draw_stars(frame)

            progress = min(1.0, frame / 60)
            scale = 0.3 + 0.7 * progress
            alpha = min(255, int(progress * 255))

            text = f"だい {q_num} もん！"
            size = int(self.H * 0.12 * scale)
            font = pygame.font.Font(self.font_path, max(10, size))
            surf = font.render(text, True, YELLOW)
            surf.set_alpha(alpha)
            rect = surf.get_rect(center=(self.W // 2, self.H // 2))
            self.screen.blit(surf, rect)

            pygame.display.flip()
            self.clock.tick(FPS)
        return True

    def question_screen(self, quiz, q_num):
        """問題画面 + 罠画像 + 選択"""
        q_type = quiz["type"]
        frame = 0
        self.selected = 0
        answered = False
        show_result = False
        result_correct = False
        result_frame = 0
        self.particles = []

        # 問題の選択肢を作成
        if q_type == "yesno":
            choices = ["⭕ ほんと", "❌ うそ"]
        elif q_type == "number":
            choices = ["あとで くろーどちゃんに こたえる！"]
        else:  # choice
            choices = ["あとで くろーどちゃんに こたえる！"]

        # 声で問題を読み上げ
        voice_key = f"q{q_num}_question"
        self.play_voice(voice_key)
        self.snd_jajan.play()

        game_name = quiz.get("game", "")
        game_color = GAME_COLORS.get(game_name, WHITE)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if not answered and not show_result:
                        if q_type == "yesno":
                            if event.key in (pygame.K_UP, pygame.K_DOWN):
                                self.selected = 1 - self.selected
                                self.snd_select.play()
                            elif event.key == pygame.K_RETURN:
                                self.snd_decide.play()
                                answered = True
                                # 判定
                                user_answer = (self.selected == 0)  # 0=ほんと=True
                                result_correct = (user_answer == quiz["answer"])
                                show_result = True
                                result_frame = 0
                                if result_correct:
                                    self.snd_pinpon.play()
                                    self.score += 1
                                    # 紙吹雪
                                    for _ in range(30):
                                        self.particles.append(
                                            Particle(
                                                random.randint(0, self.W),
                                                self.H,
                                                self.W, self.H,
                                            )
                                        )
                                else:
                                    self.snd_buzzer.play()
                        else:
                            # number/choice: Enterで次へ（声で答える問題）
                            if event.key == pygame.K_RETURN:
                                return True
                    elif show_result:
                        if event.key == pygame.K_RETURN and result_frame > 60:
                            # 正解/不正解の声を再生
                            if result_correct:
                                self.play_voice(f"q{q_num}_correct")
                            else:
                                self.play_voice(f"q{q_num}_wrong")
                            return result_correct

            self.draw_gradient_bg()
            self.draw_stars(frame)

            # ゲーム名
            self.draw_text_center(
                f"【{game_name}】", self.font_small, game_color, int(self.H * 0.05)
            )

            # 問題番号
            self.draw_text_at(
                f"Q{q_num}", self.font_medium, ORANGE,
                int(self.W * 0.05), int(self.H * 0.05),
            )

            # スコア
            self.draw_text_at(
                f"スコア: {self.score}", self.font_small, WHITE,
                int(self.W * 0.75), int(self.H * 0.05),
            )

            # 問題文（左側に表示して、右に罠画像のスペースを空ける）
            q_text = quiz["question"]
            text_x_center = self.W // 2
            # 罠画像があるなら左寄せ
            trap_key = f"q{q_num}"
            if trap_key in self.trap_images:
                text_x_center = int(self.W * 0.30)

            lines = q_text.split("\n")
            for i, line in enumerate(lines):
                y_pos = int(self.H * 0.18) + i * self.font_medium.get_linesize()
                # 影
                shadow_surf = self.font_medium.render(line, True, (0, 0, 0))
                shadow_rect = shadow_surf.get_rect(center=(text_x_center + 2, y_pos + 2))
                self.screen.blit(shadow_surf, shadow_rect)
                surf = self.font_medium.render(line, True, WHITE)
                rect = surf.get_rect(center=(text_x_center, y_pos))
                self.screen.blit(surf, rect)

            # 罠画像を表示
            self.draw_trap_image(q_num, frame)

            # 選択肢（yesnoのとき）
            if q_type == "yesno" and not show_result:
                for i, choice in enumerate(choices):
                    cy = int(self.H * 0.60) + i * int(self.H * 0.10)
                    if i == self.selected:
                        # 選択中: 明るい背景
                        sel_rect = pygame.Rect(
                            int(self.W * 0.15), cy - 5,
                            int(self.W * 0.70), int(self.H * 0.08),
                        )
                        pygame.draw.rect(self.screen, (60, 60, 120), sel_rect, border_radius=10)
                        pygame.draw.rect(self.screen, CYAN, sel_rect, 3, border_radius=10)
                        color = YELLOW
                    else:
                        color = GRAY
                    self.draw_text_center(choice, self.font_large, color, cy)
            elif q_type != "yesno" and not show_result:
                # 自由回答のガイド
                self.draw_text_center(
                    "こたえがわかったら、こえで おしえてね！",
                    self.font_medium, CYAN, int(self.H * 0.55),
                )
                self.draw_text_center(
                    "Enter キーで つぎへ",
                    self.font_small, GREEN, int(self.H * 0.70),
                )

            # 結果表示
            if show_result:
                result_frame += 1
                if result_correct:
                    # ◯ アニメーション
                    size = min(result_frame * 4, int(self.H * 0.15))
                    pygame.draw.circle(
                        self.screen, GREEN,
                        (self.W // 2, int(self.H * 0.65)), size, 8,
                    )
                    if result_frame > 20:
                        self.draw_text_center(
                            "せいかい！", self.font_large, GREEN, int(self.H * 0.78),
                        )
                else:
                    # ✕ アニメーション
                    size = min(result_frame * 4, int(self.H * 0.12))
                    cx, cy = self.W // 2, int(self.H * 0.65)
                    pygame.draw.line(self.screen, RED,
                                   (cx - size, cy - size), (cx + size, cy + size), 8)
                    pygame.draw.line(self.screen, RED,
                                   (cx + size, cy - size), (cx - size, cy + size), 8)
                    if result_frame > 20:
                        self.draw_text_center(
                            "ざんねん！", self.font_large, RED, int(self.H * 0.78),
                        )

                if result_frame > 60:
                    self.draw_text_center(
                        "Enter キーで つぎへ",
                        self.font_small, GRAY, int(self.H * 0.90),
                    )

            # パーティクル
            for p in self.particles:
                p.update()
                p.draw(self.screen)
            self.particles = [p for p in self.particles if p.age < p.life]

            pygame.display.flip()
            self.clock.tick(FPS)
            frame += 1

    def result_screen(self):
        """最終結果画面"""
        self.snd_fanfare.play()

        total = len(self.quizzes)
        # yesno問題の数だけスコア対象
        yesno_count = sum(1 for q in self.quizzes if q["type"] == "yesno")

        # ランク判定
        if yesno_count > 0:
            ratio = self.score / yesno_count
        else:
            ratio = 0
        if ratio >= 0.9:
            rank = "S  ★ てんさい！ ★"
            rank_color = YELLOW
        elif ratio >= 0.7:
            rank = "A  すごい！"
            rank_color = GREEN
        elif ratio >= 0.5:
            rank = "B  いいかんじ！"
            rank_color = CYAN
        else:
            rank = "C  つぎがんばろう！"
            rank_color = PINK

        frame = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        return

            self.draw_gradient_bg()
            self.draw_stars(frame)

            self.draw_text_center(
                "けっかはっぴょう！", self.font_xl, YELLOW, int(self.H * 0.12),
            )

            self.draw_text_center(
                f"まるばつもんだい: {self.score} / {yesno_count} せいかい",
                self.font_large, WHITE, int(self.H * 0.35),
            )

            self.draw_text_center(
                f"ランク: {rank}", self.font_large, rank_color, int(self.H * 0.52),
            )

            if (frame // 30) % 2 == 0:
                self.draw_text_center(
                    "Enter キーで おわり",
                    self.font_small, GRAY, int(self.H * 0.85),
                )

            pygame.display.flip()
            self.clock.tick(FPS)
            frame += 1

    def run(self):
        """メインループ"""
        if not self.title_screen():
            pygame.quit()
            return

        for i, quiz in enumerate(self.quizzes):
            q_num = quiz["number"]
            if not self.show_question_number(q_num):
                break
            result = self.question_screen(quiz, q_num)
            if result is None:
                break

        self.result_screen()
        pygame.quit()


def main():
    game = QuizGame()
    game.run()


if __name__ == "__main__":
    main()
