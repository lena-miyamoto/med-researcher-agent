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

Any operation that reads from or writes to the local `./med-db/` archive tree. This includes:
checking whether a paper is archived; searching the archive by keyword, topic, or PMID; reading
metadata; listing contents; archiving papers via PMID, DOI, or search query; setting up
diagnostic classifications (ICD-11, DSM-5-TR, therapy methodologies); looking up codes; syncing
or validating the index; and running integrity checks.

Other skills (analyze-med-claims, create-diet-plan, start-therapy-session) and agents
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

## Bootstrap

- `./med-db/` is gitignored and does not ship with the repo.
- Do not create `med-db/` or its subdirectories by hand; the tooling creates the archive
  tree and initial `index.json`.
- To bootstrap a fresh checkout: run any archival command (e.g.
  `uv run med-db --pmid 12345678 --validate`). The tooling auto-creates the full tree
  (`searches/`, `papers/`, `fulltext/`, `guidelines/`, `web/`) plus `index.json`.
- To verify bootstrap: `uv run med-db-integrity-check --med-db med-db`. An empty archive
  passes if all five directories and `index.json` exist.
- Query and lookup tools are read-only. If they report that `med-db/` is missing, run an
  archival command first.
- For the full knowledge base: also run `uv run med-db-download-icd11`,
  `uv run med-db-setup-dsm5`, and `uv run med-db-setup-therapy-methods`. See
  `.agents/agents/rules/knowledge-base.md` for the mandatory pre-work bootstrap check.

## Source Policies

Archive access is governed by these reference files. Consult them before archiving,
querying, or analyzing evidence from the archive:

| Domain                                              | Reference                                     |
| --------------------------------------------------- | --------------------------------------------- |
| med-db command reference with every parameter       | `.agents/agents/rules/med-db-commands.md`     |
| Knowledge base bootstrap and component overview     | `.agents/agents/rules/knowledge-base.md`      |
| Evidence quality standards and search protocol      | `.agents/agents/med-researcher.md`            |
| Script development conventions                      | `.agents/scripts/DEVELOPER.md`                |
| Overall integration and CLI contract                | `CLAUDE.md`                                   |

## Command Reference

All scripts must be invoked via `uv run` from the repo root. Query and lookup scripts
default to JSON; use `--format text` for human-readable output.

For the complete parameter reference with every flag, type, and default, see
`.agents/agents/rules/med-db-commands.md`. The table below is a quick reference for
common operations.

### Archive (`med-db`)

| Operation          | Command                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| PMID               | `uv run med-db --pmid <ID> --topic '<name>' --validate`                                          |
| DOI                | `uv run med-db --doi <DOI> --topic '<name>' --validate`                                          |
| Europe PMC record  | `uv run med-db --epmc-record '<SOURCE>:<ID>' --topic '<name>' --validate`                        |
| PubMed search      | `uv run med-db --source pubmed --query '<query>' --topic '<name>'`                               |
| Europe PMC search  | `uv run med-db --source europe-pmc --query '<query>' --topic '<name>'`                           |
| Web discovery      | `uv run med-db --source <SOURCE> --query '<query>' --topic '<name>'`                             |
| Archive first N    | `uv run med-db --source pubmed --query '<query>' --archive-first <N> --topic '<name>'`           |
| Multiple PMIDs     | `uv run med-db --pmid <ID1> --pmid <ID2> --topic '<name>' --validate`                            |
| Migrate (dry run)  | `uv run med-db --migrate-dry-run`                                                                |
| Migrate            | `uv run med-db --migrate`                                                                        |

### Query (`med-db-query`)

| Operation          | Command                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| List topics        | `uv run med-db-query --list-topics`                                                              |
| List papers/topic  | `uv run med-db-query --topic '<slug>'`                                                           |
| Check PMID         | `uv run med-db-query --check-pmid '<ID>'`                                                        |
| Check EPMC record  | `uv run med-db-query --check-epmc '<SOURCE>:<ID>'`                                               |
| PMIDs from search  | `uv run med-db-query --pmids-from-search '<path>'`                                               |
| Read metadata      | `uv run med-db-query --read-metadata '<path>'`                                                   |
| Read + abstract    | `uv run med-db-query --read-metadata '<path>' --show-abstract`                                   |
| Keyword search     | `uv run med-db-query --search-keyword '<term>'`                                                  |
| Scoped keyword     | `uv run med-db-query --search-keyword '<term>' --search-topic '<slug>'`                          |
| Recent papers      | `uv run med-db-query --recent <N>`                                                               |
| Search searches    | `uv run med-db-query --search-searches '<term>'`                                                 |

### External Lookup (`med-db-lookup`)

| Operation          | Command                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| Lookup PMID        | `uv run med-db-lookup --pmid <ID>`                                                               |
| Lookup DOI         | `uv run med-db-lookup --doi <DOI>`                                                               |
| Lookup EPMC record | `uv run med-db-lookup --epmc-record '<SOURCE>:<ID>'`                                             |

### Diagnostic Classification

| Operation          | Command                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| Download ICD-11    | `uv run med-db-download-icd11 --release 2026-01`                                                 |
| ICD-11 by code     | `uv run med-db-lookup-icd11 --code '<CODE>'`                                                     |
| ICD-11 keyword     | `uv run med-db-lookup-icd11 --keyword '<term>'`                                                  |
| ICD-10 → ICD-11    | `uv run med-db-lookup-icd11 --icd10-code '<CODE>'`                                               |
| ICD-11 → ICD-10    | `uv run med-db-lookup-icd11 --icd11-to-icd10 '<CODE>'`                                           |
| Setup DSM-5-TR     | `uv run med-db-setup-dsm5`                                                                       |
| DSM-5 by code      | `uv run med-db-lookup-dsm5 --code '<CODE>'`                                                      |
| DSM-5 keyword      | `uv run med-db-lookup-dsm5 --keyword '<term>'`                                                   |
| Setup therapy      | `uv run med-db-setup-therapy-methods`                                                            |

### Maintenance

| Operation          | Command                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| Integrity check    | `uv run med-db-integrity-check --med-db med-db`                                                  |
| JSON integrity     | `uv run med-db-integrity-check --med-db med-db --json`                                           |
| All tests          | `uv run test`                                                                                    |

### Lint Rules

- After completing edits to any `*.md` file, run `uv run lint-md` (or `uv run lint-md --fix`).
- **Never run `uv run pymarkdownlnt` directly.** Only `uv run lint-md`.
- Canonical test command after editing any `*.py` file: `uv run test`. Full suite must pass.
