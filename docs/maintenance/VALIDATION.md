# Validation ledger

## Reproduction commands

Use the repository's Python environment, for example `.venv/Scripts/python.exe`
on Windows or `.venv/bin/python` on Linux. Run commands from the repository root.

```sh
python -m unittest discover -s server/tests -p test_launcher_compat.py -v
python -m unittest discover -s server/tests -p test_staging.py -v
python -m unittest discover -s server/tests -p test_session_output.py -v
```

## Existing evidence

- Linux-runtime detection: seven tests passed locally and on Windows/Linux CI.
- Session-file recovery: 275 local tests passed, one stock-asset test was skipped,
  and three timing-sensitive server tests also fail on unchanged baseline code.
- The original issues remain open upstream. The fork's first two maintenance PRs
  have been merged into `preview`.

## Runtime handoff

The maintenance batch still needs actual BeamNG checks for saved UI settings,
coastline rendering, dry below-sea-level roads, material physics, long drives,
cache relocation on another physical volume and offline travel in a downloaded area.
Record exact version, location, regeneration steps and observed outcome for each check.
