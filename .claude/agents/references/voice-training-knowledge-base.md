---
description: >
  Voice-trainer agent knowledge base — the voice-feminization evidence archive. Single component.
  Run the Mandatory Pre-Work Knowledge Check on first use per system. Read when evidence setup or
  archive query procedures are needed. For the coaching manual (technique catalog, program design,
  safety, session structure), see voice-training-methodology.md.
---

## Knowledge Base

Coaching work is backed by structured, reproducible evidence in the local archive (rebuilt per
machine, reached only through the `med-db` skill). All instances share the same root knowledge.

**One component.** Unlike the psychotherapist agent's knowledge base (research evidence plus
diagnostic classification and therapy resources), the voice-trainer agent needs only the research
evidence archive. No diagnostic classification components are required.

| Component         | Backed by                          | How to use                                                   |
| ----------------- | ---------------------------------- | ------------------------------------------------------------ |
| Research evidence | Local archive — the `med-db` skill | Read the research brief; query papers via the `med-db` skill |

### Mandatory Pre-Work Knowledge Check

**You MUST verify the knowledge base before engaging in any coaching work.** Run at the start of
every instance.

Follow the `med-db` skill to check whether the `voice-feminization` topic is populated. Populated →
ready. Skip setting up.

**Topic missing or empty → set it up:**

Dispatch the `med-researcher` agent with the research brief:

> "Read and execute the research brief in `.claude/agents/references/research-brief-voice-training.md`.
> Follow the brief's instructions to populate the local archive. Archive all core PMIDs and run all
> search queries. Validate when done. Report what was archived and under which topics."

The `med-researcher` agent checks existing archives, fetches missing papers (full text via the
`fetch-paper` skill), runs queries, and validates. Takes several minutes — run before the voice
training session, not during.

**Alternative — manual setup:** archive the core PMIDs via the `med-db` skill under topic
`voice-feminization`: 36238954, 37481572, 39465090, 38704279, 23415146, 36328187, 34706847, 34565626,
19525544, 16301101, 2299839, 10764114. Full setup needs the research brief. The `med-researcher`
approach above is strongly preferred.

If setup fails, tell the user:

> "My voice training evidence archive isn't fully set up on this system yet. I can coach from my
> training knowledge, but my technique recommendations won't be backed by the local evidence base.
> Let me fix this — it should only take a few minutes."

Run the missing setup steps. All pass → proceed with coaching work.

---

### Querying Research Evidence

Follow the `med-db` skill for all query commands. All queries are read-only.

### Keeping the Knowledge Base Current

- **Research briefs:** re-run every 12 months. When a new systematic review or meta-analysis
  supersedes a core reference, update the research brief and the methodology file.
- Citing outcomes or technique evidence from archived papers: note the publication year and
  evidence-quality assessment. Foundational perception studies over 10 years old (Wolfe 1990,
  Gelfer 2000/2005, Hillenbrand 2009): cite with year, flag as foundational.
- Guidelines not in the archive (ASHA Practice Portal): cite by URL with access date.

See `.claude/agents/references/voice-training-methodology.md` for the coaching manual: technique
catalog, program design, assessment-without-hearing, safety rules, special contexts, and session
structure.
