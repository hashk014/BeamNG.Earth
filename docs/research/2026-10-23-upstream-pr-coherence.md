# Upstream pull request coherence audit

Checked on 23 October 2026 against live GitHub metadata and fetched refs:
`main` = `18f131c`, `dev` = `b15991e`.
This audit does not update, merge or close any upstream pull request.

| Contribution | Live state | Assessment |
| --- | --- | --- |
| [#34: Windows DuckDB installer](https://github.com/TecnaGamer/BeamNG.Earth/pull/34) | Merged 19 October | Merge `e769bac` is still an ancestor of current main. No resubmission needed. |
| [#35: European road traffic](https://github.com/TecnaGamer/BeamNG.Earth/pull/35) | Merged 19 October | Merge `2a5d94f` is still an ancestor of current main. No resubmission needed. |
| [#69: urban buildings and frontages](https://github.com/TecnaGamer/BeamNG.Earth/pull/69) | Open, conflicting | Still relevant in part, but needs source and test adaptation before merging. |
| [#187: shared road rendering](https://github.com/TecnaGamer/BeamNG.Earth/pull/187) | Open, mergeable | Coherent with current main and a synthetic merge with current dev. |

Neither open PR currently has review submissions, discussion comments or inline
review comments. Absence of feedback is not approval. The account has read access
to upstream; merging there remains the maintainer's decision.

## PR #69 needs an update

Head `220b16f` has two unique commits and is missing 224 commits from current
main. Its green Windows/Linux checks ran on 20 October against the earlier base.
`git merge-tree --write-tree --name-only upstream/main origin/codex/upstream-urban-buildings`
confirms content conflicts in:

- `server/blockworker.py`
- `server/buildings.py`
- `server/earthd.py`
- `server/roads.py`

This is not only a mechanical merge:

- Upstream removed the Python twins of native kernels in `02e2187`; current
  `fast.py` requires native kernels. The PR's workflow deliberately disables
  `earthfast` for its first test run. That validation strategy must be replaced
  with tests appropriate to the current native-required pipeline. The separate
  Python-only pier-placement fix no longer has its original production role.
- Buildings now have additional upstream behavior for service-road tunnels
  (`b330c56`, related to #60), narrow structures over roads (`8be6f5e`, #48),
  false footprints in road medians (`a3b5181`, #90), sub-0.1 m mapped areas
  (`5cfda31`) and fences near roads (`352a0b0`, #105). Preserve these protections
  while integrating grounded wings, courtyard holes and local passages.
- Road generation now supplies drawn-ground sampling, terrain quantization and
  terrain-paint parameters. Conflicted worker/server call sites must keep those
  inputs while adding frontage geometry consistently to both execution paths.
- PR [#167](https://github.com/TecnaGamer/BeamNG.Earth/pull/167) adds mapped building
  facade/roof colors and materials in overlapping attribute paths. It is an
  additional integration consideration, not evidence that #69 is wholly obsolete.

The current main still has whole-building road lifts and rectangularized pitched
roof wall footprints. Therefore the old PR should not simply be discarded as
already implemented. Its text claiming to be based on "current upstream main"
and its old fallback/native totals describe the earlier snapshot, not today's
merge readiness. A refreshed patch needs new native regressions and CI. Fork
integration results cannot automatically validate the separately published PR.

## PR #187 remains coherent

Head `99c295b` is based on current main `18f131c`; it merges without conflicts.
Its [upstream Windows/Linux CI](https://github.com/TecnaGamer/BeamNG.Earth/actions/runs/39993356422)
passes. The latest dev changes do not replace its `roads_in_ground` propagation
and compatibility checks.

`git merge-tree` also produces a clean synthetic merge with `dev` at `b15991e`.
That tree was archived and extracted to an owned temporary directory, with user
and config environment paths isolated. Tests used the existing development
Python dependencies and the native binaries included in the dev tree:

| Command | Windows result on dev plus #187 |
| --- | --- |
| `python -m unittest discover -s server/tests -p test_peerwork.py -v` | 20 passed |
| `python -m unittest discover -s server/tests -p test_blockworker.py -v` | 5 passed |
| `python -m unittest discover -s server/tests -p test_roads.py -v` | 59 passed |

Total: 84 tests passed. Logs and the machine-readable result are under
`dist/pr-coherence-audit/`. This is an offline compatibility check, not BeamNG
gameplay, multiplayer driving, performance evidence or a published dev integration.

## Next action

Prioritize refreshing #69 on current main, preserving published history and the
new upstream protections, then rerun relevant native generator/worker checks.
Keep #187 focused and await maintainer review unless upstream changes again.
