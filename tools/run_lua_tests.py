"""Run engine-stub Lua tests with LuaJIT, including hosts without a luajit executable.

Install requirements-dev.txt, then: python tools/run_lua_tests.py test_trees.lua test_settings.lua
Every test has its own process because the Lua tests call os.exit(). No game is started.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "mod" / "tests"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tests", nargs="*", help="test filenames (default: all test_*.lua)")
    parser.add_argument("--child", help=argparse.SUPPRESS)
    parser.add_argument("--report", type=Path, default=ROOT / "dist" / "lua-validation.json")
    args = parser.parse_args()
    if args.child:
        from lupa.luajit21 import LuaRuntime
        path = TESTS / args.child
        if path.parent.resolve() != TESTS.resolve():
            parser.error("test must be in mod/tests")
        lua = LuaRuntime()
        lua.globals().arg = lua.table_from({0: path.name})
        lua.globals().BNGE_TEST_LUA_FILES = lua.table_from(
            [str(p) for p in sorted((ROOT / "mod" / "beamng_earth" / "lua").rglob("*.lua"))])
        lua.execute(path.read_text(encoding="utf-8"))
        return 0
    try:
        import lupa.luajit21
    except ImportError:
        parser.error("install the test dependencies first: python -m pip install -r requirements-dev.txt")
    names = args.tests or [p.name for p in sorted(TESTS.glob("test_*.lua"))]
    failed, records = [], []
    for name in names:
        print("LuaJIT: " + name, flush=True)
        try:
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child", name],
                                    cwd=TESTS, timeout=120, capture_output=True, text=True, errors="replace")
            print(result.stdout, end="", flush=True)
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
            passed = result.returncode == 0
            match = re.search(r"\b(\d+) passed, (\d+) failed", result.stdout)
            records.append({"file": name, "ok": passed, "checksPassed": int(match[1]) if match else None,
                            "checksFailed": int(match[2]) if match else None})
        except subprocess.TimeoutExpired:
            passed = False
            records.append({"file": name, "ok": False, "error": "timeout"})
        if not passed:
            failed.append(name)
    print(f"Lua files: {len(names) - len(failed)} passed, {len(failed)} failed", flush=True)
    if failed:
        print("Failed: " + ", ".join(failed))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({"scope": "LuaJIT engine-stub tests; no gameplay or FPS validation",
                                      "files": records}, indent=2) + "\n", encoding="utf-8")
    return int(bool(failed))


if __name__ == "__main__":
    sys.exit(main())
