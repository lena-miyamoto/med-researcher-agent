---
description: >
  Complete `uv run` parameter reference covering all med-db entry points. Command tables for
  archival, lookup, query, ICD-11, DSM-5-TR, therapy methods, and integrity check operations.
---

# med-db Command Reference

`uv run <entry-point> …` from repo root. Default JSON; `--format text` for readable output.

Direct Python invocation **forbidden**. Access only through `uv run` entry points — validation, indexing, integrity checks always applied.

Web discovery sources: `google-scholar`, `doaj`, `open-science-directory`,
`free-medical-journals`, `openmd`, `trip-database`. Prefer PubMed/Europe PMC for structured records.

Full-text acquisition: follow the `fetch-paper` skill.

`med-db-integrity-check` runs after every archival, setup, or download. Errors block completion (exit code 1) — fix immediately.

---

## `uv run med-db` — Archival (PubMed, Europe PMC, web discovery)

Archive searches, PMIDs, DOIs, EPMC records into local `med-db/` tree. Always include
`--topic` (human-readable name, e.g. `adhd`). Integrity check runs on completion.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--source` | choice | `pubmed` | Primary source: `pubmed`, `europe-pmc`, `google-scholar`, `doaj`, `open-science-directory`, `free-medical-journals`, `openmd`, `trip-database` |
| `--query` | str | — | Search query for selected source |
| `--search-slug` | str | — | Optional slug for saved search file |
| `--topic` | str | `uncategorized` | Medical topic for grouping output (e.g. `endometriosis`, `adhd`). Kebab-case slug auto-derived |
| `--topic-slug` | str | — | Explicit kebab-case slug; overrides `--topic` |
| `--pmid` | str[] | `[]` | PMID to archive; repeatable (`--pmid 1 --pmid 2`) |
| `--epmc-record` | str[] | `[]` | Europe PMC record as `SOURCE:ID`; repeatable |
| `--doi` | str[] | `[]` | DOI to resolve and archive; repeatable. Tries PubMed, then Europe PMC, then Crossref metadata (covers DOIs indexed in neither, e.g. APA journals) |
| `--remove-pmid` | str[] | `[]` | Remove archived paper folders by PMID; repeatable. Cannot combine with archival options |
| `--remove-epmc-record` | str[] | `[]` | Remove archived paper folders by Europe PMC record as `SOURCE:ID`; repeatable. Cannot combine with archival options |
| `--archive-first` | int | `0` | Also archive first N PMIDs returned by `--query` |
| `--retmax` | int | `20` | Machine-readable hits to request for archived search JSON |
| `--med-db` | str | `med-db` | Target `med-db/` directory path |
| `--email` | str | — | Contact email for NCBI E-utilities |
| `--delay` | float | `0.34` | Delay between PMID fetches (seconds) |
| `--migrate` | flag | off | Migrate flat `med-db/` to topic-based per-paper folders |
| `--migrate-dry-run` | flag | off | Preview `--migrate` without copying files |
| `--force` | flag | off | Re-fetch and overwrite papers already archived (useful after transient fetch failures) |
| `--format` | choice | `text` | Output format: `json` or `text` |
| `--quiet` | flag | off | Output only created folder paths, one per line |

---

## `uv run med-db-integrity-check` — Validation

Runs after every archival, setup, or download. Errors block (exit code 1) — fix immediately.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--med-db` | str | `med-db` | Target `med-db/` directory path |
| `--format` | choice | `text` | Output format: `json` or `text` |

---

## `uv run med-db-lookup` — External Lookup (read-only, no archival)

Query PubMed, Europe PMC, or resolve DOIs. At least one of `--pmid`, `--epmc-record`, or `--doi` required.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--pmid` | str[] | `[]` | PubMed ID to look up; repeatable |
| `--epmc-record` | str[] | `[]` | Europe PMC record as `SOURCE:ID`; repeatable |
| `--doi` | str[] | `[]` | DOI to resolve; repeatable |
| `--format` | choice | `json` | Output format: `json` or `text` |
| `--email` | str | — | Contact email for NCBI E-utilities |
| `--delay` | float | `0.34` | Delay between individual fetches (seconds) |

---

## `uv run med-db-query` — Local Archive Query (read-only)

Query local `med-db/` archive. Exactly one operation flag required (mutually exclusive group).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--med-db` | str | `med-db` | Path to `med-db/` root directory |
| `--format` | choice | `json` | Output format: `json` or `text` |

**Operation (mutually exclusive — pick exactly one):**

| Flag | Type | Description |
|---|---|---|
| `--list-topics` | flag | List all topics with paper and search counts |
| `--topic` | str | List all papers under a topic |
| `--check-pmid` | str | Check if a PMID is already archived |
| `--check-epmc` | str | Check if a Europe PMC record (`SOURCE:ID`) is archived |
| `--pmids-from-search` | str | Extract PMID list from search JSON file path |
| `--read-metadata` | str | Read metadata from a paper directory path |
| `--search-keyword` | str | Search papers by keyword (case-insensitive) |
| `--recent` | int | List N most recently added papers |
| `--search-searches` | str | Search archived search queries by keyword (case-insensitive) |

**Modifiers (usable with certain operations):**

| Parameter | Type | Default | Applies to | Description |
|---|---|---|---|---|
| `--search-topic` | str | — | `--search-keyword`, `--search-searches` | Restrict search to a specific topic |
| `--show-abstract` | flag | off | `--read-metadata` | Include abstract text in output |
| `--summary` | flag | off | `--search-keyword` | Compact output (identifiers + titles only) |
| `--identifiers-only` | flag | off | `--topic`, `--search-keyword`, `--recent`, `--pmids-from-search`, `--search-searches` | Output identifiers/paths/PMIDs one per line |
| `--title-only` | flag | off | `--read-metadata` | Output only the title text |
| `--abstract-only` | flag | off | `--read-metadata` | Output only the abstract text (auto-loads abstract) |
| `--names-only` | flag | off | `--list-topics` | Output topic names only, one per line |
| `--locations-only` | flag | off | `--check-pmid`, `--check-epmc` | Output archive location paths only, one per line |

---

## `uv run med-db-term` — Term Definition Archive (write)

Archive a medical term definition into `med-db/dictionary/<term-slug>/`. Used by the `define-terms`
skill. No network calls — the caller supplies the definition and source. Integrity check runs on
completion.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--term` | str | required | German term to archive (e.g. `Hypertonie`) |
| `--english` | str | `""` | English translation of the term |
| `--definition` | str | required | German definition text |
| `--source-type` | choice | `other` | Source kind: `icd11`, `dsm5`, `mesh`, `who`, `society`, `dictionary`, `literature`, `web`, `other` |
| `--source-ref` | str | `""` | Source reference: classification code, URL, or PMID/DOI |
| `--source-url` | str | `""` | Canonical source URL; falls back to `--source-ref` when it is a URL |
| `--extraction-notes` | str | `""` | Provenance note recorded in `source.md` frontmatter and `metadata.json` (e.g. `non-authoritative community usage`) |
| `--med-db` | str | `med-db` | Target `med-db/` directory path |
| `--format` | choice | `text` | Output format: `json` or `text` |

---

## `uv run med-db-term-lookup` — Term Definition Lookup (local, read-only)

Read archived term definitions from `med-db/dictionary/`. At least one of `--term`, `--keyword`, or
`--list` required. No network calls.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--term` | str | — | German term to look up (case-insensitive or by slug) |
| `--keyword` | str | — | Search term, english, definition, and source_ref by keyword |
| `--list` | flag | off | List all archived terms |
| `--limit` | int | `50` | Max keyword search results |
| `--med-db` | str | `med-db` | Target `med-db/` directory path |
| `--format` | choice | `json` | Output format: `json` or `text` |
| `--definition-only` | flag | off | Output only the definition text (for `--term`) |
| `--english-only` | flag | off | Output only the English term (for `--term`) |

---

## `uv run med-db-term-wikipedia` — Wikipedia Lead Summary (read-only)

Fetch a Wikipedia article's lead section via the Wikimedia REST API. Used by the `define-terms`
skill as the stage-5 fallback source. Returns the plain-text `extract`, the Wikidata `description`,
and the canonical article URL. No archival — archive the passage with `med-db-term` afterward.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--title` | str | required | Wikipedia article title (English), spaces or underscores (e.g. `Artificial intelligence`) |
| `--lang` | str | `en` | Wikipedia language edition |
| `--format` | choice | `json` | Output format: `json` or `text` |

---

## `uv run med-db-term-mesh` — MeSH Scope Note (read-only)

Fetch a MeSH descriptor's scope note via the NLM `id.nlm.nih.gov` API. Used by the `define-terms`
skill as a stage-3 authoritative source. Returns the descriptor ID, preferred label, and scope note.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--term` | str | required | MeSH term to look up (e.g. `Executive Function`) |
| `--format` | choice | `json` | Output format: `json` or `text` |

---

## `uv run med-db-download-icd11` — ICD-11 Setup

Download ICD-11 MMS data from WHO CDN into `med-db/`. Integrity check runs on completion.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--release` | str | `2026-01` | ICD-11 release identifier |
| `--language` | str[] | `[]` | Language code to download; repeatable. Defaults to `en` + `de` for 2026-01, `en` only for earlier releases |
| `--force` | flag | off | Re-download even if files already exist |
| `--verify` | bool | `true` | Run smoke test after download. Use `--no-verify` to skip |

---

## `uv run med-db-download-paper` — Full-Text Download

Download a paper's full text (PDF + extracted source text) into `med-db/fulltext/`. See the `fetch-paper` skill for the procedure and source policy. Integrity check runs
on completion.

At least one input required: `--reference`, `--title`, or `--url`. `--topic` is required.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--reference` | str[] | `[]` | Paper reference (DOI, PMID, arXiv ID, Europe PMC `SOURCE:ID`, or URL); repeatable |
| `--title` | str | — | Paper title for title search |
| `--year` | int | — | Publication year for title search; requires `--title` |
| `--url` | str | — | Direct URL to a paper PDF or landing page |
| `--topic` | str | required | Medical topic for grouping output (e.g. `adhd`). Kebab-case slug auto-derived |
| `--topic-slug` | str | — | Explicit kebab-case slug; overrides `--topic` |
| `--med-db` | str | `med-db` | Target `med-db/` directory path |
| `--email` | str | — | Contact email for NCBI E-utilities, Unpaywall, Crossref |
| `--delay` | float | `0.34` | Delay between downloads (seconds) |
| `--force` | flag | off | Re-download even if the paper is already archived |
| `--no-sci-hub` | flag | off | Disable Sci-Hub entirely (paywalled papers fall back to legal sources only) |
| `--sci-hub-mirror` | str | — | Override the Sci-Hub mirror list (takes precedence) |
| `--format` | choice | `text` | Output format: `json` or `text` |

---

## `uv run med-db-setup-dsm5` — DSM-5-TR Setup

Generate DSM-5-TR classification data in `med-db/`. Integrity check runs on completion.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--force` | flag | off | Regenerate `classification.json` even if it already exists |
| `--verify-only` | flag | off | Only verify presence; do not create or overwrite |

---

## `uv run med-db-setup-therapy-methods` — Therapy Methodology Setup

Generate therapy methodology guideline files in `med-db/`. Integrity check runs on completion.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--force` | flag | off | Regenerate all files even if they already exist |
| `--verify-only` | flag | off | Only verify presence; do not create or overwrite |

---

## `uv run med-db-lookup-icd11` — ICD-11 Lookup (local, read-only)

Fast local ICD-11 MMS lookup from downloaded WHO data. At least one query parameter required.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--code` | str | — | Exact ICD-11 stem code (e.g. `6A02`, `1A00.0`) |
| `--keyword` | str | — | Search ICD-11 titles by keyword (case-insensitive) |
| `--class-kind` | choice | — | Filter `--keyword` results: `chapter`, `block`, or `category` |
| `--icd10-code` | str | — | Look up equivalent ICD-11 code for an ICD-10 code |
| `--icd11-to-icd10` | str | — | Find equivalent ICD-10 code(s) for an ICD-11 code |
| `--release` | str | `2026-01` | ICD-11 release to use |
| `--language` | choice | `en` | Language for title display: `en` or `de` |
| `--limit` | int | `50` | Max keyword search results |
| `--hierarchy` | bool | `true` | Show full hierarchy for code lookups. Use `--no-hierarchy` to disable |
| `--children` | flag | off | Include direct children in code lookup output |
| `--format` | choice | `json` | Output format: `json` or `text` |
| `--title-only` | flag | off | Output only the title text (for `--code`) |

---

## `uv run med-db-lookup-dsm5` — DSM-5-TR Lookup (local, read-only)

Fast local DSM-5-TR classification lookup. At least one of `--code`, `--keyword`, `--category`, or
`--list-categories` required.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--code` | str | — | ICD-10-CM code (e.g. `F32.0`, `F90.2`) |
| `--keyword` | str | — | Search disorder names by keyword (case-insensitive) |
| `--category` | str | — | Search diagnostic categories by keyword |
| `--list-categories` | flag | `false` | List all DSM-5-TR diagnostic categories |
| `--limit` | int | `50` | Max keyword search results |
| `--format` | choice | `json` | Output format: `json` or `text` |
| `--title-only` | flag | off | Output only the disorder name (for `--code`) |
