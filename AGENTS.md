# AGENTS.md

This repo contains reusable medical research agent configuration and the local Medical DB workflow under `./med-db/`.

## Shared

- **`uv` is required for running skills in this repo.** Install `uv` first, then invoke repo tooling through `uv run ...` from the repo root.
- **Canonical test command: `uv run test`.** Always run this after editing any `*.py` file in the repo. No other test invocation is acceptable.
- **ABSOLUTE PATHS WILL BREAK TOOL EXECUTION.** Use the canonical `uv run ...` commands from the repo root exactly as shown below. Do not construct absolute script paths like `/home/.../med-researcher-agent/.agents/scripts/med-db.py ...`, or you will trigger permission prompts and bypass the repo-standard invocation path.
- Keep cross-harness skill procedure in `.agents/skills/<name>/SKILL.md`; `.github/skills` and `.claude/skills` should stay as thin wrappers only.
- Keep cross-harness agent behavior in `.agents/agents/<name>.md`; `.github/agents` and `.claude/agents` should stay as thin harness wrappers only.
- **Shared utilities go in `.agents/scripts/utils.py`.** When a helper function, constant, or data structure is needed by more than one script under `.agents/scripts/`, put it in `utils.py` and import it from there. Do *not* copy-paste the same logic into a second script — code drift between copies causes subtle, hard-to-catch bugs (e.g. one copy gets error handling added, the other doesn't). Conversely, do *not* pre-emptively move something into `utils.py` just because it *might* be reused later. A function or constant that is only consumed by a single script belongs in that script. Use common sense: the bar for extraction is *actual* duplication across at least two scripts, not speculative generalization.
- For German prose, use standard German orthography by default: write umlauts and `ß` normally instead of ASCII substitutions like `ae`, `oe`, `ue`, or `ss`, unless the user explicitly asks for ASCII or a technical constraint requires it.

## Medical DB (`./med-db/`)

- Use for medical, nutritional, or endometriosis literature collection and evidence summaries.
- Canonical PubMed archival command: `uv run med-db --query '...' --archive-first N --validate`.
- Canonical Europe PMC archival command: `uv run med-db --source europe-pmc --query '...' --archive-first N --validate`.
- Canonical Europe PMC record command: `uv run med-db --source europe-pmc --epmc-record MED:35350465 --validate`.
- Canonical Google Scholar query archive command: `uv run med-db --source google-scholar --query '...' --search-slug '...' --validate`.
- Canonical open-access web discovery archive command: `uv run med-db --source doaj --query '...' --search-slug '...' --validate`.
- Canonical PMID archival command: `uv run med-db --pmid 12345678 --pmid 23456789 --validate`.
- Canonical validation command: `uv run med-db-validate --med-db med-db`.
- Canonical PMID lookup command (fetch metadata without archival): `uv run med-db-lookup --pmid 12345678`.
- Canonical batch PMID lookup command: `uv run med-db-lookup --pmid 12345678 --pmid 23456789`.
- Canonical Europe PMC record lookup command: `uv run med-db-lookup --epmc-record MED:35350465`.
- Canonical DOI resolution command: `uv run med-db-lookup --doi 10.1000/xyz`.
- Canonical archive topic listing command: `uv run med-db-query --list-topics`.
- Canonical topic paper listing command: `uv run med-db-query --topic adhd`.
- Canonical PMID archival check command: `uv run med-db-query --check-pmid 12345678`.
- Canonical Europe PMC archival check command: `uv run med-db-query --check-epmc MED:35350465`.
- Canonical keyword search command: `uv run med-db-query --search-keyword lisdexamfetamine`.
- Canonical topic-scoped keyword search command: `uv run med-db-query --search-keyword lisdexamfetamine --search-topic adhd`.
- Canonical search JSON PMID extraction command: `uv run med-db-query --pmids-from-search searches/adhd/pubmed-search.json`.
- Canonical paper metadata read command: `uv run med-db-query --read-metadata papers/adhd/pmid-12345-title-slug`.
- Both lookup and query scripts default to JSON output. Use `--format text` for human-readable output.
- Supported web discovery sources: `google-scholar`, `doaj`, `open-science-directory`, `free-medical-journals`, `openmd`, `trip-database`.
- Use Google Scholar and the supported open-access web discovery sources in this workflow; archive reproducible query pages when available, otherwise archive source landing pages with the saved query text under `web/`; use PubMed and Europe PMC for structured machine-readable record archival.
- Skill procedure lives in `.agents/skills/<name>/SKILL.md`; wrappers in `.github/skills/<name>/SKILL.md` and `.claude/skills/<name>/SKILL.md`.
- Agent behavior lives in `.agents/agents/<name>.md`; wrappers in `.github/agents/<name>.agent.md` and `.claude/agents/<name>.md`.
- Repo-wide onboarding for GitHub Copilot lives in `.github/copilot-instructions.md`.
- **Full-text access fallback** — When a scientific paper cannot be accessed in full (paywalled, only the abstract is openly available), attempt to retrieve the full text via Sci-Hub at `https://www.sci-hub.st/` using the paper's DOI. Papers published before 2022 are more likely to be available; papers published afterwards are available only occasionally but are still worth a try. Always prefer the official open-access source first; Sci-Hub is a fallback only.

## Medical DB structure (`./med-db/`)

- Treat `./med-db` as the local literature archive. Create it if missing.
- `./med-db/INDEX.md` is mandatory. Every archived search, paper, full-text capture, guideline, and web source must be listed there with title/identifier, canonical path, source, access date, and extraction notes. Update `INDEX.md` in the same change as every new or moved archive capture.
- Do not store primary source captures as loose files directly under `./med-db/`. Use the category subfolders below.
- Use lowercase kebab-case folder and file names. Prefer clear language suffixes for multi-language captures, for example `source.en.md`, `source.de.md`.
- Required top-level archive categories:
  - `searches/<topic-slug>/` for saved literature search queries as machine-readable JSON. Group by medical topic; use `uncategorized/` when no topic is specified.
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
