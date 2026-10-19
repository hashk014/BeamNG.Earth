# World generation fidelity

This change follows the European traffic work. It addresses geometric errors in
the conversion from mapped features to playable surfaces, rather than changing
the imagery provider. The data caches and wire protocol remain compatible.

## Roads and terrain

- Road simplification measures distance to a finite segment, retaining a
  collinear reversal instead of deleting a hairpin.
- Road skin resampling keeps source vertices in addition to the two metre
  drape samples. Closed ribbons share the same edge normal at their seam.
- Concave intersection patches use ear clipping. A triangle fan could paint
  the missing corner of an L-shaped patch over a sidewalk.
- Ground grading smooths the residual from a linear grade. A short, constant
  uphill road stays uphill at its endpoints instead of flattening there.
  Bridge and tunnel smoothing retain their existing boundary treatment.
- Grading plans retain source corners when thinning the height profile.
- The grading footprint respects mapped and measured carriageway widths.
  Unknown widths still reserve the previous urban parking envelope without
  making terrain generation depend on land-cover loading order.

## Buildings

- Inner rings become open courtyards in the near mesh, coarse mesh and collision
  mesh. Inner walls face the courtyard. Roofs and raised undersides are split
  into cells around holes using an even-odd sweep, with no new dependency.
- The collision activation guard uses courtyard cells instead of one enclosing
  box. Axis-aligned courts no longer disable the entire building's collision
  simply because the vehicle is inside the courtyard.
- All components of a MultiPolygon footprint are imported, including components
  whose centre lies in another road tile. Duplicate source cells are deduplicated
  per feature and component. Building parts retain their own holes and roof tags.
- A mapped roof height is used for the actual roof rise, not only subtracted
  from the walls. The mapped ridge bearing or across-footprint orientation is
  used when it fits the footprint. The bearing convention follows the
  [Overture building schema](https://docs.overturemaps.org/schema/reference/buildings/building/).
- Pitched roof collision follows the visible roof instead of a flat lid at the
  eaves. Decorative details remain outside the simplified collision mesh.
- Foundation sampling includes points at most four metres apart along outer
  and courtyard walls. Ground sampling is batched once per tile, with a separate
  optional alpine probe. A low or high point midway along a wall is no longer
  missed merely because its corners have equal elevations.
- The procedural appearance seed uses the feature's stable ID. Moving the tile
  origin no longer changes that seed. District classification and neighbour
  availability can still affect inferred styles; this is not a guarantee that
  every aspect of a building is invariant across every rebase.

## Validation on 2026-10-19

The regression suite covers road geometry, buildings, grading, traffic,
sidewalk collision, tunnels, polygon geometry, native/Python kernel agreement,
worker output, terrain heightmaps, mesh generation and CDAE serialization.
`server/tests/test_world_fidelity.py` contains the new focused regressions.
The final selected suite ran 332 tests: 331 passed and one stock game asset
check was skipped because that existing test uses a Linux installation path.
The 16 new regressions also pass on their own:

```powershell
.venv\Scripts\python.exe -m unittest discover -s server/tests -p test_world_fidelity.py
```

A separate check used the first 200 multi-vertex ground road parts from the
cached cell containing `46.502598, -1.780002`. Of their 1,344 source vertices,
171 lay more than 25 cm from the old grading plan; the largest error was
1.410687 m. The new plan retained every source vertex with an error below
the six-decimal reporting precision. This measures fidelity to mapped
geometry, not positional accuracy of the map against a real-world survey.

The cached-data audit built nine road tiles at each of three positions, using
the same Overture 2026-09-23.1 source files and Mapterhorn elevation as before.
All 21 requested DEM tiles came from disk; no missing elevation tile was
replaced with a zero-height fallback. Generated meshes had finite vertices and
valid indices. Building mesh parts stayed within the existing 60,000 vertex
budget and were serialized and decoded as CDAE, including the coarse LOD.

| Sample | Buildings | Courtyards before / after |
| --- | ---: | ---: |
| Les Sables-d'Olonne, 46.502598, -1.780002 | 2,097 | 0 / 4 |
| Fuji region, 35.398006, 138.724365 | 1 | 0 / 0 |
| Mount Whitney, 36.5785, -118.2923 | 1 | 0 / 0 |

In the French sample, road triangles increased from 50,795 to 58,736 and
building collision triangles from 31,470 to 34,426. Visual building triangles
decreased from 347,900 to 343,046, partly because the stable ID seed changes
previously inferred appearances. These are geometry counts, not FPS results.
The two mountain samples are sparse-building smoke tests, not city coverage.
Numbers and single-run timings are in `research/world-generation-validation.json`.
Timings are not a controlled performance benchmark.

BeamNG was closed during this pass. It has not been validated by driving this
newly rebuilt world in the game. The earlier traffic-only runtime test does not
validate these world geometry changes. See `TESTER_LE_MONDE.md` for manual tests.

## Remaining limits

- Resolution and missing tags in the source data still bound accuracy. No new
  photogrammetry, interiors, facade photographs or higher-resolution DEM were
  added. Roofs without tags and facades still use procedural inference.
- Courtyard buildings currently use flat roofs. Complex pitched roofs around
  courts, arbitrary concave pitched roofs and building-part ownership across
  very large parent footprints need further work.
- The sweep expects valid simple rings with non-intersecting holes. Collision
  activation boxes around rotated cells remain conservative near sloped edges.
- A global tile boundary can still change the surrounding district and neighbour
  context. Foundations follow a more complete sampled envelope, but this does
  not reconstruct terraced floor levels or detailed retaining structures.
- Dense-city collision rebuilds, narrow hairpin mesh overlaps, long drives,
  grade transitions at junctions and visual quality need the in-game test pass.
