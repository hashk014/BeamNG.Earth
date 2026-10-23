# Validation ledger

## Experimental streaming integration (2026-10-23)

Upstream development snapshot: `b15991e`, after the 1.6.0 release. The fork adapts
its shared grading cache to retain protected upper-road profiles across workers.
The [integration report](../research/2026-10-23-streaming-stability.md) records the
scope, commands, corrected Windows test-cleanup failure and gameplay checks.

Local Windows suites: quick **62 passed**, generators **361 passed**, integration
**280 passed / 2 skipped**, streaming **96 passed / 1 skipped**. These four suites
total **799 passing checks and 3 skips**. The streaming suite is now included in
the Windows/Linux maintenance workflow, using synthetic imagery sources only.
Native version 67 loads successfully; Python compilation passes. These checks
do not establish an FPS gain, two-player reliability or original-issue resolution.

## Road rendering choice and worker consistency (2026-10-23)

The patch keeps terrain roads as the default, adds a saved startup choice, and
passes the chosen mode into local and remote workers. Before the fix, focused
regressions reproduced missing mode validation and helper-pool selection. This
does not establish the visual symptoms of upstream #179 as fixed.

| Command from the repository Python environment | Windows result | Scope |
| --- | --- | --- |
| `python tools/maintenance.py test --suite quick --report dist/road-rendering-quick-validation.json` | 62 passed | Includes seven new preference tests through fresh source/launcher processes and isolated config roots |
| `python tools/maintenance.py test --suite generators --report dist/road-rendering-generator-validation.json` | 361 passed | Existing terrain/mesh road generation, neighboring geometry and fork regressions |
| `python tools/maintenance.py test --suite integration --report dist/road-rendering-integration-validation.json` | 275 passed, 1 skipped (276 run) | Includes seven new shared-mode regressions and actual spawned workers with an opposite environment |
| `python tools/run_lua_tests.py --report dist/road-rendering-lua-validation.json` | 54 files passed | Engine stubs, not gameplay |
| Both `node mod/tests/test_mapmath.mjs` and `node server/tests/test_mapmath.mjs` | Passed | Map math |
| `python -m compileall -q server launcher.py start.py tools` | Passed | Syntax/import bytecode compilation |

Total: 698 Python tests passed, one additional check skipped because a separate
`luajit` executable is unavailable. Existing peer socket tests emit resource
warnings; there are no test failures. The full slow server/restart suites were
not repeated for this patch; their earlier results below remain historical.

The focused upstream branch at `99c295b` passes
[Windows and Linux worker checks](https://github.com/hashk014/BeamNG.Earth/actions/runs/39993299377),
covering peer work, block-worker parity and road generation against upstream
`main` at `18f131c`. It is proposed as
[upstream PR #187](https://github.com/TecnaGamer/BeamNG.Earth/pull/187), independently
of the fork's preference and maintenance documentation.
The PR's [own upstream Windows/Linux run also passed](https://github.com/TecnaGamer/BeamNG.Earth/actions/runs/39993356422).

The source ZIP built from `7bb6cdc` passed CRC, bounded-path extraction, byte
agreement for the changed modules/guides, saved mesh selection across both
extracted launchers, default reset and `launcher.py --server --help`. Checks used
temporary user/config roots and the existing development Python environment.
This validates source packaging, not an independently installed EXE. The archive
and SHA-256 are recorded in `dist/road-rendering-candidate/validation.json`.
Consolidated local evidence is also tracked in
[`../research/2026-10-23-road-rendering-validation.json`](../research/2026-10-23-road-rendering-validation.json).

This is source validation. No new public executable, original-location gameplay,
two-player driving, visual quality, physical collision or FPS improvement is
claimed. The [road-mode guide](ROAD_RENDERING.md) defines the outstanding comparison.

## Upstream 1.6.0 integration (2026-10-23)

Target: upstream release `v1.6.0-beta` at `b4c478d68795e441eef2ba9fb5981e74c7b11f49`.
Fork version: `1.6.0-europe-preview.2-dev`. Native `earthfast` version 60 is included
from upstream; its newer native-required pipeline supersedes the older fallback totals below.

| Check | Local Windows result | Evidence scope |
| --- | --- | --- |
| `python tools/maintenance.py test --suite quick --report dist/160-quick-validation.json` | 55 passed | Saved storage, quick-play compatibility, bounded water, prefetch and isolated session-file recovery |
| `python tools/maintenance.py test --suite generators --report dist/160-generator-validation.json` | 361 passed | Combined upstream/fork geometry, materials, traffic, tunnels, Decathlon and lake bounds |
| `python tools/maintenance.py test --suite integration --report dist/160-integration-validation.json` | 268 passed, 1 skipped (269 run) | Worker parity, native kernels, approach ramps, OSM widths, peer wire, checked updater, imagery, polar DEM and synthetic protocol |
| `python tools/run_lua_tests.py --report dist/160-lua-validation.json` | 54 files, 4,975 assertions passed | Engine stubs, including BeamMP, terrain swap, saved World settings and bytecode scoping |
| `node mod/tests/test_mapmath.mjs` and `node server/tests/test_mapmath.mjs` | Both passed | Map math |
| `python -m compileall -q server launcher.py start.py tools` | Passed | Python compilation |

The one protocol test requiring an external `luajit` executable skips on this PC;
Lupa runs all 54 separate Lua files successfully. The new scoping check reads
LuaJIT bytecode via `jit.util`, including nested prototypes, and receives a file
inventory from the Python runner. It does not depend on Unix `find` or a CLI LuaJIT.

The integration fixes retain the captured Decathlon regression within its original
2 cm comparison tolerance and keep the 3 percent local profile-step bound. Repaired
upper-road pieces use the same grading kernel without yielding to each other's
road IDs; ordinary road grading retains upstream's level separation. Narrow measured
widths stay authoritative. Polygon triangulation no longer shadows the terrain
quantization argument when the newer mesh follows the terrain lattice.

The maintenance workflow runs quick, generators, integration, all Lua stubs and both
map-math suites on Windows and Linux. [Both platforms passed at source merge 6eda732](https://github.com/hashk014/BeamNG.Earth/actions/runs/39989395375).
Each runner has two integration skips: no usable GPU for equivalence and no
external luajit executable. The GPU equivalence check passes on the local PC. The separate full synthetic server run passes all **43 tests** and the restart
module passes all **10 tests** (403.4 s and 81.2 s respectively). All three
historical Windows timing failures named in the 20 October recovery report pass
in this run after the upstream changes. This is one run, not proof that every
Windows scheduler/filesystem condition is resolved.

The frozen runtime passes a real protocol 4 / format 4 handshake in isolated
user/cache directories and reports the correct fork version. Its installed mod
matches the frozen mod tree. The source and BeamMP ZIP archives pass CRC checks.
See [the integration report](../research/2026-10-23-upstream-160-integration.md)
for the CI reference and the local handoff.

These are automated source checks. They do not establish BeamNG rendering, physical
collision, multiplayer interoperability, FPS or real loading-time gains. The new
1.6 performance, autodrive, small-road appearance and Melbourne flooding reports
remain open in the issue inventory. No new public executable is claimed.

## Reproduction commands

Use the repository's Python environment, for example `.venv/Scripts/python.exe`
on Windows or `.venv/bin/python` on Linux. Run commands from the repository root.

```sh
python -m unittest discover -s server/tests -p test_launcher_compat.py -v
python -m unittest discover -s server/tests -p test_staging.py -v
python -m unittest discover -s server/tests -p test_session_output.py -v
```

## Existing evidence

- Linux-runtime detection: seven tests passed locally and on Windows/Linux CI.
- Session-file recovery: 275 local tests passed, one stock-asset test was skipped,
  and three timing-sensitive server tests also fail on unchanged baseline code.
- The original issues remain open upstream. The fork's first two maintenance PRs
  have been merged into `preview`.

## Current maintenance candidate (2026-10-20)

| Check | Result on local Windows | Scope |
| --- | --- | --- |
| `python tools/maintenance.py test --suite quick` | 51 passed | Storage, launcher, filesystem recovery, synthetic teleports, surface metadata, coastal water, area prefetch |
| `python tools/maintenance.py test --suite generators` | 243 passed | Terrain, roads, physics materials, buildings, traffic, water and vegetation |
| `python tools/run_lua_tests.py` | 44 files, 4,703 checks passed | LuaJIT with engine stubs; includes new rock/prop persistence and coastal physics |
| `node mod/tests/test_mapmath.mjs` | Passed | UI map layers and credits math |
| `node server/tests/test_mapmath.mjs` | Passed | Server map-layer math |
| Live source-cache smoke | DEM, roads and imagery fetched, then read with networking disabled | Three small real cached samples; [details](PREFETCH.md) |

The Lua road test now advances a deterministic fake clock. The previous stub failure
on Windows came from testing a zero-delay rebuild against the host CPU clock before
its coarse tick advanced. Production collision timings were not weakened.

Removing solid rocks or props also requests a collision refresh through the usual
scheduler. The stub regression checks that removal requests it, in addition to
checking visible item counts; actual collision removal still needs the in-game check.

Machine-readable results are written to `dist/*validation.json`, and the consolidated
Windows/Linux CI uploads them as artifacts. This candidate does not claim the entire
legacy suite passes: historical Windows deletion timing failures and Linux-only
launcher fixture assumptions are documented in the earlier research reports.
The full slow server suite was not rerun after every change in this batch.

The maintenance workflow uses fixed Ubuntu 24.04 and Windows 2025 images. Its
checkout/setup/upload actions are pinned to the verified Node 24 release commits,
replacing the Node 20 deprecation warnings observed during the first green run.
Upgrade these pins separately and re-run the matrix when the toolchain changes.

## Surface-classifier microbenchmark

The classifier now uses a precomputed tag lookup. Ordinary single tags avoid
allocating a set and intersecting several material sets for every road feature.
Composite tags preserve the same loose-surface priority.

On local Python 3.12.10, a fixed workload of eight metadata cases, 100,000
iterations and the median of five repeats measured 0.31337 s before versus
0.15799 s with the lookup, a 1.98x speedup for this function. Outputs matched
on the workload and the material regression suites pass. This is neither an
end-to-end generation benchmark nor a game/FPS measurement.

```sh
python tools/benchmark_road_surfaces.py --baseline 6d143e6
```

The historical function is evaluated using the current shared surface-tag
constants; those constants are unchanged between these two measurements.

## Runtime handoff

The subsequent urban-geometry pass has 243 passing generator tests (including 20
new building/sidewalk regressions), 51 focused maintenance tests, and two real
Les Sables sectors rebuilt with networking disabled. See
[the scoped report](../research/2026-10-20-urban-ground-contact.md).
The exact reported annex is still awaiting location confirmation; a diagnostic
view of the main school showed a complete body. After the test handoff the player
reported that the corrected version looks better. This is limited visual feedback,
without a location list or a complete driving/collision validation.

## Upstream contribution

[Upstream PR #69](https://github.com/TecnaGamer/BeamNG.Earth/pull/69) extracts the
building/sidewalk work onto upstream `main` at `011d6b5`, including the related
building-fidelity prerequisites. It excludes unrelated fork features and launchers.
Local Windows Python 3.12.10 checks pass: 235 tests with native kernels explicitly
disabled and 266 tests with native kernels enabled (including 31 equivalence tests),
with no skips. Its [Windows/Linux CI run](https://github.com/hashk014/BeamNG.Earth/actions/runs/39499801167)
is separate from this fork's maintenance workflow.

The fallback run exposed `any(bool)` in bridge-pier road-clearance testing.
The existing `PierSitesTest.test_spacing_roads_and_low_decks` reproduces the
`TypeError` on unchanged upstream `011d6b5` with native kernels disabled.
Reusing `_seg_dist` fixes this existing fallback; the native pier path is unchanged.
That fix is also backported to this fork. All 74 tests in `test_roads`,
`test_roadmesh` and `test_urban_frontages` pass with `earthfast` disabled here.

The maintenance batch still needs actual BeamNG checks for saved UI settings,
coastline rendering, dry below-sea-level roads, material physics, long drives,
cache relocation on another physical volume and offline travel in a downloaded area.
Record exact version, location, regeneration steps and observed outcome for each check.
