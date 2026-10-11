---
description: >
  Evidence and source-priority rules for medical term definitions, corrections, and translations.
  Read when defining, correcting, or translating a term (define-terms skill).
---

# Term Source Policy

Evidence and source-priority rules for medical term definitions, corrections, and translations.

## Evidence Gate

- Define, correct, or translate a term only from an authoritative source identified in the priority
chain below. Never from model memory, training data, unstored web pages, general knowledge, or
plausibility reasoning.
- A term used colloquially within a community (e.g. the ADHD or autism community) is still definable:
source it from that community's usage and record the provenance honestly. Lack of a reference-work
entry does not make a term undefinable.
- After identifying the source, archive it into the local archive before drafting:
  - Classification and dictionary sources are captured via the `med-db` skill.
  - Article-length sources go through `fetch-paper` or `med-researcher`.
- Use standard German orthography, including umlauts and `ß`, unless the user asks for ASCII or a
technical constraint requires it.

## Source Priority

| Stage | Source                                       | Rule                                                                                                                                                                               |
| ----- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Local archive                                | Search the local archive first via the `med-db` skill.                                                                                                                             |
| 2     | Diagnostic classifications                   | ICD-11 mental-health codes via the `med-db` skill (`.claude/agents/references/icd11-mental-health-codes.md`) and DSM-5-TR (`.claude/agents/references/dsm5-tr-classification.md`). |
| 3     | Authoritative terminologies and dictionaries | MeSH (NCBI), WHO, professional-society glossaries (psychology, dietology, sports science), standard German reference works (e.g. Pschyrembel).                                     |
| 4     | Peer-reviewed literature                     | Via `med-researcher` agent / `fetch-paper` — only when the term is not in a reference work.                                                                                        |
| 5     | Wikipedia                                    | Absolute last resort when all reference and literature routes fail and the alternative is leaving the term undefined.                                                              |

Fetch a MeSH scope note via the `med-db` skill — it returns the descriptor
ID, preferred label, and scope note.

When Wikipedia is used, archive the exact passage, mark it as fallback non-authoritative secondary
evidence in extraction notes, and replace it later if primary or literature evidence becomes available.

Fetch the lead section via the `med-db` skill — it returns the
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

Term evidence is archived in the local archive under the term slug; the archive layout and file set
are defined by the `med-db` skill.

Archive a term via the `med-db` skill with the term, English label, definition, source type, source
reference, and extraction notes (for example `non-authoritative community usage`).

`--source-type` accepts `icd11`, `dsm5`, `mesh`, `who`, `society`, `dictionary`, `literature`,
`web`, or `other`. Use `--extraction-notes` to record provenance for community-sourced definitions
(for example `non-authoritative community usage`).

Look up an archived term via the `med-db` skill, and verify archive integrity via the same skill.
