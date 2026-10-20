# Native Steam runtime detection

Upstream report: [issue #56](https://github.com/TecnaGamer/BeamNG.Earth/issues/56).

Steam Linux Runtime runs the native Linux game. Its compatibility setting was
treated as Proton, so a leftover Windows user folder received the mod instead
of the native folder. Detection now recognizes Proton names, including GE-Proton,
and treats Steam Linux Runtime as native. A known native setting also takes
precedence over old Proton logs before the native user folder exists.

Missing Steam configuration still falls back to the most recently used build;
explicit `--native` and `--proton` continue to override automatic detection.

## Validation

Run from the repository root:

```sh
python -m unittest discover -s server/tests -p test_launcher_compat.py -v
```

Seven tests cover native runtime names, a first native start with a stale
Proton folder, existing native folders, Proton variants, missing configuration,
another application's setting, and explicit build overrides. The regressions
fail on the original launcher and pass with the fix.

The tests use temporary Steam configuration and user folders on Windows. They
do not launch Steam, a Linux AppImage, Proton, or BeamNG.drive. The existing
`test_launcher_linux.py` suite has Windows-specific baseline failures because
its Linux fixtures use the host platform and home-directory behavior; those
failures predate this change.
