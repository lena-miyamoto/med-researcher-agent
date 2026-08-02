---
description: >
  med-db/ knowledge base bootstrap and diagnostic classification setup (ICD-11, DSM-5-TR,
  therapy methodology guidelines) for the psychotherapist agent. Run the Mandatory Pre-Work
  Bootstrap Check on first use per system. Read when bootstrap, diagnostic classification
  setup, or classification lookup procedures are needed. For clinical work guides (diagnostic
  assessment, case formulation, intervention planning, psychoeducation, technique selection),
  see clinical-work-guides.md.
---

## Knowledge Base — med-db/ Integration

Clinical work backed by structured, reproducible evidence in `med-db/`. All instances share same root
knowledge.

**Four independent components**, each own bootstrap method. All four must be verified
before therapeutic work.

### Component Overview

| Component | Location | Bootstrap command | Lookup tool |
|---|---|---|---|
| Research evidence | `med-db/papers/`, `med-db/searches/` | Research brief → `med-researcher` agent | `med-db-query`, `med-db-lookup` |
| ICD-11 classification | `med-db/guidelines/icd-11/` | `uv run med-db-download-icd11` | `med-db-lookup-icd11` |
| DSM-5-TR classification | `med-db/guidelines/dsm-5-tr/` | `uv run med-db-setup-dsm5` | `med-db-lookup-dsm5` |
| Therapy methodologies | `med-db/guidelines/therapy-methodologies/` | `uv run med-db-setup-therapy-methods` | Read `source.md` directly |

`med-db/` gitignored — created locally, does **not** ship with repo. All components must be
bootstrapped once per system before therapeutic work.

### Mandatory Pre-Work Bootstrap Check

**You MUST verify the knowledge base before engaging in any therapeutic work.** Run at start of every instance.
Follow med-db skill (`.claude/skills/med-db/SKILL.md`) — "Diagnostic Classification Setup" for
verification commands and bootstrap procedure.

**All four components must pass.** Missing or broken → bootstrap via med-db skill.
If bootstrapping fails, tell user:

> "My diagnostic reference data isn't fully set up on this system yet. I can't provide competent DSM-5-TR or ICD-11
> assessment without it. Let me fix this — it should only take a minute."

Run missing bootstrap commands. All pass → proceed with therapeutic work.

---

### Component 1: Research Evidence (Literature in med-db/)

Neurodevelopmental specialization backed by three canonical research briefs in `.claude/agents/rules/research-briefs/`
(version-controlled). Single source of truth for evidence base:

| Brief | Topics covered | med-db topics |
|---|---|---|
| `neurodevelopmental-comorbidities.md` | ADHD, ASD, AuDHD, common comorbidities | `adhd-comorbidity`, `asd-comorbidity`, `neurodevelopmental-overlap` |
| `gender-affirming-care.md` | WPATH SOC 8, minority stress, TNB mental health, non-binary care, socio-political context, neurodivergence overlap | `gender-affirming-care`, `trans-nb-mental-health` |
| `sex-relationship-therapy.md` | Sex therapy, kink/BDSM-affirming practice, CNM/polyamory, LGBTQI+ affirmative therapy, relationship diversity, neurodivergence intersection | `sex-therapy`, `relationship-diversity` |

Each brief: core PMIDs with archival commands, DOI-only references with resolution fallbacks, PubMed search
queries, topic organization, validation steps. med-researcher agent reads brief, populates `med-db/`
with full evidence base.

**Bootstrap check:**

```bash
uv run med-db-query --list-topics
```

All seven topics (`adhd-comorbidity`, `asd-comorbidity`, `neurodevelopmental-overlap`,
`gender-affirming-care`, `trans-nb-mental-health`, `sex-therapy`, `relationship-diversity`) appear with papers →
ready. Skip bootstrapping.

**If any topic missing or empty, bootstrap:**

Dispatch `med-researcher` agent with all three research briefs:

> "Read and execute all three research briefs in `.claude/agents/rules/research-briefs/`:
>
> 1. `neurodevelopmental-comorbidities.md`
> 2. `gender-affirming-care.md`
> 3. `sex-relationship-therapy.md`
> Follow each brief's instructions to bootstrap the med-db/ knowledge base. Archive all core PMIDs and run all
> search queries. Validate when done. Report what was archived and under which topics."

med-researcher checks existing archives, fetches missing papers, runs queries, validates.
Takes several minutes — run before therapy session, not during.

**Alternative — manual bootstrap command:**

```bash
uv run med-db --pmid 28830387 --pmid 33515606 --pmid 27859581 --pmid 22303520 --pmid 29604351 --pmid 37913872 --pmid 30903940 --pmid 32873239 --validate
```

Archives core PMIDs for neurodevelopmental comorbidities only. Full bootstrapping needs all three research briefs. med-researcher approach (above)
strongly preferred.

**Querying research evidence:**

Follow med-db skill (`.claude/skills/med-db/SKILL.md`) for all query commands. All queries read-only.

---

### Component 2: ICD-11 Classification (WHO)

Stored in `med-db/guidelines/icd-11/` — 37,118 entities across 28 chapters, English (2026-01) and German (2026-01).

**Bootstrap and queries:** Follow med-db skill (`.claude/skills/med-db/SKILL.md`) — "Diagnostic Classification Setup"
and `med-db-lookup-icd11` command table.
Key codes: 6A02 (ASD), 6A05 (ADHD). All queries local — no network.
**Full mental health code listing:** `med-db/guidelines/icd-11/source.md`.

---

### Component 3: DSM-5-TR Classification (APA)

Stored as structured JSON in `med-db/guidelines/dsm-5-tr/classification.json` — 241 disorders across
19 categories with ICD-10-CM codes and specifiers. Full diagnostic criteria copyrighted by APA,
NOT included.

**Bootstrap and queries:** Follow med-db skill (`.claude/skills/med-db/SKILL.md`) — "Diagnostic Classification Setup"
and `med-db-lookup-dsm5` command table.
Key codes: F90.2 (ADHD), F84.0 (ASD), F60.3 (BPD), F64.0 (Gender Dysphoria), F43.10 (PTSD).
All queries local — no network. Cross-reference ICD-11 codes via `med-db-lookup-icd11 --icd10-code <code>`.

---

### Component 4: Therapy Methodology Guidelines

Stored in `med-db/guidelines/therapy-methodologies/` — 11 therapy methodologies across 4 categories.

**Bootstrap:** Follow med-db skill (`.claude/skills/med-db/SKILL.md`) — "Diagnostic Classification Setup".

Reference material, not lookup. Read `med-db/guidelines/therapy-methodologies/source.md`.
Structured access: `methodologies.json` in same directory.

The 11 methodologies:

| Category | Methodologies |
|---|---|
| Foundational Frameworks | Liberation Psychology (Martín-Baró), Critical Psychology (Holzkamp, Parker) |
| Integrative Modalities | Narrative Therapy (White & Epston), Systemic Therapy |
| Broader Critical Canon | Postcolonial/Decolonial Psychology, Feminist/Queer Psychology, Trauma-Informed Care, Disability Justice/Neurodiversity Paradigm, Mad Studies |
| Clinical Modalities | CBT (Beck), ACT (Hayes) |

Each entry: key figures, historical context, core concepts, therapeutic stance, key techniques,
evidence base, critique/limitations, relationship to other methodologies.

Codified Theoretical Framework. Reference foundation for modality integration, technique
selection, and critical appraisal of therapeutic approaches. Consult when:

- Selecting modalities for clinical presentation
- Adapting techniques for client context (cultural, neurodevelopmental, gender, relationship structure)
- Evaluating evidence base and limitations of proposed approach
- Understanding how methodologies relate to and inform each other
- Grounding clinical reasoning in theoretical traditions that inform agent's practice

---

### Keeping Knowledge Base Current

- **Research briefs:** Re-run every 12 months. New systematic reviews or meta-analyses superseding core
  references → update research brief and clinical guidance.
- **ICD-11:** WHO updates annually (January). Check with `uv run med-db-download-icd11
  --release 2027-01` when available (follow med-db skill). 2026-01 is current.
- **DSM-5-TR:** APA update supplements (usually September). Check `.claude/scripts/med-db-setup-dsm5.py`
  `_build_categories()`, update codes/names as needed. Published March 2022; DSM-6 not yet scheduled.
- **Therapy methodologies:** Update on major new editions or significant innovations integrating
  into Theoretical Framework. Update embedded data in
  `.claude/scripts/med-db-setup-therapy-methods.py`, re-run setup.
- Citing prevalence data or treatment guidance from med-db/ papers: note publication year and evidence-quality
  assessment. Papers >10 years: flag, check for newer evidence.

See `.claude/agents/rules/clinical-work-guides.md` for diagnostic assessment, assessment
considerations (neurodevelopmental, gender-affirming, sex/relationship), therapeutic dialogue and session work,
case conceptualization, intervention planning, psychoeducation, and technique selection.
