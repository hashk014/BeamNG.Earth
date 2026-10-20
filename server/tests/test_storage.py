"""Persistent storage selection and the real source/packaged launcher entry paths."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from server import storage


class StorageTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        patcher = mock.patch.dict(os.environ, {
            "LOCALAPPDATA": str(self.root / "local"), "XDG_CONFIG_HOME": str(self.root / "config"),
            "HOME": str(self.root), "USERPROFILE": str(self.root), storage.ENV: "",
        })
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_cli(self, script, *args):
        result = subprocess.run([sys.executable, str(ROOT / script), *args], cwd=ROOT,
                                capture_output=True, text=True, errors="replace", timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_legacy_default_stays_available(self):
        self.assertEqual(storage.cache_dir(), str(self.root / ".cache" / "beamng-earth"))

    def test_saved_path_survives_process_restarts_and_both_launchers(self):
        selected = str(self.root / "another drive" / "Earth cache")
        self.assertEqual(self.run_cli("launcher.py", "--cache-dir", selected, "--print-cache-dir"), selected)
        self.assertEqual(self.run_cli("start.py", "--print-cache-dir"), selected)
        self.assertEqual(self.run_cli("launcher.py", "--print-cache-dir"), selected)
        self.assertFalse(os.path.exists(selected), "selecting a cache neither moves nor downloads data")

    def test_start_selection_is_used_by_packaged_launcher(self):
        selected = str(self.root / "source selection")
        self.run_cli("start.py", "--cache-dir", selected, "--print-cache-dir")
        self.assertEqual(self.run_cli("launcher.py", "--print-cache-dir"), selected)

    def test_environment_overrides_saved_path(self):
        storage.save(str(self.root / "saved"))
        os.environ[storage.ENV] = str(self.root / "environment")
        self.assertEqual(storage.cache_dir(), str(self.root / "environment"))

    def test_explicit_cli_overrides_environment(self):
        os.environ[storage.ENV] = str(self.root / "environment")
        selected = str(self.root / "explicit")
        self.assertEqual(self.run_cli("launcher.py", "--cache-dir", selected, "--print-cache-dir"), selected)

    def test_reset_preserves_old_cache_files(self):
        selected = self.root / "old cache"
        selected.mkdir()
        (selected / "tile").write_bytes(b"existing")
        storage.save(str(selected))
        self.assertEqual(self.run_cli("start.py", "--reset-cache-dir", "--print-cache-dir"),
                         str(self.root / ".cache" / "beamng-earth"))
        self.assertEqual((selected / "tile").read_bytes(), b"existing")

    def test_bad_config_falls_back(self):
        path = Path(storage.config_path())
        path.parent.mkdir(parents=True)
        for content in ("{broken", "[]", '{"cache_dir": 42}', '{"cache_dir": "  "}'):
            with self.subTest(content=content):
                path.write_text(content)
                self.assertEqual(storage.cache_dir(), str(self.root / ".cache" / "beamng-earth"))

    def test_config_preserves_other_fields(self):
        path = Path(storage.config_path())
        path.parent.mkdir(parents=True)
        path.write_text('{"other": true}')
        storage.save(str(self.root / "cache"))
        self.assertTrue(json.loads(path.read_text())["other"])
        storage.save(None)
        self.assertEqual(json.loads(path.read_text()), {"other": True})

    def test_invalid_path_does_not_replace_saved_value(self):
        selected = storage.save(str(self.root / "saved"))
        for value in ("", "  ", 42):
            with self.subTest(value=value), self.assertRaises(ValueError):
                storage.save(value)
        self.assertEqual(storage.cache_dir(), selected)

    def test_failed_atomic_save_keeps_previous_config(self):
        selected = storage.save(str(self.root / "saved"))
        with mock.patch.object(storage.os, "replace", side_effect=PermissionError("locked")):
            with self.assertRaises(PermissionError):
                storage.save(str(self.root / "new"))
        self.assertEqual(storage.cache_dir(), selected)
        self.assertEqual(list(Path(storage.config_path()).parent.glob("*.tmp")), [])

    def test_server_mode_still_imports(self):
        self.assertIn("--cache-dir", self.run_cli("launcher.py", "--server", "--help"))


if __name__ == "__main__":
    unittest.main()
