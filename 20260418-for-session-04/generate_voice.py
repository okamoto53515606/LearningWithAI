"""
VoiceVox事前音声生成スクリプト（画像クイズ版）

VoiceVoxが http://localhost:50021 で起動している状態で実行してください。
quiz_data.py の各問題について、question/correct/wrong の音声を生成します。

使い方:
  uv run --project "フルパス" python "フルパス/generate_voice.py"
"""

import os
import sys
import json
import random
import urllib.request
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quiz_data import QUIZZES

VOICEVOX_URL = "http://localhost:50021"
SPEED = 1.0
SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")

# くろーどちゃんの声（しこくめたん・ノーマル）
CLAUDE_SPEAKER_ID = 2

# ランダム声プール（問題読み上げ用）
VOICE_POOL = [
    {"id": 3,  "name": "ずんだもん"},
    {"id": 8,  "name": "春日部つむぎ"},
    {"id": 10, "name": "雨晴はう"},
    {"id": 14, "name": "冥鳴ひまり"},
    {"id": 16, "name": "九州そら"},
    {"id": 20, "name": "もち子さん"},
    {"id": 47, "name": "ナースロボ＿タイプＴ"},
    {"id": 54, "name": "春歌ナナ"},
    {"id": 67, "name": "栗田まろん"},
    {"id": 69, "name": "満別花丸"},
    {"id": 74, "name": "琴詠ニア"},
    {"id": 107, "name": "東北ずん子"},
    {"id": 108, "name": "東北きりたん"},
]


def generate_audio(text, output_path, speaker_id):
    """VoiceVox APIで音声を生成してWAVファイルとして保存"""
    params = urllib.parse.urlencode({"text": text, "speaker": speaker_id})
    req = urllib.request.Request(
        f"{VOICEVOX_URL}/audio_query?{params}", method="POST"
    )
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        query = json.loads(resp.read())

    query["speedScale"] = SPEED

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
    print(f"=== VoiceVox音声生成 ({total}問 × 2 = {total * 2}ファイル) ===\n")

    # 問題ごとにランダムに声を割り当て
    voice_map = {}
    last_voice_id = None

    for i in range(total):
        candidates = [v for v in VOICE_POOL if v["id"] != last_voice_id]
        if not candidates:
            candidates = VOICE_POOL
        voice = random.choice(candidates)
        voice_map[str(i + 1)] = {"id": voice["id"], "name": voice["name"]}
        last_voice_id = voice["id"]

    voice_map_path = os.path.join(SOUNDS_DIR, "voice_map.json")
    with open(voice_map_path, "w", encoding="utf-8") as f:
        json.dump(voice_map, f, ensure_ascii=False, indent=2)
    print(f"声の割り当て: {voice_map_path}\n")

    for i, quiz in enumerate(QUIZZES):
        q_num = quiz["number"]
        voice_info = voice_map[str(q_num)]
        speaker_id = voice_info["id"]
        voice_name = voice_info["name"]
        print(f"--- Q{q_num} （声: [{speaker_id}] {voice_name}）---")

        # 問題読み上げ
        q_path = os.path.join(SOUNDS_DIR, f"q{q_num}_question.wav")
        if not os.path.exists(q_path):
            generate_audio(quiz["voice_question"], q_path, speaker_id)
        else:
            print(f"  [SKIP] {q_path} (すでにあります)")

        # 正解発表（くろーどちゃんの声）
        a_path = os.path.join(SOUNDS_DIR, f"q{q_num}_answer.wav")
        if not os.path.exists(a_path):
            generate_audio(quiz["voice_answer"], a_path, CLAUDE_SPEAKER_ID)
        else:
            print(f"  [SKIP] {a_path} (すでにあります)")

        print()

    print(f"=== 完了！ {total * 2}ファイル ===")


if __name__ == "__main__":
    main()
