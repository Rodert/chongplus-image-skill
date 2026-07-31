# ChongPlus Image Skill

ChongPlus Image API で画像生成と参照画像の編集を行う Agent Skill です。

[English](../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [Español](README.es.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

## 機能

- `gpt-image-2` によるテキストからの画像生成
- 参照画像を使った画像編集
- API Key を現在のユーザーのローカル設定ディレクトリに保存
- Base64 と URL の画像レスポンスに対応
- Python 標準ライブラリのみを使用

## 必要条件

- Codex など、Agent Skills とローカルスクリプト実行に対応するクライアント
- Python 3.9 以上
- `gpt-image-2` の権限を持つ ChongPlus API Key

通常のチャットクライアントでは、Skill の自動インストール、ローカルコードの実行、安全なキー保存はできません。その場合は API を直接使用してください。

## Codex へのインストールと使用

次の内容を Codex にそのまま貼り付けてください。

```text
ChongPlus Image Skill をインストールして使用してください:
https://github.com/Rodert/chongplus-image-skill

初回使用時には、ChongPlus API Key の入力を自発的に求めてください。キーはローカルのユーザー設定に安全に保存し、その後は直接読み込んで使用してください。環境変数を手動で設定するよう求めないでください。

公式ドキュメント:
https://api.chongplus.plus/tools/image-studio/docs/
```

インストール後、新しい Codex の会話で画像の生成または編集を依頼してください。付属クライアントはキーをローカルに保存し、以後の ChongPlus 画像リクエストで自動的に再利用します。

API Key をお持ちでない場合は、[ChongPlus Keys](https://api.chongplus.plus/keys) にログインし、キーを作成して画像生成グループを選択してください。

## ローカルでの使用

リポジトリのルートで実行します。

```bash
python3 scripts/chongplus_image.py config --set-key
python3 scripts/chongplus_image.py generate \
  --prompt "A cinematic mountain landscape at sunrise" \
  --size 1536x1024 --output-dir ./outputs
```

キーは macOS/Linux では `~/.config/chongplus-image/config.json`（または `$XDG_CONFIG_HOME`）、Windows では `%APPDATA%\\chongplus-image\\config.json` に保存されます。Unix ではディレクトリは `0700`、ファイルは `0600` です。

`config --check` はローカル設定のみを確認します。実際の生成はクォータを消費する場合があります。`403 / error code: 1010` の場合は、既定のリクエストヘッダーを変更せず、ChongPlus 運用者に Cloudflare のファイアウォールイベントを確認してもらってください。

## Skill のカスタマイズ

独自の画像ワークフローが必要な場合は、このリポジトリと [ChongPlus Image API ドキュメント](https://api.chongplus.plus/tools/image-studio/docs/) を AI Agent に渡してください。エンドポイント、パラメーター、対応サイズ、レスポンス形式はこのドキュメントを正とします。
