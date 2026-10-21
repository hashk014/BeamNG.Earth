# Maintenance status

Updated: 2026-10-21. Fork: [hashk014/BeamNG.Earth](https://github.com/hashk014/BeamNG.Earth).

## Current state

- Branch `codex/sables-road-water-quality` contains the maintenance changes
  for upper roads over small underpasses and confined lake tiles/physics.
  The Decathlon crossing is reproduced from real cached data. A frozen local
  test kit is prepared. On 21 October, the player reported that the updated
  version works better overall. This is informal gameplay feedback; no measured
  collision drive, complete site checklist or new public release is claimed.
  See [the evidence and limits](../research/2026-10-21-sables-underpass-water.md).
- Upstream has released `1.5.4-beta`. This fork candidate remains based on its
  existing preview; it does not claim a complete integration of that release.

- `preview` contains the unreleased `1.5.3-europe-preview.2-dev` candidate, merged in
  [fork PR #3](https://github.com/hashk014/BeamNG.Earth/pull/3), alongside the earlier
  Linux-runtime and session-file recovery fixes (fork PRs #1 and #2).
- `codex/maintenance-october` retains the batch's focused implementation history.
- Building and sidewalk corrections are merged in [fork PR #4](https://github.com/hashk014/BeamNG.Earth/pull/4).
  The focused upstream contribution is [PR #69](https://github.com/TecnaGamer/BeamNG.Earth/pull/69),
  based directly on upstream `main`, with separate geometry tests and Windows/Linux CI.
  It also fixes an existing Python-only pier-clearance exception, backported here.
- Git author is the existing human account `hashk014`. User-facing work must never carry a Codex signature or AI co-author trailer; see the root `AGENTS.md`.
- The issue inventory is recorded in [ISSUES.md](ISSUES.md). It distinguishes upstream state, implementation, automated checks and remaining game validation.

## Implemented in this batch

1. Integrated upstream 1.5.3 compatibility work while preserving fork geometry and traffic.
2. Added a persistent custom download-cache location (#58, #61). See [storage guide](STORAGE.md).
3. Added persisted rock and decorative-prop controls (#5, #14). In BeamNG.Earth settings,
   open **World**, then **Rocks** or **Decorative doors and benches**. Existing items update
   within the usual per-frame item budget; trees and traffic signs stay visible.
4. Improved surface classification (#31): unknown metadata falls back to road class;
   explicit loose surfaces stay loose and normalized concrete/chipseal tags are recognized.
5. Added bounded low-land coastal protection (#8, #53). This is a partial, sampled fix;
   see [water limits](WATER.md).
6. Added bounded resumable area downloads (#10, #28, #30). Source caching is implemented;
   independent map exports and a selection UI remain open. See [prefetch guide](PREFETCH.md).
7. Follow-up from the local drive: retain grounded building wings, incomplete
   parent bodies and mapped wall outlines; align foundations with graded terrain;
   repair short sidewalk links and add bounded concrete frontages. See the
   [urban geometry evidence and limits](../research/2026-10-20-urban-ground-contact.md).

Five requests have implemented corrections/features and ten have partial implementations,
including the continuity subset of the sidewalk reports. The refreshed inventory contains
77 issues, 54 open upstream after the 21 October refresh. Closed upstream reports
remain distinct from fork implementation and gameplay validation.

## Next priorities

- Drive **TEST 5 - Decathlon - passage inferieur** in both directions, then check
  the lower passage, portal faces and road-edge collision. Check **TEST 6 - Tanchet -
  lac et mer** for bank spill, absolute lake level and marine rendering. The desktop
  test shortcut now selects `runtime-sables-20261021`; earlier runtimes are retained.

- A frozen local in-game test kit, desktop shortcut and cached test locations are
  ready on the development PC. See [the French handoff](INGAME_READY.md).
  Native kernels and a real server handshake pass. The player reports that the
  corrected version looks better. Exact locations, collisions and driving behavior
  have not been systematically checked.

- Reproduce GPS/autodrive oscillation (#21/#38) and coarse/fine terrain overlap (#46).
- Locate the exact annex with the player's floating-fragment report. The main
  school body was complete during the diagnostic view; another wing was reported.
- Validate this candidate in BeamNG 0.40: water boundaries, UI persistence, material physics,
  collision at speed, dense-city frame times and offline drives.

## Verification and release boundaries

- The 21 October candidate passes 286 generator tests, 31 native equivalence tests,
  and 4,707 Lua assertions in 44 files. Its Python fallback passes 94 tests with
  three native-only skips. The real candidate server handshake passes in isolation.
  These results do not establish BeamNG rendering, driving or FPS gains.
- Previous 20 October checks: 51 focused Python tests, 243 generator tests and 4,703 checks
  across all 44 Lua engine-stub files pass. Two map-math JavaScript suites pass.
- The consolidated `Fork maintenance checks` workflow runs these suites on Windows and Linux.
  [The validated urban source run](https://github.com/hashk014/BeamNG.Earth/actions/runs/39480170941)
  passed on both platforms. Review the latest run for any later code changes.
- The extracted upstream branch passes 235 fallback tests and 266 native tests locally,
  including 31 native equivalence checks. Its CI is [tracked separately](https://github.com/hashk014/BeamNG.Earth/actions/runs/39499801167).
  On this fork, all 74 road, road-mesh and urban tests also pass with native kernels disabled.
- Previous extended Windows server suite has three reproducible baseline timing failures, detailed in `docs/research/2026-10-20-session-file-recovery.md`.
- No new standalone executable or public release has been produced for this maintenance batch.
- Engine-stub tests and synthetic server tests do not establish gameplay, rendering, multiplayer behavior or FPS gains.

## Next session

Read this page, `AGENTS.md`, `ISSUES.md` and `VALIDATION.md`. Refresh GitHub state,
inspect the working tree, then continue the highest-impact work with supported evidence.

```sh
python -m pip install --only-binary=duckdb -r requirements-dev.txt
python tools/maintenance.py issues
python tools/maintenance.py test --suite quick --report dist/quick-validation.json
python tools/maintenance.py test --suite generators --report dist/generator-validation.json
python tools/run_lua_tests.py
```
