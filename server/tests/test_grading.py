"""Ground graded under roads (grading.py): the profile smoothing, flat across the core, untouched away from
roads, junctions blended, the plans made once per cell, and GradedDem as a drop-in DEM."""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import geodesy  # noqa: E402
import grading  # noqa: E402
import mapcells  # noqa: E402
import roads  # noqa: E402
from test_roads import features, LAT, LON, FRAME  # noqa: E402


class ProfileTest(unittest.TestCase):
    def test_smoothing_keeps_grades_removes_bumps(self):
        s = np.arange(0, 400, 2.0)
        ramp = 0.05 * s
        self.assertTrue(np.allclose(grading.smooth_profile(ramp, 2.0, 12.0)[20:-20], ramp[20:-20], atol=1e-6),
                        "a constant grade stays")
        bumpy = ramp + 0.3 * np.sin(s / 3.0)
        sm = grading.smooth_profile(bumpy, 2.0, 12.0)
        self.assertLess(np.abs(sm - ramp)[20:-20].max(), 0.02, "short bumps smoothed away")
        self.assertEqual(len(sm), len(s))


class CrestTest(unittest.TestCase):
    def test_no_kinks_over_a_crest(self):
        # a road over a crest (the grade falls 4 % per 10 m): the graded centreline's slope changes smoothly, not
        # in a kink at every plan vertex (r/BeamNG 2026-10-17: 'bumpy roads, worst uphill and at speed'; with
        # 16 m vertices the slope jumped 6.4 % at each)
        xy = np.stack([np.arange(-150.0, 150.1, grading.PROFILE_STEP), np.zeros(151)], axis=1)
        z = 20.0 - 0.002 * xy[:, 0] ** 2
        plan = grading._plan(xy, z, roads.Spec(7.0, "paved", False, "residential"))
        px = np.arange(-60.0, 60.1, 0.5)
        out = grading.grade_points(px, np.zeros(len(px)), 20.0 - 0.002 * px ** 2, [plan])
        slope = np.diff(out[::4]) / 2.0                     # per 2 m (the terrain grid)
        self.assertLess(np.abs(np.diff(slope)).max(), 0.02)


def slope_ground(x, y):
    """A hillside: 10 % up to the north, plus small bumps."""
    return 0.10 * y + 0.2 * np.sin(x / 7.0) * np.cos(y / 5.0)


def plan_line(x0, x1, y, kind="paved", cls="residential", w=6.0):
    xy = np.stack([np.linspace(x0, x1, 200), np.full(200, y)], axis=1)
    z = grading.smooth_profile(slope_ground(xy[:, 0], xy[:, 1]), (x1 - x0) / 199, grading.SIGMA_M)
    keep = np.r_[np.arange(0, 199, 8), 199]
    spec = roads.Spec(w, kind, False, cls)
    width = roads.carriageway(cls, kind, True) if kind in roads.BUILT else w
    return grading.Plan(xy[keep], z[keep], width / 2 + grading.shoulder(spec)), spec


class GradePointsTest(unittest.TestCase):
    def grid(self):
        xs, ys = np.meshgrid(np.arange(-60.0, 60.1, 1.0), np.arange(-40.0, 40.1, 1.0))
        return xs.ravel(), ys.ravel(), slope_ground(xs.ravel(), ys.ravel())

    def test_flat_across_untouched_away(self):
        px, py, base = self.grid()
        p, _ = plan_line(-200, 200, 0.0)
        out = grading.grade_points(px, py, base, [p])
        core = np.abs(py) <= p.half - 0.01
        for x in (-30.0, 0.0, 25.0):
            col = core & (np.abs(px - x) < 0.5)
            self.assertLess(np.ptp(out[col]), 0.02, f"flat across the core at x={x}")
        far = np.abs(py) > p.half + grading.T_MAX + 0.5
        self.assertTrue(np.allclose(out[far], base[far]), "untouched beyond the transition")
        mid = (np.abs(py) > p.half) & (np.abs(py) < p.half + grading.T_MIN)
        self.assertTrue((np.abs(out[mid] - base[mid]) <= np.abs(out[core].mean() - base[mid]) + 1.0).all())

    def test_lift_under_roads_only(self):
        px, py, base = self.grid()
        p, _ = plan_line(-200, 200, 0.0)
        flat = grading.grade_points(px, py, base, [p])
        lifted = grading.grade_points(px, py, base, [p], lift=grading.ROAD_LIFT)
        core = np.abs(py) <= p.half - 0.01
        self.assertTrue(np.allclose(lifted[core] - flat[core], grading.ROAD_LIFT), "the physics ground under the road")
        far = np.abs(py) > p.half + grading.T_MAX + 0.5
        self.assertTrue(np.allclose(lifted[far], base[far]), "untouched away from roads")
        self.assertTrue(((lifted - flat) <= grading.ROAD_LIFT + 1e-9).all() and ((lifted - flat) >= -1e-9).all())

    def test_junction_blends_and_deterministic(self):
        px, py, base = self.grid()
        a, _ = plan_line(-200, 200, 0.0)
        b = grading.Plan(np.array([[10.0, -200], [10.0, 200]]), np.array([slope_ground(10.0, -200.0),
                                                                          slope_ground(10.0, 200.0)]), 4.0)
        out1 = grading.grade_points(px, py, base, [a, b])
        out2 = grading.grade_points(px, py, base, [a, b])
        self.assertTrue(np.array_equal(out1, out2))
        j = (np.abs(px - 10) < 0.5) & (np.abs(py) < 0.5)
        self.assertTrue(np.isfinite(out1[j]).all())


class ShoulderTest(unittest.TestCase):
    def test_sidewalk_classes_keep_the_sidewalk_flat(self):
        res = roads.Spec(6.0, "paved", True, "residential")
        self.assertGreaterEqual(grading.shoulder(res), roads.SIDEWALK["w"], "the raised slab sits on flat ground")
        self.assertEqual(grading.shoulder(roads.Spec(6.0, "paved", False, "motorway")), grading.SHOULDER_M)
        self.assertEqual(grading.shoulder(roads.Spec(4.0, "dirt", False, "track")), 0.0)


class FakeMD:
    def __init__(self, feats):
        self.feats, self.calls = feats, 0

    def cell(self, key, layers=None, kind=None):
        self.calls += 1

        class C:
            pass
        c = C()
        c.layers = {"roads": self.feats}
        return c


class FailingMD:
    def __init__(self):
        self.calls = 0

    def cell(self, key, layers=None, kind=None):
        self.calls += 1
        raise OSError("offline")


class GraderTest(unittest.TestCase):
    def test_failed_fetch_not_retried_at_once(self):
        md = FailingMD()
        g = grading.Grader(FRAME, md, lambda la, lo: np.zeros(np.shape(la)))
        lat, lon = np.full((2, 2), LAT), np.full((2, 2), LON)
        base = np.ones((2, 2))
        self.assertTrue(np.array_equal(g.apply(lat, lon, base), base), "ungraded without road data")
        n = md.calls
        g.apply(lat, lon, base)
        self.assertEqual(md.calls, n, "a failed cell waits RETRY_S before it is fetched again")

    def test_plans_once_per_cell_and_dem_dropin(self):
        f = features([[(-300, 20), (300, 20)]], ["residential"])
        md = FakeMD(f)
        g = grading.Grader(FRAME, md, lambda la, lo: np.full(np.shape(la), 10.0))
        lat = np.full((3, 3), LAT)
        lon = np.full((3, 3), LON)
        g.apply(lat, lon, np.zeros((3, 3)))
        n = md.calls
        g.apply(lat, lon, np.zeros((3, 3)))
        self.assertEqual(md.calls, n, "cell plans cached")

        class Dem:
            def sample(self, la, lo, zoom, progress=None):
                return np.zeros(np.shape(la))
            other = 42
        gd = grading.GradedDem(Dem(), g)
        la, lo, _ = FRAME.enu_to_geodetic(np.array([0.0, 0.0]), np.array([20.0, 200.0]), 0.0)
        z = gd.sample(la, lo, 15)
        self.assertAlmostEqual(float(z[0]), 10.0, delta=0.05, msg="on the road: its profile")
        self.assertAlmostEqual(float(z[1]), 0.0, delta=1e-9, msg="far from it: the DEM")
        self.assertEqual(gd.other, 42, "other attributes pass through")



class OverTunnelsParity(unittest.TestCase):
    """Grader._over_tunnels: Rust (earthfast.over_tunnel) and numpy, point for point."""

    def test_same_mask(self):
        import threading
        import types
        import fast
        if not (fast.AVAILABLE and hasattr(fast._ef, "over_tunnel")):
            self.skipTest("no earthfast.over_tunnel")
        rng = np.random.default_rng(3)
        xy = np.cumsum(rng.normal(0, 5, (400, 2)), 0)
        g = types.SimpleNamespace(lock=threading.Lock(), covers={"a": [(xy, 6.0)], "b": [(xy[::-1] + 3, 4.0)]})
        e = rng.uniform(xy[:, 0].min() - 20, xy[:, 0].max() + 20, 30000)
        n = rng.uniform(xy[:, 1].min() - 20, xy[:, 1].max() + 20, 30000)
        r = grading.Grader._over_tunnels(g, e, n)
        ef = fast._ef
        fast._ef = None
        try:
            p = grading.Grader._over_tunnels(g, e, n)
        finally:
            fast._ef = ef
        self.assertTrue(r is not None and r.any())
        np.testing.assert_array_equal(r, p)


class RoadOverUnderpass(unittest.TestCase):
    def test_raw_dem_peak_cannot_put_a_tunnel_above_the_graded_surface_road(self):
        # A short raw DEM peak can clear the minimum-run/height tests while the upper
        # road's smoothed profile lies below even the lowest tunnel vault. Do not turn
        # that unresolved crossing into a roof and raised terrain through the motorway.
        f = features([[(0, -140), (0, 140)], [(-60, 0), (60, 0)]],
                     ["motorway", "tertiary"], widths=[(0, 13.0), (1, 7.0)], flags=[(1, "is_tunnel")])

        def raw(lat, lon):
            e, n, _ = FRAME.geodetic_to_enu(lat, lon, 0.0)
            return 100 + 6 * np.exp(-(e * e + n * n) / 16)

        g = grading.Grader(FRAME, FakeMD(f), raw)
        elev = lambda la, lo: g.apply(la, lo, raw(la, lo), grading.ROAD_LIFT)
        tunnel = roads.TunnelProfiles(FRAME, lambda key: f, elev)
        tunnel.raw = raw
        tunnel.ends = lambda la, lo: g.apply(la, lo, raw(la, lo), grading.ROAD_LIFT, roads_only=True)
        lat, lon, _ = FRAME.enu_to_geodetic(np.zeros(1), np.zeros(1), 0.0)
        asphalt = elev(lat, lon)
        parts = tunnel.parts([f], (-100.0, -100.0, 100.0, 100.0))
        raised = roads.arch_raise(parts, tunnel.heights, np.zeros(1), np.zeros(1), asphalt, tunnel.mouths)
        self.assertLess(float(raised[0] - asphalt[0]), 0.02, "no terrain obstruction through the asphalt")
        self.assertFalse(parts, "raw cover cannot supply missing final road clearance")

    def test_upper_road_preserves_real_crest(self):
        f = features([[(-180, 0), (180, 0)], [(0, -80), (0, 80)]],
                     ["motorway", "tertiary"], widths=[(0, 13.0), (1, 7.0)],
                     flags=[(1, "is_tunnel", 0.4, 0.6)], levels=[(1, -1, 0.4, 0.6)])

        def elev(lat, lon):
            e, n, _ = FRAME.geodetic_to_enu(lat, lon, 0.0)
            return 100 + 2 * np.exp(-(e / 24) ** 2) - 8 * (1 - np.exp(-(n / 12) ** 2))

        g = grading.Grader(FRAME, FakeMD(f), elev)
        x = np.arange(-80, 80.1, 2.0)
        lat, lon, _ = FRAME.enu_to_geodetic(x, np.zeros(len(x)), 0.0)
        z = g.apply(lat, lon, elev(lat, lon))
        self.assertGreater(z[len(x) // 2], 101.5,
                           "filling an underpass dip must not cut an actual upper-road crest to its endpoint chord")

    def test_surface_overlay_is_independent_of_cache_warm_order(self):
        import threading
        from types import SimpleNamespace

        xy = np.array([[-60.0, 0.0], [0.0, 0.0], [60.0, 0.0]])
        low = grading.Plan(xy, np.full(3, 100.0), 4.0)
        high = grading.Plan(xy, np.full(3, 104.0), 4.0)
        unrelated = grading.Plan(xy, np.full(3, 500.0), 4.0)
        x, y, base = np.array([-12.0, 0.0, 12.0]), np.zeros(3), np.zeros(3)

        def sample(entries):
            g = SimpleNamespace(lock=threading.Lock(), crossovers=dict(entries))
            return grading.Grader._surface_over_tunnels(g, x, y, base, 0.0, ["a", "b"])

        before = sample([("a", [low]), ("b", [high])])
        after = sample([("unrelated", [unrelated]), ("b", [high]), ("a", [low])])
        np.testing.assert_array_equal(before, after,
                                      err_msg="worker completion and unrelated prior cell loads cannot change terrain")
        np.testing.assert_allclose(after, 102.0, atol=1e-9,
                                   err_msg="distinct repaired profiles with matching endpoints are both retained")

    def test_upper_road_stays_smooth_over_unresolved_lower_road(self):
        # A3 / Graßer Weg: the tunnel tag proves two levels even though the DEM resolves
        # part of the lower road in the upper carriageway and shows less than 4 m cover.
        f = features([[(-180, 0), (180, 0)], [(0, -80), (0, 80)]],
                     ["motorway", "tertiary"], widths=[(0, 13.0), (1, 7.0)],
                     flags=[(1, "is_tunnel", 0.4, 0.6)], levels=[(1, -1, 0.4, 0.6)])

        def elev(lat, lon):
            e, n, _ = FRAME.geodetic_to_enu(lat, lon, 0.0)
            return (100 + 0.02 * e - 6 * (1 - np.exp(-(n / 12) ** 2))
                    - 3 * np.exp(-(e / 8) ** 2) * np.exp(-(n / 8) ** 2))

        g = grading.Grader(FRAME, FakeMD(f), elev)
        x = np.arange(-80, 80.1, 0.5)
        lat, lon, _ = FRAME.enu_to_geodetic(x, np.zeros(len(x)), 0.0)
        z = g.apply(lat, lon, elev(lat, lon))
        self.assertLess(abs(z[len(x) // 2] - 100), 0.08, "upper road bridges the DEM's false dip")
        self.assertLess(np.abs(np.diff(z) / 0.5).max(), 0.035, "no kink at the repair's ends")
        lat, lon, _ = FRAME.enu_to_geodetic(np.zeros(2), np.array([-16.0, 16.0]), 0.0)
        portals = g.apply(lat, lon, elev(lat, lon), roads_only=True)
        self.assertTrue((portals < 97).all(), "lower portals keep their approach elevation")


if __name__ == "__main__":
    unittest.main()
