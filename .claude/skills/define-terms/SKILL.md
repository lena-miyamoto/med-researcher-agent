---
name: define-terms
description: >
  Complete glossary CSV or TSV files of medical terms (psychology, dietology, sports science),
  or define one or more terms on the fly and write them as CSV to tmp/output.csv. Backed by
  authoritative sources archived in med-db.
argument-hint: 'Either one or more .csv/.tsv file URIs to complete, or one or more terms to define into tmp/output.csv'
user-invocable: true
---

# Define Terms

Cross-harness source of truth for the `define-terms` skill. Defines and translates medical terms —
covering psychology, dietology, sports science, and adjacent health fields — into a standard
three-column glossary schema.

## When to Use

- Input is one of two modes: `.csv`/`.tsv` URIs to complete in place, or raw terms to define fresh.
- File mode: rows missing `Definition`, and optionally `Englischer Begriff`. An existing `<<COULD NOT BE DEFINED>>` counts as missing — run the lookup rather than leaving it.
- Term mode: glossary-style CSV written to `tmp/output.csv`.
- Output aligns with the repo's standard three-column schema and glossary tone.
- Evidence-gated per `references/term-source-policy.md`.

## Procedure

1. Classify the input first:
   - File mode: every parameter is a `.csv`/`.tsv` URI or path.
   - Term mode: parameters are glossary terms needing definitions.
   - Mixed input → stop and ask.
2. Source gate before any drafting or judgment:
   - Follow `references/term-source-policy.md` for the evidence gate, source priority, and
   archival conventions.
   - For definitions not covered by a reference work, invoke `med-researcher` (evidence-backed
   definition) or `fetch-paper` (article-length source) — these own acquisition and archival.
   - Wikipedia (stage 5) is the exception: fetch the lead section directly with
   `uv run med-db-term-wikipedia --title "<English title>"` — never `WebFetch`/`WebSearch`/
   `wget`/`curl` a Wikipedia page, and do not delegate the fetch to `med-researcher`.
   - Only after the source is identified and archived may you define, correct, or translate.
3. Prefer existing archived evidence and validated wording before drafting new wording.
4. File mode, per referenced file:
   - Re-read before editing; preserve the existing delimiter.
   - Expect header `Deutscher Begriff,Englischer Begriff,Definition`. Different structure → stop and
   ask.
   - Minimal edits in place:
     - Fill `Definition` first. Treat an existing `<<COULD NOT BE DEFINED>>` as empty and look the
     term up again. Write the sentinel only when no source of any kind can be found — see
     `references/term-source-policy.md`.
     - Fill `Englischer Begriff` only when reliably inferable.
     - Convert blank or English-only `Deutscher Begriff` into the proper German term.
     - Keep existing validated wording unless it conflicts with these rules.
5. Term mode: create `tmp/output.csv` from scratch:
   - Header `Deutscher Begriff,Englischer Begriff,Definition`.
   - One row per requested term; fill `Definition` for each. If no definition can be found, use the
   sentinel from `references/term-source-policy.md`.
   - Fill `Englischer Begriff` when reliably inferable.
   - Normalize English-only input into the German `Deutscher Begriff` when clear.

Schema, writing rules, and validation live here. Source priority and evidence-gating rules are owned by
`references/term-source-policy.md`.

## CSV/TSV Tooling

This skill edits `.csv`/`.tsv` files in place. Use the repo's bundled `csv-util`, not
ad-hoc Python snippets:

- Run as `uv run csv-util <command> ...` from the repo root.
- Subcommands: `stats` (row/column/empty-cell counts), `check` (field-count and required
  columns), `cut` (select columns), `head` (preview rows), `drop-empty` (remove blank
  placeholder rows), `dedupe` (remove duplicates), `fill` (fill columns from a JSON map).
- Re-read a table before editing it; preserve the existing delimiter; trust file state
  over memory; validate immediately after writing.

## Writing Rules

- Match surrounding glossary wording; do not restyle the whole table.
- Semicolons in `Definition` unless commas need proper quoting.
- Standard German orthography (umlauts, `ß`) in definitions.
- Source-bound: do not add context, later interpretations, or evaluation beyond the cited source.
- No model-memory-only definitions — every `Definition` traces to an archived or cited authoritative
source.

## Validation

1. File mode: preserve delimiter, row order, column count.
2. Term mode: `tmp/output.csv` has the standard header and one row per term.
3. Every row has exactly three logical fields.
4. No silently blank `Definition` fields: every row must have either a definition or the literal
string `<<COULD NOT BE DEFINED>>`. Remove placeholder rows like `,,`.
5. Replace unintended commas in `Definition` with semicolons.
6. Every changed or generated non-empty `Definition` (except the `<<COULD NOT BE DEFINED>>` sentinel)
and `Englischer Begriff` is backed by an archived or cited authoritative source.
7. Newly archived term evidence is under `med-db/dictionary/<term-slug>/` and referenced from
`med-db/index.json`.

## Output

- Name updated files (or `tmp/output.csv` in term mode).
- Report rows or fields completed/generated.
- Name the sources used (classification code, dictionary, PMID/DOI, URL) or state which terms are
marked `<<COULD NOT BE DEFINED>>` because no evidence could be found after exhausting all sources.
- Call out ambiguous or undefinable terms explicitly.
