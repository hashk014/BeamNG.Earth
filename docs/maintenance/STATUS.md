# Maintenance status

Updated: 2026-10-23. Fork: [hashk014/BeamNG.Earth](https://github.com/hashk014/BeamNG.Earth).

## Current state

- The [production delivery plan](PLAN_PRODUCTION.md) defines proposed release lots,
  deliverables, game checks and publication gates. It is planning documentation;
  it does not mark any additional fix implemented, tested in-game or released.
- The `1.6.0-europe-preview.2-dev` source candidate integrates the complete upstream
  release **v1.6.0-beta**, commit `b4c478d68795e441eef2ba9fb5981e74c7b11f49`.
  Upstream `main` at refresh was `18f131c`; its two later commits only change
  README/changelog text. This integration deliberately targets the released code.
- Upstream features include experimental BeamMP, shared generation, GPU image work,
  OSM lane/width metadata, painted terrain roads, raceways, polar elevation and
  the RGBA terrain-mip correction. Upstream performance figures are not fork measurements.
- Fork building footprints, courtyards, foundations/frontages, narrow-road widths,
  fixed road profiles, Decathlon upper-road protection, bounded coast/lake tiles,
  persistent cache location, rock/prop preferences and resumable area prefetch remain.
- Integration regressions check the combined behavior. Ordinary grading retains
  upstream road-level separation; repaired upper-road pieces blend as one surface.
  Both source and worker-process geometry paths carry the fork frontage data.
- The update check and checked-download updater remain scoped to this fork.
- The only existing public fork binary is still **v1.5.1-europe-preview.1**.
  The 1.6 update is source and local test-kit work, not a newly published executable.
- Git author remains the existing human identity `hashk014`. Upstream authorship,
  licence, roadmap and historical design notes are preserved.

## Issue review

The refreshed 23 October snapshot contains **163 issues, 133 open upstream**. Metadata for
all issues is refreshed; existing assessments are retained, with focused reviews
of release-related changes and the newest actionable reports. See [ISSUES.md](ISSUES.md).
An upstream issue being open or closed is independent of fork validation.

Priority follow-ups from the new 1.6 reports:

1. [#181](https://github.com/TecnaGamer/BeamNG.Earth/issues/181): slower building/road
   loading than 1.5.4. Needs comparable server/frame traces; no performance fix claimed.
2. [#180](https://github.com/TecnaGamer/BeamNG.Earth/issues/180): autodrive failure.
   The issue body has no location; attached diagnostics have not been analyzed.
3. [#179](https://github.com/TecnaGamer/BeamNG.Earth/issues/179): blurry/bright small
   roads in Taipei. Needs identical camera/settings comparison with 1.5.5.
4. [#171](https://github.com/TecnaGamer/BeamNG.Earth/issues/171): water flooding
   Ingles Street, Melbourne. Existing lake/coast tests do not establish a fix there.
5. [#182](https://github.com/TecnaGamer/BeamNG.Earth/issues/182) and
   [#183](https://github.com/TecnaGamer/BeamNG.Earth/issues/183): sharp underpass ramps,
   including precise Brazilian locations. Evaluate upstream PR #177 before duplicating it.
6. [#185](https://github.com/TecnaGamer/BeamNG.Earth/issues/185): multiple road/object
   obstructions on the MKAD. Exact affected segments still need to be identified.

## Validation and limits

- Local Windows: **55 quick tests** and **361 generator tests** pass with no skips.
- LuaJIT engine stubs: **54 files, 4,975 assertions** pass. The scoping test now
  walks bytecode and nested prototypes without Unix `find` or a separate luajit executable.
- Both JavaScript map-math suites pass. Python compilation passes.
- [Windows/Linux CI passes at source merge 6eda732](https://github.com/hashk014/BeamNG.Earth/actions/runs/39989395375).
  Each runner skips GPU equivalence (no GPU) and the separate CLI-LuaJIT check.
- Integration suite: **268 passed, 1 skipped** (269 run), covering native, OSM,
  process-worker, peer-wire, updater, imagery and protocol checks. The skip needs
  a separate luajit executable; all Lua files run through Lupa. See [VALIDATION.md](VALIDATION.md).
- All **43 synthetic server tests** and **10 restart tests** pass, including the
  three historical Windows timing failures. The old baseline remains recorded
  in [the recovery report](../research/2026-10-20-session-file-recovery.md).
- The frozen 1.6 local runtime passes its isolated real-server handshake, and its
  installed mod matches the prepared source tree. Source/BeamMP ZIP CRC checks pass.
- Native `earthfast` is now required by upstream. Historical Python-only fallback
  totals from 1.5.3 are not validation of this 1.6 candidate.
- No BeamNG gameplay, multiplayer session, physical Steam Deck run, FPS gain,
  original-issue location verification or automatic update from a hosted binary is claimed.

## Local test handoff

See [INGAME_READY.md](INGAME_READY.md) for the frozen runtime and existing shortcut.
Recheck Decathlon in both directions, Tanchet water, saved World settings, building
foundations and narrow roads after regeneration. Keep the previous runtimes for rollback.
The player-reported overall improvement on 21 October applies to the older 1.5.3 kit,
not to this 1.6 integration.

## Contribution history

Fork PRs #1 through #5 merged session recovery, Linux-runtime detection, storage/
world/prefetch settings, urban geometry and Decathlon/inland-water corrections.
[Upstream PR #69](https://github.com/TecnaGamer/BeamNG.Earth/pull/69) is still open
and conflicting at this refresh; updating the fork does not merge or close it.

## Next session

Read this page, AGENTS.md, ISSUES.md and VALIDATION.md; refresh GitHub metadata
before choosing another focused change. Keep source, automated, gameplay and release
claims separate.
