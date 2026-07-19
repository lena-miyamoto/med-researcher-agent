# CLAUDE.md

Reusable medical research agent configuration and local Medical DB workflow (`./med-db/`).

## Command Invocation Contract (MANDATORY — most-violated rule)

> **Every repo Python tool must be run via `uv run <entry-point>` from the repository root.** Applies to Claude
> Code, Copilot, all subagents. No exceptions.

**Forbidden:** `python3`, `python`, shebang, or direct-path invocation of any `.agents/scripts/*.py` file.

**Required:** `uv run <entry-point>` from repo root — `med-db`, `med-db-lookup`,
`med-db-query`, `med-db-lookup-icd11`, `med-db-lookup-dsm5`, `med-db-download-icd11`, `med-db-setup-dsm5`,
`med-db-setup-therapy-methods`, `med-db-integrity-check`, `test`, `lint-md`.

- **`uv run test`** after editing any `*.py` file. No other test invocation. **Full suite must pass** — if any
  test fails, the change is not done. Evaluate each failure: either the logic changed and the test needs to
  adapt, or the failing test revealed a real regression. Do not ship code with known failures unless the
  user explicitly approves them. Spot-checking only the files you touched is insufficient — a refactor in one
  module can break distant tests through shared imports or CLI contract changes.
- **`uv run lint-md`** after batch-editing tracked `*.md` files. Never `uv run pymarkdownlnt` directly — only
  `uv run lint-md` (or `--fix`); wraps the linter with correct config (`.pymarkdown.yaml`).

## Source-of-Truth Architecture

- Skills: `.agents/skills/<name>/SKILL.md` owns procedure; `.github/skills` and `.claude/skills` are thin wrappers.
- Agents: `.agents/agents/<name>.md` owns behavior; `.github/agents` and `.claude/agents` are thin wrappers.
- Shared utilities: `.agents/scripts/utils.py`. Extract helpers used by ≥2 scripts; don't pre-emptively generalize.
- German prose: standard orthography (umlauts, `ß`), not ASCII substitutions, unless requested.

## Coding Style

### Naming — no cryptic abbreviations

Variable, function, and parameter names must be self-explanatory. **No abbreviations** — spell words out in full.

**Allowed exceptions (only these two):**

- `i` (or `index`) for the index variable in loops
- `tmp` or `temp` for a temporary value scoped to a single short block (≤ 10 lines)

Everything else must be written out: `entry` not `e`, `disorder` not `d`, `category` not `cat`,
`record_id` not `rid`, `column_map` not `col_map`, `file_handle` not `fh`, `keyword_search` not `ks`,
`code_lookup` not `cl`, `relative_path` not `rel`, `abstract_lines` not `ab_lines`, etc.

Domain terms that are universally understood acronyms in the field (PMID, DOI, ICD, DSM, PMC) may be
used as-is.

### Functional programming by default

Stick to functional programming. Prefer pure functions, immutable data, and composing smaller functions
over mutation and shared state.

**Classes only when you can articulate a concrete reason why they are necessary.**
"Feels cleaner," "organizes the code," or "would be nice" are not valid justifications. Valid reasons:
state machines that truly benefit from encapsulation, resource managers where `__enter__`/`__exit__`
are the ergonomic API, or integration with a framework that requires classes.

Unit tests are the explicit exception — test frameworks (pytest, unittest) require classes for test
grouping. That is a framework mandate, not a design choice.

When in doubt: use a module with functions, not a class.

## Architecture (Claude-Specific)

Skills that say "dispatch the X agent" → invoke via Agent tool with `subagent_type: "X"`. Agent name = `name`
field in the shared agent file's YAML frontmatter (e.g., `med-researcher`, `fitness-coach`, `dietologist`,
`psychotherapist`). Agents inherit `CLAUDE.md` — don't restate repo conventions in agent files.

## Medical DB (`./med-db/`)

Literature archive for medical, nutritional, or endometriosis research.

### Bootstrap after fresh checkout

- `./med-db/` is gitignored — **do not create it by hand.** Run any archival command (e.g.
  `uv run med-db --pmid 12345678 --validate`); tooling auto-creates the full tree
  (`searches/`, `papers/`, `fulltext/`, `guidelines/`, `web/`) plus `index.json`.
- Verify with `uv run med-db-integrity-check --med-db med-db`. An empty archive passes if all five directories
  and `index.json` exist.
- Query tools (`med-db-query`, `med-db-lookup`) are read-only — they report "directory not found"
  if `med-db/` is missing. Run an archival command first.

### Canonical Commands

See `.agents/agents/resources/med-db-commands.md` for the complete `uv run` parameter reference
covering all 9 entry points. Every command must be invoked as `uv run <entry-point>` from the repo root.

### Script Development

Read `.agents/scripts/DEVELOPER.md` before modifying any file in `.agents/scripts/`. Internal
directory structure and conventions — only relevant when extending the med-db script stack,
not when using `uv run` entry points.
