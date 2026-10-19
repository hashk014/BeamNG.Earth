#!/usr/bin/env python3
"""Render the checked-in geometry comparison data, without running BeamNG.

    python tools/render_comparison.py

The fixture records generator output from the commits named in its metadata.
Requires numpy and Pillow, already used by the server.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BG, PANEL, TEXT, MUTED = "#0d1726", "#152437", "#f4f7fa", "#a4b5c7"
TEAL, ORANGE = "#54dcc2", "#ffbc76"


def font(size):
    for name in ("C:/Windows/Fonts/segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(name).is_file():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default(size=size)


def canvas(title, subtitle):
    im = Image.new("RGB", (1600, 820), BG)
    d = ImageDraw.Draw(im)
    d.text((48, 32), title, fill=TEXT, font=font(44))
    d.text((50, 99), subtitle, fill=MUTED, font=font(23))
    for x, label, color in ((40, "BEFORE / UPSTREAM 1.5.1", ORANGE), (820, "AFTER / EUROPE PREVIEW", TEAL)):
        d.rounded_rectangle((x, 156, x + 740, 728), radius=18, fill=PANEL)
        d.text((x + 24, 174), label, fill=color, font=font(25))
    d.text((48, 758), "Generator geometry preview. Not an in-game screenshot.", fill=MUTED, font=font(22))
    return im


def road(data, path):
    im = canvas("Keep the mapped bend", "Same road, same scale. Source outline from Overture Maps.")
    r = data["road"]
    source, centre = np.asarray(r["source"]), np.asarray(r["centre"])
    scale = 26.0
    for label, x in (("before", 40), ("after", 820)):
        panel = Image.new("RGB", (740, 460), PANEL)
        d = ImageDraw.Draw(panel)
        def xy(points):
            q = (np.asarray(points) - centre) * [scale, -scale] + [370, 230]
            return [tuple(v) for v in q]
        for k in range(-20, 21, 2):
            a = 370 + k * scale
            b = 230 + k * scale
            d.line([(a, 0), (a, 460)], fill="#20354a", width=1)
            d.line([(0, b), (740, b)], fill="#20354a", width=1)
        d.line(xy(source), fill=TEXT, width=3)
        d.line(xy(r[label]), fill=ORANGE if label == "before" else TEAL, width=7)
        for p in xy(source):
            d.ellipse((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5), fill=PANEL, outline=TEXT, width=2)
        if label == "before":
            d.line(xy([r["centre"], r["closest"]]), fill="#ff7575", width=4)
        d.rectangle((12, 7, 540, 58), fill=PANEL)
        d.text((24, 18), f"{r['error_m']:.2f} m from the mapped corner" if label == "before" else
               "Mapped corner retained", fill=ORANGE if label == "before" else TEAL, font=font(25))
        d.line([(26, 425), (26 + 2 * scale, 425)], fill=MUTED, width=3)
        d.text((32 + 2 * scale, 408), "2 m", fill=MUTED, font=font(21))
        im.paste(panel, (x, 224))
    d = ImageDraw.Draw(im)
    d.text((66, 690), "White: mapped centreline    Orange: old grading plan", fill=MUTED, font=font(19))
    d.text((846, 690), "White: mapped centreline    Green: preview grading plan", fill=MUTED, font=font(19))
    im.save(path)


def courtyard(data, path):
    im = canvas("Keep the courtyard open", "Roof viewed from above. Same mapped footprint and flat 10 m roof on both sides.")
    court = data["courtyard"]
    def project(p):
        return np.c_[p[:, 0], -p[:, 1]]
    vertices = np.concatenate([np.asarray(court[k]["vertices"]) for k in ("before", "after")])
    bounds = project(vertices)
    low, high = bounds.min(0), bounds.max(0)
    scale = min(630 / (high[0] - low[0]), 390 / (high[1] - low[1]))
    centre = (low + high) / 2
    for label, x in (("before", 40), ("after", 820)):
        p, t = np.asarray(court[label]["vertices"]), np.asarray(court[label]["triangles"])
        uv = (project(p) - centre) * scale + [x + 370, 445]
        tri = p[t]
        normal = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        d = ImageDraw.Draw(im)
        roof = (normal[:, 2] > 1e-6) & np.all(np.isclose(tri[:, :, 2], 10.0), axis=1)
        assert roof.any(), "Comparison mesh has no roof surface"
        for i in np.flatnonzero(roof):
            d.polygon([tuple(v) for v in uv[t[i]]], fill="#4da79c")
        d.text((x + 24, 680), "Courtyard covered by the generated roof" if label == "before" else
               "Courtyard void preserved in roof and collision", fill=ORANGE if label == "before" else TEAL, font=font(23))
    im.save(path)


def main():
    data = json.loads((ROOT / "docs/research/fork-comparison.json").read_text(encoding="utf-8"))
    out = ROOT / "docs/images"
    out.mkdir(exist_ok=True)
    road(data, out / "road-comparison.png")
    courtyard(data, out / "courtyard-comparison.png")
    print("Rendered two comparison images from recorded generator output.")


if __name__ == "__main__":
    main()
