"""Issue #27: prepare_anchor still returns real terrain after output folders are removed."""
import os
import shutil
import unittest
from pathlib import Path
from unittest import mock

from test_server import LAT, LON, ServerHarness
import staging


class SessionOutputRecoveryTest(ServerHarness):
    cells = 64
    block = 512
    near_visual = "mesh"

    def setUp(self):
        super().setUp()
        # ServerHarness uses a temporary user root whose sibling staging directory is shared by
        # concurrent test processes. Fault injection must stay inside this test's own root.
        stage = os.path.join(self.tmp.name, staging.STAGING)
        original = staging.staging_dir
        patcher = mock.patch.object(staging, "staging_dir",
                                    side_effect=lambda path: stage if original(path) is not None else None)
        patcher.start()
        self.addCleanup(patcher.stop)

    def check_files(self, anchor):
        terrain = anchor["terrain"]
        self.check_terrain(terrain, 0.0, 0.0)
        self.assertGreater(os.path.getsize(self.fs(terrain["ter"])), 0)

    def remove_owned(self, path):
        target, root = Path(path).resolve(), Path(self.tmp.name).resolve()
        self.assertTrue(target.is_relative_to(root) and target != root)
        shutil.rmtree(target)

    def test_missing_session_directory_before_teleport(self):
        self.remove_owned(self.server.out_dir)
        self.hello()
        self.check_files(self.prepare_anchor(1, LAT, LON))

    def test_staging_cleanup_between_teleports(self):
        self.hello()
        self.check_files(self.prepare_anchor(1, LAT, LON))
        stage = staging.staging_dir(os.path.join(self.server.out_dir, "hm_1_0_0.png"))
        self.remove_owned(stage)
        self.check_files(self.prepare_anchor(2, LAT + 0.01, LON + 0.01))


if __name__ == "__main__":
    unittest.main()
