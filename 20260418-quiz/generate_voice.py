"""
VoiceVox事前音声生成スクリプト

VoiceVoxが http://localhost:50021 で起動している状態で実行してください。
quiz_data.py の各問題について、question/correct/wrong の音声を生成します。
生成された音声は sounds/ フォルダに保存されます。
問題ごとにランダムな声を割り当て、voice_map.json に記録します。

使い方:
  uv run --project "フルパス" python "フルパス/generate_voice.py"
"""

import os
import sys
import json
import random
import urllib.request
import urllib.parse

# quiz_data.py を同じフォルダから読み込む
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quiz_data import QUIZZES

VOICEVOX_URL = "http://localhost:50021"
SPEED = 1.0

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")

# 子供向けに聞き取りやすい声をピックアップ（ノーマル系中心）
VOICE_POOL = [
    {"id": 3,  "name": "ずんだもん"},
    {"id": 8,  "name": "春日部つむぎ"},
    {"id": 10, "name": "雨晴はう"},
    {"id": 14, "name": "冥鳴ひまり"},
    {"id": 16, "name": "九州そら"},
    {"id": 20, "name": "もち子さん"},
    {"id": 30, "name": "No.7 アナウンス"},
    {"id": 47, "name": "ナースロボ＿タイプＴ"},
    {"id": 54, "name": "春歌ナナ"},
    {"id": 61, "name": "中国うさぎ"},
    {"id": 67, "name": "栗田まろん"},
    {"id": 69, "name": "満別花丸"},
    {"id": 74, "name": "琴詠ニア"},
    {"id": 107, "name": "東北ずん子"},
    {"id": 108, "name": "東北きりたん"},
]


def generate_audio(text, output_path, speaker_id):
    """VoiceVox APIで音声を生成してWAVファイルとして保存"""
    # 1. audio_query
    params = urllib.parse.urlencode({"text": text, "speaker": speaker_id})
    req = urllib.request.Request(
        f"{VOICEVOX_URL}/audio_query?{params}", method="POST"
    )
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        query = json.loads(resp.read())

    # スピード調整
    query["speedScale"] = SPEED

    # 2. synthesis
    params2 = urllib.parse.urlencode({"speaker": speaker_id})
    req2 = urllib.request.Request(
        f"{VOICEVOX_URL}/synthesis?{params2}",
        data=json.dumps(query).encode("utf-8"),
        method="POST",
    )
    req2.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req2) as resp2:
        wav_data = resp2.read()

    with open(output_path, "wb") as f:
        f.write(wav_data)

    print(f"  [OK] {output_path} ({len(wav_data)} bytes)")


def main():
    os.makedirs(SOUNDS_DIR, exist_ok=True)

    total = len(QUIZZES)
    print(f"=== VoiceVox音声生成 ({total}問 × 3 = {total * 3}ファイル) ===\n")

    # 問題ごとにランダムに声を割り当て（連続で同じ声にならないようにする）
    voice_map = {}
    last_voice_id = None
    shuffled_pool = list(VOICE_POOL)

    for i in range(total):
        # 前回と同じ声を避ける
        candidates = [v for v in shuffled_pool if v["id"] != last_voice_id]
        if not candidates:
            candidates = shuffled_pool
        voice = random.choice(candidates)
        voice_map[str(i + 1)] = {"id": voice["id"], "name": voice["name"]}
        last_voice_id = voice["id"]

    # voice_map.json に保存（quiz.py が画面表示に使う）
    voice_map_path = os.path.join(SOUNDS_DIR, "voice_map.json")
    with open(voice_map_path, "w", encoding="utf-8") as f:
        json.dump(voice_map, f, ensure_ascii=False, indent=2)
    print(f"声の割り当て: {voice_map_path}")
    for q_num, info in voice_map.items():
        print(f"  Q{q_num}: [{info['id']}] {info['name']}")
    print()

    for i, quiz in enumerate(QUIZZES):
        q_num = i + 1
        voice_info = voice_map[str(q_num)]
        speaker_id = voice_info["id"]
        voice_name = voice_info["name"]
        print(f"--- だい{q_num}もん （声: [{speaker_id}] {voice_name}）---")

        # 問題読み上げ
        generate_audio(
            quiz["voice_question"],
            os.path.join(SOUNDS_DIR, f"q{q_num}_question.wav"),
            speaker_id,
        )

        # 正解時
        generate_audio(
            quiz["voice_correct"],
            os.path.join(SOUNDS_DIR, f"q{q_num}_correct.wav"),
            speaker_id,
        )

        # 不正解時
        generate_audio(
            quiz["voice_wrong"],
            os.path.join(SOUNDS_DIR, f"q{q_num}_wrong.wav"),
            speaker_id,
        )

        print()

    print(f"=== 完了！ {total * 3}ファイル生成しました ===")
    print(f"保存先: {SOUNDS_DIR}")


if __name__ == "__main__":
    main()
