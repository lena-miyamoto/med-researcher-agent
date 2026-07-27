---
description: >
  Token-efficient compression rules for therapy session history files.
  Applied after every session (SKILL.md Step 6) to minimize token cost
  when the history file is loaded into context.
---

# Compression Rules

After writing the session note, run a compression pass on the **Session Log section only**. Goal: minimize token count
without losing any clinically important information. The file is read into context at the start of every session — every
token matters.

## Permanent Client Profile — Never Compressed

The `## Permanent Client Profile` section and everything under it is **exempt from all compression rules**. Do not
remove, rewrite, abbreviate, or collapse any content in this section. It contains intake information and clinically
essential facts that must persist verbatim across all sessions. Only update it by adding new information (Step 5b) or
correcting outdated facts (e.g., the client's pronouns have changed).

## Rules (Apply to Session Log Only)

- **Remove filler.** Cut words that don't carry information: "the client discussed," "we explored," "it was noted that."
  Replace with direct, compact phrasing. "Discussed work stress — feels overwhelmed by new manager's expectations."

- **Use sentence fragments.** Full grammatical sentences cost tokens. Bullet-point style is preferred throughout.

- **Abbreviate consistently.** Establish abbreviations in the frontmatter and reuse: `CBT` (cognitive-behavioral
  therapy), `SI` (suicidal ideation), `SH` (self-harm), `RCT` (rational emotive behavior therapy), `GAD` (generalized
  anxiety disorder), `MDD` (major depressive disorder), `ACT` (acceptance and commitment therapy), `EMDR` (eye
  movement desensitization and reprocessing). Use standard clinical abbreviations only — never invent ambiguous ones.

- **Merge redundant entries.** If the same theme appears across multiple sessions, consolidate rather than repeating:
  "Sessions 3–5: ongoing pattern of self-criticism after work conflicts." Don't lose the timeline — note when a theme
  first appeared and whether it's active or resolved.

- **Keep verbatim quotes.** Client language is high-signal. Preserve short verbatim quotes that capture their voice,
  framing, or key metaphors. These are worth the tokens.

- **Drop dead information.** Remove anything that is no longer clinically relevant: one-time events that were processed
  and closed, transient circumstances that resolved, topics the client explicitly said they were done with. If unsure,
  keep it — losing information is worse than spending tokens.

- **Collapse old sessions.** Sessions older than 10 sessions ago can be compressed more aggressively: reduce to 1-2
  lines each ("S1: [date] — intake. Key themes: X, Y. Client uses [metaphor] for anxiety.") unless they contain
  information that is still clinically active.

- **Frontmatter hygiene.** Keep the YAML frontmatter minimal: `client`, `slug`, `first_session`, `sessions`, and any
  standing abbreviations legend. Remove any frontmatter fields that have grown stale.

- **No narrative.** The file is clinical documentation, not a story. Zero narrative connective tissue. Adjacent bullet
  points that belong together don't need transition sentences — proximity is enough.

After compression, write the final compressed file back to `sessions/<client-slug>.md`.
