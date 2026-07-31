# CLAUDE.md

Reusable medical research agent configuration and local Medical DB workflow (`./med-db/`).

## Command Invocation Contract (MANDATORY — most-violated rule)

> **Every repo Python tool must be run via `uv run <entry-point>` from the repository root.** Applies to Claude
> Code, Copilot, all subagents. No exceptions.

**Forbidden — all of the following, without exception:**

- `python3`, `python`, `python3.11`, `python3.12`, or any other `python*` executable — whether as a shebang,
  direct script invocation, or `-c` inline code. This includes `python3 -c "..."`, `python -c "..."`, and any
  heredoc piped to a Python interpreter.
- `node -e "..."`, `perl -e "..."`, or any other inline-code execution that reads, parses, or manipulates
  files under `med-db/`.
- Direct filesystem access to `med-db/` contents: no `cat`, `jq`, `grep`, `sed`, `awk`, `python3 -c`, or
  any other tool that reads `med-db/index.json` or any file under `med-db/*/`. The `med-db/` directory is
  the exclusive domain of the `uv run med-db*` entry points. Read access is harmless in isolation but trains
  models to bypass the tool layer — the next step is direct writes, which corrupt the archive.

**Required:** `uv run <entry-point>` from repo root — `med-db`, `med-db-lookup`,
`med-db-query`, `med-db-lookup-icd11`, `med-db-lookup-dsm5`, `med-db-download-icd11`, `med-db-setup-dsm5`,
`med-db-setup-therapy-methods`, `med-db-integrity-check`, `test`, `lint-md`.

**Rationale:** `med-db/` data integrity depends on the tool layer. Direct file access — even read-only — erodes
the norm that the tools are the only interface. The `uv run` entry points validate, normalize, and cross-reference
on every operation. Bypassing them with inline Python or shell text processing introduces silent data corruption
risk. This rule is enforced at the settings.json level (`python*` commands are denied) and must also be followed
voluntarily by every agent and subagent.

- **`uv run test`** after editing any `*.py` file. No other test invocation. **Full suite must pass** — if any
  test fails, the change is not done. Evaluate each failure: either the logic changed and the test needs to
  adapt, or the failing test revealed a real regression. Do not ship code with known failures unless the
  user explicitly approves them. Spot-checking only the files you touched is insufficient — a refactor in one
  module can break distant tests through shared imports or CLI contract changes.
- **`uv run lint-md`** after batch-editing tracked `*.md` files. Never `uv run pymarkdownlnt` directly — only
  `uv run lint-md` (or `--fix`); wraps the linter with correct config (`.pymarkdown.yaml`).

## Branch and Worktree Discipline (MANDATORY)

- **Never create a git worktree or switch branches without asking the user first.** Worktrees and branch
  switches separate the working directory from the user's view — changes disappear from their perspective,
  causing confusion and lost work. This applies to `EnterWorktree`, `git worktree add`, `git checkout`,
  `git switch`, and any other mechanism that changes the working branch or directory.
- **Operate on the current branch.** If a task genuinely requires isolation, explain the reason and ask.
  Sub-agents that need isolation should use the default `cwd` — not a worktree — unless the user
  explicitly approves it.
- **If you entered a worktree without asking:** exit immediately (`ExitWorktree`, `action: remove`,
  `discard_changes: true`), re-apply any changes to the main branch, and apologize.

## Source-of-Truth Architecture

- Skills: `.claude/skills/<name>/SKILL.md` owns the full procedure; `.github/skills` are thin wrappers pointing to `.claude/`.
- Agents: `.claude/agents/<name>.md` owns the behavior; `.github/agents` are thin wrappers pointing to `.claude/`.
- Shared utilities: `.claude/scripts/utils.py`. Extract helpers used by ≥2 scripts; don't pre-emptively generalize.
- `.claude/` is the sole source of truth for all shared instruction files. No separate `.agents/` directory.
- German prose: standard orthography (umlauts, `ß`), not ASCII substitutions, unless requested.

## Coding Style

Read `.claude/agents/rules/coding-style.md` before writing or editing any Python file in this repo.
Naming (no abbreviations) and functional programming by default — applies to `.claude/scripts/` and
any other Python code.

## Medical DB (`./med-db/`)

Literature archive for medical, nutritional, or endometriosis research.

**All med-db access must go through the med-db skill** (`.claude/skills/med-db/SKILL.md`).
The skill owns the black-box rule, forbidden patterns, bootstrap, archival conventions,
command reference, diagnostic classification setup, and during-session usage rules.
Invoke via `Skill: "med-db"` or follow the skill file directly.

### Canonical Commands

See `.claude/agents/rules/med-db-commands.md` for the complete `uv run` parameter reference
covering all 9 entry points. Every command must be invoked as `uv run <entry-point>` from the repo root.

## Skill Procedure Completion (Mandatory)

When executing a skill that defines post-work steps — documentation, cleanup, compression, profile
updates — those steps are part of the procedure, not optional afterthoughts. A skill has not been
fully executed until every step in its SKILL.md has been completed. This is especially critical
for the therapy session skills (`start-therapy-session` delegates post-session documentation to
`end-therapy-session`, which must complete all five steps), but applies to any skill with a
multi-step procedure. Switching into an agentic persona
(e.g., therapist) does not relieve you of the obligation to complete the full procedure after that
persona's work is done.

## Script Development

Read `.claude/scripts/DEVELOPER.md` before modifying any file in `.claude/scripts/`. Internal
directory structure and conventions — only relevant when extending the med-db script stack,
not when using `uv run` entry points.

## Architecture (Claude-Specific)

Context engineering: `.claude/skills/optimize-repo/rules/context-engineering-best-practices.md` — authoritative standard for all instruction files in this repo.
Agent dispatch: invoke via Agent tool with `subagent_type: "<name>"` per YAML frontmatter `name` field.
Skills that say "dispatch the X agent" → invoke via Agent tool with `subagent_type: "X"`.

## Harness Entrypoints

- `CLAUDE.md` — Claude Code routing (this file)
- `.github/copilot-instructions.md` — GitHub Copilot routing
- `.github/agents/<name>.agent.md` — Copilot agent wrappers
- `.claude/agents/<name>.md` — Claude Code agents (source of truth)
- `.claude/skills/<name>/SKILL.md` — Skill procedures (source of truth)
- `.github/skills/<name>/SKILL.md` — Copilot skill wrappers
