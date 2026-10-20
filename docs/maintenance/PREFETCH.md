# Download an area before driving

Related requests: [#10](https://github.com/TecnaGamer/BeamNG.Earth/issues/10),
[#28](https://github.com/TecnaGamer/BeamNG.Earth/issues/28),
[#30](https://github.com/TecnaGamer/BeamNG.Earth/issues/30).

The source checkout includes a bounded area downloader. It fills the same cache
as the companion server, with elevation, selected map layers and global satellite
imagery. The tool prepares reusable source data; BeamNG still needs the companion
server to generate and stream the world.

First inspect the plan. This command downloads nothing:

```sh
python tools/prefetch.py --lat 48.86 --lon 2.35 --radius-km 2
```

Then download it, reusing the exact same options to resume after interruption:

```sh
python tools/prefetch.py --lat 48.86 --lon 2.35 --radius-km 2 --download
python tools/prefetch.py --lat 48.86 --lon 2.35 --radius-km 2 --offline-check
python start.py -- --offline
```

The saved [cache selection](STORAGE.md) is used automatically. `--cache-dir PATH`
overrides it for this tool without changing the saved selection. Use the same
folder for the server. The area is the bounding square around the chosen point;
`--radius-km` is its approximate half-width. Longitude wrapping at the date line
is supported.

## Limits and progress

- Default maximum: 2,048 jobs. The plan is rejected before download if it exceeds
  the limit. `--max-jobs` can explicitly raise it; radius is limited to 50 km.
- A job can require several source requests, including elevation-filter context.
  Job counts are not byte or HTTP-request estimates. Existing source rate limits,
  retries and cache size limits still apply.
- By default elevation zooms 5 through 15, all map layers, and EOX 2016 imagery
  zooms 5 through 14 are cached. `--layers roads,connectors,water` selects layers;
  `--layers none` or `--imagery none` leaves that category out.
- `--imagery eox2023` selects the newer global imagery with its existing source
  terms. The default EOX 2016 source is CC BY 4.0; existing in-game attribution
  remains in place. This tool does not redistribute the imagery.
- A checkpoint manifest is saved under `<cache>/preloads/` after every job.
  Failures remain incomplete and produce a nonzero exit code. Completed entries
  are revalidated through the normal cache readers on each run, so a stale
  manifest cannot hide evicted or missing data.
- `--offline-check` creates a fetcher with all network access disabled. It checks
  the selected plan, including byte decoding. It does not certify an entire game
  session's horizon, high-resolution regional imagery, real weather, online place
  search or routes beyond the selected area.
- Downloads are not pinned against later cache eviction. Check coverage again
  before going offline, and choose a cache size large enough for the area.

No independently playable map export or in-game area-selection UI is included.

## Verification

`test_area_prefetch.py` checks size bounds, antimeridian wrapping, failure and
resume, eviction, cancellation checkpoints and manifest mismatch. A live smoke
test cached and then read with networking disabled:

| Data | Cached sample | Bytes |
| --- | --- | ---: |
| Elevation | Mapterhorn `5/5/12` | 212,818 |
| Roads | Overture `14/2953/6428`, release `2026-09-23.1` | 174,104 |
| Imagery | EOX 2016 `5/5/12` | 23,326 |

The live samples are near Las Vegas and prove those cache paths work. They do
not constitute a downloaded city or in-game offline-drive test.
