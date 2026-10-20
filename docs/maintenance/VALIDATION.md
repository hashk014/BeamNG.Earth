# Validation ledger

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
| `python tools/maintenance.py test --suite quick` | 47 passed | Storage, launcher, filesystem recovery, synthetic teleports, surface metadata, coastal water, area prefetch |
| `python tools/maintenance.py test --suite generators` | 223 passed | Terrain, roads, physics materials, buildings, traffic, water and vegetation |
| `python tools/run_lua_tests.py` | 44 files, 4,702 checks passed | LuaJIT with engine stubs; includes new rock/prop persistence and coastal physics |
| `node mod/tests/test_mapmath.mjs` | Passed | UI map layers and credits math |
| `node server/tests/test_mapmath.mjs` | Passed | Server map-layer math |
| Live source-cache smoke | DEM, roads and imagery fetched, then read with networking disabled | Three small real cached samples; [details](PREFETCH.md) |

The Lua road test now advances a deterministic fake clock. The previous stub failure
on Windows came from testing a zero-delay rebuild against the host CPU clock before
its coarse tick advanced. Production collision timings were not weakened.

Machine-readable results are written to `dist/*validation.json`, and the consolidated
Windows/Linux CI uploads them as artifacts. This candidate does not claim the entire
legacy suite passes: historical Windows deletion timing failures and Linux-only
launcher fixture assumptions are documented in the earlier research reports.
The full slow server suite was not rerun after every change in this batch.

## Runtime handoff

The maintenance batch still needs actual BeamNG checks for saved UI settings,
coastline rendering, dry below-sea-level roads, material physics, long drives,
cache relocation on another physical volume and offline travel in a downloaded area.
Record exact version, location, regeneration steps and observed outcome for each check.
