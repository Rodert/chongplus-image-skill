#!/usr/bin/env python3
"""Portable standard-library client for the ChongPlus Image API."""

import argparse
import base64
import getpass
import json
import mimetypes
import os
import secrets
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "https://api.chongplus.plus"
MODEL = "gpt-image-2"
SIZES = {"1024x1024", "2048x2048", "1536x1024", "1024x1536", "3840x2160", "2160x3840"}


def config_path():
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "chongplus-image" / "config.json"


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def private_mode(path, mode):
    if os.name != "nt":
        os.chmod(path, mode)


def save_key(key):
    key = key.strip()
    if not key:
        fail("API key cannot be empty.")
    path = config_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    private_mode(path.parent, 0o700)
    temporary = path.parent / f".{path.name}.{secrets.token_hex(8)}.tmp"
    try:
        with open(temporary, "w", encoding="utf-8") as handle:
            private_mode(temporary, 0o600)
            json.dump({"api_key": key}, handle)
            handle.write("\n")
        os.replace(temporary, path)
        private_mode(path, 0o600)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_key():
    try:
        with open(config_path(), encoding="utf-8") as handle:
            key = json.load(handle).get("api_key", "").strip()
    except (OSError, json.JSONDecodeError):
        key = ""
    if not key:
        fail("No ChongPlus API key is saved. Ask the user for their key, then run config --set-key or config --set-key-stdin.")
    return key


def request(endpoint, body, content_type):
    headers = {
        "Authorization": f"Bearer {load_key()}",
        "Content-Type": content_type,
        "Accept": "application/json",
        "User-Agent": "ChongPlusImageSkill/1.0 (portable local client)",
    }
    req = urllib.request.Request(BASE_URL + endpoint, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            raw = response.read()
            if not raw:
                fail(f"API returned an empty response with HTTP {response.status}.")
            try:
                result = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                fail(f"API returned non-JSON data with HTTP {response.status}: {raw[:1000].decode('utf-8', errors='replace')}")
            if not isinstance(result, dict):
                fail(f"API returned an unexpected JSON response with HTTP {response.status}.")
            return result
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")[:1000]
        fail(f"API request failed with HTTP {error.code}: {details}")
    except urllib.error.URLError as error:
        fail(f"Could not reach ChongPlus: {error.reason}")


def multipart(fields, image_path):
    boundary = "----ChongPlus" + secrets.token_hex(16)
    parts = []
    for name, value in fields.items():
        parts.extend([f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(), str(value).encode(), b"\r\n"])
    mime = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
    parts.extend([f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="image"; filename="{image_path.name}"\r\n'.encode(), f"Content-Type: {mime}\r\n\r\n".encode(), image_path.read_bytes(), b"\r\n", f"--{boundary}--\r\n".encode()])
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def image_extension(content_type):
    return {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}.get(content_type.split(";", 1)[0].lower(), "png")


def png_dimensions(raw):
    if raw[:8] == b"\x89PNG\r\n\x1a\n" and raw[12:16] == b"IHDR":
        return int.from_bytes(raw[16:20], "big"), int.from_bytes(raw[20:24], "big")
    return None


def save_results(response, output_dir):
    entries = response.get("data")
    if not isinstance(entries, list) or not entries:
        fail("API response contains no image data.")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    for index, item in enumerate(entries, 1):
        if "b64_json" in item:
            try:
                raw = base64.b64decode(item["b64_json"], validate=True)
            except (ValueError, TypeError):
                fail("API returned invalid Base64 image data.")
            suffix = "png"
        elif "url" in item:
            try:
                with urllib.request.urlopen(item["url"], timeout=300) as result:
                    raw = result.read()
                    suffix = image_extension(result.headers.get_content_type())
            except urllib.error.URLError as error:
                fail(f"Could not download generated image: {error.reason}")
        else:
            fail("An image result has neither url nor b64_json.")
        path = output_dir / f"chongplus-{timestamp}-{index}.{suffix}"
        path.write_bytes(raw)
        dimensions = png_dimensions(raw)
        message = str(path.resolve())
        if dimensions:
            message += f" ({dimensions[0]}x{dimensions[1]})"
        print(message)


def run_image(args):
    if args.size not in SIZES:
        fail(f"Unsupported size: {args.size}. Choose one of: {', '.join(sorted(SIZES))}")
    if not 1 <= args.n <= 4:
        fail("n must be between 1 and 4.")
    if args.action == "generate":
        body = json.dumps({"model": MODEL, "prompt": args.prompt, "size": args.size, "n": args.n, "response_format": "b64_json"}).encode()
        response = request("/v1/images/generations", body, "application/json")
    else:
        image = Path(args.image).expanduser().resolve()
        if not image.is_file():
            fail(f"Image file does not exist: {image}")
        body, content_type = multipart({"model": MODEL, "prompt": args.prompt, "size": args.size, "n": args.n}, image)
        response = request("/v1/images/edits", body, content_type)
    save_results(response, Path(args.output_dir).expanduser())


def main():
    parser = argparse.ArgumentParser(description="ChongPlus Image API client")
    commands = parser.add_subparsers(dest="action", required=True)
    config = commands.add_parser("config")
    config.add_argument("--show-status", action="store_true")
    config.add_argument("--check", action="store_true")
    config.add_argument("--set-key", action="store_true")
    config.add_argument("--set-key-stdin", action="store_true")
    for action in ("generate", "edit"):
        command = commands.add_parser(action)
        command.add_argument("--prompt", required=True)
        command.add_argument("--size", default="2048x2048")
        command.add_argument("--n", type=int, default=1)
        command.add_argument("--output-dir", default="outputs")
        if action == "edit":
            command.add_argument("--image", required=True)
    args = parser.parse_args()
    if args.action != "config":
        run_image(args)
    elif args.set_key_stdin:
        save_key(sys.stdin.read())
        print("ChongPlus API key saved securely.")
    elif args.set_key:
        try:
            save_key(getpass.getpass("ChongPlus API Key: "))
        except (EOFError, KeyboardInterrupt):
            fail("API key entry was cancelled.")
        print("ChongPlus API key saved securely.")
    elif args.show_status or args.check:
        print("configured" if config_path().is_file() else "not configured")
    else:
        fail("Use --show-status, --check, --set-key, or --set-key-stdin.")


if __name__ == "__main__":
    main()
