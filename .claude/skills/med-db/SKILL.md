---
name: med-db
description: >
  Access the med-db archive — search, query, archive, validate, look up diagnostic
  classifications, or bootstrap. Every read and write to the local archive must go
  through this skill. Never touch med-db/ files directly.
user-invocable: false
---

# med-db

Cross-harness source of truth for the `med-db` skill. Owns all archive access rules, the
command contract, bootstrap logic, and the quick-reference command table.

## When to Use

Any operation reading from or writing to the local `./med-db/` archive tree: checking whether
a paper is archived; searching by keyword, topic, or PMID; reading metadata; listing contents;
archiving via PMID, DOI, or search query; setting up diagnostic classifications (ICD-11,
DSM-5-TR, therapy methodologies); looking up codes; syncing or validating the index; running
integrity checks.

Other skills (`analyze-med-claims`, `create-diet-plan`, `start-therapy-session`) and agents
(med-researcher, psychotherapist, dietologist) delegate archive operations to this skill.

## Black-Box Rule

- **Never read, write, or manipulate any file under `./med-db/` directly.** This includes
  `cat`, `head`, `tail`, `jq`, `grep`, `sed`, `awk`, `python3 -c`, `python3` scripts,
  `node -e`, and every other ad-hoc snippet or shell tool.
- The archive is a black box: **every read** goes through `uv run med-db-query ...` or
  `uv run med-db-lookup* ...` and **every write** goes through `uv run med-db ...` or
  `uv run med-db-setup-* ...` or `uv run med-db-download-* ...`. There are zero exceptions.
- Do not run repo scripts with `python`, `python3`, direct script paths, absolute paths,
  or shebang execution. All repo Python tools run through `uv run ...` from the repo root.
- **If the `uv run` tools don't support a query pattern you need, report it — do not work
  around it with inline code.**

### Forbidden Patterns — Never Do Any of These

These patterns violate the Command Invocation Contract. Each one has been observed
in real sessions. **None of them are acceptable.**

| Forbidden | Why | Use Instead |
|---|---|---|
| `python3 -c "import json; ..."` reading `index.json` | Bypasses validation layer | `uv run med-db-query --search-keyword "..."` |
| `python3 -c "..."` for JSON post-processing | Tools have extraction flags for this | `uv run med-db-query ... --{identifiers,names,locations,title,abstract}-only` |
| `python3 -c "..."` for any med-db operation | Direct file access, no integrity checks | `uv run med-db-lookup --pmid ...` |
| `jq` / `cat` / `grep` on `med-db/index.json` | Bypasses the tool layer | `uv run med-db-query --list-topics` |
| `jq` / `sed` / `awk` on JSON output | Extraction flags output plain text directly | `uv run med-db-query ... --identifiers-only` etc. |
| `python3` or `python` in any form | Forbidden by CLAUDE.md contract | `uv run <entry-point>` |
| `node -e`, `perl -e` touching med-db files | Same bypass, different language | `uv run med-db-*` tools |
| `WebFetch` / `WebSearch` / `wget` / `curl` on a Wikipedia article | Scrapes raw HTML, bypasses the REST summary tool and its error contract | `uv run med-db-term-wikipedia --title "<English title>"` |

## Bootstrap

- `./med-db/` is gitignored and does not ship with the repo.
- Do not create `med-db/` or its subdirectories by hand; the tooling creates the archive
  tree and initial `index.json`.
- To bootstrap a fresh checkout: run any archival command (e.g.
  `uv run med-db --pmid 12345678`). The tooling auto-creates the full tree
  (`searches/`, `papers/`, `fulltext/`, `guidelines/`, `web/`, `dictionary/`) plus `index.json`.
- To verify bootstrap: `uv run med-db-integrity-check --med-db med-db`. An empty archive
  passes if all six directories and `index.json` exist.
- Query and lookup tools are read-only. If they report that `med-db/` is missing, run an
  archival command first.

### Diagnostic Classification Setup

Three optional components add structured diagnostic reference data to `med-db/guidelines/`.
Each is independent — set up only what you need:

| Component | Bootstrap command | Lookup tool |
|---|---|---|
| ICD-11 classification | `uv run med-db-download-icd11 --release 2026-01` | `uv run med-db-lookup-icd11` |
| DSM-5-TR classification | `uv run med-db-setup-dsm5` | `uv run med-db-lookup-dsm5` |
| Therapy methodologies | `uv run med-db-setup-therapy-methods` | Read `med-db/guidelines/therapy-methodologies/source.md` |

To verify all components at once:

```bash
uv run med-db-query --list-topics 2>/dev/null
uv run med-db-download-icd11 --release 2026-01 --verify 2>&1
uv run med-db-setup-dsm5 --verify-only 2>&1
uv run med-db-setup-therapy-methods --verify-only 2>&1
```

All checks must pass. If any component is missing, run its bootstrap command above.
See `.claude/agents/references/knowledge-base.md` for the psychotherapist agent's full knowledge
base bootstrap procedure including research briefs.

## Source Policies

Archive access is governed by these reference files. Consult them before archiving,
querying, or analyzing evidence from the archive:

| Domain                                              | Reference                                     |
| --------------------------------------------------- | --------------------------------------------- |
| med-db command reference with every parameter       | `.claude/agents/references/med-db-commands.md`     |
| Knowledge base bootstrap and component overview     | `.claude/agents/references/knowledge-base.md`      |
| Evidence quality standards and search protocol      | `.claude/agents/med-researcher.md`            |
| Full-text download procedure and source policy      | `fetch-paper`                                 |
| Script development conventions                      | `.claude/scripts/DEVELOPER.md`                |
| Overall integration and CLI contract                | `CLAUDE.md`                                   |

## Archival Conventions

- Always include `--topic <name>` on archival commands (human-readable name, e.g. `adhd`,
  `endometriosis`). The tool derives the kebab-case slug automatically.
- Use `--topic-slug` only when automatic derivation fails.
- Full-text downloads go through the `fetch-paper` skill,
  which archives into `fulltext/` via `uv run med-db-download-paper`.
- Integrity check runs automatically after every archival, setup, or download operation.
  Errors block completion (exit code 1) and must be fixed immediately.

## During-Session / Real-Time Use

When operating in a live session (e.g., therapy, coaching, consultation), only **read-only,
local, no-network** commands are permitted during the session:

| Permitted during session | Must wait until after session |
|---|---|
| `uv run med-db-query --search-keyword "..."` | `uv run med-db --pmid ...` (archival — writes) |
| `uv run med-db-query --search-keyword "..." --identifiers-only` | `uv run med-db --source pubmed --query "..."` (network search) |
| `uv run med-db-query --list-topics` | `uv run med-db-download-icd11` (setup — writes) |
| `uv run med-db-query --list-topics` | `uv run med-db-download-paper ...` (full-text download — network + writes) |
| `uv run med-db-query --list-topics --names-only` | `uv run med-db-setup-dsm5` (setup — writes) |
| `uv run med-db-query --check-pmid "..."` | `uv run med-db-setup-therapy-methods` (setup — writes) |
| `uv run med-db-query --check-pmid "..." --locations-only` | `uv run med-db-integrity-check` (harmless but unnecessary mid-session) |
| `uv run med-db-query --read-metadata "..."` | `WebSearch`, `WebFetch` for new papers (network) |
| `uv run med-db-query --read-metadata "..." --title-only` | Dispatching `med-researcher` agent (writes to med-db/) |
| `uv run med-db-query --read-metadata "..." --abstract-only` | Dispatching any sub-agent other than Haiku for med-db access |
| `uv run med-db-query --pmids-from-search "..." --identifiers-only` | |
| `uv run med-db-query --search-searches "..." --identifiers-only` | |
| `uv run med-db-query --recent N --identifiers-only` | |
| `uv run med-db-lookup --pmid ...` | |
| `uv run med-db-lookup-icd11 --code "..."` | |
| `uv run med-db-lookup-icd11 --code "..." --title-only` | |
| `uv run med-db-lookup-dsm5 --code "..."` | |
| `uv run med-db-lookup-dsm5 --code "..." --title-only` | |
| `uv run med-db-lookup --doi ...` | |
| Reading `med-db/guidelines/therapy-methodologies/source.md` | |
| Dispatching Haiku sub-agent for read-only med-db queries | |

Read-only commands: sub-second, local, equivalent to consulting a reference shelf.
Network searches and archival: between-session work.

**Haiku sub-agent pattern for therapy sessions:** Psychotherapist agent may dispatch a
Haiku-model sub-agent to run read-only med-db commands during a session. The sub-agent must
use only commands from the "Permitted during session" column above. It must never run archival,
network, or write commands. This pattern lets the therapist consult the reference shelf without
breaking therapeutic presence.

## Extraction Flags — Get Data Without JSON Post-Processing

Every query and lookup command defaults to JSON (`--format json`). For a single field,
use an extraction flag instead of piping through `python3 -c`, `jq`, `grep`, or `sed`.
Extraction flags output plain text, one value per line — no post-processing needed.

| Flag | Applies to | Output |
|---|---|---|
| `--identifiers-only` | `--topic`, `--search-keyword`, `--recent`, `--pmids-from-search`, `--search-searches` | Identifiers (PMIDs, EPMC IDs, or paths) one per line |
| `--title-only` | `--read-metadata`, ICD-11 `--code`, DSM-5 `--code` | Title/disorder name text |
| `--abstract-only` | `--read-metadata` | Abstract text (auto-loads it — no `--show-abstract` needed) |
| `--names-only` | `--list-topics` | Topic names one per line |
| `--locations-only` | `--check-pmid`, `--check-epmc` | Archive folder paths one per line |

**Archive (`med-db`) also supports:** `--format json` (structured machine output),
`--quiet` (created folder paths only, one per line). Default is `--format text`.

**Diagnostic lookups** support `--title-only` for `--code` (ICD-11: condition title;
DSM-5: disorder name). For partial code matches, all matching titles are printed one per line.

## Command Reference

All scripts must be invoked via `uv run` from the repo root. Query and lookup scripts
default to JSON. Use `--format text` for human-readable output, or an extraction flag
(`--identifiers-only`, `--title-only`, `--abstract-only`, `--names-only`, `--locations-only`)
to get a single field as plain text — no `jq`, `python3 -c`, or `grep` needed.

For the complete parameter reference with every flag, type, and default, see
`.claude/agents/references/med-db-commands.md`. The table below is a quick reference for
common operations.

### Archive (`med-db`)

Default text output; `--format json` for structured, `--quiet` for folder paths only.

| Operation              | Command                                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| PMID                   | `uv run med-db --pmid <ID> --topic '<name>'`                                                     |
| DOI                    | `uv run med-db --doi <DOI> --topic '<name>'`                                                     |
| Europe PMC record      | `uv run med-db --epmc-record '<SOURCE>:<ID>' --topic '<name>'`                                   |
| PubMed search          | `uv run med-db --source pubmed --query '<query>' --topic '<name>'`                               |
| Europe PMC search      | `uv run med-db --source europe-pmc --query '<query>' --topic '<name>'`                           |
| Web discovery          | `uv run med-db --source <SOURCE> --query '<query>' --topic '<name>'`                             |
| Archive first N        | `uv run med-db --source pubmed --query '<query>' --archive-first <N> --topic '<name>'`           |
| Multiple PMIDs         | `uv run med-db --pmid <ID1> --pmid <ID2> --topic '<name>'`                                       |
| Remove PMID            | `uv run med-db --remove-pmid <ID>`                                                               |
| Remove EPMC record     | `uv run med-db --remove-epmc-record '<SOURCE>:<ID>'`                                             |
| Re-fetch / overwrite   | `uv run med-db ... --force`                                                                      |
| JSON output            | `uv run med-db ... --format json`                                                                |
| Paths only (quiet)     | `uv run med-db ... --quiet`                                                                      |
| Migrate (dry run)      | `uv run med-db --migrate-dry-run`                                                                |
| Migrate                | `uv run med-db --migrate`                                                                        |

DOI resolution tries PubMed, then Europe PMC, then Crossref metadata — Crossref covers DOIs indexed in neither (e.g. APA journals).

### Full-Text Download (`med-db-download-paper`)

PDF + extracted text into `med-db/fulltext/`. Owned by the `fetch-paper` skill (procedure, source
policy, Sci-Hub fallback); full parameter reference in `med-db-commands.md`.

| Operation    | Command                                                                                       |
| ------------ | --------------------------------------------------------------------------------------------- |
| Download PDF | `uv run med-db-download-paper --reference '<DOI|PMID|arXiv|SOURCE:ID|URL>' --topic '<name>'`  |
| Title + year | `uv run med-db-download-paper --title '<title>' --year <YEAR> --topic '<name>'`               |

### Query (`med-db-query`)

Default JSON. Use `--format text` for readable output, or extraction flags for single-field plain text.

| Operation               | Command                                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------ |
| List topics             | `uv run med-db-query --list-topics`                                                              |
| Topic names only        | `uv run med-db-query --list-topics --names-only`                                                 |
| List papers/topic       | `uv run med-db-query --topic '<slug>'`                                                           |
| Paper IDs only          | `uv run med-db-query --topic '<slug>' --identifiers-only`                                        |
| Check PMID              | `uv run med-db-query --check-pmid '<ID>'`                                                        |
| PMID locations only     | `uv run med-db-query --check-pmid '<ID>' --locations-only`                                       |
| Check EPMC record       | `uv run med-db-query --check-epmc '<SOURCE>:<ID>'`                                               |
| EPMC locations only     | `uv run med-db-query --check-epmc '<SOURCE>:<ID>' --locations-only`                              |
| PMIDs from search       | `uv run med-db-query --pmids-from-search '<path>'`                                               |
| PMIDs only              | `uv run med-db-query --pmids-from-search '<path>' --identifiers-only`                            |
| Read metadata           | `uv run med-db-query --read-metadata '<path>'`                                                   |
| Title only              | `uv run med-db-query --read-metadata '<path>' --title-only`                                      |
| Abstract only           | `uv run med-db-query --read-metadata '<path>' --abstract-only`                                   |
| Read + abstract (JSON)  | `uv run med-db-query --read-metadata '<path>' --show-abstract`                                   |
| Keyword search          | `uv run med-db-query --search-keyword '<term>'`                                                  |
| Scoped keyword          | `uv run med-db-query --search-keyword '<term>' --search-topic '<slug>'`                          |
| Keyword IDs only        | `uv run med-db-query --search-keyword '<term>' --identifiers-only`                               |
| Recent papers           | `uv run med-db-query --recent <N>`                                                               |
| Recent IDs only         | `uv run med-db-query --recent <N> --identifiers-only`                                            |
| Search searches         | `uv run med-db-query --search-searches '<term>'`                                                 |
| Search paths only       | `uv run med-db-query --search-searches '<term>' --identifiers-only`                              |

### External Lookup (`med-db-lookup`)

| Operation          | Command                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| Lookup PMID        | `uv run med-db-lookup --pmid <ID>`                                                               |
| Lookup DOI         | `uv run med-db-lookup --doi <DOI>`                                                               |
| Lookup EPMC record | `uv run med-db-lookup --epmc-record '<SOURCE>:<ID>'`                                             |

### Dictionary Terms (`med-db-term`, `med-db-term-lookup`)

Term definitions for the `define-terms` skill. Archive writes to `dictionary/<term-slug>/`;
lookup is read-only.

| Operation       | Command                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------ |
| Archive term    | `uv run med-db-term --term '<Term>' --definition '<Definition>' --source-type <TYPE>`            |
| Lookup term     | `uv run med-db-term-lookup --term '<Term>'`                                                       |
| Keyword search  | `uv run med-db-term-lookup --keyword '<text>'`                                                    |
| List all terms  | `uv run med-db-term-lookup --list`                                                                |

### Term Source Helpers (`med-db-term-wikipedia`, `med-db-term-mesh`)

Read-only fetchers for the `define-terms` skill. Wikipedia is the stage-5 fallback; MeSH is a
stage-3 authoritative source. Both default to JSON (`--format text` for readable output).

| Operation       | Command                                                              |
| --------------- | -------------------------------------------------------------------- |
| Wikipedia lead  | `uv run med-db-term-wikipedia --title '<English title>'`             |
| MeSH scope note | `uv run med-db-term-mesh --term '<English term>'`                    |

### Diagnostic Classification

| Operation             | Command                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| Download ICD-11       | `uv run med-db-download-icd11 --release 2026-01`                                                 |
| ICD-11 by code        | `uv run med-db-lookup-icd11 --code '<CODE>'`                                                     |
| ICD-11 title only     | `uv run med-db-lookup-icd11 --code '<CODE>' --title-only`                                        |
| ICD-11 keyword        | `uv run med-db-lookup-icd11 --keyword '<term>'`                                                  |
| ICD-10 → ICD-11       | `uv run med-db-lookup-icd11 --icd10-code '<CODE>'`                                               |
| ICD-11 → ICD-10       | `uv run med-db-lookup-icd11 --icd11-to-icd10 '<CODE>'`                                           |
| Setup DSM-5-TR        | `uv run med-db-setup-dsm5`                                                                       |
| DSM-5 by code         | `uv run med-db-lookup-dsm5 --code '<CODE>'`                                                      |
| DSM-5 title only      | `uv run med-db-lookup-dsm5 --code '<CODE>' --title-only`                                         |
| DSM-5 keyword         | `uv run med-db-lookup-dsm5 --keyword '<term>'`                                                   |
| Setup therapy         | `uv run med-db-setup-therapy-methods`                                                            |

### Maintenance

| Operation             | Command                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| Integrity check       | `uv run med-db-integrity-check --med-db med-db`                                                  |
| Integrity check JSON  | `uv run med-db-integrity-check --med-db med-db --format json`                                    |
| All tests             | `uv run test`                                                                                    |

### Lint Rules

Follow `CLAUDE.md` (Command Invocation Contract section) for `uv run lint-md` and
`uv run test` invocation rules.
