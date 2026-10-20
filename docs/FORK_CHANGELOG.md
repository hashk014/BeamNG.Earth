# Fork changelog

## Urban geometry follow-up, unreleased

- Keeps grounded wings beside inferred road passages and retains the body of
  buildings whose mapped parts cover only a roof or one wing.
- Shares graded foundation heights between related building parts and keeps
  mapped walls instead of expanding them into roof rectangles.
- Removes unsupported roof equipment, retains short sidewalk links, joins tiny
  end gaps and paves short gaps from existing sidewalks to facing facades.
- Adds 20 geometry regressions and an offline rebuild of two real town sectors.
  The player reports an improved appearance; the exact floating annex and driving
  behavior still need specific game checks. Submitted upstream as PR #69.
- Fixes the Python-only bridge-pier clearance exception (`any(bool)`), covered
  by the existing spacing regression and 74 fallback road/urban tests on this fork.

## 1.5.3-europe-preview.2-dev (unreleased source)

- Integrates upstream 1.5.3 compatibility and high-speed collision changes,
  preserving fork traffic, building geometry and the previous two maintenance fixes.
- Saves a download-cache location across source, launcher and server entry paths
  (#58, #61), with reset and environment overrides.
- Adds saved Off/Low/Normal rocks and decorative doors/benches controls (#5, #14).
- Uses road-class defaults for unknown surface metadata and respects normalized
  explicit/mixed surface tags (#31).
- Refines ocean squares over mapped dry low land and confines their hidden water
  physics (#8, #53). Sampling/data limits and conservative gaps remain.
- Adds bounded, resumable area downloads and cache verification with networking
  disabled (#10, #28, #30). No standalone map export or in-game area selector.
- Adds durable project instructions, an assessed inventory of all 59 issues in
  the 2026-10-20 snapshot, shared test commands and Windows/Linux CI.

See [maintenance status](maintenance/STATUS.md) and [validation](maintenance/VALIDATION.md).
This source candidate has no new standalone build or gameplay/FPS certification.

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
