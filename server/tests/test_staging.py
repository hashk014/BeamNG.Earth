"""staging: atomic writes into the game's user folder stage their temporary file outside it."""
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import staging  # noqa: E402
import heightmap  # noqa: E402
import numpy as np
from PIL import Image


class StagingTest(unittest.TestCase):
    def remove_owned(self, root, path):
        target, root = Path(path).resolve(), Path(root).resolve()
        self.assertTrue(target.is_relative_to(root) and target != root)
        shutil.rmtree(target)

    def target(self, root):
        return os.path.join(root, "BeamNG.drive", "current", "temp", "beamngEarth", "s1", "hm_11_0_0.png")

    def test_outside_the_user_folder_same_disk(self):
        with tempfile.TemporaryDirectory() as root:
            user = os.path.join(root, "BeamNG.drive", "current")
            target = os.path.join(user, "temp", "beamngEarth", "s1", "far_1_2.cdae")
            os.makedirs(os.path.dirname(target))
            tmp = staging.tmp_for(target)
            self.assertEqual(os.path.dirname(tmp), os.path.join(root, "BeamNG.drive", staging.STAGING))
            self.assertFalse(tmp.startswith(user))
            with open(tmp, "wb") as f:
                f.write(b"x")
            os.replace(tmp, target)
            self.assertTrue(os.path.exists(target))
            self.assertNotEqual(staging.tmp_for(target), staging.tmp_for(target))   # one per write

    def test_elsewhere_beside_the_file(self):
        self.assertEqual(staging.tmp_for("/home/x/.cache/beamng-earth/dem/1/2.webp"),
                         "/home/x/.cache/beamng-earth/dem/1/2.webp.tmp")

    def test_old_leftovers_swept(self):
        with tempfile.TemporaryDirectory() as root:
            d = os.path.join(root, "BeamNG.drive", staging.STAGING)
            os.makedirs(d)
            old, new = os.path.join(d, "a.tmp"), os.path.join(d, "b.tmp")
            for p in (old, new):
                open(p, "w").close()
            t = time.time() - staging.SWEEP_AGE_S - 10
            os.utime(old, (t, t))
            staging.tmp_for(os.path.join(root, "BeamNG.drive", "current", "temp", "x", "y.json"))
            self.assertFalse(os.path.exists(old))
            self.assertTrue(os.path.exists(new))

    def test_cleaned_staging_folder_is_recreated(self):
        with tempfile.TemporaryDirectory() as root:
            target = self.target(root)
            os.makedirs(os.path.dirname(target))
            first = staging.tmp_for(target)
            self.remove_owned(root, os.path.dirname(first))
            second = staging.tmp_for(target)
            with open(second, "wb") as f:
                f.write(b"complete")
            os.replace(second, target)
            self.assertEqual(Path(target).read_bytes(), b"complete")

    def test_missing_session_folder_is_recreated(self):
        with tempfile.TemporaryDirectory() as root:
            target = self.target(root)
            tmp = staging.tmp_for(target)
            Path(tmp).write_bytes(b"complete")
            staging.replace(tmp, target)
            self.assertEqual(Path(target).read_bytes(), b"complete")
            self.assertFalse(os.path.exists(tmp))

    def test_cleanup_between_encode_and_publish(self):
        with tempfile.TemporaryDirectory() as root:
            target = self.target(root)
            os.makedirs(os.path.dirname(target))
            save = Image.Image.save

            def clean_after_save(image, *args, **kwargs):
                save(image, *args, **kwargs)
                self.remove_owned(root, os.path.dirname(target))

            heights = np.arange(16, dtype=np.float64).reshape(4, 4)
            with mock.patch.object(Image.Image, "save", clean_after_save):
                _, _, _, qgrid = heightmap.write_png(target, heights)
            with Image.open(target) as image:
                np.testing.assert_array_equal(np.asarray(image), qgrid[::-1])

    def test_fallback_can_write_when_session_folder_is_missing(self):
        with tempfile.TemporaryDirectory() as root:
            target = self.target(root)
            make = os.makedirs
            stage = staging.staging_dir(target)

            def no_stage(path, **kwargs):
                if path == stage:
                    raise PermissionError("staging folder unavailable")
                return make(path, **kwargs)

            with mock.patch.object(staging.os, "makedirs", side_effect=no_stage):
                tmp = staging.tmp_for(target)
                self.assertEqual(tmp, target + ".tmp")
                Path(tmp).write_bytes(b"complete")
                staging.replace(tmp, target)
            self.assertEqual(Path(target).read_bytes(), b"complete")

    def test_missing_source_is_not_hidden(self):
        with tempfile.TemporaryDirectory() as root:
            target = self.target(root)
            with self.assertRaises(FileNotFoundError):
                staging.replace(os.path.join(root, "missing.tmp"), target)
            self.assertFalse(os.path.exists(os.path.dirname(target)))

    def test_cache_writes_do_not_create_missing_parent(self):
        with tempfile.TemporaryDirectory() as root:
            target = os.path.join(root, "cache", "tile.bin")
            tmp = os.path.join(root, "cache.tmp")
            Path(tmp).write_bytes(b"complete")
            with self.assertRaises(FileNotFoundError):
                staging.replace(tmp, target)
            self.assertTrue(os.path.isfile(tmp))
            self.assertFalse(os.path.exists(os.path.dirname(target)))

    def test_permission_errors_are_not_retried(self):
        with tempfile.TemporaryDirectory() as root:
            target = self.target(root)
            tmp = staging.tmp_for(target)
            Path(tmp).write_bytes(b"complete")
            with mock.patch.object(staging.os, "replace", side_effect=PermissionError("locked")) as replace:
                with self.assertRaises(PermissionError):
                    staging.replace(tmp, target)
                self.assertEqual(replace.call_count, 1)
            self.assertTrue(os.path.isfile(tmp))


if __name__ == "__main__":
    unittest.main()
