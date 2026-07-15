# AGENTS.md

This repo contains reusable medical research agent configuration and the local Medical DB workflow under `./med-db/`.

## Shared

### Command Invocation Contract (MANDATORY — most-violated rule)

> **Every repo Python tool must be run via `uv run <entry-point>` from the repository root.** This applies to Claude
> Code, Copilot, and every subagent. No exceptions.

**Forbidden — any of these will break:**

- `python3 .agents/scripts/med-db.py ...`
- `python .agents/scripts/med-db-query.py ...`
- `.agents/scripts/med-db-validate.py ...` (direct script invocation)
- `/home/.../med-researcher-agent/.agents/scripts/med-db.py ...` (absolute path)
- Any equivalent `python`, `python3`, shebang, or direct-path invocation

**Required — rewrite to:**

- `uv run med-db ...`
- `uv run med-db-validate ...`
- `uv run med-db-lookup ...`
- `uv run med-db-query ...`
- `uv run test ...`
- `uv run lint-md ...`

- **`uv run test`** after editing any `*.py` file. No other test invocation.
- **`uv run lint-md`** after batch-editing tracked `*.md` files. Never run `uv run pymarkdownlnt` directly — only
  `uv run lint-md` (or `--fix`), which wraps the linter with the correct config (`.pymarkdown.yaml`).

### Source-of-Truth Architecture

- Keep cross-harness skill procedure in `.agents/skills/<name>/SKILL.md`; `.github/skills` and `.claude/skills` should
stay as thin wrappers only.
- Keep cross-harness agent behavior in `.agents/agents/<name>.md`; `.github/agents` and `.claude/agents` should stay as
thin harness wrappers only.
- **Shared utilities go in `.agents/scripts/utils.py`.** Extract helpers duplicated across at least two scripts;
  don't pre-emptively generalize single-consumer code. Never copy-paste logic across scripts.
- For German prose, use standard German orthography by default: write umlauts and `ß` normally instead of ASCII
substitutions like `ae`, `oe`, `ue`, or `ss`, unless the user explicitly asks for ASCII or a technical constraint
requires it.

## Medical DB (`./med-db/`)

- Use for medical, nutritional, or endometriosis literature collection and evidence summaries.

### Bootstrap after fresh checkout

- `./med-db/` is gitignored — it does **not** ship with the repo. **Do not create it by hand.**
- Run any `uv run med-db ...` archival command (e.g. `uv run med-db --pmid 12345678 --validate`). The tooling
  auto-creates the full directory tree (`searches/`, `papers/`, `fulltext/`, `guidelines/`, `web/`) and
  `index.json` on the first run — no manual setup.
- Verify: `uv run med-db-validate --med-db med-db`. An empty archive (0 entries) passes if all five directories
  and `index.json` exist.
- Query tools (`med-db-query`, `med-db-lookup`) are read-only and do **not** bootstrap — they report "directory
  not found" if `med-db/` is missing. Run an archival command first.

### Canonical Commands

**Archival (`med-db`)**

| Operation | Command |
|---|---|
| PubMed search + archive | `uv run med-db --query '...' --archive-first N --validate` |
| Europe PMC search + archive | `uv run med-db --source europe-pmc --query '...' --archive-first N --validate` |
| Europe PMC single record | `uv run med-db --source europe-pmc --epmc-record MED:35350465 --validate` |
| Google Scholar search | `uv run med-db --source google-scholar --query '...' --search-slug '...' --validate` |
| Web discovery (DOAJ etc.) | `uv run med-db --source doaj --query '...' --search-slug '...' --validate` |
| PMID archival | `uv run med-db --pmid 12345678 --pmid 23456789 --validate` |

**Validation (`med-db-validate`)**

| Operation | Command |
|---|---|
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

- Both lookup and query scripts default to JSON output. Use `--format text` for human-readable output.
- Supported web discovery sources: `google-scholar`, `doaj`, `open-science-directory`, `free-medical-journals`,
  `openmd`, `trip-database`. Archive reproducible query pages under `web/`; use PubMed and Europe PMC for
  structured machine-readable records.
- **Full-text access fallback** — When a paper is paywalled, try Sci-Hub at `https://www.sci-hub.st/` via DOI.
  Prefer official open-access sources first. Papers before 2022 are more likely available; newer papers occasionally.

## Medical DB structure (`./med-db/`)

- Treat `./med-db` as the local literature archive.
- `./med-db/index.json` is mandatory. Every archived search, paper, full-text capture, guideline, and web source must be
listed there with title/identifier, canonical path, source, access date, and extraction notes. Update `index.json` in
the same change as every new or moved archive capture.
- Use lowercase kebab-case folder and file names. Prefer clear language suffixes for multi-language captures, e.g.
`source.en.md`, `source.de.md`.
- Required top-level archive categories:
  - `searches/<topic-slug>/` — saved literature search queries as machine-readable JSON. Use `uncategorized/` when
    no topic is specified.
  - `papers/<topic-slug>/<identifier>-<title-slug>/` — each folder must contain `metadata.json` and `abstract.txt`.
    Keep together; never split across flat directories.
  - `fulltext/<topic-slug>/<identifier>-<title-slug>/` — full-text via open access or Sci-Hub fallback. Each folder
    must contain `source.md` (YAML frontmatter with `title`, `authors`, `source`, `source_url`, `access_date`,
    `language`, `extraction_notes`) plus the original `metadata.json`.
  - `guidelines/<topic-slug>/<title-slug>/` — clinical practice guidelines. Each folder: `source.<lang>.md` with
    YAML frontmatter.
  - `web/<topic-slug>/` — archived web pages or reproducible search definition pages.
- **Paper archive standard** — `papers/`: `metadata.json` + `abstract.txt`. `fulltext/`: `source.md` + `metadata.json`.
  No intermediate download artifacts.
- **YAML frontmatter on every source file** — minimum fields: `title`, `authors`, `source`, `source_url`, `access_date`
  (YYYY-MM-DD), `language`, `extraction_notes`.
- **Source priority:** check `index.json` → `searches/` → fetch. External: PubMed (E-utilities), Europe PMC (REST
  API) for structured records → DOAJ, open-access directories for full-text → Google Scholar for broad searches →
  Sci-Hub for paywalled papers.
- Keep the medical evidence lens explicit and source-backed. Flag study types and evidence categories per the
  med-researcher agent's Evidence Hierarchy (`.agents/agents/med-researcher.md`).
- For reusable research write-ups, create new files under `tmp/` rather than overwriting the source brief or archived
records.
