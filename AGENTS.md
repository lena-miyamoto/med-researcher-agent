# AGENTS.md

This repo contains reusable medical research agent configuration and the local Medical DB workflow under `./med-db/`.

## Shared

- **ABSOLUTE PATHS WILL BREAK TOOL EXECUTION.** Every script in this repo MUST be invoked with a relative path from the repo root, exactly as shown in the canonical commands below. The tool-allow list ONLY matches the relative form. If you construct an absolute path like `/home/.../med-researcher-agent/.agents/scripts/med-db.py ...`, you WILL trigger a permission prompt on every single invocation — the command will not run automatically. Always use the form `python3 .agents/scripts/med-db.py ...` or `python3 .agents/scripts/med-db-validate.py ...`. This applies to every agent and every script in this repository.
- Make the smallest local change that works; if patch context is stale, re-read the exact snippet and retry; treat scratch files as ephemeral unless asked to preserve them.
- Keep cross-harness skill procedure in `.agents/skills/<name>/SKILL.md`; `.github/skills` and `.claude/skills` should stay as thin wrappers only.
- Keep cross-harness agent behavior in `.agents/agents/<name>.md`; `.github/agents` and `.claude/agents` should stay as thin harness wrappers only.
- For German prose, use standard German orthography by default: write umlauts and `ß` normally instead of ASCII substitutions like `ae`, `oe`, `ue`, or `ss`, unless the user explicitly asks for ASCII or a technical constraint requires it.

## Medical DB (`./med-db/`)

- Use for medical, nutritional, or endometriosis literature collection and evidence summaries.
- Canonical PubMed archival command: `python3 .agents/scripts/med-db.py --query '...' --archive-first N --validate`.
- Canonical Europe PMC archival command: `python3 .agents/scripts/med-db.py --source europe-pmc --query '...' --archive-first N --validate`.
- Canonical Europe PMC record command: `python3 .agents/scripts/med-db.py --source europe-pmc --epmc-record MED:35350465 --validate`.
- Canonical Google Scholar query archive command: `python3 .agents/scripts/med-db.py --source google-scholar --query '...' --search-slug '...' --validate`.
- Canonical open-access web discovery archive command: `python3 .agents/scripts/med-db.py --source doaj --query '...' --search-slug '...' --validate`.
- Canonical PMID archival command: `python3 .agents/scripts/med-db.py --pmid 12345678 --pmid 23456789 --validate`.
- Canonical validation command: `python3 .agents/scripts/med-db-validate.py --med-db med-db`.
- Supported web discovery sources: `google-scholar`, `doaj`, `open-science-directory`, `free-medical-journals`, `openmd`, `trip-database`.
- Use Google Scholar and the supported open-access web discovery sources in this workflow; archive reproducible query pages when available, otherwise archive source landing pages with the saved query text under `web/`; use PubMed and Europe PMC for structured machine-readable record archival.
- Repository-wide onboarding for GitHub Copilot lives in `.github/copilot-instructions.md`.
- Detailed medical-research behavior belongs in `.agents/agents/med-researcher.md`; harness wrappers live in `.github/agents/med-researcher.agent.md` and `.claude/agents/med-researcher.md`.
- Detailed shared-skill creation behavior belongs in `.agents/skills/create-med-skill/SKILL.md`; harness-specific skill wrappers live in `.github/skills/create-med-skill/SKILL.md` and `.claude/skills/create-med-skill/SKILL.md`.
- Detailed shared-agent creation behavior belongs in `.agents/skills/create-med-agent/SKILL.md`; harness-specific skill wrappers live in `.github/skills/create-med-agent/SKILL.md` and `.claude/skills/create-med-agent/SKILL.md`.
- Detailed instruction cleanup behavior belongs in `.agents/skills/optimize-repo/SKILL.md`; harness-specific skill wrappers live in `.github/skills/optimize-repo/SKILL.md` and `.claude/skills/optimize-repo/SKILL.md`.
- Detailed medical-claim analysis behavior belongs in `.agents/skills/analyze-med-claims/SKILL.md`; harness-specific skill wrappers live in `.github/skills/analyze-med-claims/SKILL.md` and `.claude/skills/analyze-med-claims/SKILL.md`.
- **Full-text access fallback** — When a scientific paper cannot be accessed in full (paywalled, only the abstract is openly available), attempt to retrieve the full text via Sci-Hub at `https://www.sci-hub.st/` using the paper's DOI. Papers published before 2022 are more likely to be available; papers published afterwards are available only occasionally but are still worth a try. Always prefer the official open-access source first; Sci-Hub is a fallback only.

## Medical DB structure (`./med-db/`)

- Treat `./med-db` as the local literature archive. Create it if missing.
- `./med-db/INDEX.md` is mandatory. Every archived search, paper, full-text capture, guideline, and web source must be listed there with title/identifier, canonical path, source, access date, and extraction notes. Update `INDEX.md` in the same change as every new or moved archive capture.
- Do not store primary source captures as loose files directly under `./med-db/`. Use the category subfolders below.
- Use lowercase kebab-case folder and file names. Prefer clear language suffixes for multi-language captures, for example `source.en.md`, `source.de.md`.
- Required top-level archive categories:
  - `searches/<topic-slug>/` for saved literature search queries as machine-readable JSON. Group by medical topic; use `_uncategorized/` when no topic is specified.
  - `papers/<topic-slug>/<identifier>-<title-slug>/` for individual paper records. Each paper folder must contain `metadata.json` (structured record from PubMed or Europe PMC) and `abstract.txt` (plain-text abstract). Metadata and abstract must be kept together — never store them in separate flat directories.
  - `fulltext/<topic-slug>/<identifier>-<title-slug>/` for full-text papers retrieved via open access or Sci-Hub fallback. Each folder must contain `source.md` with YAML frontmatter (`title`, `authors`, `source`, `source_url`, `access_date`, `language`, `extraction_notes`) and full text, plus the original `metadata.json`.
  - `guidelines/<topic-slug>/<title-slug>/` for clinical practice guidelines. Each folder must contain `source.<lang>.md` with YAML frontmatter.
  - `web/<topic-slug>/` for archived web pages or reproducible search definition pages used in review.
- **Paper archive standard** — Every paper folder under `papers/` must contain exactly `metadata.json` and `abstract.txt`. Every full-text capture under `fulltext/` must contain `source.md` with YAML frontmatter and `metadata.json`. Do not leave intermediate download artifacts in the archive.
- **YAML frontmatter on every source file.** Every `source.<lang>.md` and every full-text capture must open with a YAML frontmatter block containing at minimum: `title`, `authors`, `source`, `source_url`, `access_date` (YYYY-MM-DD), `language`, and `extraction_notes`.
- Prefer the archive and existing searches before ad-hoc web browsing. Check `INDEX.md` first, then `searches/`, then fetch externally.
- **External source priority for literature:** PubMed (E-utilities) and Europe PMC (REST API) for structured machine-readable records → DOAJ and open-access directories for full-text discovery → Google Scholar for broad searches → Sci-Hub for paywalled full-text fallback.
- Keep the medical evidence lens explicit and source-backed. Flag study types (RCT, systematic review, meta-analysis, cohort, case report, in-vitro, animal model) and distinguish risk, therapy, biomarker, and mechanistic evidence — these are not interchangeable.
- For reusable research write-ups, create new files under `tmp/` rather than overwriting the source brief or archived records.
