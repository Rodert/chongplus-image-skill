import contextlib
import io
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import urllib.error


CLIENT = Path(__file__).parents[1] / "scripts" / "chongplus_image.py"
SPEC = importlib.util.spec_from_file_location("chongplus_image", CLIENT)
CLIENT_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLIENT_MODULE)


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.TemporaryDirectory()
        self.original_home = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = self.home.name

    def tearDown(self):
        if self.original_home is None:
            os.environ.pop("XDG_CONFIG_HOME", None)
        else:
            os.environ["XDG_CONFIG_HOME"] = self.original_home
        self.home.cleanup()

    def test_save_key_is_private_on_unix(self):
        CLIENT_MODULE.save_key("sk-test-value")
        path = CLIENT_MODULE.config_path()
        self.assertEqual(json.loads(path.read_text())["api_key"], "sk-test-value")
        if os.name != "nt":
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)

    def test_png_dimensions(self):
        raw = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + (1024).to_bytes(4, "big") + (1536).to_bytes(4, "big")
        self.assertEqual(CLIENT_MODULE.png_dimensions(raw), (1024, 1536))

    def test_unknown_size_is_rejected(self):
        self.assertNotIn("1x2", CLIENT_MODULE.SIZES)

    def test_request_prefers_ai_endpoint(self):
        CLIENT_MODULE.save_key("sk-test-value")
        response = MagicMock()
        response.read.return_value = b'{"data": []}'
        response.__enter__.return_value = response
        with patch.object(CLIENT_MODULE.urllib.request, "urlopen", return_value=response) as urlopen:
            self.assertEqual(CLIENT_MODULE.request("/v1/images/generations", b"{}", "application/json"), {"data": []})
        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(urlopen.call_args.args[0].full_url, "https://ai.chongplus.plus/v1/images/generations")

    def test_request_falls_back_to_api_endpoint(self):
        CLIENT_MODULE.save_key("sk-test-value")
        response = MagicMock()
        response.read.return_value = b'{"data": []}'
        response.__enter__.return_value = response
        with patch.object(
            CLIENT_MODULE.urllib.request,
            "urlopen",
            side_effect=[urllib.error.URLError("unavailable"), response],
        ) as urlopen:
            self.assertEqual(CLIENT_MODULE.request("/v1/images/generations", b"{}", "application/json"), {"data": []})
        self.assertEqual(urlopen.call_count, 2)
        self.assertEqual(urlopen.call_args_list[1].args[0].full_url, "https://api.chongplus.plus/v1/images/generations")

    def test_request_does_not_fallback_after_http_response(self):
        CLIENT_MODULE.save_key("sk-test-value")
        error = urllib.error.HTTPError("https://ai.chongplus.plus/v1/images/generations", 503, "unavailable", {}, None)
        with patch.object(CLIENT_MODULE.urllib.request, "urlopen", side_effect=error) as urlopen:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                CLIENT_MODULE.request("/v1/images/generations", b"{}", "application/json")
        self.assertEqual(urlopen.call_count, 1)

    def test_request_failure_summary_hides_upstream_details(self):
        message = CLIENT_MODULE.request_failure_summary([("http", 502), ("network", None)])
        self.assertEqual(message, "ChongPlus image service is temporarily unavailable. Please retry later.")
        self.assertNotIn("chongplus.plus", message)
        self.assertNotIn("502", message)

    def test_empty_base64_uses_result_url(self):
        CLIENT_MODULE.save_key("sk-test-value")
        response = MagicMock()
        response.read.return_value = b"image-bytes"
        response.headers.get_content_type.return_value = "image/png"
        response.__enter__.return_value = response
        output_dir = Path(self.home.name) / "outputs"
        with patch.object(CLIENT_MODULE.urllib.request, "urlopen", return_value=response) as urlopen:
            with contextlib.redirect_stdout(io.StringIO()):
                CLIENT_MODULE.save_results({"data": [{"b64_json": "", "url": "https://example.test/result"}]}, output_dir)
        self.assertEqual(urlopen.call_args.args[0].full_url, "https://example.test/result")
        self.assertEqual(next(output_dir.iterdir()).read_bytes(), b"image-bytes")

    def test_url_download_includes_authentication_headers(self):
        CLIENT_MODULE.save_key("sk-test-value")
        response = MagicMock()
        response.read.return_value = b"image-bytes"
        response.headers.get_content_type.return_value = "image/png"
        response.__enter__.return_value = response
        with patch.object(CLIENT_MODULE.urllib.request, "urlopen", return_value=response) as urlopen:
            CLIENT_MODULE.download_image("https://example.test/result")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer sk-test-value")
        self.assertEqual(request.get_header("User-agent"), CLIENT_MODULE.USER_AGENT)
