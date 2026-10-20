# Coastal water and low dry land

Issues: [#8](https://github.com/TecnaGamer/BeamNG.Earth/issues/8),
[#53](https://github.com/TecnaGamer/BeamNG.Earth/issues/53).

The existing ocean mask already uses mapped water. The rendering problem is that
a square WaterBlock was kept if any of its samples were sea: its full square can
extend across a dry polder. The smallest original sea square spans 2 km.

The planner now refines squares that contain both sea and known dry land more
than 25 cm below sea level. It keeps safe water squares, splits mixed squares
down to 32 m and omits unresolved squares. It does not raise the terrain. Work
is bounded to 256 additional nodes and 96 additional water squares per plan;
open ocean does not need the extra dry-land queries.

Refined coastal squares carry a `C` key prefix. The mod disables their overlap
and confines the invisible player-water physics box to the approved square.
Otherwise the old 256 m physics box could flood dry land beside a small square.

## Validation and limits

```sh
python -m unittest discover -s server/tests -p test_coastal_water.py -v
python -m unittest discover -s server/tests -p test_seatiles.py -v
python -m unittest discover -s server/tests -p test_seacarve.py -v
python tools/run_lua_tests.py test_sea.lua
```

Synthetic coastline tests check dry-land protection, preserved open-ocean behavior,
deterministic bounded work and rejection of unknown map data as proof of dry land.
Lua engine-stub tests verify visible and hidden volumes at small coastal squares.

This is a conservative, sampled boundary treatment. Unknown or incorrect source
data can still cause errors; narrow details below the sampling grid can be missed.
Where refinement reaches its size or work limit, water can have gaps. Inland water
below sea level and the original lake-level estimation are separate remaining work.
No Netherlands gameplay or water-object performance measurement has been performed.
