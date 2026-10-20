"""Plan or download a bounded area's reusable source data. No game or world generation is started."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
import mapcells
import mapdata
import overture
import storage


def make_plan(lat, lon, radius_km=2, dem_zoom=15, layers=mapdata.ALL_LAYERS,
              imagery="eox2016", max_jobs=2048):
    if not all(math.isfinite(v) for v in (lat, lon, radius_km)):
        raise ValueError("coordinates and radius must be finite")
    if not -mapcells.MAX_LAT < lat < mapcells.MAX_LAT or not -180 <= lon <= 180:
        raise ValueError("coordinates must be within the Web Mercator map")
    if not 0 < radius_km <= 50 or not 5 <= dem_zoom <= 15 or not 1 <= max_jobs <= 100000:
        raise ValueError("radius must be in (0, 50] km, DEM zoom in [5, 15], and job limit in [1, 100000]")
    layers = tuple(dict.fromkeys(layers))
    if set(layers) - set(mapdata.ALL_LAYERS):
        raise ValueError("unknown map layer")
    if imagery not in ("none", "eox2016", "eox2023"):
        raise ValueError("imagery must be none, eox2016 or eox2023")
    dlat = radius_km * 1000 / 111320
    south, north = max(-mapcells.MAX_LAT, lat - dlat), min(mapcells.MAX_LAT, lat + dlat)
    dlon = dlat / math.cos(math.radians(max(abs(south), abs(north))))
    west, east = (lon - dlon + 180) % 360 - 180, (lon + dlon + 180) % 360 - 180
    if dlon >= 180:
        west, east = -180, 180
    jobs = []

    def add(kind, zoom, layer=""):
        for key in mapcells.cells_for_bbox(south, west, north, east, z=zoom, max_cells=max_jobs):
            jobs.append({"kind": kind, "key": list(key), "layer": layer})
            if len(jobs) > max_jobs:
                raise ValueError(f"plan exceeds {max_jobs} jobs; reduce the area or explicitly raise --max-jobs")

    # Coarser terrain is needed by the far field; loading only the finest tiles leaves offline gaps.
    for zoom in range(5, dem_zoom + 1):
        add("dem", zoom)
    for layer in layers:
        add("map", mapcells.ZOOM, layer)
    if imagery != "none":
        for zoom in range(5, 15):
            add("imagery", zoom, imagery)
    return {"schema": 1, "center": [lat, lon], "radiusKm": radius_km,
            "bounds": [south, west, north, east], "demZoom": dem_zoom, "layers": list(layers),
            "imagery": imagery, "overtureRelease": overture.RELEASE,
            "layerVersions": mapdata.LAYER_VERSIONS, "jobs": jobs}


def job_id(job):
    return f"{job['kind']}:{job['layer']}:" + "/".join(str(v) for v in job["key"])


def plan_id(plan, cache_dir):
    content = json.dumps({"plan": plan, "cache": storage.normalise(str(cache_dir))}, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()


def write_manifest(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix="prefetch-", suffix=".tmp", delete=False) as f:
            tmp = f.name
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)


def execute(plan, backend, manifest, progress=print):
    signature = plan_id(plan, backend.cache_dir)
    path = Path(manifest)
    # The ID covers every job; keep only the small plan metadata in checkpoints, rather than
    # serializing the full job list again after every download.
    metadata = {k: v for k, v in plan.items() if k != "jobs"}
    state = {"schema": 1, "planId": signature, "plan": metadata, "completed": [], "errors": {}}
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        if old.get("planId") != signature:
            raise ValueError("manifest belongs to another plan or cache folder")
        state = old
    done = set(state["completed"])
    failed = {}
    for index, job in enumerate(plan["jobs"], 1):
        ident = job_id(job)
        try:
            # Completed jobs are checked again: the cache may have been cleared or evicted.
            # DEM jobs re-read through Dem.tiles so all their source/ground-filter dependencies are checked.
            backend.fetch(job)
            done.add(ident)
            state["errors"].pop(ident, None)
        except Exception as exc:
            done.discard(ident)
            failed[ident] = state["errors"][ident] = f"{type(exc).__name__}: {str(exc)[:300]}"
        state["completed"] = sorted(done)
        write_manifest(path, state)
        progress(f"{index}/{len(plan['jobs'])} {ident}: {'failed' if ident in failed else 'cached'}")
    return {"total": len(plan["jobs"]), "completed": len(done), "failed": len(failed)}


class Backend:
    def __init__(self, cache_dir, offline=False):
        import cache
        import netfetch
        self.cache_dir = cache_dir
        self.net = netfetch.Fetcher(stats_dir=os.path.join(cache_dir, "netstats"), offline=offline)
        self.disk = cache.Cache(cache_dir)
        self.dem = self.maps = self.images = None

    def fetch(self, job):
        key = tuple(job["key"])
        if job["kind"] == "dem":
            import dem
            if self.dem is None:
                self.dem = dem.Dem(os.path.join(self.cache_dir, "dem"), fetch_workers=2, fetcher=self.net)
                self.dem.disk = self.disk
            self.dem.tiles([key])
        elif job["kind"] == "map":
            if self.maps is None:
                self.maps = mapdata.MapData(self.cache_dir, fetcher=self.net)
            self.maps.cell(key, layers=(job["layer"],), kind="demand")
            path = self.maps.path(mapcells.CellKey(*key), job["layer"])
            if os.path.exists(path):
                self.disk.used(path)
        else:
            import imagery
            if self.images is None:
                self.images = imagery.Imagery(os.path.join(self.cache_dir, "imagery"), chain=(job["layer"],),
                                               fetch_workers=2, fetcher=self.net)
                self.images.disk = self.disk
            source = imagery.SOURCES[job["layer"]]
            result = self.images.tiles([(source, *key)])
            if result[(source, *key)] is None:
                raise IOError("imagery source has no data for this tile")

    def close(self):
        if self.dem is not None:
            self.dem.pool.shutdown(wait=True)
            self.dem.urgent_pool.shutdown(wait=True)
        if self.maps is not None:
            self.maps.close()
        if self.images is not None:
            self.images.close()
        self.disk.close()
        self.net.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--radius-km", type=float, default=2)
    parser.add_argument("--dem-zoom", type=int, default=15)
    parser.add_argument("--layers", default=",".join(mapdata.ALL_LAYERS), help="comma-separated map layers or none")
    parser.add_argument("--imagery", choices=("none", "eox2016", "eox2023"), default="eox2016")
    parser.add_argument("--max-jobs", type=int, default=2048)
    parser.add_argument("--cache-dir", default=storage.cache_dir(), type=storage.normalise)
    parser.add_argument("--manifest", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--download", action="store_true", help="download the plan (otherwise only print it)")
    mode.add_argument("--offline-check", action="store_true", help="check the cache with all network access disabled")
    args = parser.parse_args()
    try:
        layers = () if args.layers == "none" else tuple(x.strip() for x in args.layers.split(","))
        plan = make_plan(args.lat, args.lon, args.radius_km, args.dem_zoom, layers, args.imagery, args.max_jobs)
    except ValueError as exc:
        parser.error(str(exc))
    counts = {kind: sum(j["kind"] == kind for j in plan["jobs"]) for kind in ("dem", "map", "imagery")}
    print(json.dumps({"cache": args.cache_dir, "jobs": counts, "bounds": plan["bounds"]}))
    if not args.download and not args.offline_check:
        print("Plan only. Add --download to cache it, or --offline-check to verify existing data.")
        return 0
    manifest = args.manifest or Path(args.cache_dir) / "preloads" / (plan_id(plan, args.cache_dir)[:16] + ".json")
    backend = Backend(args.cache_dir, offline=args.offline_check)
    try:
        summary = execute(plan, backend, manifest)
    finally:
        backend.close()
    print(json.dumps({**summary, "manifest": str(manifest)}))
    return int(summary["failed"] > 0)


if __name__ == "__main__":
    sys.exit(main())
