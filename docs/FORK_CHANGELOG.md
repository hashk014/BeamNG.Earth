# Fork changelog

## 1.5.1-europe-preview.1

First experimental release of the hashk014 fork, based on TecnaGamer's
BeamNG.Earth 1.5.1-beta.

### Traffic

- Detected roundabouts get consistent one-way flow and ring priority.
- Incoming approaches receive give-way signs, with lower target speeds.
- Narrow measured streets keep appropriate carriageway and sidewalk widths.
- Traffic geometry follows bends and hairpins more closely.
- Target speeds respond to curvature and narrow two-way roads, with braking
  propagated along the route.
- Mapped speed changes along a feature are represented in the graph.
- Long road segments crossing the graph window are retained.

Proposed upstream in [pull request #35](https://github.com/TecnaGamer/BeamNG.Earth/pull/35).

### World generation

- Road skins and terrain grading preserve mapped corners.
- Closed road ribbons meet at their seam. Concave intersection patches no
  longer get an asphalt triangle across their missing corner.
- Short, constant road slopes retain their grade at the ends.
- Courtyard voids survive in detailed, coarse and collision building meshes.
- Multipart footprints and building parts retain more of their mapped geometry.
- Supported roof metadata controls the roof rise and ridge orientation.
- Pitched roof collision follows the visible roof instead of a flat lid.
- Foundation sampling follows walls, with ground queries batched by tile.
- Stable feature IDs determine procedural appearance seeds.

### Setup and distribution

- Windows installations avoid compiling DuckDB from source.
- Preview builds have a distinct version, release notes and downloads.
- Update notices and report links point to this fork.
- The server handshake and network user agent use the packaged VERSION.
- The default `preview` branch contains the fork changes. `main` retains the
  upstream baseline.

The installer fix is proposed upstream in
[pull request #34](https://github.com/TecnaGamer/BeamNG.Earth/pull/34).

### Validation

The world-generation suite recorded 331 passing checks and one skipped
stock-asset check. The cached-data audit generated 2,099 buildings. The
traffic graph had a short in-game smoke test with three AI cars. See
[world validation](WORLD_GENERATION.md), [traffic validation](TRAFFIC_IMPROVEMENTS.md)
and the release notes for packaging checks.

Full-world in-game driving and dense-city FPS remain to be assessed. Preview 1
does not claim photorealism, collision-free AI or a performance gain.
