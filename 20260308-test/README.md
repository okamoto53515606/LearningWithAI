# 20260308-test

## 概要
LearningWithAI プロジェクトの動作確認用テストアプリ（2026-03-08 作成）。

以下の技術スタックと MCP ツールの疎通確認を行った。

## 確認済み項目

| 項目 | 結果 |
|------|------|
| Brave Search MCP (`brave_image_search`) | ✅ 画像検索・URL取得 |
| curl.exe による画像ダウンロード | ✅ `images/` フォルダへ保存 |
| VoiceVox MCP `get_voices` | ✅ 四国めたん含む117音声を取得 |
| VoiceVox MCP `text_to_speech` (speaker_id:2, speed:1.2) | ✅ 四国めたん（ノーマル）で再生・WAV保存 |
| uv + Python 3.12 + pygame 環境 | ✅ `uv run python main.py` で起動 |
| numpy 音声合成（ステレオ対応） | ✅ `np.column_stack` でステレオ化 |
| PowerShell 実行ポリシー | ✅ `RemoteSigned (CurrentUser)` 設定済み |

## main.py の内容

「무궁화 꽃이 피었습니다（だるまさんがころんだ）」アニメーションデモ。

- **人形（ヨンヒ）**：pygame で描画。後ろ向き ↔ 正面向きをアニメーションで切り替え。正面時は Brave でDLしたイカゲーム人形の顔画像を使用。
- **参加者**：番号付きジャンプスーツのキャラが画面を歩く。
- **音楽**：numpy で `무궁화 꽃이 피었습니다` のメロディーを合成して再生。
- **状態機械**：GREEN（進め）→ TURN（振り返り）→ RED（止まれ）をループ。

## 環境

- Python: 3.12
- pygame: 2.6.1
- numpy: 2.4.2
- 管理: uv

## 起動方法

```powershell
uv run python main.py
# ESC で終了
```
