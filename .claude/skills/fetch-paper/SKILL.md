---
name: fetch-paper
description: >
  Download the full text of a scientific paper or article (PDF plus extracted source text) into the
  med-db archive. Use when research needs a paper's full text identified by DOI, PMID, arXiv ID,
  Europe PMC record, title, or URL. Legal open-access sources first; Sci-Hub only as last resort.
argument-hint: "DOI, PMID, arXiv ID, Europe PMC SOURCE:ID, title (+year), or URL of the paper to download"
user-invocable: true
---

# Fetch Paper

Downloads the full text of one scientific paper or article (PDF plus extracted source text) into the
med-db archive via `uv run med-db-download-paper`. Legal open-access sources are tried first; Sci-Hub
is a last-resort fallback. All archive access rules follow the med-db skill (`.claude/skills/med-db/SKILL.md`).

## When to Use

- Research needs a paper's full text, referenced by DOI, PMID, arXiv ID, Europe PMC `SOURCE:ID`, title
  (+year), or URL.
- `med-researcher`, `evaluate-paper`, and `analyze-med-claims` delegate full-text retrieval here.
- **Not** for metadata/abstract-only archival — that is the med-db skill (`.claude/skills/med-db/SKILL.md`).
- **Not** for quality grading — that is the evaluate-paper skill (`.claude/skills/evaluate-paper/SKILL.md`).
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

Check whether the paper is already archived (read-only): `uv run med-db-query` — by PMID, Europe PMC
record, or keyword search on the title. If the full text is already present, stop and report. The
download script is idempotent and skips archived papers anyway.

### 3. Resolve metadata

`uv run med-db-lookup --doi <DOI>` / `--pmid <ID>` / `--epmc-record <SOURCE:ID>` (read-only, no
archival) to confirm identifiers and get the canonical title.

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

If step 2 showed no `papers/` entry for the paper, archive the metadata record too:

```text
uv run med-db --pmid <ID> --topic '<name>'
uv run med-db --doi <DOI> --topic '<name>'
```

The full text is already in the archive after step 4; this step keeps `papers/` metadata complete.

### 6. Report

Report: archived path in `med-db/fulltext/`, identifier, source used, and the fallback chain taken
(from the script output).

## Source Chain (Policy)

The script tries sources in this exact order and stops at the first success. Every attempt is recorded
in `metadata.json` provenance (`source_chain`) and, on success, `source.md` frontmatter.

1. **Europe PMC fullTextXML** — open-access full text for Europe PMC records (coverage varies by paper;
   also attempted for PMID/DOI-resolved records via the `MED:<pmid>` alias).
2. **Unpaywall** — best open-access location for the DOI. Requires a real email via `--email`
   (placeholder domains are rejected with HTTP 422).
3. **OpenAlex** — best open-access location for the DOI.
4. **Publisher open access** — DOI content negotiation (`Accept: application/pdf`).
5. **arXiv** — direct PDF for arXiv IDs.
6. **Sci-Hub — last resort only.** Use only when every legal/open source above failed and the paper
   is otherwise unobtainable. Never use Sci-Hub for papers available from any legal source. Every
   Sci-Hub download is recorded: `metadata.json` provenance (`sci_hub_used: true`, `pdf_source`) and
   `source.md` frontmatter (`extraction_notes`). To disable the fallback entirely, pass `--no-sci-hub`.

PMC open access is intentionally absent: the PMC PDF endpoint now requires a JavaScript
proof-of-work challenge, and the PMC OA service is deprecated (ends 2026-08-24). Unpaywall and
OpenAlex surface PMC-hosted PDFs when available.

**Missing email rule:** when a legal source needs a real email address and none is available, ask
the user to enter one. Offer Sci-Hub as the alternative the user may approve. Always present both
options — the user decides. Never fail silently or proceed to Sci-Hub without the user's choice.

## Writing Rules

- All operations via `uv run` entry points — never edit `med-db/` files directly (black-box rule,
  med-db skill `.claude/skills/med-db/SKILL.md`).
- Always pass `--topic` on archival and download commands.
- Never run downloads or any network/write operation during a live therapy session (med-db skill
  "During-Session / Real-Time Use").
- Cross-reference the med-db skill by path — do not restate its rules here.
- ASCII only.

## Validation

1. Archive folder exists under `med-db/fulltext/<topic-slug>/` with `paper.pdf` (unless text-only),
   `source.md`, and `metadata.json` — no empty files.
2. Integrity check passed (script exit code 0); on failure fix the reported errors.
3. Legal sources were tried before any Sci-Hub use; any Sci-Hub use is recorded in `metadata.json`
   provenance and `source.md` frontmatter.
4. `papers/` metadata archived via `uv run med-db ... --topic '<name>'` when it was missing.
5. Report states: path, identifier, source used, fallback chain.

## Output

- `med-db/fulltext/<topic-slug>/<identifier>-<title-slug>/` — `paper.pdf` + `source.md` (YAML
  frontmatter: `title`, `authors`, `source`, `source_url`, `access_date`, `language`,
  `extraction_notes` + extracted text) + `metadata.json` (raw record + provenance).
- Updated `med-db/index.json` (fulltext entry).
- CLI report: text or `--format json`.
