# Maintenance status

Updated: 2026-10-20. Fork: [hashk014/BeamNG.Earth](https://github.com/hashk014/BeamNG.Earth).

## Current state

- `preview` contains the previous Europe Preview work plus the merged Linux-runtime detection and session-file recovery fixes (fork PRs #1 and #2).
- The next maintenance batch is developed on `codex/maintenance-october`.
- Git author is the existing human account `hashk014`. User-facing work must never carry a Codex signature or AI co-author trailer; see the root `AGENTS.md`.
- The issue inventory is recorded in [ISSUES.md](ISSUES.md). It distinguishes upstream state, implementation, automated checks and remaining game validation.

## Active work

1. Integrate upstream 1.5.3 compatibility work while preserving fork geometry and traffic.
2. Persist a custom download-cache location for source and packaged starts (#58, #61).
3. Add persisted controls for rocks and decorative props (#5, #14).
4. Improve road-surface fallback and consistency (#31).
5. Improve below-sea-level coastal water boundaries (#8, #53).
6. Provide a bounded, resumable area-download tool (#10, #28, #30).

## Verification and release boundaries

- Previous targeted CI: 34 filesystem/terrain checks and 7 launcher checks on both Windows and Linux.
- Previous extended Windows server suite has three reproducible baseline timing failures, detailed in `docs/research/2026-10-20-session-file-recovery.md`.
- No new standalone executable or public release has been produced for this maintenance batch.
- Engine-stub tests and synthetic server tests do not establish gameplay, rendering, multiplayer behavior or FPS gains.

## Next session

Read this page, `AGENTS.md`, `ISSUES.md` and `VALIDATION.md`. Refresh GitHub state,
inspect the working tree, then continue the highest-impact work with supported evidence.
