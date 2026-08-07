---
description: >
  Token-efficient compression rules for therapy session history files.
  Applied after every session (SKILL.md Step 6) to minimize token cost
  when the history file is loaded into context.
---

# Compression Rules

After writing session note, run compression pass on **Session Log Archive section only**. Goal: minimize
token count without losing clinically important information. File read into context at every session
start — every token matters.

## Permanent Client Profile — Never Compressed

`## Permanent Client Profile` section and everything under it **exempt from all compression rules**.
Do not remove, rewrite, abbreviate, or collapse any content in this section. Contains intake information
and clinically essential facts that must persist verbatim across all sessions. Only update by adding new
information (Step 5b) or correcting outdated facts (e.g., client's pronouns changed).

## Rules (Apply to Session Log Archive Only)

- **Remove filler.** Cut words that don't carry information: "the client discussed," "we explored," "it was noted that."
  Replace with direct, compact phrasing. "Discussed work stress — feels overwhelmed by new manager's expectations."

- **Use sentence fragments.** Full grammatical sentences cost tokens. Bullet-point style is preferred throughout.

- **Abbreviate consistently.** Establish abbreviations in the frontmatter and reuse: `CBT` (cognitive-behavioral
  therapy), `SI` (suicidal ideation), `SH` (self-harm), `RCT` (rational emotive behavior therapy), `GAD` (generalized
  anxiety disorder), `MDD` (major depressive disorder), `ACT` (acceptance and commitment therapy), `EMDR` (eye
  movement desensitization and reprocessing). Use standard clinical abbreviations only — never invent ambiguous ones.

- **Merge redundant entries.** Same theme across multiple sessions → consolidate rather than repeat:
  "Sessions 3–5: ongoing pattern of self-criticism after work conflicts." Don't lose timeline — note when theme
  first appeared and whether active or resolved.

- **Keep verbatim quotes.** Client language is high-signal. Preserve short verbatim quotes that capture their voice,
  framing, or key metaphors. These are worth the tokens.

- **Drop dead information.** Remove anything no longer clinically relevant: one-time events processed
  and closed, transient circumstances resolved, topics client explicitly said done with. If unsure,
  keep — losing information worse than spending tokens.

- **Collapse old sessions.** Sessions older than 10 sessions ago → compress aggressively: reduce to 1-2
  lines each ("S1: [date] — intake. Key themes: X, Y. Client uses [metaphor] for anxiety.") unless
  information still clinically active.

- **Frontmatter hygiene.** Keep YAML frontmatter minimal: `client`, `slug`, `first_session`, `sessions`,
  any standing abbreviations legend. Remove frontmatter fields grown stale.

- **No narrative.** File is clinical documentation, not a story. Zero narrative connective tissue.
  Adjacent bullets that belong together don't need transition sentences — proximity is enough.

- **Preserve therapist reflection.** `Therapist reflection` field carries clinical self-reflection that
  must transfer to future sessions — how therapist improves across sessions. Never drop entirely.
  Sessions older than 5 → compress to pattern-to-watch portion only. Sessions 5 or newer → keep full
  reflection line intact.

After compression, write compressed file back to `sessions/<client-slug>.md`.
