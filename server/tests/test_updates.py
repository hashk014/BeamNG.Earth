"""updates: the GitHub version check."""
import sys
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import netfetch  # noqa: E402
import updates  # noqa: E402


class FakeNet:
    def __init__(self, body=None, err=None):
        self.body, self.err, self.urls = body, err, []

    def get(self, url, kind="demand"):
        self.urls.append((url, kind))
        if self.err:
            raise self.err

        class R:
            pass
        r = R()
        r.body = self.body.encode()
        return r


class UpdatesTest(unittest.TestCase):
    def test_newer(self):
        self.assertTrue(updates.newer("1.4.1-preview", "1.4.0-preview"))
        self.assertTrue(updates.newer("1.4.0", "1.4.0-preview"), "a release is newer than its preview")
        self.assertFalse(updates.newer("1.4.0-preview", "1.4.0"))
        self.assertFalse(updates.newer("1.4.0-preview", "1.4.0-preview"))
        self.assertTrue(updates.newer("1.10.0", "1.9.3"), "numbers, not text")
        self.assertFalse(updates.newer("<html>404</html>", "1.0.0"), "not a version: no update")

    def test_check(self):
        net = FakeNet("1.5.0-preview\n")
        r = updates.check("1.4.0-preview", net)
        self.assertEqual(r["latest"], "1.5.0-preview")
        self.assertEqual(r["url"], updates.PAGE_URL)
        self.assertEqual(net.urls[0], (updates.VERSION_URL, "background"))
        self.assertIsNone(updates.check("1.5.0-preview", FakeNet("1.5.0-preview")), "up to date")
        self.assertIsNone(updates.check("1.4.0", FakeNet(err=netfetch.FetchError("offline"))), "offline: nothing")
        self.assertIsNone(updates.check(None, FakeNet("2.0.0")), "no local VERSION: nothing")


if __name__ == "__main__":
    unittest.main()


class OpenPageTest(unittest.TestCase):
    """The update notice's 'Open releases page' (the game's openWebBrowser does nothing on native Linux, 2026-10-18):
    the server opens this project's GitHub pages only."""

    def test_only_the_projects_pages(self):
        calls = []
        with mock.patch.object(updates.os, "startfile", create=True) as startfile:
            ok = updates.open_page(updates.PAGE_URL, popen=lambda *a, **k: calls.append(a))
            self.assertTrue(ok)
            if updates.sys.platform == "win32":
                startfile.assert_called_once_with(updates.PAGE_URL)
            else:
                self.assertEqual(calls[0][0][1], updates.PAGE_URL)
        for bad in ("https://evil.example/x", "https://github.com/someone/else", None, 5,
                    updates.PAGE_URL + '\" && rm -rf ~'):
            self.assertFalse(updates.open_page(bad, popen=lambda *a, **k: calls.append(a)), bad)
