# BeamNG.Earth Europe Preview

Drive real roads in BeamNG.drive, with improved European traffic, narrow
streets and world geometry.

An experimental fork maintained by [hashk014](https://github.com/hashk014),
based on [TecnaGamer's BeamNG.Earth](https://github.com/TecnaGamer/BeamNG.Earth).

**[Download Preview 1](https://github.com/hashk014/BeamNG.Earth/releases/tag/v1.5.1-europe-preview.1)**
· [Before and after](docs/COMPARISON.md)
· [Guide de test en français](docs/TESTER_LE_MONDE.md)
· [Report a problem](https://github.com/hashk014/BeamNG.Earth/issues)

## What this fork changes

| Area | Changes in Europe Preview |
| --- | --- |
| Roundabouts | Consistent one-way flow on detected rings, priority on the ring and give-way signs at incoming approaches |
| Narrow streets | Reliable measured carriageways down to 3 m, adjusted sidewalks and matching terrain grading |
| Curves and hairpins | Better preservation of mapped bends, fewer geometry shortcuts, lower target speeds and earlier braking |
| Speed limits | Changes in mapped limits along a road are represented in the traffic graph |
| Intersections | Concave asphalt patches follow their outline instead of filling missing corners |
| Slopes | Short constant road grades keep their slope instead of flattening at the endpoints |
| Buildings | Open courtyards, more complete multipart footprints, mapped roof height and orientation where supported |
| Collision | Pitched roofs follow their visible shape; courtyard space stays open in both detailed and coarse meshes |
| Foundations | Ground samples along walls catch dips and ridges missed by sampling corners alone |
| Windows setup | DuckDB uses prebuilt packages, with a clear recovery path when no compatible package is available |

The original streamed Earth, satellite imagery, terrain, weather, navigation,
vegetation and other features remain the foundation of this fork. See the
[upstream project](https://github.com/TecnaGamer/BeamNG.Earth) and [credits](CREDITS.md).

## Before and after

These are **generator geometry comparisons**, not screenshots from BeamNG.
Both sides use the same mapped footprint or road. The [comparison page](docs/COMPARISON.md)
explains the data and method.

![The old grading plan cuts across a mapped bend; the preview retains its source vertices](docs/images/road-comparison.png)

![The same mapped courtyard building before and after courtyard preservation](docs/images/courtyard-comparison.png)

## What has been checked

- **331 checks passed, one skipped** in the selected world-generation regression suite.
- **2,099 buildings** generated from cached data across a French town and two mountain samples.
- On **200 real road parts**, 171 source vertices were over 25 cm from the old grading plan,
  with a maximum discrepancy of **1.41 m**. The preview retains those vertices.
- Three native AI cars were observed driving for about 30 seconds with the updated traffic graph.
- Windows release builds run a packaged server startup check before upload.

The geometry work has been validated outside the game. The traffic test used a
temporary graph in an existing world. Long drives in a fully regenerated world,
complex roundabout interactions and dense-city performance still need testing.
See [validation and limits](docs/WORLD_GENERATION.md).

**This is an experimental preview.** Source data still limits realism. Missing
building tags require estimates, courtyard roofs currently use a flat fallback,
and roundabout recognition uses geometry heuristics. No FPS improvement is claimed.

## Download and play

Use this fork's **[Preview 1 release](https://github.com/hashk014/BeamNG.Earth/releases/tag/v1.5.1-europe-preview.1)**.
The original project's downloads contain its own server and do not include this fork's changes.

### Windows

1. Download `BeamNG.Earth-1.5.1-europe-preview.1.exe` from the release assets.
2. Close any other BeamNG.Earth companion server. Keep Steam running.
3. Run the file. It installs the mod, starts the companion server and starts BeamNG.drive.
4. In the game, choose **Freeroam > BeamNG.Earth**.

The standalone Windows download includes Python and the server dependencies.
BeamNG.drive itself must already be installed. The executable is unsigned.

### Source ZIP, Windows or Linux

1. Download `BeamNG.Earth-1.5.1-europe-preview.1.zip` and extract it.
2. Install **Python 3.10+**, with 64-bit Python 3.12 recommended on Windows.
3. On Windows, double-click `run_server.bat`. On Linux, run `python3 install.py`, then `./run_server.sh`.
4. Leave the server running, start BeamNG.drive and load **BeamNG.Earth**.

First-time setup downloads dependencies. Map data downloads while you explore.
This preview's geometry checks ran on Windows; Linux gameplay has not been
retested for the fork. A Linux standalone binary is not included in Preview 1.

More help: [quick start](docs/QUICKSTART.md) and [French test guide](docs/TESTER_LE_MONDE.md).

### From Git

```sh
git clone https://github.com/hashk014/BeamNG.Earth.git
cd BeamNG.Earth
python install.py
python start.py
```

The default branch is `preview`. `main` keeps the upstream baseline.
Update notices and report links in this fork point to this repository.

## Help test the preview

Try a familiar town, a narrow street, a roundabout and a road with hairpins.
Start without traffic, then add three AI cars. Watch for gaps, abrupt bumps,
floating walls, blocked lanes and cars driving against the expected flow.

- **Ctrl+Shift+E** captures a report with a screenshot and the exact location.
- **Ctrl+Shift+Y** records a 30-second performance profile.
- Include the report folder, vehicle, speed, direction and whether traffic was enabled.

Reports stay on your computer until you choose to share them. Submit fork
problems to [this repository's issues](https://github.com/hashk014/BeamNG.Earth/issues).

## Development and attribution

[Fork changelog](docs/FORK_CHANGELOG.md) · [World generation](docs/WORLD_GENERATION.md)
· [Traffic changes](docs/TRAFFIC_IMPROVEMENTS.md) · [Architecture](docs/ARCHITECTURE.md)

The release is based on upstream **1.5.1-beta**, with additional changes by
hashk014. Contributions already proposed upstream are linked in the fork changelog.

Original code by **TecnaGamer**, under the [MIT license](LICENSE). Data sources
include Overture Maps, OpenStreetMap contributors, Mapterhorn, national imagery
providers and others listed in [CREDITS.md](CREDITS.md). Their terms apply to
downloaded data. The game shows source attribution.

BeamNG.drive is a trademark of BeamNG GmbH. This is an unofficial fan project
and does not distribute the game or its assets.
