"""Road rendering preferences and compute sharing, without real user/game folders."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "server"))


class RenderingPreferenceTest(unittest.TestCase):
    def setUp(self):
        from server import roadconfig
        self.config = roadconfig
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        env = mock.patch.dict(os.environ, {
            "LOCALAPPDATA": str(self.root / "local"), "XDG_CONFIG_HOME": str(self.root / "config"),
            "HOME": str(self.root), "USERPROFILE": str(self.root),
        })
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop(roadconfig.ENV, None)

    def cli(self, script, *args, ok=True):
        result = subprocess.run([sys.executable, str(ROOT / script), *args], cwd=ROOT,
                                capture_output=True, text=True, errors="replace", timeout=30)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result.stdout.strip()

    def test_default_and_corrupt_preferences_keep_terrain(self):
        self.assertEqual(self.config.mode(), "terrain")
        path = Path(self.config.config_path())
        path.parent.mkdir(parents=True)
        for value in ("bad json", "[]", '{"road_rendering": "unknown"}', '{"road_rendering": null}'):
            path.write_text(value, encoding="utf-8")
            self.assertEqual(self.config.mode(), "terrain")

    def test_both_launchers_save_and_read_across_restarts(self):
        for script in ("start.py", "launcher.py"):
            self.assertEqual(self.cli(script, "--road-rendering", "mesh", "--print-road-rendering"), "mesh")
            self.assertEqual(self.cli("start.py", "--print-road-rendering"), "mesh")
            self.assertEqual(self.cli("launcher.py", "--print-road-rendering"), "mesh")
            self.assertEqual(self.cli(script, "--reset-road-rendering", "--print-road-rendering"), "terrain")
        self.assertFalse((self.root / ".cache").exists(), "print/select must not start a server")

    def test_environment_override_and_explicit_choice(self):
        self.config.save("mesh")
        os.environ[self.config.ENV] = "1"
        self.assertEqual(self.config.mode(), "terrain")
        self.assertEqual(self.cli("launcher.py", "--road-rendering", "mesh", "--print-road-rendering"), "mesh")
        self.assertEqual(self.cli("start.py", "--print-road-rendering"), "terrain")
        os.environ[self.config.ENV] = "0"
        self.assertEqual(self.config.mode(), "mesh")
        self.assertEqual(self.cli("start.py", "--reset-road-rendering", "--print-road-rendering"), "terrain")

    def test_bad_choice_keeps_previous_file(self):
        self.config.save("mesh")
        before = Path(self.config.config_path()).read_bytes()
        self.cli("launcher.py", "--road-rendering", "invalid", "--print-road-rendering", ok=False)
        self.assertEqual(Path(self.config.config_path()).read_bytes(), before)

    def test_failed_save_keeps_previous_file_and_cleans_temp(self):
        self.config.save("mesh")
        before = Path(self.config.config_path()).read_bytes()
        with mock.patch.object(self.config.os, "replace", side_effect=PermissionError("locked")):
            with self.assertRaises(PermissionError):
                self.config.save("terrain")
        self.assertEqual(Path(self.config.config_path()).read_bytes(), before)
        self.assertEqual(list(Path(self.config.config_path()).parent.glob("roads-*.tmp")), [])

    def test_server_import_uses_saved_mode(self):
        self.config.save("mesh")
        result = subprocess.run([sys.executable, "-c", "import roads; print(roads.ROADS_IN_GROUND)"],
                                cwd=ROOT / "server", capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "False")

    def test_startup_exports_resolved_choice_for_children(self):
        self.config.save("mesh")
        parser = argparse.ArgumentParser()
        self.config.add_arguments(parser)
        self.assertFalse(self.config.configure(parser.parse_args([]), parser))
        self.assertEqual(os.environ[self.config.ENV], "0")


if __name__ == "__main__":
    unittest.main()
