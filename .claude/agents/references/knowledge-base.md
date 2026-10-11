---
description: >
  Psychotherapist agent knowledge base — research evidence setup plus diagnostic
  classification and therapy methodology reference files. Run the Mandatory Pre-Work
  Knowledge Check on first use per system. Read when evidence setup, diagnostic reference,
  or classification lookup is needed. For clinical work guides (diagnostic assessment, case
  formulation, intervention planning, psychoeducation, technique selection), see
  clinical-work-guides.md.
---

## Knowledge Base

Clinical work is backed by two kinds of reference material:

- **Version-controlled resources** ship with the repo — the diagnostic classification and
  therapy methodology reference files under `.claude/agents/references/`.
- **The local archive** is rebuilt per machine and does not ship with the repo — it holds the
  archived research papers and the full ICD-11 dataset. Reach it only through the `med-db`
  skill.

### Components

| Component               | Backed by                                                          | How to use                                                                                             |
| ----------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| Research evidence       | Local archive — the `med-db` skill                                 | Read the research briefs below; query archived papers via the `med-db` skill                           |
| ICD-11 classification   | Local archive (full dataset) + resource file (mental-health codes) | Read `.claude/agents/references/icd11-mental-health-codes.md`; look up any code via the `med-db` skill |
| DSM-5-TR classification | Resource file                                                      | Read `.claude/agents/references/dsm5-tr-classification.md`                                             |
| Therapy methodologies   | Resource file                                                      | Read `.claude/agents/references/therapy-methodologies.md`                                              |

### Mandatory Pre-Work Knowledge Check

**You MUST verify the knowledge base before engaging in any therapeutic work.** Run at the
start of every instance.

- **Diagnostic and therapy references** — always available; they ship with the repo. Read the
  three resource files listed in the Components table.
- **Research evidence** — archived per machine. Follow the `med-db` skill to check whether the
  topics below are populated. If they are missing or empty, set them up as described in
  Component 1.

If the research evidence archive cannot be set up, tell the user:

> "My research evidence archive isn't set up on this system yet. Diagnostic assessment still works
> from the references that ship with the repo, but I can't ground clinical decisions in the archived
> literature until it's populated. Let me fix this — it should only take a minute."

Once the research topics are populated, proceed with therapeutic work.

---

### Component 1: Research Evidence

Neurodevelopmental specialization is backed by three canonical research briefs in
`.claude/agents/references/` (version-controlled). Single source of truth for the evidence base:

| Brief                                                | Topics covered                                                                                                                              | Archive topics                                                      |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `research-brief-neurodevelopmental-comorbidities.md` | ADHD, ASD, AuDHD, common comorbidities                                                                                                      | `adhd-comorbidity`, `asd-comorbidity`, `neurodevelopmental-overlap` |
| `research-brief-gender-affirming-care.md`            | WPATH SOC 8, minority stress, TNB mental health, non-binary care, socio-political context, neurodivergence overlap                          | `gender-affirming-care`, `trans-nb-mental-health`                   |
| `research-brief-sex-relationship-therapy.md`         | Sex therapy, kink/BDSM-affirming practice, CNM/polyamory, LGBTQI+ affirmative therapy, relationship diversity, neurodivergence intersection | `sex-therapy`, `relationship-diversity`                             |

Each brief holds core PMIDs, DOI-only references, PubMed search queries, topic organization,
and validation steps. The `med-researcher` agent reads a brief and populates the local archive
with the full evidence base.

**Check:** list the archive topics via the `med-db` skill. All seven topics
(`adhd-comorbidity`, `asd-comorbidity`, `neurodevelopmental-overlap`, `gender-affirming-care`,
`trans-nb-mental-health`, `sex-therapy`, `relationship-diversity`) appear with papers → ready.
Skip setting up.

**If any topic is missing or empty, set it up:**

Dispatch the `med-researcher` agent with all three research briefs:

> "Read and execute all three research briefs in `.claude/agents/references/`:
>
> 1. `research-brief-neurodevelopmental-comorbidities.md`
> 2. `research-brief-gender-affirming-care.md`
> 3. `research-brief-sex-relationship-therapy.md`
> Follow each brief's instructions to populate the local archive. Archive all core PMIDs and run all
> search queries. Validate when done. Report what was archived and under which topics."

The `med-researcher` agent checks existing archives, fetches missing papers (full text via the
`fetch-paper` skill), runs queries, and validates. Takes several minutes — run before a therapy
session, not during.

**Alternative — manual setup:** archive the core PMIDs for neurodevelopmental comorbidities via
the `med-db` skill: 28830387, 33515607, 27859581, 22303520, 29477617, 37913872, 32847520.
Full setup needs all three research briefs. The `med-researcher` approach above is strongly
preferred.

**Querying research evidence:** follow the `med-db` skill for all query commands. All queries
are read-only.

---

### Component 2: ICD-11 Classification (WHO)

The full ICD-11 MMS dataset (all chapters, English and German, release 2026-01) lives in the
local archive, reached via the `med-db` skill. **Mental-health code listing:**
`.claude/agents/references/icd11-mental-health-codes.md` (Chapter 06 codes and titles, ships
with the repo).

Key codes: 6A02 (ASD), 6A05 (ADHD). Follow the `med-db` skill to download the dataset or look up
any code, including ICD-10 ↔ ICD-11 cross-references. All lookups are local — no network.

---

### Component 3: DSM-5-TR Classification (APA)

Ships as `.claude/agents/references/dsm5-tr-classification.md` — 241 disorders across 19
categories with ICD-10-CM codes and specifiers. Full diagnostic criteria are copyrighted by APA
and are NOT included; consult the DSM-5-TR volume for the criteria.

Key codes: F90.2 (ADHD), F84.0 (ASD), F60.3 (BPD), F64.0 (Gender Dysphoria), F43.10 (PTSD).
Cross-reference ICD-10 ↔ ICD-11 codes via the `med-db` skill.

---

### Component 4: Therapy Methodology Guidelines

Ships as `.claude/agents/references/therapy-methodologies.md` — 12 therapy methodologies across
4 categories:

| Category                | Methodologies                                                                                                                                                                                    |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Foundational Frameworks | Liberation Psychology (Martín-Baró), Critical Psychology (Holzkamp, Parker)                                                                                                                      |
| Integrative Modalities  | Narrative Therapy (White & Epston), Systemic Therapy                                                                                                                                             |
| Broader Critical Canon  | Postcolonial/Decolonial Psychology, Feminist/Queer Psychology, Trauma-Informed Care, Disability Justice/Neurodiversity Paradigm, Mad Studies, Trans/Kink/Relationship-Diverse Affirming Practice |
| Clinical Modalities     | CBT (Beck), ACT (Hayes)                                                                                                                                                                          |

Each entry: key figures, historical context, core concepts, therapeutic stance, key techniques,
evidence base, critique/limitations, relationship to other methodologies. Also includes Minority
Stress Theory (Meyer) and the seven Core Principles.

Codified Theoretical Framework. Reference foundation for modality integration, technique
selection, critical appraisal of therapeutic approaches. Consult when:

- Selecting modalities for a clinical presentation
- Adapting techniques for client context (cultural, neurodevelopmental, gender, relationship structure)
- Evaluating evidence base and limitations of a proposed approach
- Understanding how methodologies relate to and inform each other
- Grounding clinical reasoning in the theoretical traditions informing the agent's practice

---

### Keeping the Knowledge Base Current

- **Research briefs:** re-run every 12 months. When a new systematic review or meta-analysis
  supersedes a core reference, update the research brief and the clinical guidance.
- **ICD-11:** WHO updates annually (January). When a newer release is available, re-download via
  the `med-db` skill (release 2026-01 is current), and refresh
  `.claude/agents/references/icd11-mental-health-codes.md` if Chapter 06 changed.
- **DSM-5-TR:** APA update supplements (usually September). Update the codes and names in
  `.claude/agents/references/dsm5-tr-classification.md` as needed. Published March 2022; DSM-6
  is not yet scheduled.
- **Therapy methodologies:** update `.claude/agents/references/therapy-methodologies.md` on major
  new editions or significant innovations integrated into the Theoretical Framework.
- Citing prevalence data or treatment guidance from archived papers: note the publication year
  and evidence-quality assessment. Papers over 10 years old: flag and check for newer evidence.

See `.claude/agents/references/clinical-work-guides.md` for diagnostic assessment, assessment
considerations (neurodevelopmental, gender-affirming, sex/relationship), therapeutic dialogue and
session work, case conceptualization, intervention planning, psychoeducation, and technique
selection.
