"""Compare the surface classifier with a historical function on a fixed synthetic workload."""
import argparse
import ast
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import timeit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
import roads

WORK = [("residential", "asphalt"), ("primary", None), ("track", "gravel"), ("secondary", "unknown"),
        ("primary", "concrete:plates"), ("track", "unpaved"), ("residential", " Asphalt "), ("primary", "asphalt;gravel")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default="6d143e6")
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "surface-benchmark.json")
    args = parser.parse_args()
    if args.iterations < 1 or args.repeats < 1:
        parser.error("iterations and repeats must be positive")
    source = subprocess.check_output(["git", "show", args.baseline + ":server/roads.py"], cwd=ROOT,
                                     text=True, encoding="utf-8")
    function = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "surface_kind")
    namespace = dict(roads.__dict__)
    exec(compile(ast.Module(body=[function], type_ignores=[]), "<surface-baseline>", "exec"), namespace)
    before = namespace["surface_kind"]
    if any(before(*row) != roads.surface_kind(*row) for row in WORK):
        parser.error("classifier outputs differ on this workload; a speed comparison would be misleading")
    old = statistics.median(timeit.repeat(lambda: [before(*row) for row in WORK], repeat=args.repeats, number=args.iterations))
    new = statistics.median(timeit.repeat(lambda: [roads.surface_kind(*row) for row in WORK], repeat=args.repeats, number=args.iterations))
    result = {"scope": "synthetic metadata only; historical function uses current shared tag constants; no gameplay/FPS measurement",
              "python": platform.python_version(), "baseline": args.baseline, "workload": WORK,
              "callsPerRepeat": args.iterations * len(WORK), "repeats": args.repeats,
              "baselineMedianSeconds": old, "lookupMedianSeconds": new, "speedup": old / new}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
