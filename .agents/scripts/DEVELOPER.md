---
description: >
  Internal med-db directory structure and conventions. Only relevant when extending the script stack
  in .agents/scripts/ — never when using uv run entry points.
---

# med-db Developer Notes

Internal directory structure and conventions. **Only relevant when extending the med-db script
stack.** Agents and skills must never manipulate `med-db/` directly — all access goes through the
`uv run` entry points documented in `../agents/resources/med-db-commands.md`.

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
  DOAJ / open-access directories → Google Scholar → Sci-Hub for paywalled papers.
- Flag evidence per `med-researcher` Evidence Hierarchy (`../agents/med-researcher.md`).
  Reusable write-ups → `tmp/`, not overwriting source briefs or archived records.
