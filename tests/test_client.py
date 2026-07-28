import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


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
