# Recover generated files after temporary-directory cleanup

Upstream report: [issue #27](https://github.com/TecnaGamer/BeamNG.Earth/issues/27).

The report names a missing `hm_11_0_0.png` under a session directory. Creating
that directory manually lets terrain generation resume. The server creates
its output directory at startup, but did not recover if that directory was
removed later. The staging helper also remembered a staging directory forever,
even if that directory no longer existed.

Generated files now use `staging.replace`: it first attempts the normal atomic
rename. If the source still exists and the destination is in the game's temp
tree, it recreates the destination directory and retries once. Heightmaps,
terrain, textures, meshes and JSON output use the same publishing helper.
The staging directory is also checked before reuse. When staging is unavailable,
the adjacent temporary-file fallback recreates its missing destination directory.

Errors involving missing source files, permissions or download-cache paths keep
their normal behavior. This recovery cannot restore already deleted tiles that
the server believes are loaded; after clearing an active game's cache, a server
restart or teleport may still be needed to regenerate those tiles.

## Validation

```sh
python -m unittest discover -s server/tests -p test_staging.py -v
python -m unittest discover -s server/tests -p test_heightmap.py -v
python -m unittest discover -s server/tests -p test_session_output.py -v
```

All 10 staging tests and 22 heightmap tests pass on Windows. The new tests
reproduce removed staging directories, missing session directories, the adjacent
fallback, and cleanup after a real PNG has been encoded but before it is renamed.
The PNG contents are verified after recovery. Error propagation is checked too.
Two protocol tests also pass: a synthetic server returns `anchor_ready` with
readable PNG and terrain files after removing the session directory, and after
removing an isolated staging directory between teleports. Both tests fail with
the original staging behavior. Their cleanup paths stay within their own
temporary directory.

The related mesh, CDAE, material-slot, surface, road-mesh, building, navigation,
imagery and vegetation suites also pass: 223 tests pass in these 11 suites
including staging and heightmaps; one additional stock-asset test is skipped
because the test runner cannot find a BeamNG.drive installation.

The extended Windows run covers 277 tests: 273 pass, one stock-asset test is
skipped, and three existing timing-sensitive tests fail:

- `test_server.DaeServerTest.test_session`
- `test_server.ServerTest.test_session`
- `test_server.DeleteQueueTest.test_rate_and_rebuilt_tile`

The two session tests still have retired files after their five-second cleanup
deadline. The deletion-rate test observes fewer callbacks than its two-second
threshold requires. All three failures were reproduced on the unchanged server
code in `preview`; they are not presented as passing. All 10 restart tests pass.
The two new protocol tests pass separately, bringing this patch's local total
to 275 passing tests, three baseline failures and one skip.

GitHub Actions runs the staging, heightmap and protocol tests on Windows and Linux.
These are filesystem and generator tests, with no in-game teleport validation.
The report does not establish which program removed the original directory.
