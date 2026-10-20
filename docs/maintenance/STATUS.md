# Maintenance status

Updated: 2026-10-20. Fork: [hashk014/BeamNG.Earth](https://github.com/hashk014/BeamNG.Earth).

## Current state

- `preview` contains the unreleased `1.5.3-europe-preview.2-dev` candidate, merged in
  [fork PR #3](https://github.com/hashk014/BeamNG.Earth/pull/3), alongside the earlier
  Linux-runtime and session-file recovery fixes (fork PRs #1 and #2).
- `codex/maintenance-october` retains the batch's focused implementation history.
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

Five requests have implemented corrections/features and eight have partial implementations.
All 59 issues in the snapshot have individual assessments; 48 were open upstream.

## Next priorities

- A frozen local in-game test kit, desktop shortcut and cached test locations are
  ready on the development PC. See [the French handoff](INGAME_READY.md).
  Native kernels and a real server handshake pass. The updated urban geometry
  needs a fresh server session and player verification.

- Reproduce GPS/autodrive oscillation (#21/#38) and coarse/fine terrain overlap (#46).
- Locate the exact annex with the player's floating-fragment report. The main
  school body was complete during the diagnostic view; another wing was reported.
- Validate this candidate in BeamNG 0.40: water boundaries, UI persistence, material physics,
  collision at speed, dense-city frame times and offline drives.

## Verification and release boundaries

- Current local checks: 51 focused Python tests, 243 generator tests and 4,703 checks
  across all 44 Lua engine-stub files pass. Two map-math JavaScript suites pass.
- The consolidated `Fork maintenance checks` workflow runs these suites on Windows and Linux.
  [The validated source run](https://github.com/hashk014/BeamNG.Earth/actions/runs/39461712951)
  passed on both platforms. Review the latest run for any later code changes.
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
