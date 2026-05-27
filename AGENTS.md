# AGENTS.md

This repo contains reusable medical research agent configuration and the local Medical DB workflow under `./med-db/`.

## Shared

- Make the smallest local change that works; if patch context is stale, re-read the exact snippet and retry; treat scratch files as ephemeral unless asked to preserve them.
- For German prose, use standard German orthography by default: write umlauts and `ß` normally instead of ASCII substitutions like `ae`, `oe`, `ue`, or `ss`, unless the user explicitly asks for ASCII or a technical constraint requires it.

## Medical DB (`./med-db/`)

- Use for medical, nutritional, or endometriosis literature collection and evidence summaries.
- Canonical PubMed archival command: `med-db.py --query '...' --archive-first N --validate`.
- Canonical Europe PMC archival command: `med-db.py --source europe-pmc --query '...' --archive-first N --validate`.
- Canonical Europe PMC record command: `med-db.py --source europe-pmc --epmc-record MED:35350465 --validate`.
- Canonical Google Scholar query archive command: `med-db.py --source google-scholar --query '...' --search-slug '...' --validate`.
- Canonical PMID archival command: `med-db.py --pmid 12345678 --pmid 23456789 --validate`.
- Canonical validation command: `med-db-validate.py --med-db med-db`.
- Use Google Scholar in this workflow as a broader discovery surface and archive reproducible query pages under `web/`; use PubMed and Europe PMC for structured machine-readable record archival.
- Repository-wide onboarding for GitHub Copilot lives in `.github/copilot-instructions.md`.
- Detailed medical-research behavior belongs in the dedicated med-researcher agent definitions under `.github/agents/med-researcher.agent.md` and `.claude/agents/med-researcher.md`.
