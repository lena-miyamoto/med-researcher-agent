---
description: >
  med-db/ knowledge base bootstrap for the voice-trainer agent. Single component: the
  voice-feminization evidence archive. Run the Mandatory Pre-Work Bootstrap Check on first use per
  system. Read when bootstrap or archive query procedures are needed. For the coaching manual
  (technique catalog, program design, safety, session structure), see voice-training-methodology.md.
---

## Knowledge Base — med-db/ Integration

Coaching work backed by structured, reproducible evidence in `med-db/`. All instances share same root
knowledge.

**One component.** Unlike the psychotherapist agent's four-component knowledge base (research evidence,
ICD-11, DSM-5-TR, therapy methodologies), the voice-trainer agent needs only the research evidence
archive. No diagnostic classification components are required.

| Component | Location | Bootstrap | Lookup tool |
|---|---|---|---|
| Research evidence | `med-db/papers/`, `med-db/searches/` | Research brief → `med-researcher` agent | `med-db-query`, `med-db-lookup` |

`med-db/` gitignored — created locally, does **not** ship with repo. Must be bootstrapped once per
system before coaching work.

### Mandatory Pre-Work Bootstrap Check

**You MUST verify the knowledge base before engaging in any coaching work.** Run at start of every instance.

List topics via the `med-db` skill (`med-db-query --list-topics`). The `voice-feminization` topic
appears with papers → ready. Skip bootstrapping.

**Topic missing or empty → bootstrap:**

Dispatch `med-researcher` agent with the research brief:

> "Read and execute the research brief in `.claude/agents/references/research-brief-voice-training.md`.
> Follow the brief's instructions to bootstrap the med-db/ knowledge base. Archive all core PMIDs and
> run all search queries. Validate when done. Report what was archived and under which topics."

med-researcher checks existing archives, fetches missing papers (full text via the `fetch-paper`
skill), runs queries, validates. Takes several minutes — run before the voice training session,
not during.

**Alternative — manual bootstrap:**

Archive the core PMIDs via the `med-db` skill under topic `voice-feminization`: 36238954, 37481572,
39465090, 38704279, 23415146, 36328187, 34706847, 34565626, 19525544, 16301101, 2299839, 10764114.
Full bootstrapping needs the research brief. med-researcher approach (above) strongly preferred.

If bootstrapping fails, tell user:

> "My voice training evidence archive isn't fully set up on this system yet. I can coach from my
> training knowledge, but my technique recommendations won't be backed by the local evidence base.
> Let me fix this — it should only take a few minutes."

Run missing bootstrap commands. All pass → proceed with coaching work.

---

### Querying Research Evidence

Follow `med-db` skill for all query commands. All queries read-only.

### Keeping Knowledge Base Current

- **Research briefs:** Re-run every 12 months. New systematic reviews or meta-analyses superseding core
  references → update research brief and methodology file.
- Citing outcomes or technique evidence from med-db/ papers: note publication year and evidence-quality
  assessment. Foundational perception studies >10 years old (Wolfe 1990, Gelfer 2000/2005, Hillenbrand
  2009): cite with year, flag as foundational.
- Guidelines not in med-db (ASHA Practice Portal): cite by URL with access date.

See `.claude/agents/references/voice-training-methodology.md` for the coaching manual: technique
catalog, program design, assessment-without-hearing, safety rules, special contexts, and session
structure.
