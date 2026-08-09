# CLAUDE.md

Reusable medical research agent configuration and Medical DB workflow.

## MANDATORY Command Invocation Contract

> **Every repo Python tool must be run via `uv run <entry-point>` from the repository root.** Applies to Claude
> Code, Copilot, all subagents. No exceptions.

**Forbidden:** `python3`, `python`, `python*` — shebang, direct invocation, or `-c` inline code. `node -e`, `perl -e`, or any inline-code touching `med-db/`! No direct filesystem access to `med-db/` — directory is the exclusive domain of `med-db` skill!

**Rationale:** `med-db/` data integrity depends on the tool layer. Direct file access erodes the norm that the tools are the only interface.

## Source-of-Truth Architecture

- Skills: `.claude/skills/<name>/SKILL.md` owns full procedure; `.github/skills` are thin wrappers pointing to `.claude/`.
- Agents: `.claude/agents/<name>.md` owns behavior; `.github/agents` are thin wrappers pointing to `.claude/`.
- Shared utilities: `.claude/scripts/utils.py`. Extract helpers used by ≥2 scripts; don't pre-emptively generalize.
- `.claude/` is sole source of truth for all shared instruction files. No separate `.agents/` directory.
- German prose: standard orthography (umlauts, `ß`), not ASCII substitutions, unless requested.

## Medical DB (`./med-db/`)

Literature archive for medical, psychological, nutritional or exercise-related research.

**All med-db access must go through the med-db skill** (`.claude/skills/med-db/SKILL.md`).
Skill owns the black-box rule, forbidden patterns, bootstrap, archival conventions,
command reference, diagnostic classification setup, and during-session usage rules.
Invoke via `Skill: "med-db"` or follow the skill file directly.

## Script Development

Read `.claude/agents/rules/coding-style.md` before writing or editing any Python file.
No-abbreviation naming, functional programming by default — applies to `.claude/scripts/` and
any other Python code.

Read `.claude/scripts/DEVELOPER.md` before modifying files in `.claude/scripts/`. Internal
directory structure and conventions — only relevant when extending the med-db script stack,
not when using `uv run` entry points.

## Architecture (Claude-Specific)

Context engineering: `.claude/skills/optimize-repo/rules/context-engineering-best-practices.md` — authoritative standard for all instruction files.
Agent dispatch: invoke via Agent tool with `subagent_type: "<name>"` per YAML frontmatter `name` field.
