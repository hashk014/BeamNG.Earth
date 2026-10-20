"""Issue #56: native Steam runtimes must not select a stale Proton user folder.

Use temporary Steam config, native and Proton folders on any test host.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import install
import launcher


class SteamCompatibilityTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.steam = self.root / "Flatpak Steam"
        self.config = self.steam / "config" / "config.vdf"
        self.config.parent.mkdir(parents=True)
        self.native = str(self.root / "native" / "current")
        self.proton = str(self.root / "proton" / "0.32")
        os.makedirs(self.proton)
        log = Path(self.proton) / "beamng.log"
        log.touch()
        os.utime(log, (1000, 1000))
        for name, value in (
            ("_steam_roots", [str(self.steam)]),
            ("native_user_dirs", [self.native]),
            ("candidate_user_dirs", [self.proton]),
            ("flatpak_steam", False),
        ):
            patcher = mock.patch.object(install, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def setting(self, name, app_id=None):
        self.config.write_text(
            '"InstallConfigStore"\n{\n\t"Software"\n\t{\n\t\t"Valve"\n\t\t{\n'
            '\t\t\t"Steam"\n\t\t\t{\n\t\t\t\t"CompatToolMapping"\n\t\t\t\t{\n'
            f'\t\t\t\t\t"{app_id or launcher.APP_ID}"\n\t\t\t\t\t{{\n'
            f'\t\t\t\t\t\t"name"\t\t"{name}"\n'
            '\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n\t\t}\n\t}\n}\n',
            encoding="utf-8",
        )

    def test_native_tools_are_not_proton(self):
        for name in ("steamlinuxruntime_4", "steamlinuxruntime_sniper", "steamlinuxruntime_soldier", ""):
            with self.subTest(tool=name):
                self.setting(name)
                self.assertEqual(launcher.steam_compat_tool(), "")

    def test_known_native_setting_wins_even_before_first_native_start(self):
        self.setting("steamlinuxruntime_4")
        self.assertFalse(os.path.exists(self.native))
        self.assertEqual(launcher.linux_build(), ("native", self.native))
        self.assertTrue(os.path.isdir(self.native))

    def test_known_native_setting_ignores_proton_logs(self):
        os.makedirs(self.native)
        for name in ("steamlinuxruntime_4", "steamlinuxruntime_sniper", ""):
            with self.subTest(tool=name):
                self.setting(name)
                self.assertEqual(launcher.linux_build(), ("native", self.native))

    def test_proton_variants_still_select_windows_build(self):
        for name in ("proton_9", "proton_experimental", "GE-Proton10-4"):
            with self.subTest(tool=name):
                self.setting(name)
                self.assertEqual(launcher.steam_compat_tool(), name)
                self.assertEqual(launcher.linux_build(), ("proton", self.proton))

    def test_missing_config_uses_last_played_build(self):
        self.assertIsNone(launcher.steam_compat_tool())
        self.assertEqual(launcher.linux_build(), ("proton", self.proton))
        os.makedirs(self.native)
        log = Path(self.native) / "beamng.log"
        log.touch()
        os.utime(log, (2000, 2000))
        self.assertEqual(launcher.linux_build(), ("native", self.native))

    def test_other_app_setting_is_not_used(self):
        self.setting("proton_experimental", app_id="12345")
        self.assertEqual(launcher.steam_compat_tool(), "")
        self.assertEqual(launcher.linux_build(), ("native", self.native))

    def test_explicit_build_overrides_steam(self):
        self.setting("steamlinuxruntime_4")
        self.assertEqual(launcher.linux_build("proton"), ("proton", self.proton))
        self.setting("proton_experimental")
        self.assertEqual(launcher.linux_build("native"), ("native", self.native))


class QuickPlayTest(unittest.TestCase):
    def test_windows_direct_and_steam_fallback_keep_level_and_renderer(self):
        for fails in (False, True):
            with self.subTest(fallback=fails), \
                 mock.patch.object(launcher, "IS_WIN", True), \
                 mock.patch.object(launcher, "windows_game_dir", return_value="game folder"), \
                 mock.patch.object(launcher.subprocess, "Popen") as popen, \
                 mock.patch.object(launcher, "steam_launch") as steam:
                if fails:
                    popen.side_effect = OSError("cannot start directly")
                launcher.start_game(False, gfx="dx11", level="beamng_earth")
                self.assertEqual(popen.call_args.args[0], [
                    os.path.join("game folder", "BeamNG.drive.exe"), "-gfx", "dx11", "-level", "beamng_earth"])
                if fails:
                    steam.assert_called_once_with(["-gfx", "dx11", "-level", "beamng_earth"])
                else:
                    steam.assert_not_called()

    def test_linux_steam_and_proton_receive_level(self):
        for build in ("native", "proton"):
            with self.subTest(build=build), \
                 mock.patch.object(launcher, "IS_WIN", False), \
                 mock.patch.object(launcher, "linux_game_exe", return_value=None), \
                 mock.patch.object(launcher, "steam_launch") as steam:
                launcher.start_game(False, build=build, level="beamng_earth")
                steam.assert_called_once_with(["-level", "beamng_earth"])

    def test_default_start_does_not_select_a_level(self):
        with mock.patch.object(launcher, "IS_WIN", True), \
             mock.patch.object(launcher, "windows_game_dir", return_value="game folder"), \
             mock.patch.object(launcher.subprocess, "Popen") as popen:
            launcher.start_game(False)
            self.assertEqual(popen.call_args.args[0], [os.path.join("game folder", "BeamNG.drive.exe")])

    def test_linux_native_direct_start_keeps_level(self):
        with mock.patch.object(launcher, "IS_WIN", False), \
             mock.patch.object(launcher, "linux_game_exe", return_value="/game/BinLinux/BeamNG.drive.x64"), \
             mock.patch.object(launcher, "sandboxed_game", return_value=False), \
             mock.patch.object(launcher, "steam_running", return_value=True), \
             mock.patch.object(launcher, "clean_env", return_value={}), \
             mock.patch.object(launcher.time, "time", side_effect=[0, 100]), \
             mock.patch.object(launcher.subprocess, "Popen") as popen:
            popen.return_value.poll.return_value = None
            launcher.start_game(False, level="beamng_earth")
            self.assertEqual(popen.call_args.args[0], [
                "/game/BinLinux/BeamNG.drive.x64", "-level", "beamng_earth"])


if __name__ == "__main__":
    unittest.main()
