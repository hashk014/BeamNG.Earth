"""Ground graded under roads (docs/ROADMAP.md v1.6; docs/research/2026-10-11-official-road-study.md §3, §5.3):
the physics block and the near mesh tiles sample one graded elevation, so tyres, DecalRoads and the
visible ground agree.

Per road (roads.road_specs; bridges, tunnels and off-ground segments are left out by it):
- along: the centreline height is the DEM sampled every PROFILE_STEP m and smoothed (Gaussian,
  SIGMA_M m; dirt roads DIRT_SIGMA_M), so grades stay real and small bumps go (the official maps:
  |2nd difference| per 10 m 0.02-0.1 m);
- across: flat over the core (the carriageway as a city street would have it, parking included, plus
  SHOULDER_M, or the sidewalk plus SIDEWALK_MARGIN_M on the classes that get sidewalks in towns, so a
  raised sidewalk slab sits on flat ground), then back to the natural ground over a transition of 2x the height difference (a
  1:2 cut or fill slope), clamped to [T_MIN, T_MAX] m;
- several roads at one point (junctions, divided carriageways) blend their targets by inverse distance
  from each centreline (BLEND_R), so they meet in a gradual slope.
The core width never depends on the land cover (it is taken as urban for every built road), and
each map cell's plan is made once per anchor and cached, so the block and the tiles built later from
the same anchor always agree.

GradedDem(dem, grader) is a drop-in for dem.Dem where only sample() is graded; use it for the block
and the levels <= 0 tiles only (coarser tiles sink under the block and cover far more ground).
"""
import logging
import math
import threading
import time

import numpy as np

import mapcells
import roads as roadsmod

log = logging.getLogger("earthd.grading")

VERSION = 4
PROFILE_STEP = 2.0          # m between profile samples
SIGMA_M = 12.0              # m, profile smoothing of built roads
DIRT_SIGMA_M = 5.0          # m, profile smoothing of gravel / dirt roads
SHOULDER_M = 1.0            # m of flat shoulder beyond the carriageway, each side
SIDEWALK_MARGIN_M = 0.5     # m of flat ground beyond a sidewalk (roads.SIDEWALK_CLASSES)
T_MIN, T_MAX = 5.0, 12.0    # m, transition back to the natural ground (5: roads close together meet gently)
SLOPE_RUN = 2.0             # transition = SLOPE_RUN x the height difference (1:2 slope)
VERTEX_STEP = 4.0           # m between the plan's vertices (segments for the grading pass; linear between: at 16 m a
                            # crest or a sag was a kink every 16 m, 'bumpy roads, worst uphill and at speed' on r/BeamNG,
                            # 2026-10-17: a San Francisco street's slope changed 4.4 % rms per 2 m, 1.2 % at 4 m;
                            # grading a 1 km block 0.06 -> 0.14 s)
BUCKET = 32.0               # m, query-point buckets
PAIR_BATCH = 2_000_000      # (segment, point) pairs graded at once (bounds the temporaries, ~200 MB)
ROAD_LIFT = 0.04            # m the physics ground is raised under roads (see Grader.apply)
BLEND_R = 4.0               # m: roads near each other blend their targets by 1 / (1 + (d / BLEND_R)^2)
PROFILE_ZOOM = 15           # DEM zoom of the profiles (one zoom for every caller)
WALL_CUT_M = 2.0            # a road cut deeper than this into the ground: a retaining wall at the core's edge
WALL_T_M = 0.8              # (roadmesh.retaining_walls) and the ground at its natural height right behind it, over
                            # this; on a 1:2 slope Central Park's sunken transverse was a grassy ditch between its
                            # stone walls (the user, 2026-10-17)
WALL_FLAT_M = 2.0           # ... after one terrain grid step at the road's level behind the wall: rising at the wall
                            # itself, the 2 m grid's triangles stood as dark wedges in front of its face; the wall's
                            # top (roadmesh.WALL_THICK_M) covers the strip
TUNNEL_TAG = ":tun"          # in the fid of the tunnels' own plans (open sections, mouths): apply(roads_only) skips them
MOUTH_PLAN_M = 4.0          # m into a tunnel from a portal its floor is a grading plan too (Grader._mouth_plans)
TUNNEL_KEEP_IN_M = 3.0      # (roads.LOW_HOLE_M: a low arch's mouths, flat at its floor)
TUNNEL_KEEP_M = 5.0         # m beside a covered tunnel's road where the ground over it is left ungraded
WALL_AHEAD_M = 2.5          # ... only beside a segment or this little past its end (a joint between two: VERTEX_STEP)
RETRY_S = 60.0              # s before a cell whose road data failed is asked for again
CROSSOVER_CONTEXT_M = 96.0 # widest accepted roads (40 m), profile smoothing and the local repair's fade


def smooth_profile(z, step, sigma, preserve_grade=False):
    """Gaussian smoothing, optionally of residuals from the end-to-end grade. Pure.

    Reflecting raw heights flattens every short uphill segment at its ends.
    Removing the linear grade first preserves a constant slope, including the
    endpoints, with both the native kernel and the numpy fallback.
    """
    z = np.asarray(z, np.float64)
    if len(z) < 3 or sigma <= 0:
        return z.copy()
    trend = np.linspace(z[0], z[-1], len(z)) if preserve_grade else np.zeros(len(z))
    residual = z - trend
    import fast
    if fast.AVAILABLE:          # the Rust loop (~7000 roads a 9-tile set; equal to ~1e-12 m)
        return trend + fast._ef.smooth_profile(np.ascontiguousarray(residual), float(step), float(sigma))
    r = int(math.ceil(3 * sigma / step))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) * step / sigma) ** 2)
    k /= k.sum()
    pad = np.pad(residual, r, mode="reflect") if len(z) > r else np.pad(residual, r, mode="edge")
    return trend + np.convolve(pad, k, mode="valid")


def resample(xy, step):
    """Points every `step` m along a polyline (xy (k, 2)), the last point kept, and their arc lengths."""
    import fast
    if fast.AVAILABLE and len(xy):
        return fast._ef.resample(np.ascontiguousarray(np.asarray(xy, np.float64)[:, :2]), float(step))
    seg = np.hypot(*np.diff(xy, axis=0).T)
    s = np.r_[0.0, np.cumsum(seg)]
    if s[-1] <= 0:
        return xy[:1].copy(), np.zeros(1)
    t = np.r_[np.arange(0.0, s[-1], step), s[-1]]
    return np.stack([np.interp(t, s, xy[:, 0]), np.interp(t, s, xy[:, 1])], axis=1), t


class Plan:
    """One road's grading: vertices (n, 2) in the frame's ENU metres, their target heights, core half width."""
    __slots__ = ("xy", "z", "half", "bbox")

    def __init__(self, xy, z, half):
        self.xy, self.z, self.half = xy, z, float(half)
        pad = half + T_MAX
        self.bbox = (xy[:, 0].min() - pad, xy[:, 1].min() - pad, xy[:, 0].max() + pad, xy[:, 1].max() + pad)


def plan_road(frame, lonlat, spec, elev):
    """The Plan of one road part (lonlat (k, 2)); elev(lat, lon) -> m at PROFILE_ZOOM. Pure given elev."""
    return plan_roads(frame, [(lonlat, spec)], elev)[0]


def plan_roads(frame, parts, elev):
    """plan_road for many (lonlat, spec) parts with one elev call (its cost is per call). Pure given elev."""
    if not parts:
        return []
    ll = np.concatenate([lonlat for lonlat, _ in parts])
    E, N, _ = frame.geodetic_to_enu(ll[:, 1], ll[:, 0], 0.0)
    prof, paths, distances, k = [], [], [], 0
    for lonlat, spec in parts:
        m = len(lonlat)
        path = np.stack([E[k:k + m], N[k:k + m]], axis=1)
        xy, distance = resample(path, PROFILE_STEP)
        k += m
        prof.append(xy if len(xy) >= 2 else None)
        paths.append(path)
        distances.append(distance)
    pts = [xy for xy in prof if xy is not None]
    if not pts:
        return [None] * len(parts)
    allxy = np.concatenate(pts)
    la, lo, _ = frame.enu_to_geodetic(allxy[:, 0], allxy[:, 1], 0.0)
    zall = np.asarray(elev(la, lo), np.float64)
    out, k = [], 0
    for (lonlat, spec), xy, path, distance in zip(parts, prof, paths, distances):
        if xy is None:
            out.append(None)
            continue
        z = zall[k:k + len(xy)]
        k += len(xy)
        out.append(_plan(xy, z, spec, path, distance))
    return out


def _plan(xy, z, spec, path=None, distance=None):
    built = spec.kind in roadsmod.BUILT
    zs = smooth_profile(z, PROFILE_STEP, SIGMA_M if built else DIRT_SIGMA_M, preserve_grade=True)
    # thin to VERTEX_STEP (the profile stays smooth between: linear in the grading pass)
    every = max(1, int(round(VERTEX_STEP / PROFILE_STEP)))
    keep = np.r_[np.arange(0, len(xy) - 1, every), len(xy) - 1]
    # the carriageway as a city street would have it (never from the land cover), or the measured one
    width = spec.width
    # Keep every source corner in the physical road as well as in its skin.
    # Heights still come from the uniformly sampled, smoothed profile.
    if path is not None:
        source_s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
        target_s = np.unique(np.r_[distance[keep], source_s])
        xy_out = np.column_stack([np.interp(target_s, source_s, path[:, j]) for j in (0, 1)])
        z_out = np.interp(target_s, distance, zs)
    else:
        xy_out, z_out = xy[keep], zs[keep]
    return Plan(xy_out, z_out, width / 2 + shoulder(spec))


def shoulder(spec):
    """m of flat ground beyond the carriageway edge, each side. Like the core width, never from the land
    cover: a road class that gets sidewalks in towns keeps a sidewalk-wide verge everywhere."""
    if spec.kind not in roadsmod.BUILT:
        return 0.0
    if spec.cls in roadsmod.SIDEWALK_CLASSES or (spec.cls == "trunk" and (not spec.oneway
                                                                          or roadsmod._arterial(spec))):
        return spec.walk + SIDEWALK_MARGIN_M
    return SHOULDER_M


def _urban_core(lat, lon):
    """Unknown widths retain room for urban parking; mapped/measured widths win.

    A stable function keeps road_specs' memoization independent of tile order
    and avoids a land-cover lookup in the terrain worker.
    """
    return np.ones(np.broadcast(lat, lon).shape, bool)


class Grader:
    """The road plans of one anchor frame, per map cell, made once (worker threads; it fetches the road
    cells it lacks)."""

    def __init__(self, frame, mapdata, elev, widths=None):
        self.frame, self.md, self.elev, self.widths = frame, mapdata, elev, widths
        self.cells = {}
        self.failed = {}        # cell key -> monotonic time of the last failed fetch
        self.lock = threading.Lock()
        self.key_locks = {}     # cell key -> Lock: one thread plans a cell, the others wait for it
        self.covers = {}        # cell key -> [(xy (k, 2), half width)]: the tunnels whose ground over them stays
        self.opens = {}         # cell key -> [(xy (k, 2), Spec)]: the tunnels' open sections (roads in the open)
        self.crossovers = {}    # cell key -> Plans of surface roads crossing an explicitly mapped tunnel

    def _cell_plans(self, key):
        with self.lock:
            got = self.cells.get(key)
            kl = self.key_locks.setdefault(key, threading.Lock())
        if got is not None:
            return got
        with kl:
            return self._plan_cell(key)

    def _plan_cell(self, key):
        with self.lock:
            got = self.cells.get(key)
            failed = self.failed.get(key)
        if got is not None:
            return got
        if failed is not None and time.monotonic() - failed < RETRY_S:
            return []               # offline: no block waits on the same failing fetch again
        try:
            feats = self.md.cell(key, layers=("roads",), kind="demand").layers.get("roads")
        except Exception as e:      # no road data: ungraded (asked again after RETRY_S)
            log.debug("grading: roads of %s: %s: %s", key, type(e).__name__, e)
            with self.lock:
                self.failed[key] = time.monotonic()
            return []
        plans = []
        if feats is not None and len(feats):
            specs = roadsmod.road_specs(feats, _urban_core, self.widths)
            parts, ids = [], []
            for i in range(len(feats)):
                if specs[i] is None:
                    continue
                for ring in roadsmod.ground_parts(feats, i):     # not bridges / tunnels
                    parts.append((np.asarray(ring, np.float64), specs[i]))
                    ids.append(str(feats.ids[i]))
            for fid, p in zip(ids, plan_roads(self.frame, parts, self.elev)):
                if p is not None:
                    plans.append((fid, p))
            road_plans = [p for _f, p in plans]
            crossovers = self._surface_crossings(feats, key, road_plans)
            secs = self._tunnel_sections(feats, key, road_plans, crossovers)
            plans.extend((fid + TUNNEL_TAG, Plan(xy, z, spec.width / 2 + shoulder(spec)))
                         for fid, spec, xy, z, k in secs if k == 0)
            plans.extend(self._mouth_plans(secs))
            covers = [(xy, spec.width / 2 + TUNNEL_KEEP_M) for _f, spec, xy, _z, k in secs if k]
            opens = [(xy, spec) for _f, spec, xy, _z, k in secs if k == 0]
        else:
            covers, opens, crossovers = [], [], []
        with self.lock:
            self.cells.setdefault(key, plans)
            self.covers.setdefault(key, covers)
            self.opens.setdefault(key, opens)
            self.crossovers.setdefault(key, crossovers)
            return self.cells[key]

    def _surface_crossings(self, feats, key, road_plans):
        """The surface road owns its carriageway above an explicit tunnel, even when a coarse DEM
        cannot resolve the two levels. The lower road's approaches must not dig a trench through it.
        Keep only a short piece around each crossing, so normal junction grading elsewhere is unchanged.
        """
        out = []
        ts = roadsmod.tunnel_specs(feats)
        for i in range(len(feats)):
            if ts[i] is None:
                continue
            for j, ring in enumerate(roadsmod.tunnel_parts(feats, i)):
                ring = np.asarray(self._longest(str(feats.ids[i]), j, ring, key), np.float64)
                if len(ring) < 2:
                    continue
                e, n, _ = self.frame.geodetic_to_enu(ring[:, 1], ring[:, 0], 0.0)
                xy = np.c_[e, n]
                repair = ts[i].width / 2 + 3 * SIGMA_M
                lo, hi = xy.min(0), xy.max(0)
                for p in road_plans:
                    if p.bbox[2] < lo[0] or p.bbox[0] > hi[0] or p.bbox[3] < lo[1] or p.bbox[1] > hi[1]:
                        continue
                    # End touches are the tunnel's own approaches, not an upper road.
                    s = np.r_[0.0, np.cumsum(np.hypot(*np.diff(p.xy, axis=0).T))]
                    crossings = sorted({round(float(sp), 6) for _pi, sp, q in
                                        roadsmod._crossings([p.xy], [xy]) if 1.0 < sp < s[-1] - 1.0
                                        and min(np.linalg.norm(q - xy[0]), np.linalg.norm(q - xy[-1])) > 1.0})
                    if not crossings:
                        continue
                    for sp in crossings:
                        # The DEM often resolves the lower road and leaves a false dip in the
                        # upper one. Bridge it from the undisturbed profile beyond the smoother's
                        # footprint instead of smoothing the lower road's elevation into it.
                        a, b = max(0.0, sp - repair), min(s[-1], sp + repair)
                        start, end = max(0.0, a - T_MAX), min(s[-1], b + T_MAX)
                        local_s = np.r_[start, s[(s > start) & (s < end)], end]
                        local_xy = np.c_[np.interp(local_s, s, p.xy[:, 0]), np.interp(local_s, s, p.xy[:, 1])]
                        z = np.interp(local_s, s, p.z)
                        inside = (local_s >= a) & (local_s <= b)
                        z[inside] = np.maximum(z[inside], np.interp(local_s[inside], [a, b],
                                                                 np.interp([a, b], s, p.z)))
                        out.append(Plan(local_xy, z, p.half))
        return out

    def _longest(self, fid, j, ring, key):
        """Part j of tunnel fid as the cells at its ends have it, the longest (a part comes clipped differently in
        the cells around: graded as the 30 m piece, 97th Street's 45 m arch got an open road graded in it; the
        same rule as roads.BridgeProfiles._load, 2026-10-17)."""
        best = ring
        for p in (ring[0], ring[-1]):
            ck = mapcells.cell_of(float(p[1]), float(p[0]))
            if key is not None and str(ck) == str(key):
                continue
            try:
                f = self.md.cell(ck, layers=("roads",), kind="demand").layers.get("roads")
            except Exception:
                continue
            if f is None or not len(f):
                continue
            ids = [str(x) for x in f.ids]
            if fid not in ids:
                continue
            i = ids.index(fid)
            parts = roadsmod.tunnel_parts(f, i)
            if j < len(parts) and len(parts[j]) > len(best):
                best = parts[j]
        return best

    def _tunnel_sections(self, feats, key=None, road_plans=(), crossovers=()):
        """[(fid, spec, xy, z, kind)] of the tunnels' sections (roads.tunnel_sections on the ungraded ground, its
        ends graded by road_plans: the cell's road Plans, as roads.TunnelProfiles.ends grades them with the roads'
        plans alone): kind 0 an open road at z, 1 a low arch, 2 a full tunnel."""
        out = []
        ts = roadsmod.tunnel_specs(feats)
        ground = []
        if any(sp is not None for sp in ts):
            # Use exactly the source geometries and carriageway widths that
            # BridgeProfiles._load gives TunnelProfiles, without grading shoulders.
            rs = roadsmod.road_specs(feats)
            for i in range(len(feats)):
                if rs[i] is None:
                    continue
                for ring in roadsmod.ground_parts(feats, i):
                    e, n = roadsmod.mapgeom.enu_xy(feats, self.frame, ring)
                    ground.append((np.c_[e, n], rs[i].width))
        for i in range(len(feats)):
            if ts[i] is None:
                continue
            for j, ring in enumerate(roadsmod.tunnel_parts(feats, i)):
                ring = self._longest(str(feats.ids[i]), j, ring, key)
                ll = np.asarray(ring, np.float64)
                if len(ll) < 2:
                    continue
                E, N, _ = self.frame.geodetic_to_enu(ll[:, 1], ll[:, 0], 0.0)
                xy, s = resample(np.stack([np.asarray(E), np.asarray(N)], axis=1), VERTEX_STEP)
                if len(xy) < 2 or s[-1] <= 0:
                    continue
                la, lo, _ = self.frame.enu_to_geodetic(xy[:, 0], xy[:, 1], 0.0)
                g = np.asarray(self.elev(la, lo), np.float64)
                if road_plans:
                    g = g.copy()
                    g[[0, -1]] = grade_points(xy[[0, -1], 0], xy[[0, -1], 1], g[[0, -1]], list(road_plans))
                covered = roadsmod.tunnel_crossing_mask(xy, ground)
                upper = None
                if covered.any() and crossovers:
                    footprint = roadsmod.tunnel_crossing_mask(xy, ground, margin=0.0, extend=False)
                    upper = grade_points(xy[:, 0], xy[:, 1], g, crossovers, ROAD_LIFT)
                    upper[~footprint] = np.nan
                floor, kinds = roadsmod.tunnel_sections(s, g, covered=covered, upper=upper)
                i0 = 0
                while i0 < len(kinds):
                    i1 = i0
                    while i1 + 1 < len(kinds) and kinds[i1 + 1] == kinds[i0]:
                        i1 += 1
                    a = max(0, i0 - 1)          # sharing the end sample with the section before
                    if i1 > a:
                        out.append((str(feats.ids[i]), ts[i], xy[a:i1 + 1], floor[a:i1 + 1], int(kinds[i0])))
                    i0 = i1 + 1
        return out

    @staticmethod
    def _mouth_plans(secs):
        """(fid, Plan) of the covered sections' mouths: the floor MOUTH_PLAN_M into the tube from a portal (where an
        open section or nothing comes before / after it): the ground at the portal graded to the road on both sides
        of it (the grading faded from the road's plan into the ungraded hill there, and the road tile and the
        terrain block, sampled at different zooms, came out a few cm apart: the block poked through the road
        outside 97th Street's arch, 2026-10-17)."""
        out = []
        for n, (fid, spec, xy, z, kind) in enumerate(secs):
            if not kind or len(xy) < 2:
                continue
            same = lambda m: 0 <= m < len(secs) and secs[m][0] == fid     # noqa: E731
            s = np.r_[0.0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]
            hw = spec.width / 2 + shoulder(spec)
            for at_start in (True, False):
                nb = n - 1 if at_start else n + 1
                if same(nb) and secs[nb][4] != 0:
                    continue                    # inside the hill: a full tunnel goes on
                if at_start:
                    m = s <= MOUTH_PLAN_M
                    t = np.interp(MOUTH_PLAN_M, s, np.arange(len(s)))
                else:
                    m = s >= s[-1] - MOUTH_PLAN_M
                    t = np.interp(s[-1] - MOUTH_PLAN_M, s, np.arange(len(s)))
                i0 = int(np.floor(t))
                p = xy[i0] + (t - i0) * (xy[min(i0 + 1, len(xy) - 1)] - xy[i0])
                pz = z[i0] + (t - i0) * (z[min(i0 + 1, len(z) - 1)] - z[i0])
                if at_start:
                    pxy, pzz = np.r_[xy[m], p[None]], np.r_[z[m], pz]
                else:
                    pxy, pzz = np.r_[p[None], xy[m]], np.r_[pz, z[m]]
                if len(pxy) >= 2:
                    out.append((fid + TUNNEL_TAG + ("m0" if at_start else "m1"), Plan(pxy, pzz, hw)))
        return out

    def _covered_tunnels(self, feats):
        """[(xy, half width)] of the tunnels' covered sections (not open roads): the grading leaves the ground over
        them as it is (apply): the approaches' grading reached up to T_MAX past a portal and cut a park bridge's soil
        down under its arch's vault, the terrain then cut away over it (2026-10-17)."""
        return [(xy, spec.width / 2 + TUNNEL_KEEP_M) for _f, spec, xy, _z, kind in self._tunnel_sections(feats) if kind]

    def _open_tunnels(self, feats):
        """(fid, Plan) of the tunnels' open sections (roads.TUNNEL_OPEN_COVER): the ground graded to the road's floor
        (the lower hull of the ground), as the road is drawn (roads._tunnel_chunks): over a footbridge's hump in the
        DEM the road climbed it, the ground over the road (Central Park's transverses, 2026-10-17)."""
        return [(fid, Plan(xy, z, spec.width / 2 + shoulder(spec)))
                for fid, spec, xy, z, kind in self._tunnel_sections(feats) if kind == 0]

    def planned(self, key):
        """True once cell key's plans exist (made, or failed recently)."""
        with self.lock:
            f = self.failed.get(key)
            return key in self.cells or (f is not None and time.monotonic() - f < RETRY_S)

    def warm(self, key):
        """Make cell key's plans now (worker threads: the lookahead ahead of the player)."""
        self._cell_plans(key)

    def _plan_keys(self, lat, lon):
        pad = max(T_MAX + 40.0, CROSSOVER_CONTEXT_M) / 111320.0
        padlon = pad / max(0.05, math.cos(math.radians(float(np.mean(lat)))))
        return mapcells.cells_for_bbox(float(lat.min()) - pad, float(lon.min()) - padlon,
                                       float(lat.max()) + pad, float(lon.max()) + padlon)

    def plans(self, lat, lon, roads_only=False):
        """The Plans touching the points' area (each road once); roads_only: not the tunnels' (TUNNEL_TAG)."""
        lat = np.asarray(lat, np.float64)
        lon = np.asarray(lon, np.float64)
        seen, out = set(), []
        for key in self._plan_keys(lat, lon):
            for fid_part, p in self._cell_plans(key):
                if roads_only and TUNNEL_TAG in fid_part:
                    continue
                k = (fid_part, p.xy[0, 0], p.xy[0, 1])
                if k not in seen:
                    seen.add(k)
                    out.append(p)
        return out

    def apply(self, lat, lon, base, lift=0.0, roads_only=False):
        """base (the ungraded heights at the points) graded under the roads. Same shape as base.
        lift: m added under the roads (tapering with the grading's weight): the physics block and the
        road mesh use ROAD_LIFT, the visible ground tiles 0, so the road mesh lies exactly on the
        ground the tyres touch while the visible ground stays a little below it (no z-fighting;
        2026-10-11 the user saw the tyres sink into a road mesh lifted above the physics ground)."""
        lat = np.asarray(lat, np.float64)
        lon = np.asarray(lon, np.float64)
        base = np.asarray(base, np.float64)
        shape = base.shape
        if base.size == 0:
            return base
        plans = self.plans(lat, lon, roads_only)
        if not plans:
            return base
        e, n, _ = self.frame.geodetic_to_enu(lat.ravel(), lon.ravel(), 0.0)
        e, n = np.asarray(e), np.asarray(n)
        out = grade_points(e, n, base.ravel(), plans, lift)
        keep = self._over_tunnels(e, n)
        if keep is not None:
            out[keep] = base.ravel()[keep]
        if not roads_only:
            out = self._surface_over_tunnels(e, n, out, lift, self._plan_keys(lat, lon))
        return out.reshape(shape)

    def _surface_over_tunnels(self, e, n, base, lift, keys):
        """Restore only the upper carriageway at grade-separated crossings. A narrow shoulder fade
        leaves the tunnel portals at the lower road's approach height.
        """
        with self.lock:
            unique = {}
            for key in keys:
                for p in self.crossovers.get(key, ()):
                    unique.setdefault((p.half, p.xy.tobytes(), p.z.tobytes()), p)
            plans = [unique[key] for key in sorted(unique)]
        if not plans or not len(e):
            return base
        x0, y0, x1, y1 = e.min(), n.min(), e.max(), n.max()
        plans = [p for p in plans if not (p.bbox[2] < x0 or p.bbox[0] > x1 or p.bbox[3] < y0 or p.bbox[1] > y1)]
        if not plans:
            return base
        weight = np.zeros(len(e))
        for p in plans:
            lo, hi = p.xy.min(0) - p.half - WALL_T_M, p.xy.max(0) + p.half + WALL_T_M
            ii = np.flatnonzero((e >= lo[0]) & (e <= hi[0]) & (n >= lo[1]) & (n <= hi[1]))
            if not len(ii):
                continue
            points = np.c_[e[ii], n[ii]]
            distances = roadsmod._seg_dist(points, p.xy[:-1], p.xy[1:])
            nearest = distances.argmin(1)
            distance = distances[np.arange(len(ii)), nearest]
            ab = np.diff(p.xy, axis=0)
            lengths = np.hypot(*ab.T)
            arc = np.r_[0.0, np.cumsum(lengths)]
            t = np.clip(((points - p.xy[nearest]) * ab[nearest]).sum(1) /
                        np.maximum(lengths[nearest] ** 2, 1e-12), 0.0, 1.0)
            along = arc[nearest] + t * lengths[nearest]
            v = np.clip(np.minimum(along, arc[-1] - along) / T_MAX, 0.0, 1.0)
            u = np.clip((distance - p.half) / WALL_T_M, 0.0, 1.0)
            weight[ii] = np.maximum(weight[ii], (1 - u * u * (3 - 2 * u)) * v * v * (3 - 2 * v))
        ii = np.flatnonzero(weight > 0)
        if not len(ii):
            return base
        target = grade_points(e[ii], n[ii], base[ii], plans, lift)
        out = base.copy()
        out[ii] += weight[ii] * (target - out[ii])
        return out

    def open_tunnels(self, lat, lon):
        """[(lat (k,), lon (k,), Spec)] of the tunnels' open sections planned near the points: roads on the ground
        that the map calls tunnels (surface.paint_roads paints them: grass grew over the open road of Central Park's
        79th Street Transverse, 2026-10-17)."""
        lat = np.asarray(lat, np.float64)
        lon = np.asarray(lon, np.float64)
        if lat.size == 0:
            return []
        for key in mapcells.cells_for_bbox(float(lat.min()), float(lon.min()), float(lat.max()), float(lon.max())):
            self._cell_plans(key)
        with self.lock:
            secs = [o for v in self.opens.values() for o in v]
        out, seen = [], set()
        for xy, spec in secs:
            k = (round(float(xy[0, 0]), 2), round(float(xy[0, 1]), 2), len(xy))
            if k in seen:
                continue
            seen.add(k)
            la, lo, _ = self.frame.enu_to_geodetic(xy[:, 0], xy[:, 1], 0.0)
            la, lo = np.asarray(la), np.asarray(lo)
            if la.max() < lat.min() - 0.001 or la.min() > lat.max() + 0.001 or \
                    lo.max() < lon.min() - 0.0015 or lo.min() > lon.max() + 0.0015:
                continue
            out.append((la, lo, spec))
        return out

    def _over_tunnels(self, e, n):
        """Which points lie over a covered tunnel (its half width + TUNNEL_KEEP_M), or None."""
        with self.lock:
            zones = [z for v in self.covers.values() for z in v]
        if not zones or not len(e):
            return None
        x0, y0, x1, y1 = e.min(), n.min(), e.max(), n.max()
        import fast
        if fast.AVAILABLE and hasattr(fast._ef, "over_tunnel"):     # (Rust: the same sums, without the GIL)
            mask = np.zeros(len(e), bool)
            ee, nn = np.ascontiguousarray(e, np.float64), np.ascontiguousarray(n, np.float64)
            for xy, hw in zones:
                fast._ef.over_tunnel(mask, ee, nn, np.ascontiguousarray(xy[:, :2], np.float64), float(hw),
                                     float(TUNNEL_KEEP_IN_M))
            return mask if mask.any() else None
        mask = None
        for xy, hw in zones:
            if xy[:, 0].max() + hw < x0 or xy[:, 0].min() - hw > x1 or xy[:, 1].max() + hw < y0 or xy[:, 1].min() - hw > y1:
                continue
            a, b = xy[:-1], xy[1:]
            ab = b - a
            L2 = np.maximum((ab * ab).sum(1), 1e-12)
            sj = np.r_[0.0, np.cumsum(np.sqrt(L2))]
            # only the segments near the points (the Gotthard road tunnel's 4,200 segments each took a pass over a
            # block's points: 140 s of grading per block, 2026-10-18)
            near = ((np.minimum(a[:, 0], b[:, 0]) - hw <= x1) & (np.maximum(a[:, 0], b[:, 0]) + hw >= x0)
                    & (np.minimum(a[:, 1], b[:, 1]) - hw <= y1) & (np.maximum(a[:, 1], b[:, 1]) + hw >= y0))
            for j in np.flatnonzero(near):
                t = ((e - a[j, 0]) * ab[j, 0] + (n - a[j, 1]) * ab[j, 1]) / L2[j]
                # over it, from TUNNEL_KEEP_IN_M inside its portals: its mouths graded to the road (a road's last row
                # at a portal took the hill's height, the road mesh a wedge up into the opening, 2026-10-17)
                s_ = sj[j] + t * np.sqrt(L2[j])
                inside = (t > 0.0) & (t < 1.0) & (s_ > TUNNEL_KEEP_IN_M) & (s_ < sj[-1] - TUNNEL_KEEP_IN_M)
                d = np.abs((e - a[j, 0]) * ab[j, 1] - (n - a[j, 1]) * ab[j, 0]) / np.sqrt(L2[j])
                m = inside & (d <= hw)
                mask = m if mask is None else (mask | m)
        return mask


def grade_points(px, py, base, plans, lift=0.0):
    """base at the points (px, py) graded under the plans (see the module doc). Pure.
    All segments at once, in batches of about PAIR_BATCH (segment, point) pairs (a Python loop per
    segment was the server's largest CPU cost while driving, 2026-10-12)."""
    px = np.asarray(px, np.float64)
    py = np.asarray(py, np.float64)
    base = np.asarray(base, np.float64)
    out = base.copy()
    if not len(px):
        return out
    x0, y0, x1, y1 = px.min(), py.min(), px.max(), py.max()
    bx = np.floor((px - x0) / BUCKET).astype(np.int64)
    by = np.floor((py - y0) / BUCKET).astype(np.int64)
    nbx = int(bx.max()) + 1
    key = by * nbx + bx
    order = np.argsort(key, kind="stable")
    sk = key[order]
    # every segment of the plans near the points: ends, end heights, reach (core half width + T_MAX)
    A, B, ZA, ZB, H = [], [], [], [], []
    for p in plans:
        if p.bbox[2] < x0 or p.bbox[0] > x1 or p.bbox[3] < y0 or p.bbox[1] > y1 or len(p.xy) < 2:
            continue
        A.append(p.xy[:-1])
        B.append(p.xy[1:])
        ZA.append(p.z[:-1])
        ZB.append(p.z[1:])
        H.append(np.full(len(p.xy) - 1, p.half))
    if not A:
        return out
    A, B, ZA, ZB, H = (np.concatenate(v) for v in (A, B, ZA, ZB, H))
    import fast
    if fast.AVAILABLE and getattr(fast._ef, "VERSION", 0) >= 27:   # the Rust loop: the same pairs in the same order
        f64 = np.float64
        return fast._ef.grade_points(np.ascontiguousarray(px, f64), np.ascontiguousarray(py, f64),
                                     np.ascontiguousarray(base, f64), np.ascontiguousarray(A[:, :2], f64),
                                     np.ascontiguousarray(B[:, :2], f64), np.ascontiguousarray(ZA, f64),
                                     np.ascontiguousarray(ZB, f64), np.ascontiguousarray(H, f64), float(lift),
                                     float(SLOPE_RUN), float(T_MIN), float(T_MAX), float(BLEND_R), float(BUCKET),
                                     float(WALL_CUT_M), float(WALL_T_M), float(WALL_FLAT_M), float(WALL_AHEAD_M))
    reach = H + T_MAX
    lo_x = np.minimum(A[:, 0], B[:, 0]) - reach
    hi_x = np.maximum(A[:, 0], B[:, 0]) + reach
    lo_y = np.minimum(A[:, 1], B[:, 1]) - reach
    hi_y = np.maximum(A[:, 1], B[:, 1]) + reach
    near = ~((hi_x < x0) | (lo_x > x1) | (hi_y < y0) | (lo_y > y1))
    A, B, ZA, ZB, H = A[near], B[near], ZA[near], ZB[near], H[near]
    lo_x, hi_x, lo_y, hi_y = lo_x[near], hi_x[near], lo_y[near], hi_y[near]
    cx0 = np.maximum(0, np.floor((lo_x - x0) / BUCKET)).astype(np.int64)
    cx1 = np.minimum(nbx - 1, np.floor((hi_x - x0) / BUCKET)).astype(np.int64)
    cy0 = np.maximum(0, np.floor((lo_y - y0) / BUCKET)).astype(np.int64)
    cy1 = np.floor((hi_y - y0) / BUCKET).astype(np.int64)
    # (segment, bucket row) pairs -> the sorted points' range of that row's buckets cx0..cx1
    nrow = np.maximum(cy1 - cy0 + 1, 0)
    seg = np.repeat(np.arange(len(A)), nrow)
    row = np.repeat(cy0, nrow) + (np.arange(nrow.sum()) - np.repeat(np.cumsum(nrow) - nrow, nrow))
    i0 = np.searchsorted(sk, row * nbx + cx0[seg], "left")
    i1 = np.searchsorted(sk, row * nbx + cx1[seg], "right")
    cnt = np.maximum(i1 - i0, 0)
    keep = cnt > 0
    seg, i0, cnt = seg[keep], i0[keep], cnt[keep]
    num = np.zeros(len(px))
    den = np.zeros(len(px))
    wmax = np.zeros(len(px))
    ends = np.cumsum(cnt)
    start = 0
    while start < len(seg):
        stop = int(np.searchsorted(ends, (ends[start - 1] if start else 0) + PAIR_BATCH, "right"))
        stop = max(stop, start + 1)
        c = cnt[start:stop]
        s_ = np.repeat(seg[start:stop], c)
        idx = order[np.repeat(i0[start:stop], c) + (np.arange(c.sum()) - np.repeat(np.cumsum(c) - c, c))]
        a = A[s_]
        ab = B[s_] - a
        qx, qy = px[idx] - a[:, 0], py[idx] - a[:, 1]
        L2 = ab[:, 0] * ab[:, 0] + ab[:, 1] * ab[:, 1]
        long_ = L2 > 1e-12
        t = np.where(long_, np.clip((qx * ab[:, 0] + qy * ab[:, 1]) / np.where(long_, L2, 1.0), 0.0, 1.0), 0.0)
        d = np.hypot(qx - t * ab[:, 0], qy - t * ab[:, 1])
        target = ZA[s_] + (ZB[s_] - ZA[s_]) * t
        Lab = np.sqrt(np.maximum(L2, 1e-24))
        side = np.abs(qx * ab[:, 1] - qy * ab[:, 0]) / Lab
        along = (qx * ab[:, 0] + qy * ab[:, 1]) / Lab
        ahead = np.maximum(np.maximum(-along, along - Lab), 0.0)
        wall = (base[idx] - target > WALL_CUT_M) & (ahead < side) & (ahead < WALL_AHEAD_M)
        T = np.where(wall, WALL_T_M, np.clip(SLOPE_RUN * np.abs(target - base[idx]), T_MIN, T_MAX))
        u = np.clip((d - H[s_] - np.where(wall, WALL_FLAT_M, 0.0)) / T, 0.0, 1.0)
        w = 1.0 - u * u * (3.0 - 2.0 * u)           # 1 on the core, smooth to 0 over T
        m = w > 0
        i = idx[m]
        # the blend between roads by inverse distance from each centreline (times w), so two roads
        # near each other (divided carriageways, junctions) meet in a gradual slope; with w alone
        # the target jumped at a core's edge (2026-10-11, the user's car flipped at speed:
        # centreline 2nd difference p99 0.17 m per metre, worst 0.5 m)
        wb = w[m] / (1.0 + (d[m] / BLEND_R) ** 2)
        num += np.bincount(i, wb * target[m], len(px))
        den += np.bincount(i, wb, len(px))
        np.maximum.at(wmax, i, w[m])
        start = stop
    g = den > 0
    out[g] = base[g] + wmax[g] * (num[g] / den[g] - base[g] + lift)
    return out


class GradedDem:
    """dem.Dem with sample() graded under the roads; everything else passes through."""

    def __init__(self, dem, grader):
        self._dem, self._grader = dem, grader

    def sample(self, lat, lon, zoom, progress=None):
        base = self._dem.sample(lat, lon, zoom, progress) if progress is not None else self._dem.sample(lat, lon, zoom)
        return self._grader.apply(lat, lon, base)

    def __getattr__(self, name):
        return getattr(self._dem, name)
