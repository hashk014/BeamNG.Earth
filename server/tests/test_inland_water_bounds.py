"""Inland water must not leak across a dam into low ground beside the lake."""
import sys
from pathlib import Path
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seatiles


class FlatFrame:
    def enu_to_geodetic(self, east, north, up):
        return np.asarray(north), np.asarray(east), np.zeros(np.shape(east))

    def geodetic_to_enu(self, lat, lon, height):
        return np.asarray(lon), np.asarray(lat), np.asarray(height)


class InlandBounds(unittest.TestCase):
    def test_finest_tile_cannot_flood_land_below_a_coastal_lake(self):
        # A lake above the sea, separated by a narrow bank. Even the last 16 m tile
        # must reject the low ground outside the water footprint.
        lake = lambda la, lo: np.where(np.asarray(lo) >= 7.0, 8.4, np.nan)
        ground = lambda la, lo: np.where(np.asarray(lo) >= 7.0, 8.4, 0.0)
        tiles = seatiles.plan_lakes(FlatFrame(), 20, 20, lake, ground, radius=100)
        self.assertTrue(tiles, "valid interior water is retained")
        for tile in tiles:
            self.assertGreaterEqual(tile.x - tile.size / 2, 7.0,
                                    "an exhausted refinement cannot justify flooding the sea-side bank")
        self.assertLessEqual(len(tiles), seatiles.LAKE_MAX_TILES)
        self.assertEqual(tiles, seatiles.plan_lakes(FlatFrame(), 20, 20, lake, ground, radius=100))

    def test_lake_on_high_banks_does_not_need_extra_refinement(self):
        lake = lambda la, lo: np.where(np.asarray(lo) >= 7.0, 8.4, np.nan)
        ground = lambda la, lo: np.where(np.asarray(lo) >= 7.0, 8.4, 12.0)
        tiles = seatiles.plan_lakes(FlatFrame(), 20, 20, lake, ground, radius=100)
        self.assertTrue(tiles)
        self.assertTrue(all(t.size == seatiles.LAKE_TILE_MAX for t in tiles))


if __name__ == "__main__":
    unittest.main()
