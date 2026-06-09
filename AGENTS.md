# AGENTS.md

This repo contains reusable medical research agent configuration and the local Medical DB workflow under `./med-db/`.

## Shared

- Make the smallest local change that works; if patch context is stale, re-read the exact snippet and retry; treat scratch files as ephemeral unless asked to preserve them.
- Keep cross-harness skill procedure in `.agents/skills/<name>/SKILL.md`; `.github/skills` and `.claude/skills` should stay as thin wrappers only.
- Keep cross-harness agent behavior in `.agents/agents/<name>.md`; `.github/agents` and `.claude/agents` should stay as thin harness wrappers only.
- For German prose, use standard German orthography by default: write umlauts and `ß` normally instead of ASCII substitutions like `ae`, `oe`, `ue`, or `ss`, unless the user explicitly asks for ASCII or a technical constraint requires it.

## Medical DB (`./med-db/`)

- Use for medical, nutritional, or endometriosis literature collection and evidence summaries.
- Canonical PubMed archival command: `med-db.py --query '...' --archive-first N --validate`.
- Canonical Europe PMC archival command: `med-db.py --source europe-pmc --query '...' --archive-first N --validate`.
- Canonical Europe PMC record command: `med-db.py --source europe-pmc --epmc-record MED:35350465 --validate`.
- Canonical Google Scholar query archive command: `med-db.py --source google-scholar --query '...' --search-slug '...' --validate`.
- Canonical open-access web discovery archive command: `med-db.py --source doaj --query '...' --search-slug '...' --validate`.
- Canonical PMID archival command: `med-db.py --pmid 12345678 --pmid 23456789 --validate`.
- Canonical validation command: `med-db-validate.py --med-db med-db`.
- Supported web discovery sources: `google-scholar`, `doaj`, `open-science-directory`, `free-medical-journals`, `openmd`, `trip-database`.
- Use Google Scholar and the supported open-access web discovery sources in this workflow; archive reproducible query pages when available, otherwise archive source landing pages with the saved query text under `web/`; use PubMed and Europe PMC for structured machine-readable record archival.
- Repository-wide onboarding for GitHub Copilot lives in `.github/copilot-instructions.md`.
- Detailed medical-research behavior belongs in `.agents/agents/med-researcher.md`; harness wrappers live in `.github/agents/med-researcher.agent.md` and `.claude/agents/med-researcher.md`.
- Detailed shared-skill creation behavior belongs in `.agents/skills/create-med-skill/SKILL.md`; harness-specific skill wrappers live in `.github/skills/create-med-skill/SKILL.md` and `.claude/skills/create-med-skill/SKILL.md`.
- Detailed shared-agent creation behavior belongs in `.agents/skills/create-med-agent/SKILL.md`; harness-specific skill wrappers live in `.github/skills/create-med-agent/SKILL.md` and `.claude/skills/create-med-agent/SKILL.md`.
- Detailed instruction cleanup behavior belongs in `.agents/skills/optimize-repo/SKILL.md`; harness-specific skill wrappers live in `.github/skills/optimize-repo/SKILL.md` and `.claude/skills/optimize-repo/SKILL.md`.
- **Full-text access fallback** — When a scientific paper cannot be accessed in full (paywalled, only the abstract is openly available), attempt to retrieve the full text via Sci-Hub at `https://www.sci-hub.st/` using the paper's DOI. Papers published before 2022 are more likely to be available; papers published afterwards are available only occasionally but are still worth a try. Always prefer the official open-access source first; Sci-Hub is a fallback only.
