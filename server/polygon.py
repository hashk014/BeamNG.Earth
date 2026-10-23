"""Point-in-polygon for numpy arrays (even-odd rule), in place of matplotlib.path.Path.contains_points:
the server used matplotlib for nothing else, and the players' install (install.py: server/requirements.txt)
did not have it, so the server did not start from the release zip (2026-10-15).

    Path(ring).contains_points(pts) -> bool array    ring: (N, 2) vertices, open or closed; pts: (M, 2)
"""
import numpy as np

import fast


def contains_points(ring, pts):
    """Which of pts (M, 2) lie inside the polygon ring (N, 2) (even-odd crossings of a ray toward +x)."""
    ring = np.asarray(ring, np.float64).reshape(-1, 2)
    pts = np.asarray(pts, np.float64).reshape(-1, 2)
    fast.require(0, "contains_points")       # the Rust loop: crossings in horizontal bands of the ring's edges
    return np.asarray(fast._ef.contains_points(np.ascontiguousarray(ring), np.ascontiguousarray(pts)))


class Path:
    """The part of matplotlib.path.Path the server uses."""

    def __init__(self, vertices):
        self.vertices = np.asarray(vertices, np.float64).reshape(-1, 2)

    def contains_points(self, pts):
        return contains_points(self.vertices, pts)


def roof_cells(outer, holes=()):
    """Convex cells covering a polygon with holes, using an even-odd sweep.

    Each band lies between consecutive vertex heights. Boundary edges are
    linear within a band, so paired crossings form exact trapezoids. This
    preserves courtyards without a new triangulation dependency or bridges
    across the holes. Input rings must be simple and non-intersecting.
    """
    rings = [np.asarray(r, np.float64)[:, :2] for r in (outer, *holes) if len(r) >= 3]
    if not rings:
        return []
    a = np.concatenate(rings)
    b = np.concatenate([np.roll(r, -1, axis=0) for r in rings])
    ys = np.unique(a[:, 1])
    out = []
    for low, high in zip(ys[:-1], ys[1:]):
        if high - low <= 1e-9:
            continue
        mid = (low + high) / 2
        active = (np.minimum(a[:, 1], b[:, 1]) < mid) & (np.maximum(a[:, 1], b[:, 1]) > mid)
        p, q = a[active], b[active]
        slope = (q[:, 0] - p[:, 0]) / (q[:, 1] - p[:, 1])
        order = np.argsort(p[:, 0] + (mid - p[:, 1]) * slope, kind="stable")
        x0 = p[:, 0] + (low - p[:, 1]) * slope
        x1 = p[:, 0] + (high - p[:, 1]) * slope
        for left, right in zip(order[::2], order[1::2]):
            cell = np.array([(x0[left], low), (x0[right], low),
                             (x1[right], high), (x1[left], high)])
            keep = np.linalg.norm(cell - np.roll(cell, 1, axis=0), axis=1) > 1e-9
            if keep.sum() >= 3:
                out.append(cell[keep])
    return out


def subtract_cells(outer, cutters=(), holes=()):
    """Convex cells of outer minus the union of cutters and holes.

    Unlike the even-odd roof sweep, overlapping cutters must remain empty.
    Split at segment intersections too, so the boundary order stays constant
    inside each band. This also handles parts crossing a parent's outline.
    """
    rings = [np.asarray(r, np.float64)[:, :2] for r in (outer, *holes, *cutters) if len(r) >= 3]
    if not rings:
        return []
    a = np.concatenate(rings)
    b = np.concatenate([np.roll(r, -1, axis=0) for r in rings])
    group = np.repeat(np.arange(len(rings)), [len(r) for r in rings])
    d = b - a
    ys = list(a[:, 1])
    # A vectorised row at a time avoids an unbounded N x N allocation.
    for i in range(len(a) - 1):
        other = np.arange(i + 1, len(a))
        q, e = a[other] - a[i], d[other]
        den = d[i, 0] * e[:, 1] - d[i, 1] * e[:, 0]
        safe = np.where(np.abs(den) > 1e-12, den, 1.0)
        t = (q[:, 0] * e[:, 1] - q[:, 1] * e[:, 0]) / safe
        u = (q[:, 0] * d[i, 1] - q[:, 1] * d[i, 0]) / safe
        hit = (np.abs(den) > 1e-12) & (t > 1e-9) & (t < 1 - 1e-9) & (u > 1e-9) & (u < 1 - 1e-9)
        ys.extend((a[i, 1] + t[hit] * d[i, 1]).tolist())
    ys = np.unique(ys)
    out = []
    for low, high in zip(ys[:-1], ys[1:]):
        if high - low <= 1e-8:
            continue
        mid = (low + high) / 2
        active = np.flatnonzero((np.minimum(a[:, 1], b[:, 1]) < mid) &
                                (np.maximum(a[:, 1], b[:, 1]) > mid))
        slope = d[active, 0] / d[active, 1]
        order = np.argsort(a[active, 0] + (mid - a[active, 1]) * slope, kind='stable')
        x0 = a[active, 0] + (low - a[active, 1]) * slope
        x1 = a[active, 0] + (high - a[active, 1]) * slope
        inside = np.zeros(len(rings), bool)
        for k, left in enumerate(order[:-1]):
            inside[group[active[left]]] ^= True
            if not inside[0] or inside[1:].any():
                continue
            right = order[k + 1]
            cell = np.array([(x0[left], low), (x0[right], low),
                             (x1[right], high), (x1[left], high)])
            area = abs(np.sum(cell[:, 0] * np.roll(cell[:, 1], -1) -
                              np.roll(cell[:, 0], -1) * cell[:, 1])) / 2
            keep = np.linalg.norm(cell - np.roll(cell, 1, axis=0), axis=1) > 1e-8
            if area > 1e-7 and keep.sum() >= 3:
                out.append(cell[keep])
    return out
