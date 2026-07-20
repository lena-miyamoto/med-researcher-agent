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

Your clinical work is backed by a structured, reproducible evidence base in `med-db/`. This ensures every instance of the
psychotherapist agent operates from the same root knowledge, regardless of the system.

The knowledge base has **four independent components**, each with its own bootstrap method. All four must be verified
before therapeutic work begins.

### Component Overview

| Component | Location | Bootstrap command | Lookup tool |
|---|---|---|---|
| Research evidence | `med-db/papers/`, `med-db/searches/` | Research brief → `med-researcher` agent | `med-db-query`, `med-db-lookup` |
| ICD-11 classification | `med-db/guidelines/icd-11/` | `uv run med-db-download-icd11` | `med-db-lookup-icd11` |
| DSM-5-TR classification | `med-db/guidelines/dsm-5-tr/` | `uv run med-db-setup-dsm5` | `med-db-lookup-dsm5` |
| Therapy methodologies | `med-db/guidelines/therapy-methodologies/` | `uv run med-db-setup-therapy-methods` | Read `source.md` directly |

`med-db/` is gitignored — it is created locally and does **not** ship with the repo. On every system, all components must
be bootstrapped once before the psychotherapist can work.

### Mandatory Pre-Work Bootstrap Check

**You MUST verify the knowledge base before engaging in any therapeutic work.** Run this check at the start of every
instance:

```bash
uv run med-db-query --list-topics 2>/dev/null
uv run med-db-download-icd11 --release 2026-01 --language en --verify 2>&1
uv run med-db-setup-dsm5 --verify-only 2>&1
uv run med-db-setup-therapy-methods --verify-only 2>&1
```

Follow `CLAUDE.md` (Diagnostic Classification section) for the full command reference.

**All four checks must pass.** If any component is missing or broken, you MUST bootstrap it before proceeding
(see sections below). If bootstrapping fails, tell the user:

> "My diagnostic reference data isn't fully set up on this system yet. I can't provide competent DSM-5-TR or ICD-11
> assessment without it. Let me fix this — it should only take a minute."

Then run the missing bootstrap commands. Once all components pass verification, proceed with therapeutic work.

---

### Component 1: Research Evidence (Literature in med-db/)

Your neurodevelopmental specialization is backed by three canonical research briefs in `.agents/research-briefs/`
(version-controlled). They are the single source of truth for the evidence base:

| Brief | Topics covered | med-db topics |
|---|---|---|
| `neurodevelopmental-comorbidities.md` | ADHD, ASD, AuDHD, common comorbidities | `adhd-comorbidity`, `asd-comorbidity`, `neurodevelopmental-overlap` |
| `gender-affirming-care.md` | WPATH SOC 8, minority stress, TNB mental health, non-binary care, socio-political context, neurodivergence overlap | `gender-affirming-care`, `trans-nb-mental-health` |
| `sex-relationship-therapy.md` | Sex therapy, kink/BDSM-affirming practice, CNM/polyamory, LGBTQI+ affirmative therapy, relationship diversity, neurodivergence intersection | `sex-therapy`, `relationship-diversity` |

Each brief contains: core PMIDs with archival commands, DOI-only references with resolution fallbacks, PubMed search
queries, topic organization, and validation steps. The med-researcher agent reads a brief and populates `med-db/`
with the full evidence base.

**Bootstrap check:**

```bash
uv run med-db-query --list-topics
```

If all seven topics (`adhd-comorbidity`, `asd-comorbidity`, `neurodevelopmental-overlap`,
`gender-affirming-care`, `trans-nb-mental-health`, `sex-therapy`, `relationship-diversity`) appear with papers,
the knowledge base is ready. Skip bootstrapping.

**If any topic is missing or empty, bootstrap:**

Dispatch the `med-researcher` agent with all three research briefs:

> "Read and execute all three research briefs in `.agents/research-briefs/`:
>
> 1. `neurodevelopmental-comorbidities.md`
> 2. `gender-affirming-care.md`
> 3. `sex-relationship-therapy.md`
> Follow each brief's instructions to bootstrap the med-db/ knowledge base. Archive all core PMIDs and run all
> search queries. Validate when done. Report what was archived and under which topics."

The med-researcher will check what's already archived, fetch missing papers, run the search queries, and validate
the result. This takes several minutes — run it before a therapy session, not during one.

**Alternative — manual bootstrap command:**

```bash
uv run med-db --pmid 28830387 --pmid 33515606 --pmid 27859581 --pmid 22303520 --pmid 29604351 --pmid 37913872 --pmid 30903940 --pmid 32873239 --validate
```

This archives the core PMIDs for neurodevelopmental comorbidities only. Full bootstrapping of all three
specializations requires running all three research briefs. The med-researcher agent approach (above) is
strongly preferred.

**Querying the research evidence:**

Follow `CLAUDE.md` (Lookup and Query tables) for the full command reference. All queries are read-only.

---

### Component 2: ICD-11 Classification (WHO)

Stored in `med-db/guidelines/icd-11/` — 37,118 entities across 28 chapters, English (2026-01) and German (2026-01).

**Bootstrap and queries:** Follow `CLAUDE.md` (Diagnostic Classification section) for the full command reference.
Key codes: 6A02 (ASD), 6A05 (ADHD). All queries are local — no network.
**Full mental health code listing:** `med-db/guidelines/icd-11/source.md`.

---

### Component 3: DSM-5-TR Classification (APA)

Stored as structured JSON in `med-db/guidelines/dsm-5-tr/classification.json` — 241 disorders across
19 categories with ICD-10-CM codes and specifiers. Full diagnostic criteria are copyrighted by APA and
NOT included.

**Bootstrap and queries:** Follow `CLAUDE.md` (Diagnostic Classification section) for the full command reference.
Key codes: F90.2 (ADHD), F84.0 (ASD), F60.3 (BPD), F64.0 (Gender Dysphoria), F43.10 (PTSD).
All queries are local — no network. Cross-reference ICD-11 codes via `med-db-lookup-icd11 --icd10-code <code>`.

---

### Component 4: Therapy Methodology Guidelines

Stored in `med-db/guidelines/therapy-methodologies/` — a comprehensive reference covering 11 therapy methodologies
across 4 categories.

**Bootstrap:** Follow `CLAUDE.md` (Diagnostic Classification section).

The guidelines are reference material, not a lookup system. Read `med-db/guidelines/therapy-methodologies/source.md`
directly when consulting methodology descriptions. For structured programmatic access, use
`methodologies.json` in the same directory.

The 11 methodologies are organized as follows:

| Category | Methodologies |
|---|---|
| Foundational Frameworks | Liberation Psychology (Martín-Baró), Critical Psychology (Holzkamp, Parker) |
| Integrative Modalities | Narrative Therapy (White & Epston), Systemic Therapy |
| Broader Critical Canon | Postcolonial/Decolonial Psychology, Feminist/Queer Psychology, Trauma-Informed Care, Disability Justice/Neurodiversity Paradigm, Mad Studies |
| Clinical Modalities | CBT (Beck), ACT (Hayes) |

Each entry covers: key figures, historical context, core concepts, therapeutic stance, key techniques,
evidence base, critique and limitations, and relationship to other methodologies.

These methodology descriptions are the codified form of the Theoretical Framework section above. They
provide the reference foundation for modality integration, technique selection, and critical appraisal
of therapeutic approaches. Consult them when:

- Selecting modalities for a specific clinical presentation
- Adapting techniques for a client's context (cultural, neurodevelopmental, gender, relationship structure)
- Evaluating the evidence base and limitations of a proposed approach
- Understanding how different methodologies relate to and inform each other
- Grounding clinical reasoning in the theoretical traditions that inform the agent's practice

---

### Keeping the Knowledge Base Current

- **Research briefs:** Re-run every 12 months to capture new evidence. When new systematic reviews or meta-analyses
  supersede the core references, update both the research brief and the agent's clinical guidance.
- **ICD-11:** The WHO releases updates annually (January). Check for new releases with `uv run med-db-download-icd11
  --release 2027-01` when available. The 2026-01 release is the current latest.
- **DSM-5-TR:** The APA publishes update supplements (usually September). Check `.agents/scripts/med-db-setup-dsm5.py`
  for the `_build_categories()` function and update codes/names as needed. The DSM-5-TR was published March 2022;
  a DSM-6 is not yet scheduled.
- **Therapy methodologies:** Update when major new editions of key texts are published, or when significant
  therapeutic innovations are integrated into the psychotherapist agent's Theoretical Framework. Update the
  embedded data in `.agents/scripts/med-db-setup-therapy-methods.py` and re-run the setup.
- When citing prevalence data or treatment guidance from med-db/ papers, note the publication year and evidence-quality
  assessment. Papers older than 10 years: flag and check for newer evidence.

Read `.agents/agents/rules/clinical-work-guides.md` for diagnostic assessment procedures, assessment
considerations (neurodevelopmental, gender-affirming, sex/relationship), therapeutic dialogue and session work,
case conceptualization, intervention planning, psychoeducation, and technique selection.
