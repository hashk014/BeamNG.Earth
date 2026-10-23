"""Refresh the public issue inventory and run reproducible offline maintenance checks."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TRACKING = ROOT / "docs" / "maintenance"
SUITES = {
    "quick": ["test_storage", "test_road_rendering", "test_launcher_compat", "test_staging", "test_session_output", "test_road_surfaces",
              "test_coastal_water", "test_area_prefetch"],
    "generators": ["test_heightmap", "test_roads", "test_surface", "test_roadmesh", "test_buildings",
                   "test_navgraph", "test_vegetation", "test_seatiles", "test_seacarve", "test_world_fidelity",
                   "test_european_traffic", "test_urban_frontages", "test_grading", "test_tunnels",
                   "test_fixed_road_profiles", "test_sables_crossings", "test_inland_water_bounds"],
    "server": ["test_server", "test_restart", "test_protocol_agreement"],
    "streaming": ["test_plancache", "test_cache", "test_cpupin", "test_dsmground", "test_detail",
                  "test_imagery.ReprojectionTest", "test_imagery.ChainTest", "test_imagery.ExportImageryTest",
                  "test_imagery.GutterTest", "test_imagery.ToneTest", "test_imagery.DdsTest",
                  "test_imagery.LatLonBboxTest"],  # synthetic sources only; excludes NetworkImageryTest
    "integration": ["test_approaches", "test_blockworker", "test_peerwork", "test_selfupdate", "test_updates",
                    "test_fast", "test_osmtags", "test_roadwidth", "test_terrainpatch", "test_pools", "test_budget",
                    "test_bridgetypes", "test_netfetch", "test_mapdata", "test_bc7", "test_colormatch", "test_polardem",
                    "test_protocol_agreement"],
}


def refresh(repo):
    path = TRACKING / "issues.json"
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"issues": []}
    reviews = {i["number"]: i.get("review", {}) for i in old["issues"]}
    raw = subprocess.check_output(["gh", "issue", "list", "--repo", repo, "--state", "all", "--limit", "1000",
                                   "--json", "number,title,state,url,updatedAt,labels"], text=True, encoding="utf-8")
    issues = sorted(json.loads(raw), key=lambda i: i["number"])
    for issue in issues:
        issue["labels"] = [label["name"] for label in issue["labels"]]
        issue["review"] = reviews.get(issue["number"], {
            "status": "needs-review" if issue["state"] == "OPEN" else "upstream-closed",
            "priority": "P2", "notes": "", "validation": "not assessed",
        })
    snapshot = {"repository": repo, "refreshedAt": datetime.now(timezone.utc).isoformat(), "issues": issues}
    TRACKING.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    render(snapshot)
    print(f"Reviewed inventory: {len(issues)} issues, {sum(i['state'] == 'OPEN' for i in issues)} open upstream")


def render(snapshot):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["# Issue inventory", "", f"Source: `{snapshot['repository']}`. Snapshot: {snapshot['refreshedAt']}.", "",
             "Upstream state is separate from the fork's assessment. Implemented changes still need the",
             "validation listed below. Refresh with `python tools/maintenance.py issues`; edit the `review`",
             "fields in `issues.json`, then use `python tools/maintenance.py render`. Refresh preserves reviews.", "",
             "| Issue | Upstream | Priority | Fork assessment | Validation / next action |",
             "| --- | --- | --- | --- | --- |"]
    for issue in snapshot["issues"]:
        r = issue["review"]
        title = cell(issue["title"])
        lines.append(f"| [#{issue['number']}]({issue['url']}) {title} | {issue['state']} | {cell(r['priority'])} | "
                     f"{cell(r['status'])}: {cell(r['notes'])} | {cell(r['validation'])} |")
    (TRACKING / "ISSUES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_tests(suite, report):
    sys.path.insert(0, str(ROOT / "server" / "tests"))
    sys.path.insert(0, str(ROOT))
    names = SUITES[suite]
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    data = {"suite": suite, "time": datetime.now(timezone.utc).isoformat(), "tests": result.testsRun,
            "failures": [t.id() for t, _ in result.failures], "errors": [t.id() for t, _ in result.errors],
            "skipped": [{"test": t.id(), "reason": reason} for t, reason in result.skipped],
            "scope": "offline Python tests; no game or FPS validation"}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return int(not result.wasSuccessful())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    issue = sub.add_parser("issues", help="refresh metadata only; preserves local review notes")
    issue.add_argument("--repo", default="TecnaGamer/BeamNG.Earth")
    sub.add_parser("render", help="render the inventory after editing issues.json review fields")
    test = sub.add_parser("test", help="run an offline Python suite")
    test.add_argument("--suite", choices=SUITES, default="quick")
    test.add_argument("--report", type=Path, default=ROOT / "dist" / "maintenance-validation.json")
    args = parser.parse_args()
    if args.command == "issues":
        refresh(args.repo)
    elif args.command == "render":
        render(json.loads((TRACKING / "issues.json").read_text(encoding="utf-8")))
    else:
        return run_tests(args.suite, args.report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
