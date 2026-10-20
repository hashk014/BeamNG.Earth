"""Bounded area plans and checkpointed, cache-validated downloads without network calls."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools import prefetch


class FakeBackend:
    def __init__(self, root):
        self.cache_dir = str(root)
        self.cached, self.fail, self.network = set(), set(), []

    def fetch(self, job):
        ident = prefetch.job_id(job)
        if ident in self.fail:
            raise IOError("temporarily unavailable")
        if ident not in self.cached:
            self.network.append(ident)
            self.cached.add(ident)


class AreaPrefetchTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.backend = FakeBackend(self.root / "cache")
        self.manifest = self.root / "manifest.json"
        self.plan = prefetch.make_plan(48.86, 2.35, .1, dem_zoom=5, layers=("roads",), imagery="none")

    def run_plan(self, plan=None):
        return prefetch.execute(plan or self.plan, self.backend, self.manifest, progress=lambda _: None)

    def test_plan_contains_coarse_and_fine_terrain_without_duplicate_jobs(self):
        plan = prefetch.make_plan(48.86, 2.35, 1)
        self.assertEqual({j["key"][0] for j in plan["jobs"] if j["kind"] == "dem"}, set(range(5, 16)))
        ids = [prefetch.job_id(j) for j in plan["jobs"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertFalse(self.manifest.exists(), "planning does not write a manifest")

    def test_antimeridian_wrap_is_small_and_unique(self):
        plan = prefetch.make_plan(10, 179.999, .5, layers=(), imagery="none")
        self.assertLess(len(plan["jobs"]), 100)
        self.assertGreater(plan["bounds"][1], plan["bounds"][3])
        self.assertTrue(all(0 <= j["key"][1] < 2 ** j["key"][0] for j in plan["jobs"]))

    def test_invalid_and_oversized_plans_fail_before_download(self):
        for kwargs in ({"lat": float("nan")}, {"lon": 181}, {"lat": 89}, {"radius_km": 0},
                       {"radius_km": 51}, {"dem_zoom": 30}, {"layers": ("bad",)}, {"max_jobs": 1}):
            args = dict(lat=48.86, lon=2.35)
            args.update(kwargs)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                prefetch.make_plan(**args)
        self.assertFalse(self.backend.network)

    def test_failed_jobs_remain_incomplete_and_resume_reuses_cached_data(self):
        ident = prefetch.job_id(self.plan["jobs"][-1])
        self.backend.fail.add(ident)
        first = self.run_plan()
        self.assertEqual(first["failed"], 1)
        self.assertNotIn(ident, json.loads(self.manifest.read_text())["completed"])
        previous = len(self.backend.network)
        self.backend.fail.clear()
        final = self.run_plan()
        self.assertEqual(final["failed"], 0)
        self.assertEqual(final["completed"], final["total"])
        self.assertEqual(len(self.backend.network), previous + 1)

    def test_evicted_data_is_revalidated_despite_completed_manifest(self):
        self.run_plan()
        removed = self.backend.cached.pop()
        count = len(self.backend.network)
        self.run_plan()
        self.assertEqual(len(self.backend.network), count + 1)
        self.assertEqual(self.backend.network[-1], removed)

    def test_wrong_manifest_plan_or_cache_is_refused(self):
        self.run_plan()
        self.backend.cache_dir = str(self.root / "another cache")
        count = len(self.backend.network)
        with self.assertRaises(ValueError):
            self.run_plan()
        self.assertEqual(len(self.backend.network), count)

    def test_cancellation_keeps_previous_checkpoint(self):
        original = self.backend.fetch
        calls = 0
        def fetch(job):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise KeyboardInterrupt()
            return original(job)
        with mock.patch.object(self.backend, "fetch", fetch), self.assertRaises(KeyboardInterrupt):
            self.run_plan()
        self.assertEqual(len(json.loads(self.manifest.read_text())["completed"]), 1)

    def test_corrupt_manifest_is_not_overwritten(self):
        self.manifest.write_text("broken")
        with self.assertRaises(ValueError):
            self.run_plan()
        self.assertEqual(self.manifest.read_text(), "broken")


if __name__ == "__main__":
    unittest.main()
