## 【pygbag WEB公開 技術メモ】

### pygbagとは
pygame製ゲームをブラウザで遊べるWebAssembly形式に変換するツール。
`uv add --dev pygbag` でインストール可能。

### WEB公開手順

```powershell
# 1. ゲームファイルだけのフォルダを作る（.venv を含まないこと！）
#    game-src/ に main.py・claude_draw.py・font.ttf だけを置く

# 2. ビルド＆ローカルサーバー起動
$env:PYTHONUTF8 = "1"
uv run --project "プロジェクトフォルダ" python -m pygbag "game-src\main.py"

# 3. ブラウザで http://localhost:8000/ を開く（初回ロード1〜2分）
```

### アップロードするファイル（公開するフォルダ）

```
game-src/build/web/     ← このフォルダの中身をまるごとアップロード
    index.html          ← ゲームのHTMLページ
    game-src.apk        ← ゲームデータ
    game-src.tar.gz     ← ゲームデータ（itch.io以外向け）
    favicon.png         ← アイコン
```

**itch.io の場合：** `build/web/` フォルダをzipにしてアップロード → HTMLゲームとして公開できる。

### コード変換のルール（Windows版→Web版）

| 変更前（Windows版） | 変更後（Web版） | 理由 |
|---|---|---|
| `import numpy as np` | 削除 | `pygame.sndarray`がWASM非対応でクラッシュ |
| `pygame.sndarray.make_sound()` | `SND_XX = None` に置き換え | 同上 |
| `pygame.mixer.init(...)` | 削除 | 同上 |
| `if SND_XX: SND_XX.play()` | そのまま（Noneチェック済み） | Noneなら何も起きない |
| `def main():` | `async def main():` | pygbag必須 |
| `while running:` ループの末尾 | `await asyncio.sleep(0)` を追加 | ブラウザに制御を返すため |
| `if __name__=="__main__": main()` | `asyncio.run(main())` | pygbag必須 |
| フォントパス（Windowsシステムフォント） | ローカルの `font.ttf` を優先 | WebにWindowsフォントは存在しない |

### 日本語フォントのダウンロード（BIZ UD Gothic）

```powershell
curl.exe -L "https://github.com/google/fonts/raw/main/ofl/bizudpgothic/BIZUDPGothic-Regular.ttf" -o "game-src\font.ttf"
```
※ファイルサイズ約4.5MB。先頭4バイトが `0 1 0 0` なら正常なTTF。

### ハマりポイントと対策

| 問題 | 原因 | 対策 |
|---|---|---|
| `UnicodeDecodeError: cp932` | 日本語WindowsのエンコーディングとpygbagのPython読み込みが衝突 | `$env:PYTHONUTF8 = "1"` を先に設定する |
| pygbagが長時間終わらない | `.venv` フォルダを丸ごとスキャンしてしまう | ゲームファイルだけの `game-src/` サブフォルダを作り、そこを指定する |
| `Unsupported device pixel ratio 1.25` | Windows 125%表示スケール設定と pygame-ce WASM の衝突 | `index.html` の先頭に `Object.defineProperty(window,'devicePixelRatio',{get:()=>1.0})` を注入する（pygbag再ビルド後は再注入が必要） |
| グレー画面のまま止まる | `numpy` + `pygame.sndarray` がWASM環境でクラッシュ | `numpy` を完全に除去。サウンドは `SND_XX = None` でスキップ |
| numpy wheelをダウンロードするのに時間がかかる | `import numpy` があるとpygbagが自動ダウンロード | `numpy` をコードから完全に削除することで不要になる |

### ビルド後に毎回必要な index.html パッチ

```powershell
# pygbag再ビルド後にこのコマンドを実行してdpi問題を修正する
$f = "game-src\build\web\index.html"
$patch = "<html lang=`"en-us`"><script>`nObject.defineProperty(window, 'devicePixelRatio', { get: function() { return 1.0; } });`n</script>"
(Get-Content $f -Raw) -replace '<html lang="en-us">', $patch | Set-Content $f -Encoding UTF8
Write-Host "パッチ完了"
```

---

### セッション終了後にWEB化する際の手順（父→くろーどちゃんへ依頼するとき）

#### 作業の全体像

1. pygbagでビルド（既存の手順通り）
2. ビルドファイルを `docs/<フォルダ名>/` にコピー
3. `docs/index.html` に新しいリンク行を1行追加
4. コミット＆push

#### ステップ①：ビルドとDPRパッチ

```powershell
# ゲームフォルダ（main.pyだけのフォルダ）を指定してビルド
$env:PYTHONUTF8 = "1"
uv run --project "プロジェクトフォルダ" python -m pygbag "ゲームフォルダ\main.py"

# DPRパッチ（ビルドごとに毎回必要）
$f = "ゲームフォルダ\build\web\index.html"
(Get-Content $f -Raw) -replace '<html lang="en-us">', '<html lang="en-us"><script>Object.defineProperty(window,''devicePixelRatio'',{get:function(){return 1.0;}});</script>' | Set-Content $f -Encoding UTF8
Write-Host "パッチ完了"
```

#### ステップ②：docsにコピー

```powershell
# フォルダ名は作品の内容に合わせて決める（英字・ハイフン）
$name = "my-new-game"   # ← ここを変更
$src  = "ゲームフォルダ\build\web"
$dst  = "LearningWithAI\docs\$name"

New-Item -ItemType Directory -Path $dst -Force
Copy-Item "$src\*" $dst -Force
```

#### ステップ③：docs/index.html にリンクを追記

`docs/index.html` の `<!-- 新しい作品はここに追加する -->` の直下に以下を追加：

```html
<a href="my-new-game/" class="item">
  <div class="item-emoji">🎮</div>
  <div class="item-body">
    <div class="item-title">作品タイトル（ひらがな）</div>
    <div class="item-desc">一行の説明</div>
  </div>
  <div class="item-date">YYYY/MM/DD</div>
</a>
```

#### ステップ④：コミット＆push

```powershell
Set-Location "LearningWithAI"
git add docs/
git commit -m "Add <作品名> web game"
git push origin main
```

#### 注意点

| 注意 | 内容 |
|---|---|
| フォルダ名 | 英字・ハイフンのみ。日本語・スペース不可（URLになるため） |
| DPRパッチ | ビルドのたびに index.html が上書きされる。**コピー前ではなく、コピー後**のファイルにパッチを当てること |
| index.htmlの追加順 | 上に追加すると「新しい順」になる |
| ゲーム以外もOK | ゲームでなくてもリストに追加していい（アニメ・クイズ・絵など何でも） |
