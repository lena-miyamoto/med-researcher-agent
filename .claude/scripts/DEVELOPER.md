---
description: >
  Internal med-db directory structure and conventions. Development workflow commands for
  testing and linting. Only relevant when modifying files in .claude/scripts/ or any other
  Python code in the repo.
---

# med-db Developer Notes

Internal archive conventions. **Only relevant when extending the med-db script
stack.** Agents and skills must never manipulate the archive directly — all access goes through the
`uv run` entry points documented in `../agents/references/med-db-commands.md`.

## Development Workflow

- **`uv run test`** after editing any `*.py` file. No other test invocation. **Full suite must pass** — if any
  test fails, the change is not done. Evaluate each failure: logic changed → test adapts; or real
  regression surfaced. Do not ship code with known failures unless the user explicitly approves them.
  Spot-checking touched files insufficient — refactor in one module can break distant tests through
  shared imports or CLI contract changes.
- **`uv run lint-md`** after batch-editing tracked `*.md` files. Never `uv run rumdl` directly — only
  `uv run lint-md` (or `--fix`); wraps the linter with correct config (`.rumdl.toml`).

## Directory Structure

The `med-db` skill owns the user-facing archive layout. This section documents it from the script
side — a deliberate, justified deviation, because the tool layer implements the layout and script
developers need it here.

Lowercase kebab-case names. `index.json` at the archive root is mandatory — every entry listed
there. Update it with every new or moved archive.

Required top-level categories:

- `searches/<topic-slug>/` — machine-readable JSON (`uncategorized/` when no topic specified).
- `papers/<topic-slug>/<identifier>-<title-slug>/` — `metadata.json` + `abstract.txt`. Never split across dirs.
- `fulltext/<topic-slug>/<identifier>-<title-slug>/` — `paper.pdf` + `source.md` with YAML frontmatter + `metadata.json`.
- `guidelines/<topic-slug>/<title-slug>/` — `source.<lang>.md` with YAML frontmatter.
- `web/<topic-slug>/` — archived web pages or reproducible search definitions.

## Conventions

- **Paper standard:** `papers/`: `metadata.json` + `abstract.txt`. `fulltext/`: `paper.pdf` + `source.md` +
  `metadata.json`. No intermediate artifacts.
- **YAML frontmatter** on every source file: `title`, `authors`, `source`, `source_url`, `access_date`
  (YYYY-MM-DD), `language`, `extraction_notes`.
- **Source priority:** `index.json` → `searches/` → fetch. PubMed (E-utilities), Europe PMC (REST API) →
  DOAJ / open-access directories → Google Scholar. Full-text acquisition: see the `fetch-paper` skill.
- Flag evidence per `med-researcher` Evidence Hierarchy (`../agents/med-researcher.md`).
  Reusable write-ups → `tmp/`, not overwriting source briefs or archived records.
- **No backwards-compat shims.** Scripts have no version history — the agent only knows the
  current interface. No deprecated aliases, no deprecation warnings, no transitional flags.
  If a flag name is wrong, change it. See `../agents/references/coding-style.md`.

## Entry Points

Single-module layout. `entrypoints.py` dynamically loads script modules via `importlib` and
dispatches to their `main()` functions. The `pyproject.toml` `[project.scripts]` table maps
command names to entry-point functions.

### CLI contract

Every script exposes an agent-friendly CLI through `main()`:

- `main()` returns an int exit code (0 success, non-zero failure) — never call `sys.exit()` inline.
- The `__main__` guard wraps `main()` with `utils.run_cli(main)` (KeyboardInterrupt → exit 130).
- Errors print to stderr; results print to stdout. No traceback should reach the agent.
- Read-only scripts (`med-db-query`, `med-db-lookup`, `med-db-lookup-icd11`, `med-db-term-lookup`,
  `med-db-term-wikipedia`, `med-db-term-mesh`, `med-db-integrity-check`) and the archival scripts
  offer machine-parseable output via `--format {json,text}`. `med-db` also accepts `--quiet` to
  print only the archived folder path; query and lookup scripts expose extraction flags
  (`--identifiers-only`, `--title-only`, `--abstract-only`, `--names-only`, `--locations-only`)
  for single-field plain-text output.

| Script                      | Entry point(s)                      | Purpose                                                                                    |
| --------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------ |
| `med-db.py`                 | `med-db`                            | Archival: PubMed/Europe PMC/web search, PMID, DOI, EPMC record. Index sync, entry removal. |
| `med-db-query.py`           | `med-db-query`                      | Read-only local archive queries.                                                           |
| `med-db-lookup.py`          | `med-db-lookup`                     | Read-only external lookups (PubMed, Europe PMC, DOI resolution).                           |
| `med-db-term.py`            | `med-db-term`                       | Term definition archival into `dictionary/`.                                               |
| `med-db-term-lookup.py`     | `med-db-term-lookup`                | Read-only local term definition lookup.                                                    |
| `med-db-term-wikipedia.py`  | `med-db-term-wikipedia`             | Read-only Wikipedia lead summary (Wikimedia REST API).                                     |
| `med-db-term-mesh.py`       | `med-db-term-mesh`                  | Read-only MeSH scope note lookup (NLM API).                                                |
| `med-db-lookup-icd11.py`    | `med-db-lookup-icd11`               | Read-only local ICD-11 MMS lookup.                                                         |
| `med-db-download-icd11.py`  | `med-db-download-icd11`             | Downloads ICD-11 MMS data from WHO CDN into `guidelines/`.                                 |
| `med-db-download-paper.py`  | `med-db-download-paper`             | Full-text paper download (PDF + extracted text) into `fulltext/`.                          |
| `med-db-integrity-check.py` | `med-db-integrity-check`            | Structural and data integrity validation.                                                  |
| `check-retraction.py`       | `check-retraction`                  | Read-only retraction status (Crossref + PubMed).                                           |
| `session-protocol.py`       | `session-protocol`                  | Extract a speaker-labelled session protocol from a Claude Code transcript.                 |
| `fetch-archive.py`          | `fetch-archive`                     | Headed-browser archive.is scrape for paywalled full text.                                  |
| `csv-util.py`               | `csv-util`                          | Inspect and transform CSV/TSV (stats, check, cut, head, drop-empty, dedupe, fill).         |
| `utils.py`                  | _(shared library)_                  | Network fetch, YAML frontmatter, slugify, atomic write, index lock, integrity checks.      |
| `entrypoints.py`            | `lint-md`, `lint`, `format`, `test` | CLI bridge: `lint-md` wraps rumdl; `lint`/`format` wrap ruff; `test` wraps pytest.         |
