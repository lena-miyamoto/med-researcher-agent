---
description: >
  Pre-session knowledge gap analysis procedure for returning therapy clients. Read when preparing for a returning
  client session (Step 0b of start-therapy-session). Scans session history for uncovered topics, checks coverage
  across med-db/, resource files, and therapy methodology guidelines, dispatches med-researcher agent for gaps.
---

# Knowledge Gap Analysis (Returning Clients)

**For returning clients only** (history file exists with ≥1 prior sessions). Skip this step for new clients.

Before the session begins, the agent must fill any knowledge gaps identified in previous sessions. This is not optional —
a therapist who never learns from their clients is a deteriorating one. Each client should leave the knowledge base broader
than it was before.

## 0b-i. Scan for Knowledge Gaps

Read the full session history. For every session note, identify:

- **Conditions mentioned** — any diagnosis, symptom cluster, or clinical presentation discussed
- **Techniques and modalities referenced** — any therapeutic approach named or applied
- **Concepts and terminology** — any clinical concept, framework, or specialized term that appeared
- **Medications named** — any psychopharmacological agent the client mentioned (even in passing)
- **Life experiences and contexts** — any social, cultural, or experiential domain that is clinically relevant (e.g.,
  a specific form of discrimination, a cultural practice, a health condition, a relationship structure)
- **Topics flagged in "Gaps flagged" fields** — anything the agent explicitly admitted it didn't know enough about
  during a previous session and committed to researching

## 0b-ii. Check Coverage

For each identified item, check whether the knowledge base has adequate coverage:

1. **med-db/ coverage**: Is there at least one relevant paper archived under a matching topic? Query with
   `uv run med-db-query --search-keyword "<term>"` or `uv run med-db-query --list-topics` to check topic presence.
2. **Resource file coverage**: Do the agent's resource files (`neurodevelopmental-specialization`,
   `gender-affirming-care`, `sex-relationship-therapy`, `knowledge-base`) cover this? Read the relevant file and check.
3. **Therapy methodology coverage**: Do the bootstrapped therapy methodology guidelines
   (`med-db/guidelines/therapy-methodologies/`) cover techniques or modalities mentioned?

An item has **adequate coverage** if at least one of these three sources provides substantive clinical information —
not just a passing mention, but enough to inform competent therapeutic work.

## 0b-iii. Dispatch Research for Gaps

For every item with inadequate coverage, dispatch the `med-researcher` agent with a focused, well-scoped prompt. Examples:

> "Research and archive evidence on [condition X] in adults. Focus on: prevalence, diagnostic criteria, evidence-based
> treatments, and any relevant clinical practice guidelines. Archive the top 3–5 most relevant papers in med-db/ under a
> new or existing topic."
>
> "Research and archive evidence on [technique Y] for [population Z]. What is the evidence base, effect sizes,
> limitations, and adaptations needed? Archive key papers."
>
> "Client mentioned [medication M]. Research and archive: mechanism of action, indications, common side effects, evidence
> quality, and interactions relevant to [client's other conditions/medications]."

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
- Client's own language for their experience (verbatim phrases from past notes)
- Interventions that have been used and how they landed
- Any known diagnoses, important life context, or standing concerns
- **Knowledge gaps newly filled** — brief summary of what was researched and archived this cycle (so the agent knows what
  new knowledge is available)
- **Unresolved gaps** — topics flagged in previous sessions that still lack coverage (so the agent can be honest with the
  client if they come up)

Assemble this into a brief context block (keep it compact — the agent will read the full file itself if needed).
