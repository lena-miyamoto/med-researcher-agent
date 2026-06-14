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

If you find yourself about to type `python3` or an absolute path: stop, and rewrite to the matching `uv run` entry
point.

- **`uv run test`** after editing any `*.py` file. No other test invocation.
- **`uv run lint-md`** after batch-editing tracked `*.md` files. Config: `.pymarkdown.yaml`.
- **Never run `uv run pymarkdownlnt` directly.** Only `uv run lint-md` (or `uv run lint-md --fix`). The entry point
wraps the linter with the correct config and default paths — bypassing it breaks the contract.

### Source-of-Truth Architecture

- Keep cross-harness skill procedure in `.agents/skills/<name>/SKILL.md`; `.github/skills` and `.claude/skills` should
stay as thin wrappers only.
- Keep cross-harness agent behavior in `.agents/agents/<name>.md`; `.github/agents` and `.claude/agents` should stay as
thin harness wrappers only.
- **Shared utilities go in `.agents/scripts/utils.py`.** When a helper function, constant, or data structure is needed
by more than one script, put it in `utils.py` and import from there. Do _not_ copy-paste logic across scripts — code
drift between copies causes subtle, hard-to-catch bugs. Conversely, do _not_ pre-emptively extract something into
`utils.py` that is only consumed by a single script — the bar is _actual_ duplication across at least two scripts, not
speculative generalization.
- For German prose, use standard German orthography by default: write umlauts and `ß` normally instead of ASCII
substitutions like `ae`, `oe`, `ue`, or `ss`, unless the user explicitly asks for ASCII or a technical constraint
requires it.

## Medical DB (`./med-db/`)

- Use for medical, nutritional, or endometriosis literature collection and evidence summaries.

### Bootstrap after fresh checkout

- `./med-db/` is gitignored and does **not** ship with the repo. After `git clone`, the directory does not exist.
- **Do not create `med-db/` or its subdirectories by hand.** The tooling auto-creates the full directory tree
(`searches/`, `papers/`, `fulltext/`, `guidelines/`, `web/`) and an initial `index.json` on the first archival run. No
manual setup step is needed.
- To bootstrap: run any `uv run med-db ...` archival command (e.g. `uv run med-db --pmid 12345678 --validate`). The
tooling calls `ensure_med_db_structure()` and `sync_index()` automatically — every subdirectory and a valid `index.json`
are created as a side effect.
- To verify the bootstrap was correct: `uv run med-db-validate --med-db med-db`. An empty archive (0 entries per
category) passes validation as long as all five directories and `index.json` exist.
- Query tools (`med-db-query`, `med-db-lookup`) are read-only and do **not** bootstrap — they will report "directory not
found" if `med-db/` is missing. When you see that, run an archival command first.

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
`openmd`, `trip-database`.
- Use Google Scholar and the supported open-access web discovery sources in this workflow; archive reproducible query
pages when available, otherwise archive source landing pages with the saved query text under `web/`; use PubMed and
Europe PMC for structured machine-readable record archival.
- **Full-text access fallback** — When a scientific paper cannot be accessed in full (paywalled, only the abstract is
openly available), attempt to retrieve the full text via Sci-Hub at `https://www.sci-hub.st/` using the paper's DOI.
Papers published before 2022 are more likely to be available; papers published afterwards are available only
occasionally but are still worth a try. Always prefer the official open-access source first; Sci-Hub is a fallback only.

## Medical DB structure (`./med-db/`)

- Treat `./med-db` as the local literature archive. Create it if missing.
- `./med-db/index.json` is mandatory. Every archived search, paper, full-text capture, guideline, and web source must be
listed there with title/identifier, canonical path, source, access date, and extraction notes. Update `index.json` in
the same change as every new or moved archive capture.
- Do not store primary source captures as loose files directly under `./med-db/`. Use the category subfolders below.
- Use lowercase kebab-case folder and file names. Prefer clear language suffixes for multi-language captures, for
example `source.en.md`, `source.de.md`.
- Required top-level archive categories:
  - `searches/<topic-slug>/` for saved literature search queries as machine-readable JSON. Group by medical topic; use
  `uncategorized/` when no topic is specified.
  - `papers/<topic-slug>/<identifier>-<title-slug>/` for individual paper records. Each paper folder must contain
  `metadata.json` (structured record from PubMed or Europe PMC) and `abstract.txt` (plain-text abstract). Metadata and
  abstract must be kept together — never store them in separate flat directories.
  - `fulltext/<topic-slug>/<identifier>-<title-slug>/` for full-text papers retrieved via open access or Sci-Hub
  fallback. Each folder must contain `source.md` with YAML frontmatter (`title`, `authors`, `source`, `source_url`,
  `access_date`, `language`, `extraction_notes`) and full text, plus the original `metadata.json`.
  - `guidelines/<topic-slug>/<title-slug>/` for clinical practice guidelines. Each folder must contain
  `source.<lang>.md` with YAML frontmatter.
  - `web/<topic-slug>/` for archived web pages or reproducible search definition pages used in review.
- **Paper archive standard** — Every paper folder under `papers/` must contain exactly `metadata.json` and
`abstract.txt`. Every full-text capture under `fulltext/` must contain `source.md` with YAML frontmatter and
`metadata.json`. Do not leave intermediate download artifacts in the archive.
- **YAML frontmatter on every source file.** Every `source.<lang>.md` and every full-text capture must open with a YAML
frontmatter block containing at minimum: `title`, `authors`, `source`, `source_url`, `access_date` (YYYY-MM-DD),
`language`, and `extraction_notes`.
- Prefer the archive and existing searches before ad-hoc web browsing. Check `index.json` first, then `searches/`, then
fetch externally.
- **External source priority for literature:** PubMed (E-utilities) and Europe PMC (REST API) for structured
machine-readable records → DOAJ and open-access directories for full-text discovery → Google Scholar for broad searches
→ Sci-Hub for paywalled full-text fallback.
- Keep the medical evidence lens explicit and source-backed. Flag study types and evidence categories per the
  med-researcher agent's Evidence Hierarchy (`.agents/agents/med-researcher.md`).
- For reusable research write-ups, create new files under `tmp/` rather than overwriting the source brief or archived
records.
