# Choose road surfaces

The source candidate offers a saved choice between the two existing road pipelines:

| Choice | Behavior |
| --- | --- |
| `terrain` | Upstream 1.6 default: carriageways painted into the ground. |
| `mesh` | Legacy carriageway overlays, for comparing small-road edges and appearance. |

Close the world server and leave the Earth level before changing modes. From the
source folder, select a mode and start normally:

```sh
python start.py --road-rendering mesh
```

The choice applies to later starts through both `start.py` and `launcher.py`.
To save a choice without starting the server, installing a mod or launching the game:

```sh
python launcher.py --road-rendering mesh --print-road-rendering
python start.py --print-road-rendering
```

Return to the default:

```sh
python start.py --reset-road-rendering --print-road-rendering
```

Then start the server and re-enter the level to regenerate the world. No cache
deletion is needed. This is a startup option, not a live pause-menu setting.
It changes the existing road-rendering pipeline; it does not restore the whole
1.5 generator or add the hybrid pipeline proposed in upstream issue #179.

The preference lives in `beamng-earth/roads.json` under `%LOCALAPPDATA%` on Windows
or `$XDG_CONFIG_HOME` (default `~/.config`) on Linux. Download-cache selection,
game settings and saved places remain in their existing files. The historical
`BNGE_ROADS_IN_GROUND=0` override still selects mesh roads; other set values select
terrain roads. An explicit launcher choice wins for that launch and is saved.
A persistent environment override takes precedence again on later launches.

The launcher exports the resolved choice to its child processes. Each local
worker receives the server's selected mode explicitly. Helpers use a separate
worker pool per mode and compute-sharing cache keys include the mode. BeamMP
participants with different modes reject shared jobs and fall back to their own
generation; this is covered by offline protocol tests, not a multiplayer drive.

## Availability and validation

This change is source-only. The public `v1.5.1-europe-preview.1` executable does
not contain it. A future executable built from this source uses the same launcher
arguments; packaging must still be checked before a binary release is claimed.

Automated checks cover saved preferences across fresh launcher processes,
invalid/corrupt configuration, atomic-write failures, old environment overrides,
shared-job mode rejection, distinct helper pools/cache keys, and actual spawned
workers with an opposite environment setting. Existing generator tests cover
both carriageway modes. See [VALIDATION.md](VALIDATION.md) for exact results.

## Game comparison still needed

At Taipei `25.05901, 121.55196`, record the same camera, vehicle, texture settings,
time/weather and cache state with each mode. Compare alley edges, asphalt color,
markings, curbs, intersections, slopes and tile transitions. Repeat on a rural
road and the Decathlon crossing. Drive each route in both directions and record
collisions and loading/frame traces. In a two-player session, check matching and
different modes and confirm local fallback.

The default remains terrain until game evidence supports a change. No visual
quality, collision, FPS or loading-time improvement is established by these tests,
and upstream #179 remains open.
