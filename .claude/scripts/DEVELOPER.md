---
description: >
  Internal med-db directory structure and conventions. Development workflow commands for
  testing and linting. Only relevant when modifying files in .claude/scripts/ or any other
  Python code in the repo.
---

# med-db Developer Notes

Internal directory structure and conventions. **Only relevant when extending the med-db script
stack.** Agents and skills must never manipulate `med-db/` directly — all access goes through the
`uv run` entry points documented in `../agents/rules/med-db-commands.md`.

## Development Workflow

- **`uv run test`** after editing any `*.py` file. No other test invocation. **Full suite must pass** — if any
  test fails, the change is not done. Evaluate each failure: logic changed → test adapts; or real
  regression surfaced. Do not ship code with known failures unless the user explicitly approves them.
  Spot-checking touched files insufficient — refactor in one module can break distant tests through
  shared imports or CLI contract changes.
- **`uv run lint-md`** after batch-editing tracked `*.md` files. Never `uv run pymarkdownlnt` directly — only
  `uv run lint-md` (or `--fix`); wraps the linter with correct config (`.pymarkdown.yaml`).

## Directory Structure (`./med-db/`)

Lowercase kebab-case names. `./med-db/index.json` mandatory — every entry listed there.
Update `index.json` with every new or moved archive.

Required top-level categories:

- `searches/<topic-slug>/` — machine-readable JSON (`uncategorized/` when no topic specified).
- `papers/<topic-slug>/<identifier>-<title-slug>/` — `metadata.json` + `abstract.txt`. Never split across dirs.
- `fulltext/<topic-slug>/<identifier>-<title-slug>/` — `source.md` with YAML frontmatter + `metadata.json`.
- `guidelines/<topic-slug>/<title-slug>/` — `source.<lang>.md` with YAML frontmatter.
- `web/<topic-slug>/` — archived web pages or reproducible search definitions.

## Conventions

- **Paper standard:** `papers/`: `metadata.json` + `abstract.txt`. `fulltext/`: `source.md` + `metadata.json`.
  No intermediate artifacts.
- **YAML frontmatter** on every source file: `title`, `authors`, `source`, `source_url`, `access_date`
  (YYYY-MM-DD), `language`, `extraction_notes`.
- **Source priority:** `index.json` → `searches/` → fetch. PubMed (E-utilities), Europe PMC (REST API) →
  DOAJ / open-access directories → Google Scholar. Full-text fallback: follow the Sci-Hub policy in `.claude/agents/med-researcher.md`.
- Flag evidence per `med-researcher` Evidence Hierarchy (`../agents/med-researcher.md`).
  Reusable write-ups → `tmp/`, not overwriting source briefs or archived records.
- **No backwards-compat shims.** Scripts have no version history — the agent only knows the
  current interface. No deprecated aliases, no deprecation warnings, no transitional flags.
  If a flag name is wrong, change it. See `../agents/rules/coding-style.md`.
