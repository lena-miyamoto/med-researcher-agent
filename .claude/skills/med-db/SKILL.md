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
- **If the `uv run` tools don't support a query pattern you need, report it — do not work
  around it with inline code.**

### Forbidden Patterns — Never Do Any of These

These patterns violate the Command Invocation Contract. Each one has been observed
in real sessions. **None of them are acceptable.**

| Forbidden | Why | Use Instead |
|---|---|---|
| `python3 -c "import json; ..."` reading `index.json` | Bypasses validation layer | `uv run med-db-query --search-keyword "..."` |
| `python3 -c "..."` for any med-db operation | Direct file access, no integrity checks | `uv run med-db-lookup --pmid ...` |
| `jq` / `cat` / `grep` on `med-db/index.json` | Bypasses the tool layer | `uv run med-db-query --list-topics` |
| `python3` or `python` in any form | Forbidden by CLAUDE.md contract | `uv run <entry-point>` |
| `node -e`, `perl -e` touching med-db files | Same bypass, different language | `uv run med-db-*` tools |

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
See `.claude/agents/rules/knowledge-base.md` for the psychotherapist agent's full knowledge
base bootstrap procedure including research briefs.

## Source Policies

Archive access is governed by these reference files. Consult them before archiving,
querying, or analyzing evidence from the archive:

| Domain                                              | Reference                                     |
| --------------------------------------------------- | --------------------------------------------- |
| med-db command reference with every parameter       | `.claude/agents/rules/med-db-commands.md`     |
| Knowledge base bootstrap and component overview     | `.claude/agents/rules/knowledge-base.md`      |
| Evidence quality standards and search protocol      | `.claude/agents/med-researcher.md`            |
| Script development conventions                      | `.claude/scripts/DEVELOPER.md`                |
| Overall integration and CLI contract                | `CLAUDE.md`                                   |

## Archival Conventions

- Always include `--topic <name>` on archival commands (human-readable name, e.g. `adhd`,
  `endometriosis`). The tool derives the kebab-case slug automatically.
- Use `--topic-slug` only when automatic derivation fails.
- Always include `--validate` when archiving by PMID, DOI, or EPMC record.
- Integrity check runs automatically after every archival, setup, or download operation.
  Errors block completion (exit code 1) and must be fixed immediately.

## During-Session / Real-Time Use

When operating in a live session (e.g., therapy, coaching, consultation), only **read-only,
local, no-network** commands are permitted during the session:

| Permitted during session | Must wait until after session |
|---|---|
| `uv run med-db-query --search-keyword "..."` | `uv run med-db --pmid ...` (archival — writes) |
| `uv run med-db-query --list-topics` | `uv run med-db --source pubmed --query "..."` (network search) |
| `uv run med-db-query --read-metadata "..."` | `uv run med-db-download-icd11` (setup — writes) |
| `uv run med-db-lookup --pmid ...` | `uv run med-db-setup-dsm5` (setup — writes) |
| `uv run med-db-lookup-icd11 --code "..."` | `uv run med-db-setup-therapy-methods` (setup — writes) |
| `uv run med-db-lookup-dsm5 --code "..."` | `uv run med-db-integrity-check` (harmless but unnecessary mid-session) |
| `uv run med-db-lookup --doi ...` | `WebSearch`, `WebFetch` for new papers (network) |
| Reading `med-db/guidelines/therapy-methodologies/source.md` | Dispatching `med-researcher` agent (writes to med-db/) |
| Dispatching Haiku sub-agent for read-only med-db queries | Dispatching any sub-agent other than Haiku for med-db access |

Read-only commands are sub-second, local, and equivalent to consulting a reference shelf.
Network searches and archival are between-session work.

**Haiku sub-agent pattern for therapy sessions:** The psychotherapist agent may dispatch a
Haiku-model sub-agent to run read-only med-db commands during a session. The sub-agent must
use only commands from the "Permitted during session" column above. It must never run archival,
network, or write commands. This pattern lets the therapist consult the reference shelf without
breaking therapeutic presence.

## Command Reference

All scripts must be invoked via `uv run` from the repo root. Query and lookup scripts
default to JSON; use `--format text` for human-readable output.

For the complete parameter reference with every flag, type, and default, see
`.claude/agents/rules/med-db-commands.md`. The table below is a quick reference for
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

Follow `CLAUDE.md` (Command Invocation Contract section) for `uv run lint-md` and
`uv run test` invocation rules.
