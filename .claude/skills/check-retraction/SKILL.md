---
name: check-retraction
description: >
  Check whether a scientific paper is retracted or has an outstanding expression of concern, via the
  Crossref and PubMed APIs. Run before citing, trusting, archiving, or scoring any paper.
argument-hint: 'DOI, PMID, or paper title to check'
user-invocable: true
---

# Check Retraction

Determines whether a paper is retracted or has an outstanding expression of concern. Sole owner of
retraction checking in this repo — other skills and agents delegate here.

## When to Use

- A paper needs its retraction status confirmed before it is cited, trusted, archived, or scored.
- Input is a DOI (preferred), PMID, or paper title.

## Procedure

### 1. Resolve the identifier

- DOI → use directly.
- PMID → use directly.
- Title → resolve to DOI (WebSearch or Crossref `query.bibliographic`), then confirm the resolved
  title matches before checking.

### 2. Run the check

Crossref is the single authoritative retraction source — do not query any separate retraction
database or API. Run the deterministic checker (Crossref primary + PubMed cross-check, with DOI↔PMID
resolution built in):

```bash
uv run check-retraction --doi <DOI>
uv run check-retraction --pmid <PMID>
```

The script inspects the Crossref `update-to` array (a retracted paper has an entry with
`type: "retraction"`; publisher-registered and third-party-integrated records are both exposed there)
and the PubMed `pubtype` field. It returns a JSON verdict with `status`, `sources_checked`, and
per-source detail; pass `--format text` for a human-readable summary.

The script reads only the direct DOI record — never the fuzzy
`filter=update-type:retraction&query.bibliographic=...` endpoint, which matches unrelated records.

### 3. Fallback when the record is inconclusive

If the script returns `status: unknown` (network or API failure), WebSearch the paper title plus
`retracted` — the most reliable cross-source check.

## Decision rules

- **`retracted`** → report it with the retraction date, source, and reason if findable. Verify with
  at least two sources.
- **`expression-of-concern`** → report it; do not treat the paper as clean.
- **`not-retracted`** → report it and state which sources were checked.
- **`unknown`** → fall back to step 3; if still inconclusive, say so.

## Output

Summarise the script verdict as: `status` (`retracted` / `expression-of-concern` / `not-retracted` /
`unknown`), `sources checked`, and `retraction date` + `reason` when available.

## Validation

1. Ran `uv run check-retraction` on the direct identifier (never the fuzzy bibliographic filter).
2. Retracted papers are reported with the retraction record, not a bare flag.
3. A `not-retracted` verdict names the sources that were checked.
