# Download-cache location

Issues: [#58](https://github.com/TecnaGamer/BeamNG.Earth/issues/58),
[#61](https://github.com/TecnaGamer/BeamNG.Earth/issues/61).

Choose a folder once. The source starter, launcher and companion server share the
saved choice, including later starts of a standalone build containing this change.

```powershell
python launcher.py --cache-dir "D:\BeamNG-Earth-cache" --print-cache-dir
python start.py --print-cache-dir
```

For a future standalone executable, replace `python launcher.py` with that
executable's filename. Preview 1 does not contain these commands.

```sh
python launcher.py --cache-dir /mnt/games/beamng-earth-cache --print-cache-dir
python launcher.py --reset-cache-dir --print-cache-dir
```

The selection is stored in `%LOCALAPPDATA%/beamng-earth/storage.json` on Windows
or `$XDG_CONFIG_HOME/beamng-earth/storage.json` on Linux (`~/.config` by default).
`BNGEARTH_CACHE_DIR` overrides a saved selection. An explicit launcher `--cache-dir`
sets both the saved preference and the path for that start. The original default
is `~/.cache/beamng-earth`.

The server's own `--cache-dir` remains a per-run override. Options after the
launcher's `--` also override the server for that run, without changing the saved
choice. The launcher prints the saved/environment selection; the server's startup
message shows any override passed after `--`.

Selecting or resetting a path does not move or delete existing cache files. To
reuse old downloads, stop the server and copy the old cache contents into the
new folder before playing. Generated session files remain in the game's user
folder because BeamNG loads them through its virtual filesystem. Launcher logs
remain in their existing location.

Validation: `python -m unittest discover -s server/tests -p test_storage.py -v`
checks saved values across real Python processes, both entry paths, environment
precedence, reset, malformed configuration and atomic-write failure. A different
physical drive and a rebuilt standalone executable still need runtime testing.
