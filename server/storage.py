"""Persistent download-cache selection shared by source and packaged launch paths."""
import json
import os
import tempfile

ENV = "BNGEARTH_CACHE_DIR"


def config_path():
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "beamng-earth", "storage.json")


def normalise(path):
    if not isinstance(path, str) or not path.strip():
        raise ValueError("cache directory must be a non-empty path")
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


def load():
    try:
        with open(config_path(), encoding="utf-8") as f:
            value = json.load(f)
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def cache_dir():
    """Environment override, saved preference, then the original default (no implicit migration)."""
    for value in (os.environ.get(ENV), load().get("cache_dir")):
        if isinstance(value, str) and value.strip():
            return normalise(value)
    return os.path.join(os.path.expanduser("~"), ".cache", "beamng-earth")


def save(path):
    value = normalise(path) if path is not None else None
    data = load()
    if value is None:
        data.pop("cache_dir", None)
    else:
        data["cache_dir"] = value
    dst = config_path()
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=os.path.dirname(dst),
                                         prefix="storage-", suffix=".tmp", delete=False) as f:
            tmp = f.name
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp, dst)
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
    return value


def add_arguments(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--cache-dir", metavar="PATH", help="save the download-cache folder for future starts")
    group.add_argument("--reset-cache-dir", action="store_true", help="restore the default download-cache folder")
    parser.add_argument("--print-cache-dir", action="store_true", help="print the selected cache folder and exit")


def configure(args, parser):
    try:
        if args.cache_dir is not None:
            os.environ[ENV] = save(args.cache_dir)
        elif args.reset_cache_dir:
            save(None)
            os.environ.pop(ENV, None)
    except (OSError, ValueError) as exc:
        parser.error("could not save the cache folder: " + str(exc))
    if args.print_cache_dir:
        print(cache_dir())
        return True
    return False
