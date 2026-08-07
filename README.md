# ChongPlus Image Skill

An Agent Skill for text-to-image and image editing through the ChongPlus Image API.

Languages: [English](README.md) | [简体中文](docs/README.zh-CN.md) | [繁體中文](docs/README.zh-TW.md) | [日本語](docs/README.ja.md) | [Español](docs/README.es.md) | [Русский](docs/README.ru.md) | [한국어](docs/README.ko.md)

## What it does

- Generates images with `gpt-image-2`
- Edits a supplied reference image
- Stores the API key in the current user's local configuration directory
- Supports Base64 and URL image responses
- Routes image requests through `https://ai.chongplus.plus` first and falls back to the official API address, `https://api.chongplus.plus`, only for network failures or timeouts
- Uses standard API client headers required to avoid a known Cloudflare `403 / 1010` block
- Uses Python standard library only

## Requirements

- An Agent Skills-compatible client, such as Codex
- Python 3.9 or newer
- Permission for the client to execute local Python and write user configuration files
- A ChongPlus API Key with access to `gpt-image-2`

This repository cannot make arbitrary chat clients execute local code or securely store credentials. In those clients, use the API directly instead.

## Install and use in Codex

Copy the following into Codex:

```text
Install and use the ChongPlus Image Skill from https://github.com/Rodert/chongplus-image-skill

On first use, proactively ask me for my ChongPlus API Key. Save it securely in the local user configuration, then read and reuse it automatically for later requests. Do not ask me to configure an environment variable.

Follow the official ChongPlus Image Studio documentation: https://api.chongplus.plus/tools/image-studio/docs/
```

After installation, start a new Codex turn and ask it to generate or edit an image. The bundled client stores the key locally and reuses it for later ChongPlus image requests.

Need an API Key? Sign in at [ChongPlus Keys](https://api.chongplus.plus/keys), create a key, and select the image-generation group.

## Local use

Run commands from the repository root:

```bash
python3 scripts/chongplus_image.py config --set-key
python3 scripts/chongplus_image.py generate \
  --prompt "A cinematic mountain landscape at sunrise" \
  --size 1536x1024 --output-dir ./outputs
```

For non-interactive automation, pass the key only on standard input:

```bash
printf '%s' "$KEY" | python3 scripts/chongplus_image.py config --set-key-stdin
```

Do not place API keys in command arguments, repository files, or committed configuration.

## Credential storage

| Platform | Path |
| --- | --- |
| macOS/Linux | `$XDG_CONFIG_HOME/chongplus-image/config.json`, or `~/.config/chongplus-image/config.json` |
| Windows | `%APPDATA%\\chongplus-image\\config.json` |

On Unix systems the client applies directory mode `0700` and file mode `0600`. Windows uses its normal per-user profile access controls.

## Connection checks and failures

`python3 scripts/chongplus_image.py config --check` only verifies that a local key file exists. ChongPlus does not document a free authentication-only endpoint, so validating a key through image generation may consume quota.

If a request returns `403` and `error code: 1010`, Cloudflare blocked it before the ChongPlus application handled it. The bundled client sends the documented `Authorization` header plus `Accept: application/json` and a stable `User-Agent`; do not remove these headers. Ask the ChongPlus operator to inspect its Cloudflare firewall events for the request time.

See [references/troubleshooting.md](references/troubleshooting.md) for the error table and [references/api.md](references/api.md) for the endpoint summary.

## Customizing the Skill

Give an AI Agent the official [ChongPlus Image API documentation](https://api.chongplus.plus/tools/image-studio/docs/) together with this repository when you need a custom image workflow. The documentation is the source of truth for endpoints, parameters, supported sizes, and response formats.

## Development

```bash
python3 -m unittest discover -s tests
```

The tests do not call ChongPlus and do not need a real key.
