"""Issue #31: incomplete surface metadata must not turn mapped paved streets into dirt."""
import unittest
import numpy as np
from test_roads import features
import roads


class SurfaceMetadataTest(unittest.TestCase):
    def test_unknown_values_use_the_road_class(self):
        for value in (None, "", "  ", "unknown", "unrecognised", np.nan, {}, np.str_("unknown")):
            for cls in ("primary", "residential", "motorway"):
                with self.subTest(value=value, cls=cls):
                    self.assertEqual(roads.surface_kind(cls, value), "paved")
            self.assertEqual(roads.surface_kind("track", value), "dirt")

    def test_normalised_explicit_surfaces_override_class(self):
        for value, kind in (
            (" Asphalt ", "paved"), ("concrete:plates", "paved"), ("concrete:lanes", "paved"),
            ("chipseal", "paved"), ("cobblestone:flattened", "cobble"), ("paving_stones", "cobble"),
            ("fine_gravel", "gravel"), ("crushed_stone", "gravel"), (" SAND ", "dirt"), ("earth", "dirt"),
        ):
            with self.subTest(value=value):
                self.assertEqual(roads.surface_kind("primary", value), kind)
                self.assertEqual(roads.surface_kind("track", value), kind)

    def test_mixed_tags_keep_explicit_loose_surfaces(self):
        for value, kind in (("asphalt;concrete", "paved"), ("asphalt;gravel", "gravel"),
                            ("sand;asphalt", "dirt"), ("unknown;asphalt", "paved")):
            with self.subTest(value=value):
                self.assertEqual(roads.surface_kind("primary", value), kind)

    def test_visible_road_and_physics_specs_share_the_classification(self):
        f = features([[(0, 0), (20, 0)]] * 3, ["residential", "track", "primary"],
                     surfaces=[(0, "unknown"), (1, "concrete:plates"), (2, "unpaved")])
        self.assertEqual([s.kind for s in roads.road_specs(f)], ["paved", "paved", "dirt"])


if __name__ == "__main__":
    unittest.main()
