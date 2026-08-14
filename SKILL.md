---
name: chongplus-image
description: Generate images and edit reference images using the ChongPlus Image API and gpt-image-2. Use for ChongPlus text-to-image, image-to-image, restyling, or image revisions. On first use, ask for the user's ChongPlus API Key and save it with the bundled local client; never require an environment variable.
---

# ChongPlus Image

Run the bundled client from this Skill's directory. Resolve `SKILL_DIR` as the directory containing this `SKILL.md`; do not use an absolute path from another machine.

The client tries `https://ai.chongplus.plus` first for image requests and automatically falls back to `https://api.chongplus.plus` only when the first endpoint cannot be reached because of a network failure or timeout.

## Mandatory skill update check

Before every `generate`, `edit`, or retry request, check whether this skill has an available upstream update. Compare the installed skill with the latest version from `https://github.com/Rodert/chongplus-image-skill`.

When no update is available, continue silently. When an update is available, tell the user that it may contain bug fixes or compatibility changes needed for image generation, and ask for authorization to install it. Do not fetch, install, or execute updated code without that explicit authorization. If an authorized update fails, report the failure and retain the current version. If local modifications would block an update, report that conflict and ask the user how to proceed.

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

## Request lifecycle and quota protection

Each `generate` or `edit` invocation may consume image-generation quota. Treat a started invocation as in progress until its process exits; delayed, partial, or not-yet-displayed terminal output is not a failure. Do not submit an equivalent retry while the earlier invocation may still be running.

When the client has not returned an explicit error, image generation normally takes 30 to 120 seconds. Treat no result before 30 seconds as normal. From 30 through 120 seconds, continue waiting and do not submit a retry. If 120 seconds pass without a result, inspect the process state and output directory before deciding whether the request failed or needs another action.

An explicit client error overrides the waiting window: handle it immediately under **Error handling**. Do not wait for 30 or 120 seconds after a summarized authentication, authorization, rate-limit, invalid-request, network, or service error.

After the process exits, inspect its exit status and the output directory before deciding that it failed or needs another request. Retry only after a confirmed failure, or with the user's explicit instruction.

If an accidental duplicate request occurs, tell the user that the earlier request had not yet returned and that both completed, so both may have consumed quota. Return every image from every completed request. When the user explicitly asks for multiple requests, make each requested invocation and return all images produced by each one.

## Edit

```bash
python3 "$SKILL_DIR/scripts/chongplus_image.py" edit \
  --image /absolute/path/to/source.png \
  --prompt 'Keep the product unchanged and replace the background with a clean white studio backdrop.' \
  --size 2048x2048 --output-dir ./outputs
```

## Error handling

Report only the bundled client's summarized error to the user. Do not expose request URLs, upstream host names, HTTP response bodies, proxy or firewall details, or API keys. Explain the next action from the summary: update the key or access for authentication failures, wait and retry for rate limits or temporary service failures, and otherwise retry later. See `references/troubleshooting.md` for the public error categories.
