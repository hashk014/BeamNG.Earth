"""Startup-only road rendering preference, shared by source and packaged launches."""
import json
import os
import tempfile

try:
    from . import storage
except ImportError:  # earthd.py and packaged server modules also run as top-level imports
    import storage

ENV = "BNGE_ROADS_IN_GROUND"
MODES = ("terrain", "mesh")


def config_path():
    return os.path.join(os.path.dirname(storage.config_path()), "roads.json")


def _load():
    try:
        with open(config_path(), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def mode():
    """Keep the existing environment override; otherwise saved choice, then 1.6 terrain."""
    if ENV in os.environ:
        return "mesh" if os.environ[ENV] == "0" else "terrain"
    value = _load().get("road_rendering")
    return value if value in MODES else "terrain"


def save(value):
    if value is not None and value not in MODES:
        raise ValueError("road rendering must be terrain or mesh")
    data = _load()
    if value is None:
        data.pop("road_rendering", None)
    else:
        data["road_rendering"] = value
    dst = config_path()
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=os.path.dirname(dst),
                                         prefix="roads-", suffix=".tmp", delete=False) as f:
            tmp = f.name
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp, dst)
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)


def add_arguments(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--road-rendering", choices=MODES,
                       help="save road surfaces for future starts: terrain (1.6 default) or mesh (legacy overlay)")
    group.add_argument("--reset-road-rendering", action="store_true",
                       help="restore terrain road surfaces for future starts")
    parser.add_argument("--print-road-rendering", action="store_true",
                        help="print the selected road rendering mode and exit without starting the game/server")


def configure(args, parser):
    try:
        if args.road_rendering is not None:
            save(args.road_rendering)
            os.environ[ENV] = "1" if args.road_rendering == "terrain" else "0"
        elif args.reset_road_rendering:
            save(None)
            os.environ.pop(ENV, None)
    except (OSError, ValueError) as exc:
        parser.error("could not save road rendering: " + str(exc))
    selected = mode()
    # Freeze the selection for subprocesses even if the preference file changes mid-session.
    os.environ[ENV] = "1" if selected == "terrain" else "0"
    if args.print_road_rendering:
        print(selected)
        return True
    return False
