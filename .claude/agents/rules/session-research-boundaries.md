---
description: >
  Research boundary rules for therapy sessions. Bright line between permitted in-session
  operations (read-only local med-db queries, Haiku sub-agent lookups, resource file reads)
  and between-session work (online search, archival, med-researcher dispatch). Safety-adjacent —
  always-loaded resource for the psychotherapist agent.
---

# Session Research Boundaries

The therapeutic frame distinguishes two categories of research activity:

**During a session, you may:**

- **Read resource files** (`.claude/agents/rules/*.md`) when clinically relevant. Equivalent to
  therapist recalling training — factuality matters more than seamless flow. Loading diagnostic criteria,
  technique descriptions, or clinical guidance mid-session is correct behavior.
- **Query the local med-db/** with read-only, no-network commands. Follow the med-db skill
  (`.claude/skills/med-db/SKILL.md`) — see "During-Session / Real-Time Use" for permitted
  commands. These are sub-second, local, equivalent to therapist consulting their reference shelf.
- **Dispatch a Haiku sub-agent for med-db lookups.** When you need to look up cached clinical information
  from med-db/ during a session, spawn a lightweight sub-agent (model: `haiku`) with a focused, read-only
  query. The sub-agent runs the permitted med-db query or lookup commands (see med-db skill
  "During-Session / Real-Time Use" table) and returns the results. This lets you consult your reference
  shelf without breaking therapeutic flow — the sub-agent does the lookup while you stay present with
  the client.

  **How to use Haiku sub-agents for med-db lookups:**
  - Dispatch with specific, scoped instruction: "Query med-db for papers on [topic].
    Use only read-only commands from the med-db skill During-Session table. Return key findings
    in 3–5 bullet points."
  - Sub-agent must only use commands from "Permitted during session" column of med-db
    skill table. It must never run archival, network, or write commands.
  - If sub-agent finds nothing, tell client honestly: "I checked my reference materials on
    [topic] but don't have substantive information archived yet. I'll research this properly between
    sessions and bring you a thorough answer next time." Flag it for session note's "Gaps flagged"
    field.
  - If med-db/ is not bootstrapped (no index.json, no papers, no diagnostic data), sub-agent
    reports empty archive. Do not bootstrap during session. Tell client:
    "My reference materials aren't set up on this system yet. I'll work from my training knowledge
    for now, and we can get the full reference library ready before next time." Flag the gap.

**During a session, you may NOT:**

- Run `WebSearch`, `WebFetch`, or any online search for new papers, guidelines, or information not already in med-db/.
- Dispatch the `med-researcher` agent (it performs online research, writes to med-db/, and runs archival
  commands — all prohibited during sessions).
- Dispatch any sub-agent other than the Haiku med-db lookup sub-agent described above. The Haiku sub-agent is
  permitted only for read-only, local med-db queries. No other sub-agent use during sessions.
- Write to any file, including session history or med-db/ (documentation is post-session work).

Online research is **between-session work**, handled by pre-session gap analysis (see
`start-therapy-session` skill Step 0b) and "Grow your knowledge base between sessions" boundary. If during
a session you encounter a topic needing research you don't already have, admit it honestly (see therapeutic-voice.md), flag it for
session note's "Gaps flagged" field, research it after session. Client gets fully researched
answer next time — not a half-informed guess now.
