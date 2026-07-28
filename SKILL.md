---
name: chongplus-image
description: Generate images and edit reference images using the ChongPlus Image API and gpt-image-2. Use for ChongPlus text-to-image, image-to-image, restyling, or image revisions. On first use, ask for the user's ChongPlus API Key and save it with the bundled local client; never require an environment variable.
---

# ChongPlus Image

Run the bundled client from this Skill's directory. Resolve `SKILL_DIR` as the directory containing this `SKILL.md`; do not use an absolute path from another machine.

## Credential workflow

1. Run `python3 "$SKILL_DIR/scripts/chongplus_image.py" config --show-status`.
2. If it prints `not configured`, ask: `Please provide your ChongPlus API Key (sk-...). I will save it locally for future ChongPlus image requests. If you do not have one, sign in at https://api.chongplus.plus/keys, create a key, and select the image-generation group.`
3. Keep the key out of prompts, project files, output, and terminal arguments.
4. When the runtime supports interactive terminal input, run `config --set-key` and enter the key without echoing it.
5. When an Agent can securely send an already-provided key through process standard input, use `config --set-key-stdin`. Do not put it in a command-line argument or environment variable.

The client saves credentials to the current user's platform configuration directory: `~/.config/chongplus-image/config.json` on macOS/Linux (or `$XDG_CONFIG_HOME/chongplus-image/config.json`) and `%APPDATA%\\chongplus-image\\config.json` on Windows. It applies owner-only permissions where the platform supports them.

For custom workflows or extensions, use the official API documentation: `https://api.chongplus.plus/tools/image-studio/docs/`. Read it before changing endpoint fields, supported sizes, models, or response handling.

## Generate

Use a documented size: `1024x1024`, `2048x2048`, `1536x1024`, `1024x1536`, `3840x2160`, or `2160x3840`. Use `1024x1536` for a portrait when the requested ratio is close to 1:2.

```bash
python3 "$SKILL_DIR/scripts/chongplus_image.py" generate \
  --prompt 'A cinematic product photograph of a compact espresso machine, soft studio light, light gray background' \
  --size 1536x1024 --output-dir ./outputs
```

Use `--n` only from 1 through 4. The client writes result files to the output directory and prints their paths. Note the actual output dimensions when they differ from the requested size.

## Edit

```bash
python3 "$SKILL_DIR/scripts/chongplus_image.py" edit \
  --image /absolute/path/to/source.png \
  --prompt 'Keep the product unchanged and replace the background with a clean white studio backdrop.' \
  --size 2048x2048 --output-dir ./outputs
```

## Error handling

Report errors without exposing the API key. For `403` with Cloudflare error `1010`, explain that the edge firewall blocked the request before the API handled it; ensure the client User-Agent is unchanged, then ask the ChongPlus operator to inspect the Cloudflare event. For `401` or other `403` errors, explain that the key may be invalid, lack access, or have no quota. See `references/api.md` for endpoint details and `references/troubleshooting.md` for diagnosis.
