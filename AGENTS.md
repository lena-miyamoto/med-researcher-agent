# AGENTS.md

This repo is for the Medical DB workflow under `./med-db/`.

## Shared

- Make the smallest local change that works; if patch context is stale, re-read the exact snippet and retry; treat scratch files as ephemeral unless asked to preserve them.
- For German prose, use standard German orthography by default: write umlauts and `ß` normally instead of ASCII substitutions like `ae`, `oe`, `ue`, or `ss`, unless the user explicitly asks for ASCII or a technical constraint requires it.

## Medical DB (`./med-db/`)

- Use for medical, nutritional, or endometriosis literature collection and evidence summaries.
- The Python scripts live in `.agents/scripts/` and must be run from the repo root with Python `>= 3.12`. Later references omit the path and interpreter prefix for brevity.
- Treat `./med-db` as the local archive; create it if missing and keep every used search result, abstract, metadata record, and source page updated.
- Use NCBI E-utilities or `pubmed-med-db.py`, not PubMed HTML, as the primary PubMed workflow.
- Prefer formal evidence over general summaries; do not use mechanistic, animal, or risk-association studies as treatment evidence.
- Before concluding, rerun the exact machine-readable search and record query, access date, PMID, DOI, journal, and study type.
- If full text is blocked, summarize only what is supported by abstract, metadata, PMC, or accessible supplements.
- Use cautious wording, avoid turning absence of evidence into harm, and name important evidence limits.
- Use `pubmed-med-db.py` for archiving and `med-db-validate.py` for archive validation.
