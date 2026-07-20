# med-db Command Reference

Every command must be invoked as `uv run <entry-point> …` from the repo root. Default output is JSON
unless noted; use `--format text` for human-readable output.

`python3`, `python`, and any direct Python invocation are **forbidden**. All access must go through the
`uv run` entry points so validation, indexing, and integrity checks are always applied.

Supported web discovery sources: `google-scholar`, `doaj`, `open-science-directory`,
`free-medical-journals`, `openmd`, `trip-database`. Prefer PubMed and Europe PMC for structured records.

Full-text fallback: follow the Sci-Hub policy in `.agents/agents/med-researcher.md`. Prefer official
open-access sources first.

Integrity enforcement: `med-db-integrity-check` runs automatically after every archival, setup, or
download operation. Errors block completion (exit code 1) and must be fixed immediately.

---

## `uv run med-db` — Archival (PubMed, Europe PMC, web discovery)

Archives searches, PMIDs, DOIs, and EPMC records into the local `med-db/` tree. Always include
`--topic` (human-readable name, e.g. `adhd`). Integrity check runs automatically on completion.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--source` | choice | `pubmed` | Primary source: `pubmed`, `europe-pmc`, `google-scholar`, `doaj`, `open-science-directory`, `free-medical-journals`, `openmd`, `trip-database` |
| `--query` | str | — | Search query for the selected source |
| `--search-slug` | str | — | Optional slug for the saved search file |
| `--topic` | str | `uncategorized` | Medical topic for grouping output (e.g. `endometriosis`, `adhd`). Tool derives kebab-case slug automatically |
| `--topic-slug` | str | — | Explicit kebab-case slug; overrides `--topic` |
| `--pmid` | str[] | `[]` | PMID to archive; repeatable (`--pmid 1 --pmid 2`) |
| `--epmc-record` | str[] | `[]` | Europe PMC record as `SOURCE:ID`; repeatable |
| `--doi` | str[] | `[]` | DOI to resolve and archive; repeatable. Tries PubMed first, then Europe PMC |
| `--archive-first` | int | `0` | Also archive first N PMIDs returned by `--query` |
| `--retmax` | int | `20` | Machine-readable hits to request for the archived search JSON |
| `--med-db` | str | `med-db` | Target `med-db/` directory path |
| `--email` | str | — | Contact email for NCBI E-utilities |
| `--delay` | float | `0.34` | Delay between PMID fetches (seconds) |
| `--migrate` | flag | off | Migrate flat `med-db/` structure to topic-based per-paper folders |
| `--migrate-dry-run` | flag | off | Preview `--migrate` without copying files |

---

## `uv run med-db-integrity-check` — Validation

Runs automatically after every archival, setup, or download operation. Errors block completion (exit
code 1) and must be fixed immediately.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--med-db` | str | `med-db` | Target `med-db/` directory path |
| `--json` | flag | off | Emit findings as machine-parseable JSON |

---

## `uv run med-db-lookup` — External Lookup (read-only, no archival)

Queries PubMed, Europe PMC, or resolves DOIs. At least one of `--pmid`, `--epmc-record`, or `--doi`
is required.

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

Queries the local `med-db/` archive. Exactly one operation flag from the mutually exclusive group is
required.

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
| `--pmids-from-search` | str | Extract PMID list from a search JSON file path |
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

---

## `uv run med-db-download-icd11` — ICD-11 Setup

Downloads ICD-11 MMS data from the WHO CDN into `med-db/`. Integrity check runs automatically on
completion.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--release` | str | `2026-01` | ICD-11 release identifier |
| `--language` | str[] | `[]` | Language code to download; repeatable. Defaults to `en` + `de` for 2026-01, `en` only for earlier releases |
| `--force` | flag | off | Re-download even if files already exist |
| `--verify` | bool | `true` | Run smoke test after download. Use `--no-verify` to skip |

---

## `uv run med-db-setup-dsm5` — DSM-5-TR Setup

Generates the DSM-5-TR classification data in `med-db/`. Integrity check runs automatically on
completion.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--force` | flag | off | Regenerate `classification.json` even if it already exists |
| `--verify-only` | flag | off | Only verify presence; do not create or overwrite |

---

## `uv run med-db-setup-therapy-methods` — Therapy Methodology Setup

Generates therapy methodology guideline files in `med-db/`. Integrity check runs automatically on
completion.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--force` | flag | off | Regenerate all files even if they already exist |
| `--verify-only` | flag | off | Only verify presence; do not create or overwrite |

---

## `uv run med-db-lookup-icd11` — ICD-11 Lookup (local, read-only)

Fast local ICD-11 MMS lookup from downloaded WHO data. At least one query parameter is required.

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

---

## `uv run med-db-lookup-dsm5` — DSM-5-TR Lookup (local, read-only)

Fast local DSM-5-TR classification lookup. At least one of `--code`, `--keyword`, `--category`, or
`--list-categories` is required.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `--code` | str | — | ICD-10-CM code (e.g. `F32.0`, `F90.2`) |
| `--keyword` | str | — | Search disorder names by keyword (case-insensitive) |
| `--category` | str | — | Search diagnostic categories by keyword |
| `--list-categories` | flag | `false` | List all DSM-5-TR diagnostic categories |
| `--limit` | int | `50` | Max keyword search results |
| `--format` | choice | `json` | Output format: `json` or `text` |
