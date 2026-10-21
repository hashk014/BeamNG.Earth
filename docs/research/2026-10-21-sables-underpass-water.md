# Road separation and inland-water bounds at Les Sables-d'Olonne

Maintenance changes, 21 October 2026. No new public release.

After trying the prepared local version, the player reported that it works
better overall. This is informal gameplay feedback, without a measured drive,
render captures or a completed checklist for the two reported locations.

The player reported holes where a main road passes over a small tunnel near
Decathlon, and excessive water around Lac de Tanchet and the neighbouring sea.
The changes use mapped geometry and elevations; no location is special-cased
in production code.

## Decathlon crossing

Cached Overture Maps 2026-09-23.1 data locates a 25.5 m underpass at
`46.514217, -1.784525`, about 300 m from the shop. Its feature ID is
`907bce43-1f96-427d-b40c-af586d3b3845`. Two primary carriageways cross it.

The lower road's grading blended into the upper road. Separately, low-arch
portal flattening and hole masks could remove upper-road ground even after
its height profile had been repaired.

The candidate:

- Restores a bounded section of the upper carriageway from its own smoothed
  profile, filling false dips while retaining real crests and lower approaches.
- Uses resolved upper-road heights to establish cover when the coarse DEM
  resolves only the lower road. A tube is rejected when those heights cannot
  fit the minimum vault and soil.
- Protects crossing carriageways and the terrain triangles at their edges
  from portal cuts and flattening. The lower tunnel is retained.
- Omits the decorative soil cap under mapped surface roads.
- Preserves solved bridge/tunnel vertical curves within 2 cm during mesh
  simplification and preserves sloping abutment profiles during bridge smoothing.

The separation and profile work adapts Alex Schenker's (Alfao)
[upstream PR #71](https://github.com/TecnaGamer/BeamNG.Earth/pull/71), commit
`0df42a67b31b39f7d0f503b62bb39edf31d20f97`, under the existing MIT licence.
Portal-cut protection and the resolved-cover follow-up were added in this fork.

Offline measurements from cached source, compared with checkout base
`c9059347b3fa358b67fa1d631e0d5e890b29765a`:

| Measurement | Before | Candidate |
| --- | ---: | ---: |
| First carriageway height at crossing | 13.205 m | 16.041 m |
| Second carriageway height at crossing | 13.156 m | 16.096 m |
| Largest one-metre height change within 24 m of first crossing | 0.539 m | 0.0275 m |
| Largest one-metre height change within 24 m of second crossing | 0.516 m | 0.0187 m |
| Upper-road grid samples cut by unprotected / protected portal mask | 82 | 0 |

The final structure probe retains one 3.6 m-high lower tube, with no upper-road
height change from arch raising or portal flattening on the sampled grid.
The committed profile fixture and tests require no cache, network or game.
These numbers do not establish driving safety at speed. Outside this 48 m
crossing corridor, sampled neighbouring roads still contain steep transitions.

## Lac de Tanchet and coastal water

The lake polygon is `a2667c2d-1bc2-33c9-aa95-adb38c615d49`, from OSM relation
`r1310399@3`. Cached interior DEM samples have a median of 8.375 m, producing
an estimated surface of 8.4 m. This is a source estimate, not an independent
measurement of the real lake's current water level.

- Lake checks now include square edges. Centre-only probes could miss a narrow
  low strip at the edge and accept the whole square.
- Squares that would flood low dry ground subdivide down to 16 m, then remain
  omitted if unsafe. The old minimum-size exception accepted them anyway.
- Visible inland squares have no overlap outside their approved bounds. Their
  hidden vehicle-water box is clipped to the same square, like refined coastal
  tiles, instead of extending 256 m around the player.

A diagnostic used the real Tanchet polygon and cached DEM with a fixed 8.4 m
surface, isolating placement from level estimation. On a separate 16 by 16 grid
per emitted square, the old plan covered two dry-land samples more than one
metre below the lake, up to 1.20 m deep. The candidate covers none. Its local
plan uses 32 squares instead of 20, below the unchanged 120-square cap.
This is sampling evidence, not an exact polygon-clipping proof.

The lake's altitude has not been arbitrarily lowered. Absolute water levels,
bathymetry quality, shoreline appearance and marine rendering still need game
inspection. Conservative rejection can leave small water gaps. No universal
sea, inland-water or Netherlands correction is claimed.

## Validation

Python suites used isolated workspace home, cache, app-data and temporary
directories. Geographic probes copied selected cache files into
`dist/sables-quality/cache`, used offline fetchers and did not alter the source cache.

The committed regression tests can be rerun from an activated development
environment. Use an isolated workspace home/cache/temp environment on Windows,
as required by `AGENTS.md`.

```sh
python tools/maintenance.py test --suite generators --report dist/generator-validation.json
python -m unittest discover -s server/tests -p test_fast.py
python tools/run_lua_tests.py
git diff --check
```

The original isolated-process runner, cached-source probes and local-runtime
handshake helper are machine-local scripts under ignored `dist/`. Their
recorded outcomes are in `2026-10-21-sables-quality-evidence.json`; the source
profile fixtures used by the published regression tests are committed.

- Generator suite: 286 passed, no skips or failures. New suites are included in
  `tools/maintenance.py` for the existing Windows/Linux workflow.
- Focused Python fallback: 97 discovered, 94 passed, three native-only checks
  skipped, no failures.
- Existing native-kernel equivalence suite: 31 passed.
- LuaJIT engine stubs: all 44 files pass, 4,707 assertions, including confined
  lake volumes, dry neighbouring ground and tilted inland-water planes.
- A real server process from the frozen candidate answers with protocol 4 /
  format 4, using temporary user and cache directories.
- `git diff --check` passes. CI has not run for this local candidate.

The previous extended Windows server timing failures in
[the session-file report](2026-10-20-session-file-recovery.md) were not rerun or
claimed fixed. No automated BeamNG session, measured collision drive, render
comparison or FPS measurement was performed. The player's informal feedback
above is separate from these automated checks.

The existing desktop shortcut now selects `dist/ingame-ready/runtime-sables-20261021`.
The previous runtime and installed water module/settings were preserved. Two
favourites were added without removing existing places: **TEST 5 - Decathlon -
passage inferieur** and **TEST 6 - Tanchet - lac et mer**. See the
[test handoff](../maintenance/INGAME_READY.md).
