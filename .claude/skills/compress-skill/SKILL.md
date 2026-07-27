---
name: compress-skill
description: "Compresses instruction .md files to cut token cost, keeping meaning exact. Accepts a file, directory, glob, or list of these. Rewrites body text in place: short fragments, plain words, technical jargon kept verbatim. No scripts, no external calls. Skips README.md, CONTRIBUTING.md, DEVELOPMENT.md, CHANGELOG.md unless named directly. Invoke after editing any instruction file, or when explicitly asked to compress instruction files."
disable-model-invocation: false
user-invocable: true
---

# compress-skill

Compress instruction `.md` files. Cut token cost, keep meaning exact.

## Input handling

Arg: file path, directory, glob, or space/comma-separated list.

- File → target directly.
- Directory → `find <dir> -name '*.md'` via `Bash`.
- Glob pattern → expand via `Bash` (`shopt -s globstar nullglob; printf '%s\n' <pattern>`).
- List → split on whitespace/comma; resolve each per rules above; dedupe.

No arg → ask for file(s), directory, or glob; stop until given.

## Scope — skip by default

Files named `README.md`, `CONTRIBUTING.md`, `DEVELOPMENT.md`, `CHANGELOG.md`.

Override: file named directly as arg → process anyway. Files pulled in via directory/glob/list stay filtered.

## Process

Per file, one pass — no scripts, no external calls:

1. Resolve arg into target list (see Input handling).
2. Scope check per file — skip if matched, unless named directly as a file arg.
3. Read file (skip if already in context this turn). Already dense → skip file, note it, continue.
4. Rewrite body text via `Edit`/`Write`, applying rules below.
5. Self-check (below), using content already in context — no new Read call. Fix in place if needed.
6. Repeat 2–5 per remaining file.

## Lossless definition

Lossless means these survive compression exactly as in the original, with unchanged strength and order:

- Emphasis keywords and formatting — bold, italic, and emphasis words (CRITICAL, MUST, NEVER, ALWAYS,
  IMPORTANT, ESSENTIAL).
- Temporal framing — sequencing and timing words (before, after, at session opening, first, then).
- Enumerated elements — count and order of listed items, especially when items carry distinct meanings
  or the list defines a complete set (e.g., "four non-negotiable elements: ...").
- Identity-level claims — statements about what something *is* or *is not*, category membership,
  foundational definitions ("you are [not] practicing from...", "this is [not]...").
- Consequence statements — cause-effect chains, conditional outcomes ("Without X, Y", "You cannot...
  without...", "Skipping this means...").
- Per-item symmetry — if every item in a list carries a shared emphasis phrase (e.g., "Never skip it"),
  all items must retain it equally.

Any compression that loses one of these categories is over-optimized — restore the lost content.

## Compression rules

### Word + sentence level

- Fragments, not full sentences; drop subject, articles (a/an/the).
- Cut filler (just, really, basically, actually, simply, essentially, generally), pleasantries (sure, certainly, happy to), hedging (might be worth, could consider, it would be good to), connective fluff (however, furthermore, additionally, in addition).
- Shorten redundant phrasing: "in order to" → "to", "make sure to" → "ensure", "the reason is because" → "because", "utilize" → "use".
- Plain, everyday words. Exception: technical jargon (library/API names, protocols, CLI flags, error strings) — keep exact, never paraphrase or simplify.
- Sentences that must stay full: ≤20 words.
- Merge or cut bullets/examples making the same point twice.
- Comparatives (more than N, at least N, no more than N, up to N) → keep direction exact. Don't collapse to shorthand like "N+" — that can silently shift the threshold.

### Never touch — preserve byte-exact

- Code blocks (fenced + indented), inline code, inline formatting (`**bold**`, `*italic*`)
- URLs, markdown links, file paths, commands, env vars
- Technical terms, proper nouns, numbers, dates, version strings
- Emphasis keywords beyond must/should/never/always: `CRITICAL`, `IMPORTANT:`, `YOU MUST`, `NEVER`,
  `ALWAYS`, `ESSENTIAL`, `MANDATORY`, `NOT OPTIONAL` — treat as obligation words, never weaken or drop.
- Headings (exact text + order), list nesting, table structure (compress cell text only), frontmatter/YAML

### Self-check before done

Compare to original, from context, once:

- Byte-exact spans above unchanged?
- Heading count + order unchanged?
- No leaked meta-commentary, stray `---`, or fence artifacts?
- Emphasis markers (bold `**`/`__`, italic `*`/`_`) and all emphasis keywords (CRITICAL, IMPORTANT,
  YOU MUST, NEVER, ALWAYS, ESSENTIAL, MANDATORY, NOT OPTIONAL, must, should, always, never) unchanged
  in presence, strength, and direction?
- Temporal framing words (before/after, first/then, at session opening, sequencing) preserved?
- Enumerated element count and order preserved when the enumeration defines a complete set or carries
  distinct meanings per item?
- Identity-level claims ("you are [not]...", "this is [not]...", category membership) unchanged?
- Consequence statements ("Without X, Y", "You cannot... without...", "Skipping this means...",
  cause-effect chains) preserved in full?
- Per-item symmetric emphasis (e.g., "Never skip it" on every item) preserved equally?
- Trailing newline still there?

Any check fails → fix directly. Don't restart from scratch.

## Pattern

Example: "You should always make sure to run the test suite before pushing any changes to the main branch. This is important because it helps catch bugs early and prevents broken builds from being deployed to production." → "Run tests before push to main. Catches bugs early, prevents broken prod deploys."
