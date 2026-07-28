# ChongPlus Image Skill

通过 ChongPlus Image API 生成图片和编辑参考图的 Agent Skill。

[English](../README.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

## 功能

- 使用 `gpt-image-2` 文生图
- 基于参考图进行编辑
- 自动将 API Key 保存到当前用户的本机配置目录
- 支持 Base64 和 URL 格式的图片响应
- 仅依赖 Python 标准库

## 要求

- 支持 Agent Skills 和本地脚本执行的客户端，例如 Codex
- Python 3.9 或更高版本
- 已开通 `gpt-image-2` 的 ChongPlus API Key

普通聊天客户端无法自动安装 Skill、执行本地脚本或安全保存密钥，请直接使用 API。

## 在 Codex 中安装

让 Codex 安装此仓库，或运行其 Skill 安装器：

```bash
python3 /path/to/install-skill-from-github.py \
  --repo Rodert/chongplus-image-skill --path .
```

安装后在新的 Codex 对话中说“使用 ChongPlus 生成一张日出山景”。首次使用时会请求 API Key 并保存到本机，不需要配置环境变量。

还没有 API Key？请前往 [ChongPlus 密钥页面](https://api.chongplus.plus/keys) 登录、创建密钥，并选择“生图”分组。

## 本地使用

在仓库根目录运行：

```bash
python3 scripts/chongplus_image.py config --set-key
python3 scripts/chongplus_image.py generate \
  --prompt "A cinematic mountain landscape at sunrise" \
  --size 1536x1024 --output-dir ./outputs
```

密钥会保存至 macOS/Linux 的 `~/.config/chongplus-image/config.json`（或 `$XDG_CONFIG_HOME`），Windows 的 `%APPDATA%\\chongplus-image\\config.json`。Unix 系统上目录权限为 `0700`，文件权限为 `0600`。

`config --check` 只检查本地配置。真实生成请求可能消耗额度。若出现 `403 / error code: 1010`，请保留客户端默认请求头，并请 ChongPlus 运营方检查 Cloudflare 防火墙事件。

## 定制 Skill

需要自定义生图工作流时，可将本仓库和 [ChongPlus 生图 API 文档](https://api.chongplus.plus/tools/image-studio/docs/) 一并交给 AI Agent。接口、参数、支持尺寸和响应格式应以该文档为准。
