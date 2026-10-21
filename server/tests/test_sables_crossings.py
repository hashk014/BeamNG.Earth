"""Captured road profiles at the user's Decathlon underpass, without a live cache."""
import json
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import geodesy
import grading
import roads
from test_grading import FakeMD
from test_roads import features, FRAME


class SablesCrossing(unittest.TestCase):
    def test_real_upper_carriageway_does_not_blend_into_the_underpass(self):
        record = json.loads((Path(__file__).parent / 'fixtures/sables-decathlon-profile.json').read_text())
        frame = geodesy.EnuFrame(*record['anchor'])
        f = features([[(0, 0), (1, 1)]], ['unclassified'], flags=[(0, 'is_tunnel')],
                     ids=[record['tunnel_id']])
        f.lonlat = np.asarray(record['tunnel_lonlat'])
        grader = grading.Grader(frame, FakeMD(f), lambda la, lo: np.zeros(np.shape(la)))
        plans = [grading.Plan(np.asarray(p['xy']), np.asarray(p['z']), p['half'])
                 for p in record['upper_plans']]
        crossovers = grader._surface_crossings(f, None, plans)
        self.assertTrue(crossovers)
        grader.crossovers['recorded'] = crossovers
        xy = np.asarray(record['probe_xy'])
        before = np.asarray(record['baseline_heights'])
        after = grader._surface_over_tunnels(xy[:, 0], xy[:, 1], before, 0.0, ['recorded'])
        self.assertGreater(abs(np.diff(before)).max(), 0.5, 'the captured baseline contains a trench')
        self.assertLess(abs(np.diff(after)).max(), 0.03, 'the upper road stays below 3 percent here')
        self.assertGreater(after[len(after) // 2] - before[len(before) // 2], 2.8)
        # The full recorded pipeline also restores the raw cover before this
        # overlay. Its sub-centimetre effect stays below the mesh tolerance.
        np.testing.assert_allclose(after, record['repaired_heights'], atol=0.02)

    def test_resolved_upper_profile_supplies_cover_missing_in_the_coarse_dem(self):
        # The Decathlon underpass DEM resolves the lower road, with no hill
        # across it. The separately resolved upper road is the physical cover.
        s = np.arange(0.0, 28.0, 4.0)
        raw = np.full(len(s), 10.44)
        covered = np.ones(len(s), bool)
        upper = np.full(len(s), 16.04)
        floor, kinds = roads.tunnel_sections(s, raw, covered=covered, upper=upper)
        self.assertTrue((kinds == 1).all(), 'mapped short underpass remains covered')
        np.testing.assert_allclose(floor, raw)

    def test_short_tunnel_portals_do_not_cut_the_upper_carriageways(self):
        f = features([[(-100, -5), (100, -5)], [(-100, 5), (100, 5)], [(0, -13.4), (0, 13.4)]],
                     ['primary', 'primary', 'unclassified'], flags=[(2, 'is_tunnel')],
                     widths=[(0, 8.5), (1, 8.5), (2, 5.5)])

        def elev(la, lo):
            _e, n, _u = FRAME.geodetic_to_enu(la, lo, 0.0)
            return np.where(np.minimum(abs(n - 5), abs(n + 5)) <= 4.25, 16.04, 10.44)

        tunnel = roads.TunnelProfiles(FRAME, lambda key: f, elev)
        tunnel.raw = lambda la, lo: np.full(np.shape(la), 10.44)
        tunnel.ends = tunnel.raw
        parts = tunnel.parts([f], (-40, -40, 40, 40))
        self.assertTrue(parts, 'preserve the lower tunnel')
        axis = np.arange(-32.0, 32.0, 1.0)
        x, y = np.meshgrid(axis, axis)
        la, lo, _u = FRAME.enu_to_geodetic(x.ravel(), y.ravel(), 0.0)
        ground = elev(la, lo).reshape(x.shape)
        upper = np.minimum(abs(y - 5), abs(y + 5)) <= 4.0
        unsafe = roads.tunnel_hole_mask(parts, ground, 0, 0, 1, tunnel.heights, tunnel.mouths)
        self.assertTrue(unsafe[upper].any(), 'the unprotected portal mask really cuts an upper road')
        keep = {'lat': la.reshape(x.shape), 'lon': lo.reshape(x.shape), 'u': ground}
        holes = roads.block_tunnel_holes(tunnel, lambda key: f, FRAME, keep, 0, 0, 1)
        self.assertFalse(holes[upper].any())
        self.assertTrue(holes.any(), 'lower portal openings are still cut')
        raised = roads.block_arch_raise(tunnel, lambda key: f, FRAME, la, lo, ground.ravel(),
                                        (-32, -32, 32, 32)).reshape(x.shape)
        np.testing.assert_array_equal(raised[upper], ground[upper],
                                      err_msg='portal flattening cannot lower the road above')


if __name__ == '__main__':
    unittest.main()
