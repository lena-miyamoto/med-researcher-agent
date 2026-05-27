# Copilot Repository Instructions

This repository contains reusable medical-research agent configuration plus the local `med-db/` archive and helper scripts used for evidence-backed medical and nutrition research.

## Repository Layout

- `AGENTS.md`: repo-wide, tool-agnostic context.
- `CLAUDE.md`: Claude Code routing and imports.
- `.github/agents/med-researcher.agent.md`: GitHub Copilot custom medical-research agent.
- `.claude/agents/med-researcher.md`: Claude Code subagent with the same medical-research focus.
- `.agents/scripts/`: archive helper scripts. Run them from the repo root with Python `>= 3.12`.
- `med-db/`: local archive for searches, metadata, abstracts, and source pages.
- `tmp/`: scratch outputs and generated markdown deliverables.

## Instruction Boundaries

- Keep repo-wide guidance in this file or `AGENTS.md`.
- Keep specialized medical-research workflow in the dedicated med-researcher agent files, not in `AGENTS.md`.
- Avoid duplicating the same domain workflow across `AGENTS.md`, `CLAUDE.md`, and agent prompts.

## Research And Archive Rules

- Prefer formal evidence over general summaries: guidelines, systematic reviews or meta-analyses, randomized trials, then observational studies.
- Do not treat mechanistic, animal, or risk-association studies as treatment evidence.
- Use NCBI E-utilities or the local archival script for PubMed, Europe PMC, and archived web-source workflows instead of PubMed HTML.
- Use Europe PMC as a second structured literature source when it adds relevant coverage, especially for preprints, full-text-linked records, or citation-network exploration.
- Use Google Scholar as a broader discovery surface and archive reproducible query pages or downstream accessible sources under `web/` instead of relying on brittle structured scraping.
- If full text is blocked, summarize only what is supported by abstracts, metadata, PMC, or accessible supplements.
- Use cautious wording and do not turn absence of evidence into harm.

## Deliverable Defaults

- Do not overwrite a user-supplied research brief markdown file unless the user explicitly asks to edit that exact file.
- For reusable research write-ups, create two sibling files by default: `<research-topic>.leitfaden.md` and `<research-topic>.patienten.md`.

## Validation

- After changing archive structure or relying on newly archived content, follow the canonical validation command in `AGENTS.md`.
- When editing instruction or agent markdown files, verify frontmatter and markdown diagnostics before finishing.
