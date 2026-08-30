---
description: >
  Pre-session knowledge gap analysis procedure for returning voice training clients. Read when preparing for a
  returning client session (Step 0b of start-voice-training). Scans session history for uncovered topics, checks
  coverage across med-db/ and resource files, dispatches med-researcher agent for gaps.
---

# Knowledge Gap Analysis (Returning Clients)

**For returning clients only** (history file exists with ≥1 prior sessions). Skip this step for new clients.

Before the session begins, the agent must fill any knowledge gaps identified in previous sessions. This is not optional —
a trainer who never learns from their clients is a deteriorating one. Each client should leave the knowledge base broader
than it was before.

## 0b-i. Scan for Knowledge Gaps

Read the full session history. For every session note, identify:

- **Techniques and exercises referenced** — any voice technique, exercise family, or modality named or applied
- **Voice conditions mentioned** — any dysphonia, laryngeal condition, reflux, respiratory condition, or other
  voice-affecting health issue discussed
- **Surgery types mentioned** — any voice surgery named (Wendler glottoplasty, cricothyroid approximation,
  FemLar, laser procedures) or considered
- **Anatomy and physiology concepts** — any laryngeal, respiratory, or resonance anatomy that appeared
- **Measurement tools referenced** — pitch apps, acoustic measures (F0, formants, shimmer/jitter), questionnaires
  (TWVQ) named or used
- **Singing and voice-use contexts** — singing technique, professional voice use, voice in specific contexts
  (work calls, dating, gaming voice chat) that are training-relevant
- **GAHT and medical context** — hormone therapy details, medications with voice effects (e.g., inhaled
  corticosteroids, anticholinergics), or other medical context the client shared
- **Topics flagged in "Gaps flagged" fields** — anything the agent explicitly admitted it didn't know enough about
  during a previous session and committed to researching
- **Follow-ups promised or requested** — any topic the client explicitly asked to learn more about,
  or that the trainer promised to bring information on in a future session. Look for phrases in session notes
  like "client asked about [X]," "promised to follow up on [Y]," "client wanted more information on [Z]," or
  similar. These are coaching commitments that must be honored. If the trainer said "I'll look into that" or
  "let me bring you more on that next time," it counts as a pending follow-up.

## 0b-ii. Check Coverage

For each identified item, check whether the knowledge base has adequate coverage:

1. **med-db/ coverage**: Is there at least one relevant paper archived under a matching topic (start with
   `voice-feminization`)? Follow the `med-db` skill for query commands — `--search-keyword` and `--list-topics`.
2. **Resource file coverage**: Do the agent's resource files (`voice-training-methodology`,
   `research-brief-voice-training`, `voice-training-knowledge-base`) cover this? Read the relevant file and check.

An item has **adequate coverage** if at least one of these two sources provides substantive information —
not just a passing mention, but enough to inform competent coaching work.

## 0b-iii. Dispatch Research for Gaps

For every item with inadequate coverage, dispatch the `med-researcher` agent with a focused, well-scoped prompt. Examples:

> "Research and archive evidence on [technique X] for voice feminization. What is the evidence base, expected
> effects, safety considerations, and progression protocols? Archive key papers."
>
> "Client mentioned [condition Y]. Research and archive: how it affects the voice and voice training, whether
> training modifications are needed, and red flags. Archive key papers."
>
> "Research and archive evidence on [surgery Z] for voice feminization: outcomes, risks, and the standard
> post-operative voice training pathway. Archive key papers."

Run these research dispatches **before proceeding to Step 1**. The med-researcher agent archives papers in med-db/,
populating the knowledge base for this and all future sessions. This takes a few minutes — the client is not waiting yet;
this is pre-session preparation.

If the med-researcher agent cannot find adequate evidence on a topic, note this honestly: "Research was attempted on [X]
but no high-quality evidence was found. This limitation should be disclosed to the client if the topic arises."

## 0b-iv. Prepare Session Context

After the gap analysis is complete (or if skipped for a new client), extract key information for the session:

- Client name and slug
- Session language (from frontmatter `language` field)
- Number of previous sessions (`sessions` in frontmatter)
- Last session date and the key thread noted for follow-up
- Recurring themes across sessions
- Client's own language for their voice experience (verbatim phrases from past notes)
- Techniques that have been used and how they landed
- Baseline measurements on record and home practice plan from last session
- Any known voice conditions, surgery history, GAHT status, or standing concerns
- **Knowledge gaps newly filled** — brief summary of what was researched and archived this cycle (so the agent knows what
  new knowledge is available)
- **Pending follow-ups from previous sessions** — topics the client asked to learn more about or the
  trainer promised to bring information on. Each topic should name what was requested and in which session.
  "none" if no pending requests.
- **Unresolved gaps** — topics flagged in previous sessions that still lack coverage (so the agent can be honest with the
  client if they come up)

Assemble this into a brief context block (keep it compact — the agent will read the full file itself if needed).
