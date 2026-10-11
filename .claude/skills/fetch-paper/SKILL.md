---
name: fetch-paper
description: >
  Download the full text of a scientific paper or article (PDF plus extracted source text) into the
  archive. Use when research needs a paper's full text identified by DOI, PMID, arXiv ID,
  Europe PMC record, title, or URL. Open-access papers are fetched legally; paywalled papers go
  straight to Sci-Hub, with legal alternatives tried only if Sci-Hub fails. When the automatic chain
  fails, an interactive archive.is scrape (fetch-archive) can feed the text in via --body-file.
argument-hint: "DOI, PMID, arXiv ID, Europe PMC SOURCE:ID, title (+year), or URL of the paper to download"
user-invocable: true
---

# Fetch Paper

Downloads the full text of one scientific paper or article (PDF plus extracted source text) into the
archive via the `med-db` skill. Open-access papers are fetched from legal sources;
paywalled papers go straight to Sci-Hub, and legal alternatives are tried only if Sci-Hub fails. All
archive access rules follow the `med-db` skill.

## When to Use

- Research needs a paper's full text, referenced by DOI, PMID, arXiv ID, Europe PMC `SOURCE:ID`, title
  (+year), or URL.
- `med-researcher`, `evaluate-paper`, and `analyze-med-claims` delegate full-text retrieval here.
- **Not** for metadata/abstract-only archival — that is the `med-db` skill.
- **Not** for quality grading — that is the `evaluate-paper` skill.
- **Not** for web pages or guidelines — those are archive categories, not papers.

## Procedure

### 1. Parse the reference

Detect the input type (the script auto-detects the same way):

| Input shape                                                                   | Type                           |
| ----------------------------------------------------------------------------- | ------------------------------ |
| `10.1234/...` (DOI pattern)                                                   | DOI                            |
| All digits                                                                    | PMID                           |
| `2203.15556` or `arXiv:2203.15556v2`                                          | arXiv ID                       |
| `SOURCE:ID` (e.g. `MED:35350465`)                                             | Europe PMC record              |
| URL (host-classified: doi.org, arxiv.org, europepmc.org, pubmed, pmc, `.pdf`) | URL                            |
| Anything else                                                                 | Title search (+ optional year) |

Ambiguous strings (e.g. a title that looks like `ABC: subtitle`) → force title search with `--title`.
Title matches can hit translations, reprints, or similarly titled papers — always confirm the
resolved title (step 3); if it is the wrong version, re-run with the DOI or PMID.

### 2. Check the archive first

Check whether the paper is already archived (read-only) via the `med-db` skill — by PMID, Europe PMC record, or keyword search on the title. If the
full text is already present, stop and report. The download script is idempotent and skips archived
papers anyway.

### 3. Resolve metadata

Resolve identifiers and get the canonical title via the `med-db` skill (read-only, no archival).

### 4. Download the full text

Download the full text via the `med-db` skill, telling it which reference to fetch. Pass the
reference, or a title with optional year, or a URL. Key
flags: `--topic` (required), `--force`
(re-download), `--no-sci-hub` (disable the fallback), `--sci-hub-mirror <URL>` (mirror override),
`--email <address>` (E-utilities/Unpaywall/Crossref), `--body-file <FILE>` (ingest externally
obtained full text, see archive.is fallback below), `--format json|text`. Pass `--email` whenever
one is available — Unpaywall rejects requests without an email (HTTP 422).

The script runs the Source Chain below, writes the archive entries, syncs the archive index, and runs the
integrity check (exit code 1 on failure — fix immediately). See `.claude/agents/references/med-db-commands.md`
for the complete parameter table.

### 5. Archive metadata if missing

If step 2 showed no paper metadata record, archive it too via the `med-db` skill — archival by PMID or DOI, always with `--topic`.
The full text is already in the archive after step 4; this step keeps the paper metadata complete.

### 6. Report

Report: archived path in the local archive, identifier, source used, and the fallback chain taken
(from the script output).

## Source Chain (Policy)

The script first resolves the paper, then checks OpenAlex for open-access status. Every attempt is
recorded in the archived record's provenance (`source_chain`) and, on success, its source frontmatter.

- **Europe PMC fullTextXML** — open-access full text for Europe PMC records (coverage varies by paper;
  also attempted for PMID/DOI-resolved records via the `MED:<pmid>` alias).
- **OpenAlex** — authoritative open-access status (`is_oa`) plus best OA PDF location. Needs no email,
  so it is the detection step the branch below depends on.
- **Open access → legal sources**, in order, stop at first success: OpenAlex OA PDF, Unpaywall (only
  when `--email` is given — without one it always returns HTTP 422), publisher open access via DOI
  content negotiation (`Accept: application/pdf`), then arXiv.
- **Paywalled (`is_oa: false`) → Sci-Hub first.** Do not try publisher content negotiation or
  Unpaywall before Sci-Hub; a paywalled DOI just returns an HTML paywall page. Legal alternatives run
  only after Sci-Hub fails or when Sci-Hub is disabled.

Every Sci-Hub download is recorded: archived provenance (`sci_hub_used: true`, `pdf_source`)
and source frontmatter (`extraction_notes`). To disable Sci-Hub entirely, pass `--no-sci-hub`
(paywalled papers then fall back to the legal sources only).

**Manual archive.is fallback.** When the automatic chain fails (Sci-Hub mirrors down, no open-access
copy), offer the user an interactive archive.is scrape. It opens a visible browser and waits for a
human CAPTCHA solve, so it is never auto-run — only propose it when the user can solve the CAPTCHA.
Host prerequisite: `uvx playwright install chromium`.

```text
uv run fetch-archive '<article-url>' -o tmp/<slug>.txt
```

Passing the scraped file to the `med-db` skill (`--body-file`) skips steps 1-4 of the source chain and
archives the file's text as the full text;
metadata resolution still runs, so `--reference` or `--title` is required. Provenance records
`extraction_method: archive.is-scrape` and `pdf_source: null`; the chain shows `archive.is ok`.

PMC open access is intentionally absent: the PMC PDF endpoint now requires a JavaScript
proof-of-work challenge, and the PMC OA service is deprecated (ends 2026-08-24). Unpaywall and
OpenAlex surface PMC-hosted PDFs when available.

**Email:** pass `--email` whenever one is available — it enables Unpaywall and improves
E-utilities/Crossref polite-pool limits. A missing email no longer blocks the download: paywalled
papers go to Sci-Hub, and Unpaywall is simply skipped when no email is provided.

## Writing Rules

- All operations via `uv run` entry points — never edit the local archive directly (black-box rule,
  `med-db` skill).
- Always pass `--topic` on archival and download commands.
- Never run downloads or any network/write operation during a live therapy session (`med-db` skill
  "During-Session / Real-Time Use").
- Cross-reference the `med-db` skill by name — do not restate its rules here.
- ASCII only.

## Validation

1. Archive folder exists in the local archive under `<topic-slug>/` with the expected file set for
   its category (per the `med-db` skill: PDF unless text-only, source text, metadata) — no empty files.
2. Integrity check passed (script exit code 0); on failure fix the reported errors.
3. Paywalled papers went to Sci-Hub before legal alternatives; open-access papers never used Sci-Hub.
   Any Sci-Hub use is recorded in the archived provenance and source frontmatter.
4. Paper metadata archived via the `med-db` skill (archival, with `--topic`) when it was missing.
5. Report states: path, identifier, source used, fallback chain.

## Output

- Full-text folder in the local archive — file set and folder structure are defined by the `med-db`
  skill (PDF, extracted source text, and metadata with provenance).
- Updated archive index in the local archive (fulltext entry).
- CLI report: text or `--format json`.
