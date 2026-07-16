# AGENTS.md

This repo contains reusable medical research agent configuration and the local Medical DB workflow under `./med-db/`.

## Shared

### Command Invocation Contract (MANDATORY — most-violated rule)

> **Every repo Python tool must be run via `uv run <entry-point>` from the repository root.** This applies to Claude
> Code, Copilot, and every subagent. No exceptions.

**Forbidden:** `python3`, `python`, shebang, or direct-path invocation of any `.agents/scripts/*.py` file.

**Required:** `uv run <entry-point>` from repo root — `med-db`, `med-db-validate`, `med-db-lookup`,
`med-db-query`, `med-db-lookup-icd11`, `med-db-lookup-dsm5`, `med-db-download-icd11`, `med-db-setup-dsm5`,
`med-db-setup-therapy-methods`, `test`, `lint-md`.

- **`uv run test`** after editing any `*.py` file. No other test invocation.
- **`uv run lint-md`** after batch-editing tracked `*.md` files. Never `uv run pymarkdownlnt` directly — only
  `uv run lint-md` (or `--fix`), which wraps the linter with correct config (`.pymarkdown.yaml`).

### Source-of-Truth Architecture

- Skills: `.agents/skills/<name>/SKILL.md` owns procedure; `.github/skills` and `.claude/skills` are thin wrappers.
- Agents: `.agents/agents/<name>.md` owns behavior; `.github/agents` and `.claude/agents` are thin wrappers.
- Shared utilities: `.agents/scripts/utils.py`. Extract helpers used by ≥2 scripts; don't pre-emptively generalize.
- German prose: standard orthography (umlauts, `ß`), not ASCII substitutions, unless explicitly requested.

## Medical DB (`./med-db/`)

Literature archive for medical, nutritional, or endometriosis research.

### Bootstrap after fresh checkout

- `./med-db/` is gitignored — **do not create it by hand.** Run any archival command (e.g.
  `uv run med-db --pmid 12345678 --validate`) and the tooling auto-creates the full tree
  (`searches/`, `papers/`, `fulltext/`, `guidelines/`, `web/`) plus `index.json`.
- Verify with `uv run med-db-validate --med-db med-db`. An empty archive passes if all five directories
  and `index.json` exist.
- Query tools (`med-db-query`, `med-db-lookup`) are read-only — they report "directory not found"
  if `med-db/` is missing. Run an archival command first.

### Canonical Commands

**Archival (`med-db`) and Validation (`med-db-validate`)**

| Operation | Command |
|---|---|
| PubMed search + archive | `uv run med-db --query '...' --archive-first N --validate` |
| Europe PMC search + archive | `uv run med-db --source europe-pmc --query '...' --archive-first N --validate` |
| Europe PMC single record | `uv run med-db --source europe-pmc --epmc-record MED:35350465 --validate` |
| Google Scholar search | `uv run med-db --source google-scholar --query '...' --search-slug '...' --validate` |
| Web discovery (DOAJ etc.) | `uv run med-db --source doaj --query '...' --search-slug '...' --validate` |
| PMID archival | `uv run med-db --pmid 12345678 --pmid 23456789 --validate` |
| Validate archive | `uv run med-db-validate --med-db med-db` |

**Lookup (`med-db-lookup`)**

| Operation | Command |
|---|---|
| PMID lookup | `uv run med-db-lookup --pmid 12345678` |
| Batch PMID lookup | `uv run med-db-lookup --pmid 12345678 --pmid 23456789` |
| Europe PMC record lookup | `uv run med-db-lookup --epmc-record MED:35350465` |
| DOI resolution | `uv run med-db-lookup --doi 10.1000/xyz` |

**Query (`med-db-query`)**

| Operation | Command |
|---|---|
| List topics | `uv run med-db-query --list-topics` |
| List topic papers | `uv run med-db-query --topic adhd` |
| Check PMID archived | `uv run med-db-query --check-pmid 12345678` |
| Check EPMC archived | `uv run med-db-query --check-epmc MED:35350465` |
| Keyword search | `uv run med-db-query --search-keyword lisdexamfetamine` |
| Topic-scoped keyword search | `uv run med-db-query --search-keyword lisdexamfetamine --search-topic adhd` |
| Extract PMIDs from search JSON | `uv run med-db-query --pmids-from-search searches/adhd/pubmed-search.json` |
| Read paper metadata | `uv run med-db-query --read-metadata papers/adhd/pmid-12345-title-slug` |

### Diagnostic Classification (Setup and Lookup)

**Setup** (first use per system; local, no network after setup)

| Operation | Command |
|---|---|
| Download ICD-11 (EN + DE) | `uv run med-db-download-icd11 --release 2026-01` |
| Download ICD-11 (EN only) | `uv run med-db-download-icd11 --release 2026-01 --language en` |
| Verify ICD-11 present | `uv run med-db-download-icd11 --release 2026-01 --language en --verify` |
| Setup DSM-5-TR | `uv run med-db-setup-dsm5` |
| Verify DSM-5-TR present | `uv run med-db-setup-dsm5 --verify-only` |
| Setup therapy methodology guidelines | `uv run med-db-setup-therapy-methods` |
| Verify therapy methodology guidelines | `uv run med-db-setup-therapy-methods --verify-only` |

**Lookup** (local, no network)

| Operation | Command |
|---|---|
| ICD-11 code (EN) | `uv run med-db-lookup-icd11 --code 6A02` |
| ICD-11 code (DE) | `uv run med-db-lookup-icd11 --code 6A02 --language de` |
| ICD-11 keyword search (DE) | `uv run med-db-lookup-icd11 --keyword "Aufmerksamkeit" --language de` |
| ICD-10 → ICD-11 | `uv run med-db-lookup-icd11 --icd10-code F90.0` |
| ICD-11 → ICD-10 | `uv run med-db-lookup-icd11 --icd11-to-icd10 6A02` |
| DSM-5-TR code | `uv run med-db-lookup-dsm5 --code F90.2` |
| DSM-5-TR keyword search | `uv run med-db-lookup-dsm5 --keyword "bipolar"` |
| DSM-5-TR category search | `uv run med-db-lookup-dsm5 --category "personality"` |
| DSM-5-TR list categories | `uv run med-db-lookup-dsm5 --list-categories` |

- Default output is JSON. Use `--format text` for human-readable output.
- Supported web discovery sources: `google-scholar`, `doaj`, `open-science-directory`, `free-medical-journals`,
  `openmd`, `trip-database`. Archive reproducible query pages under `web/`; prefer PubMed and Europe PMC for
  structured records.
- **Full-text fallback** — When paywalled, try Sci-Hub at `https://www.sci-hub.st/` via DOI. Prefer official
  open-access sources first. Papers before 2022 are more likely available.

## Medical DB structure (`./med-db/`)

Use lowercase kebab-case names. `./med-db/index.json` is mandatory — every entry must be listed there.
Update `index.json` in the same change as every new or moved archive.

Required top-level categories:

- `searches/<topic-slug>/` — machine-readable JSON (`uncategorized/` when no topic specified).
- `papers/<topic-slug>/<identifier>-<title-slug>/` — `metadata.json` + `abstract.txt`. Never split across dirs.
- `fulltext/<topic-slug>/<identifier>-<title-slug>/` — `source.md` with YAML frontmatter + `metadata.json`.
- `guidelines/<topic-slug>/<title-slug>/` — `source.<lang>.md` with YAML frontmatter.
- `web/<topic-slug>/` — archived web pages or reproducible search definition pages.
- **Paper standard:** `papers/`: `metadata.json` + `abstract.txt`. `fulltext/`: `source.md` + `metadata.json`.
  No intermediate artifacts.
- **YAML frontmatter** on every source file: `title`, `authors`, `source`, `source_url`, `access_date`
  (YYYY-MM-DD), `language`, `extraction_notes`.
- **Source priority:** `index.json` → `searches/` → fetch. PubMed (E-utilities), Europe PMC (REST API) →
  DOAJ / open-access directories → Google Scholar → Sci-Hub for paywalled papers.
- Flag evidence per `med-researcher` Evidence Hierarchy (`.agents/agents/med-researcher.md`).
  Reusable write-ups → `tmp/`, not overwriting source briefs or archived records.
