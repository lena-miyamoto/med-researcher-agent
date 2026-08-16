# Term Source Policy

Evidence and source-priority rules for medical term definitions, corrections, and translations.

## Evidence Gate

- Define, correct, or translate a term only from an authoritative source identified in the priority
chain below. Never from model memory, training data, unstored web pages, general knowledge, or
plausibility reasoning.
- A term used colloquially within a community (e.g. the ADHD or autism community) is still definable:
source it from that community's usage and record the provenance honestly. Lack of a reference-work
entry does not make a term undefinable.
- After identifying the source, archive it into `med-db` before drafting:
  - Classification and dictionary sources are captured via `uv run med-db-term`.
  - Article-length sources go through `fetch-paper` or `med-researcher`.
- Use standard German orthography, including umlauts and `ß`, unless the user asks for ASCII or a
technical constraint requires it.

## Source Priority

| Stage | Source                                                                    | Rule                                                                                     |
| ----- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 1     | Local archive                                                             | Search `./med-db` first via `med-db-query` and `med-db-term-lookup`.                     |
| 2     | Diagnostic classifications                                                | ICD-11 (`med-db-lookup-icd11`) and DSM-5-TR (`med-db-lookup-dsm5`) in `med-db/guidelines/`. |
| 3     | Authoritative terminologies and dictionaries                              | MeSH (NCBI), WHO, professional-society glossaries (psychology, dietology, sports science), standard German reference works (e.g. Pschyrembel). |
| 4     | Peer-reviewed literature                                                  | Via `med-researcher` agent / `fetch-paper` — only when the term is not in a reference work. |
| 5     | Wikipedia                                                                 | Absolute last resort when all reference and literature routes fail and the alternative is leaving the term undefined. |

Fetch a MeSH scope note with `uv run med-db-term-mesh --term "<English term>"` — it returns the descriptor
ID, preferred label, and scope note.

When Wikipedia is used, archive the exact passage, mark it as fallback non-authoritative secondary
evidence in extraction notes, and replace it later if primary or literature evidence becomes available.

Fetch the lead section with `uv run med-db-term-wikipedia --title "<English title>"` — it returns the
plain-text `extract`, the Wikidata `description`, and the canonical article URL.

When a term is used colloquially within a community (ADHD, autism, disability, chronic illness, and the
like) and no reference, literature, or Wikipedia coverage exists, define it from the community's actual
usage — advocacy-organisation glossaries, clinician-authored explainers, or widely-cited community
writing — and record the provenance honestly. Mark such definitions as non-authoritative community
usage in `extraction_notes`; they document real usage, not a term's invalidity.

## Undefinable Terms

Write `<<COULD NOT BE DEFINED>>` only when no source of any kind — reference work, literature,
Wikipedia, or genuine community/colloquial usage — can be found. A term is not undefinable merely
because it lacks a reference-work entry; colloquial terms are defined from their community usage with
honest attribution.

Never leave `Definition` silently blank. When re-reading a CSV, treat an existing `<<COULD NOT BE
DEFINED>>` as an empty cell that still requires a lookup.

## Archival Convention

Term evidence is archived under `med-db/dictionary/<term-slug>/`:

- `source.md` — YAML frontmatter (`title`, `english`, `source_type`, `source_ref`, `source`,
`source_url`, `access_date`, `language`, `extraction_notes`) with the definition as body.
- `metadata.json` — machine-readable mirror (`term`, `english`, `definition`, `source_type`,
`source_ref`, `source_url`, `access_date`, `extraction_notes`).

Archive a term with:

```bash
uv run med-db-term --term "Hypertonie" --english "hypertension" \
  --definition "<Definition>" --source-type who --source-ref "<URL>" \
  --extraction-notes "<Provenance note, e.g. non-authoritative community usage>"
```

`--source-type` accepts `icd11`, `dsm5`, `mesh`, `who`, `society`, `dictionary`, `literature`,
`web`, or `other`. Use `--extraction-notes` to record provenance for community-sourced definitions
(for example `non-authoritative community usage`).

Look up an archived term with `uv run med-db-term-lookup --term "<Term>"`. Verify archive integrity
with `uv run med-db-integrity-check --med-db med-db`.
