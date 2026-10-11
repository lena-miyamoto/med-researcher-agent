# CLAUDE.md

## Command Contract

- Run all repo Python tools through `uv run ...` from repo root. Applies to Claude Code, Copilot, every subagent.
- No direct filesystem access to `med-db/` — exclusive domain of the `med-db` skill. Tool layer is only interface.
- After edits to any `*.md`: `uv run lint-md` (or `--fix`). **Never run `uv run rumdl` directly**.
- After edits to `*.md` under `./med-db/`: also `uv run lint-md --fix-source-md <PATH>` on changed file or containing archive dir.
- Canonical test command after editing any `*.py`: `uv run test`.
- Lint/format: `uv run lint` and `uv run format` (default `.claude/scripts` + `tests`; `--fix` to autofix; paths to override).
- Diagnose repo Python bugs through test harness: write regression test, run `uv run test`, fix, re-run. Never poke script internals with inline interpreter or throwaway script.

## Source Of Truth

- `.claude/` owns skills/agents/scripts; `.github/` holds thin wrappers only. Shared utilities: `.claude/scripts/utils.py` (extract helpers used by ≥2 scripts; don't pre-emptively generalize).
- Instruction files under `.claude/` must never reference `med-db` archive by file path or CLI command — `med-db/` gitignored, regenerated per checkout; references break on fresh machine. Refer to `med-db` skill by name only. Exception: `med-db` skill's own files (`.claude/skills/med-db/SKILL.md` and `.claude/agents/references/med-db-commands.md`) sole owners of those paths and commands. Never cite generated, ignored, or archive output paths as templates, exemplars, or sources of truth.
- Repo-owned content (DSM-5-TR and ICD-11 mental-health codes, therapy methodology guidelines, research briefs) lives in version-controlled files under `.claude/`; copyrighted or external content fetched via the `med-db` skill at first init.
- German prose: standard orthography (umlauts, `ß`), unless requested.

## Working Rules

- Make smallest local change that works. If patch context stale, re-read and retry.
- Scratch files ephemeral unless asked otherwise.
- **Never format by hand.** Run formatter: `uv run lint-md --fix` (`*.md`), `uv run format` (`*.py`).
- Read `.claude/agents/references/coding-style.md` before writing or editing Python.
- Read `.claude/scripts/DEVELOPER.md` before modifying `.claude/scripts/`.

## Commits

Commit messages follow Conventional Commits v1.0.0 — read
`.claude/references/conventional-commits.md` before composing one.

## Medical DB

**Only the `med-db` skill may touch `./med-db/` files directly.** Sole executor.

## Architecture (Claude-Specific)

Context engineering: `.claude/skills/optimize-repo/references/context-engineering-best-practices.md`. Agent dispatch: Agent tool with `subagent_type: "<name>"` per YAML `name`.
