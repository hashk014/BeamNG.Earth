"""Issues #8/#53: bounded sea tiles must not cover known, dry below-sea-level land."""
import unittest
from unittest import mock
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seatiles
import seacarve


class FlatFrame:
    def enu_to_geodetic(self, east, north, up):
        return np.asarray(north), np.asarray(east), np.zeros(np.shape(east))

    def geodetic_to_enu(self, lat, lon, height):
        return np.asarray(lon), np.asarray(lat), np.asarray(height)


class CoastalTilesTest(unittest.TestCase):
    def test_open_sea_has_no_extra_queries_or_tiles(self):
        frame = FlatFrame()
        wet = lambda la, lo, size: np.ones(np.shape(la), bool)
        dry = mock.Mock(side_effect=AssertionError("open sea needs no land queries"))
        baseline = seatiles.plan(frame, 0, 0, wet, radius=1000)
        self.assertEqual(seatiles.plan(frame, 0, 0, wet, radius=1000, dry_at=dry), baseline)
        dry.assert_not_called()

    def test_coastal_tiles_leave_dry_polder_uncovered(self):
        wet = lambda la, lo, size: np.asarray(lo) >= 37
        tiles = seatiles.plan(FlatFrame(), 20, 10, wet, radius=1000,
                             dry_at=lambda la, lo, size: np.ones(np.shape(la), bool))
        self.assertTrue(tiles)
        for tile in tiles:
            self.assertGreaterEqual(tile.x - tile.size / 2, 37)
            self.assertTrue(tile.key.startswith("C"))
        self.assertTrue(any(t.x - t.size / 2 <= 512 < t.x + t.size / 2
                            and t.y - t.size / 2 <= 256 < t.y + t.size / 2 for t in tiles))

    def test_unknown_or_high_dry_land_preserves_existing_plan(self):
        wet = lambda la, lo, size: np.asarray(lo) >= 37
        baseline = seatiles.plan(FlatFrame(), 20, 10, wet, radius=1000)
        self.assertEqual(seatiles.plan(FlatFrame(), 20, 10, wet, radius=1000,
                                      dry_at=lambda la, lo, size: np.zeros(np.shape(la), bool)), baseline)

    def test_upstream_ground_callback_refines_low_land_without_a_map_callback(self):
        wet = lambda la, lo, size: np.asarray(lo) >= 37
        tiles = seatiles.plan(FlatFrame(), 20, 10, wet, radius=1000,
                              ground_at=lambda la, lo, size: np.full(np.shape(la), -4.0))
        self.assertTrue(tiles)
        self.assertTrue(all(t.x - t.size / 2 >= 37 for t in tiles))

    def test_mapped_dry_land_is_protected_when_ground_callback_disagrees(self):
        wet = lambda la, lo, size: np.asarray(lo) >= 37
        dry = lambda la, lo, size: np.ones(np.shape(la), bool)
        baseline = seatiles.plan(FlatFrame(), 20, 10, wet, radius=1000, dry_at=dry)
        self.assertEqual(seatiles.plan(FlatFrame(), 20, 10, wet, radius=1000, dry_at=dry,
                                      ground_at=lambda la, lo, size: np.full(np.shape(la), 3.0)), baseline)

    def test_refinement_is_bounded_and_deterministic(self):
        wet = mock.Mock(side_effect=lambda la, lo, size: np.floor(np.asarray(lo) / 17).astype(int) % 2 == 0)
        dry = lambda la, lo, size: np.ones(np.shape(la), bool)
        with mock.patch.object(seatiles, "COAST_MAX_NODES", 12), mock.patch.object(seatiles, "COAST_MAX_TILES", 4):
            first = seatiles.plan(FlatFrame(), 20, 10, wet, radius=1000, dry_at=dry)
            # Original leaves are queried in at most three size batches; refinements are capped.
            self.assertLessEqual(wet.call_count, 15)
            self.assertLessEqual(len(first), 4)
            self.assertEqual(seatiles.plan(FlatFrame(), 20, 10, wet, radius=1000, dry_at=dry), first)


class DryLandClassificationTest(unittest.TestCase):
    def test_only_known_dry_low_land_is_protected(self):
        sea = object.__new__(seacarve.SeaCarver)
        sea.water = lambda la, lo, wait=False: (
            np.array([0, 5, 3, 0, 0]), np.array([np.nan, 0, -3, np.nan, np.nan]),
            np.array([True, True, True, False, True]),
        )
        dem = mock.Mock()
        dem.sample.return_value = np.array([-4.0, 8.0])
        result = sea.dry_at(dem, np.full(5, 52.3), np.arange(5), 512)
        np.testing.assert_array_equal(result, [True, False, False, False, False])
        np.testing.assert_array_equal(dem.sample.call_args.args[1], [0, 4])


if __name__ == "__main__":
    unittest.main()
