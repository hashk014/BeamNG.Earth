# Experimental streaming stability integration

This source update integrates upstream `dev` through `b15991e` on top of the
fork's 1.6 candidate. It preserves upstream commit history and authorship.
The public fork executable remains v1.5.1-europe-preview.1.

## Why this update

Upstream [#181](https://github.com/TecnaGamer/BeamNG.Earth/issues/181),
[#190](https://github.com/TecnaGamer/BeamNG.Earth/issues/190) and
[#191](https://github.com/TecnaGamer/BeamNG.Earth/issues/191) report slower scenery
loading and driving freezes after 1.6.0. The upstream development branch already
contains work on these paths, so this update integrates it rather than building
a second scheduler.

- Terrain and urgent base photos have priority over background work. Above
  70 m/s (about 157 mph), a slow ground photo can follow the physics block later.
  This threshold is above some reported problem speeds, including #191's 138 mph.
- Moving cars request the next block earlier. Lua defers occasional expensive
  operations to light frames, and Windows terrain swaps avoid a second full
  texture rebind.
- Road plans, downloads and map cells are shared across local server processes.
  Native kernels cover more terrain/tree work. Both tracked native binaries and
  native sources are integrated; the required earthfast version is 67.
- Auxiliary caches and mirrors are pruned to their own limits. These are separate
  from the user-facing main cache cap, so that cap is not a strict total disk quota.
- BeamMP holds affect the local car. Remote-car restoration is bounded and respects
  intentional removal; undamaged cars avoid unnecessary full damage transfers.
- Windows server GPU kernels default off, with the upstream `BNGE_GPU=1` opt-in.

These are source changes and removals of redundant work. Upstream benchmark
numbers are not measurements of this fork. #191's attached profiler shows no
frames over 50 ms in its capture, so it does not itself isolate the reported hangs.

## Fork integration

The fork's road rendering preference, worker setting propagation, urban geometry,
fixed road profiles, underpass protection, water bounds, cache location and area
prefetch remain. README and road grading required explicit conflict resolution.

Upstream's plan cache serializes four grading collections. The fork also needs
the protected surface-road profiles above mapped tunnels. The integrated cache
serializes this fifth collection with all Plan fields and restores it before
grading. A versioned schema and signature reject older entries instead of silently
discarding the protection. The regression compares uncached, first-writer and
second-reader grading over an unresolved tunnel dip, requiring identical heights
and a smooth, protected upper road without another map-data fetch.

## Verification

The added `streaming` maintenance suite covers the shared plan cache, auxiliary cache limits,
CPU partitioning, DSM ground, detail terrain and synthetic imagery sources. It
deliberately excludes the imagery tests that call public tile services.

Local Windows checks use isolated HOME, USERPROFILE, app-data and temporary roots
under `dist/streaming-update`. No game installation or actual user folder is used.

| Command | Result |
| --- | --- |
| `python tools/maintenance.py test --suite quick` | 62 passed |
| `python tools/maintenance.py test --suite generators` | 361 passed |
| `python tools/maintenance.py test --suite integration` | 280 passed, 2 skipped (282 run) |
| `python tools/maintenance.py test --suite streaming` | 96 passed, 1 skipped (97 run), after harness cleanup correction |
| `python -m compileall -q server launcher.py start.py tools` | Passed |

Integration skips the separate CLI-LuaJIT check and GPU equivalence (GPU kernels
are disabled by default on Windows). Streaming skips the Linux-only affinity test.
The loaded Windows native module reports version 67, matching the required version.

The first streaming run passed the functional assertions but failed while removing
the detail-refresh test's temporary cache: background workers could still write
there. The harness now joins server executors and imagery workers before verifying
its owned root and cleaning up. All 97 streaming checks then completed with the
single platform skip above. This was addressed separately from the historical
Windows cleanup timing failures recorded on 20 October.

## Remaining gameplay checks

Compare the preceding 1.6 candidate and this snapshot using the same vehicle,
graphics settings, camera, route and hardware, with separate cold and warm caches.
Capture server timings and frame-time p95/p99, including below and above 70 m/s.
Use the Mojave location from #190 (34.466517, -117.349023) and Ohio location from
#191 (39.417312, -82.189511), plus the Decathlon upper/lower road and Tanchet water.
Check late-photo appearance, terrain transitions and both road rendering modes.
BeamMP still needs two-player driving, holds, damage and remote-car removal tests.

No gameplay, FPS gain, original-report fix or new executable release is claimed.
The existing frozen runtime/desktop shortcut is unchanged and predates this update.
