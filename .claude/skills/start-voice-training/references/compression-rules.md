---
description: >
  Token-efficient compression rules for voice training session history files.
  Applied after every session (SKILL.md Step 6) to minimize token cost
  when the history file is loaded into context.
---

# Compression Rules

After writing session note, run compression pass on **Session Log Archive section only**. Goal: minimize
token count without losing training-important information. File read into context at every session
start — every token matters.

## Permanent Client Profile — Never Compressed

`## Permanent Client Profile` section and everything under it **exempt from all compression rules**.
Do not remove, rewrite, abbreviate, or collapse any content in this section. Contains intake information
and training-essential facts that must persist verbatim across all sessions. Only update by adding new
information (Step 5b) or correcting outdated facts (e.g., client's pronouns changed).

## Rules (Apply to Session Log Archive Only)

- **Remove filler.** Cut words that don't carry information: "the client practiced," "we worked on," "it was noted that."
  Replace with direct, compact phrasing. "Straw phonation glides — good forward resonance, tension in jaw."

- **Use sentence fragments.** Full grammatical sentences cost tokens. Bullet-point style is preferred throughout.

- **Abbreviate consistently.** Establish abbreviations in the frontmatter and reuse: `SOVTE` (semi-occluded
  vocal tract exercise), `F0` (fundamental frequency, pitch), `GAHT` (gender-affirming hormone therapy),
  `HNO` (Hals-Nasen-Ohren / ENT), `FemLar` (feminization laryngoplasty), `TWVQ` (Trans Woman Voice
  Questionnaire), `MPT` (maximum phonation time). Use standard voice-science abbreviations only — never invent
  ambiguous ones. Measurements keep their units: `185 Hz`, `MPT 14 s`.

- **Merge redundant entries.** Same theme across multiple sessions → consolidate rather than repeat:
  "Sessions 3–5: consistent 10-min daily straw routine, evening slots." Don't lose timeline — note when theme
  first appeared and whether active or resolved.

- **Keep verbatim quotes.** Client language is high-signal. Preserve short verbatim quotes that capture their
  voice experience, framing, or key metaphors ("it sounds like me now"). These are worth the tokens.

- **Drop dead information.** Remove anything no longer training-relevant: one-time events processed
  and closed, transient circumstances resolved, topics client explicitly said done with. If unsure,
  keep — losing information worse than spending tokens.

- **Collapse old sessions.** Sessions older than 10 sessions ago → compress aggressively: reduce to 1-2
  lines each ("S1: [date] — intake. Baseline 142 Hz. Goals: phone passing, less dysphoria.") unless
  information still training-active (e.g., a technique the client still uses, an unresolved plateau).

- **Frontmatter hygiene.** Keep YAML frontmatter minimal: `client`, `slug`, `first_session`, `sessions`,
  any standing abbreviations legend. Remove frontmatter fields grown stale.

- **No narrative.** File is training documentation, not a story. Zero narrative connective tissue.
  Adjacent bullets that belong together don't need transition sentences — proximity is enough.

- **Preserve trainer reflection.** `Trainer reflection` field carries coaching self-reflection that
  must transfer to future sessions — how trainer improves across sessions. Never drop entirely.
  Sessions older than 5 → compress to pattern-to-watch portion only. Sessions 5 or newer → keep full
  reflection line intact.

After compression, write compressed file back to `sessions/voice/<client-slug>.md`.
