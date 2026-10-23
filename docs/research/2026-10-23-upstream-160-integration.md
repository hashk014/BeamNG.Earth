# Upstream 1.6.0 integration, 23 October 2026

## Source and issue refresh

[Upstream v1.6.0-beta](https://github.com/TecnaGamer/BeamNG.Earth/releases/tag/v1.6.0-beta)
was published on 23 October at 06:03:30 UTC. The integration target is the exact
release commit `b4c478d68795e441eef2ba9fb5981e74c7b11f49`. At refresh,
upstream main `18f131c` only adds README/changelog wording after that release.
The fork source version is `1.6.0-europe-preview.2-dev`.

The initial checkout was clean at `preview` commit `2d8bbd4`. A merge on
`codex/update-1.6.0` preserves upstream authorship and the published fork history.
The source merge is `6eda7323ac6ce56c5d2ec22b8e16f6d4f9059104`, tracked in
[fork PR #6](https://github.com/hashk014/BeamNG.Earth/pull/6).
[Upstream PR #69](https://github.com/TecnaGamer/BeamNG.Earth/pull/69) remains
open/conflicting and is not modified or merged by this fork update.

The issue snapshot now contains 159 reports, 129 open. Release notes from 1.5.4,
1.5.5 and 1.6.0 were compared with existing fork work; current PR state and the
new #171, #179, #180 and #181 discussions were read. The inventory preserves
existing assessments and separates upstream state from implementation and tests.
The attached logs in #180 have not been analyzed. No upstream issue was closed.

## Combined behavior

- Retains fork multipart bodies/courtyards, graded foundations, grounded passage
  wings, mapped roofs and bounded frontage paving, including both worker paths.
- Preserves measured narrow widths and mapped bends while adopting OSM tags,
  painted terrain roads, terrain-following meshes and native cutting/approach work.
- Keeps fixed bridge/tunnel profiles and the Decathlon upper-road/portal masks.
  Repaired pieces of one upper surface blend without yielding to their own other
  profiles; ordinary grading retains upstream road-level separation.
- Uses upstream low-arch portal caps, twin-tunnel sharing and whole underwater-chain
  omission together with fork surface-road cover bounds.
- Keeps bounded dry-coast/inland-tile protection while accepting upstream ground
  callbacks and lake-level changes. This does not prove #171 is fixed.
- Keeps persistent storage, rocks/props and resumable prefetch, while adopting
  upstream BeamMP, peer computation, native/GPU image work and corrected RGBA mips.
- Retains fork-scoped update URLs. The existing public fork binary remains Preview 1;
  this update does not publish a new executable.
- Makes bytecode scoping tests portable: `jit.util` inspects nested prototypes,
  and the Lupa runner supplies file paths without Unix tools or a CLI LuaJIT.

The merge exposed regressions in the quick-play fallback, quantization argument
shadowed by a corner polygon, short sidewalk retention, tunnel-section masks,
new portal-cap input shape and repaired-profile road IDs. Existing regressions
now pass without widening their tolerances, including the recorded Decathlon
2 cm comparison and 3 percent profile-step limit. Two new coastal tests check
both the upstream ground callback and the retained mapped-dry callback.

## Local automated results

| Check | Result |
| --- | --- |
| Maintenance quick | 55 passed, no skips |
| Maintenance generators | 361 passed, no skips |
| Maintenance integration | 268 passed, 1 skipped (269 run) |
| LuaJIT engine stubs | 54 files, 4,975 assertions passed |
| JavaScript map math | Both suites passed |
| Python compilation | Passed |
| Full synthetic server | 43 passed, 403.4 s |
| Restart server | 10 passed, 81.2 s |
| Frozen runtime handshake | Protocol 4 / format 4, correct app version |
| Local archives | Source ZIP and BeamMP ZIP CRC checks passed |

Commands and scopes are in [VALIDATION.md](../maintenance/VALIDATION.md).
The one skip requires an external `luajit` executable; the separate 54-file
Lua suite uses Lupa. The new upstream code requires native `earthfast`; its
included version is 60. Old Python-fallback totals do not apply to this update.

All three historical Windows timing failures pass in this run:
`DaeServerTest.test_session`, `ServerTest.test_session` and
`DeleteQueueTest.test_rate_and_rebuilt_tile`. No repeated timing stability claim
is made. The earlier baseline report remains unchanged.

The [Windows/Linux maintenance workflow](https://github.com/hashk014/BeamNG.Earth/actions/runs/39989395375)
passed on both Windows 2025 (7 min 17 s) and Ubuntu 24.04 (4 min 53 s)
against source merge `6eda732`. On each runner, quick has 55 passes, generators
has 361 passes, integration has 267 passes and two skips, and all 54 Lua files
pass 4,975 assertions. The runners skip GPU/CPU equivalence because no usable
GPU is available and the protocol test requiring an external luajit executable.
Both checks ran locally, except the external-luajit test. Final follow-up commits
update documentation and include the evidence in the source archive; those
archives passed local CRC and content checks.

## Local installation and rollback

The desktop shortcut still opens `TESTER_EN_JEU.cmd`, which now selects
`dist/ingame-ready/runtime-160-20261023`. The runtime contains 210 package files
from `6eda732`; `READY.json` records SHA-256 per file. Its real server was started
with temporary user/cache paths and stopped after the handshake; no BeamNG
process was started. The startup-plus-handshake observation was 0.860 s, excluding
the game and terrain generation, and is not a loading-time comparison.

Before installation, the old named mod, existing preference/database files and
kit manifests were copied to `backups/update-160-20261023-184632`. The resolved
replacement path was checked inside the explicit game user root and the game
was confirmed stopped. The installed mod's tree hash matches the frozen source.
Previous frozen runtimes are retained. See [the French handoff](../maintenance/INGAME_READY.md).

Local source and BeamMP packages are under `dist/update-160/`. They have not been
uploaded as releases. Current scripts require the existing Python environment;
there is no newly built standalone Windows executable.

## Remaining runtime checks

Regenerate and drive Decathlon both ways, inspect the lower tube and road edges,
then inspect Tanchet's absolute lake level, banks and sea. Recheck narrow streets,
foundations, saved World settings, GPS/autodrive, dense-city loading and an actual
two-player BeamMP session. New 1.6 reports on performance, small-road appearance,
autodrive and Melbourne water remain reproduction priorities. Compilation,
engine stubs, synthetic peers and server tests do not prove those gameplay results.
