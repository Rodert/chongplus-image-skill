# ChongPlus Image Skill

透過 ChongPlus Image API 產生圖片與編輯參考圖的 Agent Skill。

[English](../README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

## 功能

- 使用 `gpt-image-2` 文字生成圖片
- 依參考圖編輯圖片
- 將 API Key 儲存到目前使用者的本機設定目錄
- 支援 Base64 與 URL 圖片回應
- 僅使用 Python 標準函式庫

## 需求

- 支援 Agent Skills 與本機腳本執行的客戶端，例如 Codex
- Python 3.9 以上
- 已取得 `gpt-image-2` 權限的 ChongPlus API Key

一般聊天客戶端無法自動安裝 Skill、執行本機程式或安全儲存金鑰，請直接使用 API。

## 在 Codex 安裝並使用

將以下內容直接複製給 Codex：

```text
請安裝並使用 ChongPlus 生圖 Skill：
https://github.com/Rodert/chongplus-image-skill

首次使用時請主動提示我輸入 ChongPlus API Key，並自動安全儲存到本機設定中，之後直接讀取使用；不要要求我手動設定環境變數。

使用文件：
https://api.chongplus.plus/tools/image-studio/docs/
```

安裝後開啟新的 Codex 對話，即可要求產生或編輯圖片。隨附客戶端會將金鑰儲存在本機，並在後續 ChongPlus 生圖請求中自動讀取。

還沒有 API Key？請前往 [ChongPlus 金鑰頁面](https://api.chongplus.plus/keys) 登入、建立金鑰，並選擇「生圖」分組。

## 本機使用

在倉庫根目錄執行：

```bash
python3 scripts/chongplus_image.py config --set-key
python3 scripts/chongplus_image.py generate \
  --prompt "A cinematic mountain landscape at sunrise" \
  --size 1536x1024 --output-dir ./outputs
```

金鑰會儲存至 macOS/Linux 的 `~/.config/chongplus-image/config.json`（或 `$XDG_CONFIG_HOME`），Windows 的 `%APPDATA%\\chongplus-image\\config.json`。Unix 目錄權限為 `0700`，檔案權限為 `0600`。

`config --check` 僅檢查本機設定。實際產圖可能消耗額度。若出現 `403 / error code: 1010`，請保留客戶端預設請求標頭，並請 ChongPlus 營運方檢查 Cloudflare 防火牆事件。

## 自訂 Skill

需要自訂生圖工作流程時，可將本倉庫和 [ChongPlus 生圖 API 文件](https://api.chongplus.plus/tools/image-studio/docs/) 一併交給 AI Agent。端點、參數、支援尺寸與回應格式應以該文件為準。
