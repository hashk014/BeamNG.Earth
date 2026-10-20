# Project maintenance guide

## Identity and communication

- Never sign commits, PRs, comments, documentation or other user-facing work as Codex. Do not add generated-by or AI co-author signature trailers.
- Use the repository's existing human Git identity; inspect it before committing. Preserve upstream authorship and license attribution.
- Use plain language and avoid em dashes in generated public text.

## Continuity

- This is the hashk014/BeamNG.Earth fork; upstream is TecnaGamer/BeamNG.Earth.
- Read `docs/maintenance/STATUS.md` and `docs/maintenance/ISSUES.md` before substantial work. Update them with completed changes, remaining work and exact validation limits.
- Keep upstream's roadmap and historical design notes. Fork maintenance tracking lives in `docs/maintenance/`.
- Refresh branches, PRs and issue discussions before choosing work. Issue state and release metadata are time-sensitive.
- Prefer focused commits and PRs. Integrate tested changes into the fork without rewriting published history. Preserve uncommitted work.
- Never close an upstream issue merely because this fork has a patch. State whether a change is implemented, automatically tested, tested in-game or released.

## Implementation

- Inspect the existing implementation before adding another system. Changes should generalize across locations and preserve deterministic generation.
- Improve performance only with a measurable cost or a clear removal of redundant work. Do not claim FPS gains from offline tests.
- Keep cache/download handling bounded and compatible with source and packaged launches.
- Keep UI settings editable and understandable, with persistent values and safe defaults.

## Verification

- Run focused regressions for the changed behavior and relevant neighboring modules. Record commands, outcomes and known baseline failures.
- Filesystem fault-injection tests must use isolated temporary roots. Before recursive deletion or moving, resolve the target and assert it stays inside its owned root.
- Windows tests must not accidentally use the real home, Steam installation, game user folder or shared staging directory.
- Read `docs/research/2026-10-20-session-file-recovery.md` for the existing Windows timing failures. Separate those from new failures.
- Compilation, mock-engine Lua tests, synthetic-server tests and CI are not BeamNG gameplay evidence. Document runtime checks still needed.
