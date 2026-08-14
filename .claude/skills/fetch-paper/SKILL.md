---
name: fetch-paper
description: >
  Download the full text of a scientific paper or article (PDF plus extracted source text) into the
  med-db archive. Use when research needs a paper's full text identified by DOI, PMID, arXiv ID,
  Europe PMC record, title, or URL. Open-access papers are fetched legally; paywalled papers go
  straight to Sci-Hub, with legal alternatives tried only if Sci-Hub fails.
argument-hint: "DOI, PMID, arXiv ID, Europe PMC SOURCE:ID, title (+year), or URL of the paper to download"
user-invocable: true
---

# Fetch Paper

Downloads the full text of one scientific paper or article (PDF plus extracted source text) into the
med-db archive via `uv run med-db-download-paper`. Open-access papers are fetched from legal sources;
paywalled papers go straight to Sci-Hub, and legal alternatives are tried only if Sci-Hub fails. All
archive access rules follow the `med-db` skill.

## When to Use

- Research needs a paper's full text, referenced by DOI, PMID, arXiv ID, Europe PMC `SOURCE:ID`, title
  (+year), or URL.
- `med-researcher`, `evaluate-paper`, and `analyze-med-claims` delegate full-text retrieval here.
- **Not** for metadata/abstract-only archival — that is the `med-db` skill.
- **Not** for quality grading — that is the `evaluate-paper` skill.
- **Not** for web pages or guidelines — those are med-db archive categories, not papers.

## Procedure

### 1. Parse the reference

Detect the input type (the script auto-detects the same way):

| Input shape | Type |
| --- | --- |
| `10.1234/...` (DOI pattern) | DOI |
| All digits | PMID |
| `2203.15556` or `arXiv:2203.15556v2` | arXiv ID |
| `SOURCE:ID` (e.g. `MED:35350465`) | Europe PMC record |
| URL (host-classified: doi.org, arxiv.org, europepmc.org, pubmed, pmc, `.pdf`) | URL |
| Anything else | Title search (+ optional year) |

Ambiguous strings (e.g. a title that looks like `ABC: subtitle`) → force title search with `--title`.
Title matches can hit translations, reprints, or similarly titled papers — always confirm the
resolved title (step 3); if it is the wrong version, re-run with the DOI or PMID.

### 2. Check the archive first

Check whether the paper is already archived (read-only) via the `med-db` skill — by PMID, Europe PMC record, or keyword search on the title. If the
full text is already present, stop and report. The download script is idempotent and skips archived
papers anyway.

### 3. Resolve metadata

Resolve identifiers and get the canonical title via the `med-db` skill — `med-db-lookup` (read-only, no archival).

### 4. Download the full text

```text
uv run med-db-download-paper --reference <REF> --topic '<name>'
```

or `--title '<title>' --year <YEAR>`, or `--url <URL>`. Key flags: `--topic` (required), `--force`
(re-download), `--no-sci-hub` (disable the fallback), `--sci-hub-mirror <URL>` (mirror override),
`--email <address>` (E-utilities/Unpaywall/Crossref), `--format json|text`. Pass `--email` whenever
one is available — Unpaywall rejects requests without an email (HTTP 422).

The script runs the Source Chain below, writes the archive files, syncs `index.json`, and runs the
integrity check (exit code 1 on failure — fix immediately). See `.claude/agents/rules/med-db-commands.md`
for the complete parameter table.

### 5. Archive metadata if missing

If step 2 showed no `papers/` entry for the paper, archive the metadata record too via the `med-db` skill — `med-db` archival by PMID or DOI, always with `--topic`.
The full text is already in the archive after step 4; this step keeps `papers/` metadata complete.

### 6. Report

Report: archived path in `med-db/fulltext/`, identifier, source used, and the fallback chain taken
(from the script output).

## Source Chain (Policy)

The script first resolves the paper, then checks OpenAlex for open-access status. Every attempt is
recorded in `metadata.json` provenance (`source_chain`) and, on success, `source.md` frontmatter.

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

Every Sci-Hub download is recorded: `metadata.json` provenance (`sci_hub_used: true`, `pdf_source`)
and `source.md` frontmatter (`extraction_notes`). To disable Sci-Hub entirely, pass `--no-sci-hub`
(paywalled papers then fall back to the legal sources only).

PMC open access is intentionally absent: the PMC PDF endpoint now requires a JavaScript
proof-of-work challenge, and the PMC OA service is deprecated (ends 2026-08-24). Unpaywall and
OpenAlex surface PMC-hosted PDFs when available.

**Email:** pass `--email` whenever one is available — it enables Unpaywall and improves
E-utilities/Crossref polite-pool limits. A missing email no longer blocks the download: paywalled
papers go to Sci-Hub, and Unpaywall is simply skipped when no email is provided.

## Writing Rules

- All operations via `uv run` entry points — never edit `med-db/` files directly (black-box rule,
  `med-db` skill).
- Always pass `--topic` on archival and download commands.
- Never run downloads or any network/write operation during a live therapy session (`med-db` skill
  "During-Session / Real-Time Use").
- Cross-reference the `med-db` skill by name — do not restate its rules here.
- ASCII only.

## Validation

1. Archive folder exists under `med-db/fulltext/<topic-slug>/` with `paper.pdf` (unless text-only),
   `source.md`, and `metadata.json` — no empty files.
2. Integrity check passed (script exit code 0); on failure fix the reported errors.
3. Paywalled papers went to Sci-Hub before legal alternatives; open-access papers never used Sci-Hub.
   Any Sci-Hub use is recorded in `metadata.json` provenance and `source.md` frontmatter.
4. `papers/` metadata archived via the `med-db` skill (`med-db` archival, with `--topic`) when it was missing.
5. Report states: path, identifier, source used, fallback chain.

## Output

- `med-db/fulltext/<topic-slug>/<identifier>-<title-slug>/` — `paper.pdf` + `source.md` (YAML
  frontmatter: `title`, `authors`, `source`, `source_url`, `access_date`, `language`,
  `extraction_notes` + extracted text) + `metadata.json` (raw record + provenance).
- Updated `med-db/index.json` (fulltext entry).
- CLI report: text or `--format json`.
