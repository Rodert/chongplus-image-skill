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

BASE_URL = "https://ai.chongplus.plus"
MODEL = "gpt-image-2"
SIZES = {"1024x1024", "2048x2048", "1536x1024", "1024x1536", "3840x2160", "2160x3840"}
USER_AGENT = "ChongPlusImageSkill/1.0 (portable local client)"
DOWNLOAD_RETRIES = 0


class ClientError(SystemExit):
    def __init__(self, message):
        super().__init__(1)
        self.message = message


class RequestStatus:
    def __init__(self, path, request_id, action, output_dir):
        self.path = path
        self.data = {
            "request_id": request_id,
            "action": action,
            "output_dir": str(output_dir.resolve()),
        }

    def update(self, state, **details):
        self.data.update(details)
        self.data["state"] = state
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.data.setdefault("started_at", timestamp)
        self.data["updated_at"] = timestamp
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.parent / f".{self.path.name}.{secrets.token_hex(8)}.tmp"
        try:
            with open(temporary, "w", encoding="utf-8") as handle:
                json.dump(self.data, handle, indent=2, sort_keys=True)
                handle.write("\n")
            os.replace(temporary, self.path)
        finally:
            if temporary.exists():
                temporary.unlink()


def config_path():
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "chongplus-image" / "config.json"


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise ClientError(message)


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


def request_failure_summary(failures):
    statuses = {status for _, status in failures if status is not None}
    if 401 in statuses:
        return "ChongPlus could not authenticate the request. Check the saved API key and its access."
    if 403 in statuses:
        return "ChongPlus did not authorize this image request. Check API key access and quota."
    if 429 in statuses:
        return "ChongPlus is rate-limiting image requests. Retry after a short delay."
    if any(status >= 500 for status in statuses) or any(kind == "network" for kind, _ in failures):
        return "ChongPlus image service is temporarily unavailable. Please retry later."
    return "ChongPlus could not complete the image request. Please retry later."


def request(endpoint, body, content_type):
    headers = {
        "Authorization": f"Bearer {load_key()}",
        "Content-Type": content_type,
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    req = urllib.request.Request(BASE_URL + endpoint, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            raw = response.read()
            if not raw:
                fail(request_failure_summary([("response", response.status)]))
            try:
                result = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                fail(request_failure_summary([("response", response.status)]))
            if not isinstance(result, dict):
                fail(request_failure_summary([("response", response.status)]))
            return result
    except urllib.error.HTTPError as error:
        fail(request_failure_summary([("http", error.code)]))
    except (urllib.error.URLError, TimeoutError):
        fail(request_failure_summary([("network", None)]))


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


def download_image(url, status=None):
    headers = {
        "Authorization": f"Bearer {load_key()}",
        "User-Agent": USER_AGENT,
    }
    for attempt in range(DOWNLOAD_RETRIES + 1):
        if status:
            status.update("downloading_result", download_attempt=attempt + 1)
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                raw = response.read()
                if raw:
                    return raw, image_extension(response.headers.get_content_type())
        except urllib.error.HTTPError as error:
            if 400 <= error.code < 500:
                fail("Could not download generated image.")
        except (urllib.error.URLError, TimeoutError):
            pass
        if attempt == DOWNLOAD_RETRIES:
            fail("Could not download generated image.")
        time.sleep(1)


def save_results(response, output_dir, request_id=None, status=None):
    entries = response.get("data")
    if not isinstance(entries, list) or not entries:
        fail("API response contains no image data.")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = request_id or time.strftime("%Y%m%d-%H%M%S")
    paths = []
    for index, item in enumerate(entries, 1):
        b64_json = item.get("b64_json")
        if isinstance(b64_json, str) and b64_json:
            try:
                raw = base64.b64decode(b64_json, validate=True)
            except (ValueError, TypeError):
                fail("API returned invalid Base64 image data.")
            suffix = "png"
        elif isinstance(item.get("url"), str) and item["url"]:
            raw, suffix = download_image(item["url"], status)
        else:
            fail("An image result has neither usable b64_json nor url.")
        path = output_dir / f"chongplus-{timestamp}-{index}.{suffix}"
        path.write_bytes(raw)
        dimensions = png_dimensions(raw)
        message = str(path.resolve())
        if dimensions:
            message += f" ({dimensions[0]}x{dimensions[1]})"
        print(message)
        paths.append(str(path.resolve()))
    return paths


def run_image(args):
    output_dir = Path(args.output_dir).expanduser()
    request_id = f"{time.strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(4)}"
    status_path = Path(args.status_file).expanduser() if args.status_file else output_dir / f"chongplus-{request_id}.status.json"
    status = RequestStatus(status_path, request_id, args.action, output_dir)
    status.update("started")
    try:
        if args.size not in SIZES:
            fail(f"Unsupported size: {args.size}. Choose one of: {', '.join(sorted(SIZES))}")
        if not 1 <= args.n <= 4:
            fail("n must be between 1 and 4.")
        if args.action == "generate":
            body = json.dumps({"model": MODEL, "prompt": args.prompt, "size": args.size, "n": args.n, "response_format": "b64_json"}).encode()
            status.update("submitting_request")
            response = request("/v1/images/generations", body, "application/json")
        else:
            image = Path(args.image).expanduser().resolve()
            if not image.is_file():
                fail(f"Image file does not exist: {image}")
            body, content_type = multipart({"model": MODEL, "prompt": args.prompt, "size": args.size, "n": args.n}, image)
            status.update("submitting_request")
            response = request("/v1/images/edits", body, content_type)
        status.update("response_received")
        status.update("writing_results")
        paths = save_results(response, output_dir, request_id, status)
        status.update("succeeded", outputs=paths)
    except ClientError as error:
        status.update("failed", error=error.message)
        raise
    except Exception:
        status.update("failed", error="Unexpected client error.")
        raise


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
        command.add_argument("--status-file")
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
