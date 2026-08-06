# CLAUDE.md

Reusable medical research agent configuration and local Medical DB workflow (`./med-db/`).

## Command Invocation Contract (MANDATORY — most-violated rule)

> **Every repo Python tool must be run via `uv run <entry-point>` from the repository root.** Applies to Claude
> Code, Copilot, all subagents. No exceptions.

**Forbidden:** `python3`, `python`, or any `python*` executable — shebang, direct invocation, or `-c`
inline code. `node -e`, `perl -e`, or any inline-code execution touching `med-db/`. Direct filesystem
access to `med-db/`: no `cat`, `jq`, `grep`, `sed`, `awk` on `med-db/index.json` or `med-db/*/`. The
`med-db/` directory is the exclusive domain of `uv run med-db*` entry points — read access trains
models to bypass the tool layer; the next step is direct writes, which corrupt the archive.

**Required:** `uv run <entry-point>` from repo root — `med-db`, `med-db-lookup`,
`med-db-query`, `med-db-lookup-icd11`, `med-db-lookup-dsm5`, `med-db-download-icd11`, `med-db-setup-dsm5`,
`med-db-setup-therapy-methods`, `med-db-integrity-check`, `test`, `lint-md`.

**Rationale:** `med-db/` data integrity depends on the tool layer. Direct file access erodes the norm
that the tools are the only interface. See `.claude/skills/med-db/SKILL.md` for the black-box rule
and command reference.

- **`uv run test`** after editing any `*.py` file. No other test invocation. **Full suite must pass** — if any
  test fails, the change is not done. Evaluate each failure: either the logic changed and the test needs to
  adapt, or the failing test revealed a real regression. Do not ship code with known failures unless the
  user explicitly approves them. Spot-checking only the files you touched is insufficient — a refactor in one
  module can break distant tests through shared imports or CLI contract changes.
- **`uv run lint-md`** after batch-editing tracked `*.md` files. Never `uv run pymarkdownlnt` directly — only
  `uv run lint-md` (or `--fix`); wraps the linter with correct config (`.pymarkdown.yaml`).

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
covering all 11 entry points. Every command must be invoked as `uv run <entry-point>` from the repo root.

## Script Development

Read `.claude/scripts/DEVELOPER.md` before modifying any file in `.claude/scripts/`. Internal
directory structure and conventions — only relevant when extending the med-db script stack,
not when using `uv run` entry points.

## Architecture (Claude-Specific)

Context engineering: `.claude/skills/optimize-repo/rules/context-engineering-best-practices.md` — authoritative standard for all instruction files in this repo.
Agent dispatch: invoke via Agent tool with `subagent_type: "<name>"` per YAML frontmatter `name` field.

## Harness Entrypoints

- `CLAUDE.md` — Claude Code routing (this file); `.github/copilot-instructions.md` — GitHub Copilot routing
- `.claude/agents/<name>.md` — agents (source of truth); `.github/agents/<name>.agent.md` — Copilot wrappers
- `.claude/skills/<name>/SKILL.md` — skills (source of truth); `.github/skills/<name>/SKILL.md` — Copilot wrappers
