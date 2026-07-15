---
description: >
  Research brief for the med-researcher agent. Archives the core evidence base on gender-affirming care for
  transgender and non-binary (TNB) adults — WPATH SOC 8, minority stress model, TNB mental health disparities,
  non-binary-specific evidence, socio-political context, and the neurodivergence-gender diversity overlap.
  Run once per system to bootstrap the psychotherapist agent's TNB competence knowledge base.
topics:
  - gender-affirming-care
  - trans-nb-mental-health
version: 1.0.0
last_updated: 2026-07-15
---

# Gender-Affirming Care & TNB Mental Health — Knowledge Base Bootstrap

This brief tells the med-researcher agent exactly what to archive in `med-db/` so the psychotherapist agent has a
local evidence base for gender-affirming care and TNB mental health competence. Treat this brief as read-only.

## Pre-flight

Verify `med-db/` exists and check existing topics:

```bash
uv run med-db-query --list-topics
```

If `gender-affirming-care` and `trans-nb-mental-health` both have papers, the knowledge base may already be
bootstrapped. Check:

```bash
uv run med-db-query --topic gender-affirming-care
uv run med-db-query --topic trans-nb-mental-health
```

If both are populated, skip to the report. Otherwise, proceed through the phases.

---

## Phase 1: Core PMIDs — Clinical Guidelines & Minority Stress

Archive under `gender-affirming-care`.

### 1.1 WPATH Standards of Care Version 8 (2022)

**PMID:** 36238954
**Why:** The international clinical guideline for TNB healthcare. First WPATH version with formal evidence-based
methodology. One referral letter for adults, no mandatory psychotherapy, explicit prohibition of conversion
therapy, first-time detransition guidance. Foundation for gender-affirming therapy principles.

```bash
uv run med-db --pmid 36238954 --validate
```

### 1.2 Meyer (2003) — Minority Stress Model

**PMID:** 12956539
**Why:** Foundational conceptual framework. Distal stressors (discrimination, violence) → proximal stressors
(expectations of rejection, concealment, internalized stigma) → mental health disparities. The theoretical
basis for understanding TNB mental health disparities.

```bash
uv run med-db --pmid 12956539 --validate
```

### 1.3 Hendricks & Testa (2012) — Gender Minority Stress Adaptation

**DOI:** 10.1037/a0029597
**Why:** Landmark adaptation of Meyer's minority stress model for TGNC populations. Maps distal and proximal
stressors specific to gender minority experience. Adds nonaffirmation as a TNB-specific distal stressor.

Resolve DOI first, then archive:

```bash
uv run med-db-lookup --doi 10.1037/a0029597
```

### 1.4 Testa et al. (2015) — Gender Minority Stress and Resilience Measure

**DOI:** 10.1037/sgd0000081
**Why:** Validated 58-item GMSR measure (n=844). Nine constructs: discrimination, rejection, victimization,
nonaffirmation, internalized transphobia, negative expectations, nondisclosure, community connectedness, pride.
Clinical and research tool for assessing minority stress in TNB clients.

Resolve DOI and archive as above.

---

## Phase 2: Core PMIDs — TNB Mental Health

Archive under `trans-nb-mental-health`.

### 2.1 Hainey et al. (2025) — Umbrella Review of TNB Mental Health

**PMID:** 40768163
**Why:** 24 systematic reviews synthesized. Pooled prevalence: suicidal ideation 50%, suicide attempts 29%,
NSSI 47%, eating disorders 18%, ASD 11%. OR vs. cisgender: suicidal ideation 3.48, suicide attempts 3.45.
Critical for evidence-backed prevalence data.

```bash
uv run med-db --pmid 40768163 --validate
```

### 2.2 Polidori et al. (2024) — Suicide Attempt Meta-Analysis

**PMID:** 38320410
**Why:** 35 reports, 37,563 gender-diverse individuals. Suicide attempt rate 20.1% vs. cisgender 1.90% —
a 10.6-fold difference. Most cited statistic for TNB suicide risk.

```bash
uv run med-db --pmid 38320410 --validate
```

### 2.3 Pinna et al. (2022) — Mental Health in Transgender Individuals

**PMID:** 36151828
**Why:** Systematic review of 165 articles. Extensive evidence for elevated depression, anxiety, substance use
disorders, and trauma-related disorders in TNB populations.

```bash
uv run med-db --pmid 36151828 --validate
```

### 2.4 Klinger et al. (2024) — Non-Binary Youth Mental Health Meta-Analysis

**PMID:** 39385290
**Why:** 21 studies, 16,114 non-binary participants. Non-binary vs. cisgender: worse general mental health
(d=0.48), elevated depression (d=0.52), elevated anxiety (d=0.44). Non-binary vs. binary trans: worse general
mental health (d=0.24).

```bash
uv run med-db --pmid 39385290 --validate
```

### 2.5 Kallstrom et al. (2022) — Finnish Population Study

**PMID:** 36327285
**Why:** Population-based (n=8,589). Non-binary individuals reported highest rates of anxiety and depression
among all sexual and gender minority subgroups. Key evidence for non-binary-specific mental health disparities.

```bash
uv run med-db --pmid 36327285 --validate
```

---

## Phase 3: Core PMIDs — Intersection with Neurodivergence

Archive under `gender-affirming-care`.

### 3.1 Kallitsounaki et al. (2023) — ASD and Gender Dysphoria Meta-Analysis

**PMID:** 35596023
**Why:** Pooled prevalence of ASD diagnoses in GD populations: 11%. Effect size for ASD traits in GD vs.
controls: g=0.67. Concludes chances of no link between ASD and GD are "negligible."

```bash
uv run med-db --pmid 35596023 --validate
```

### 3.2 Bouzy et al. (2023) — Transidentities and ASD Systematic Review

**PMID:** 36996732
**Why:** 77 articles. Five themes: sex ratio, explanatory theories, sexual orientation, clinical/social
consequences, care implications. Explicitly states autism is NOT a contraindication for gender-affirming
treatment.

```bash
uv run med-db --pmid 36996732 --validate
```

### 3.3 Thrower et al. (2020) — ASD and ADHD in Gender Dysphoria

**PMID:** 31732891
**Why:** 30 studies. ASD prevalence in transgender populations: 6-26% using formal diagnostic criteria.
Evidence for ADHD rates insufficient but elevated.

```bash
uv run med-db --pmid 31732891 --validate
```

---

## Phase 4: Core PMIDs — Eating Disorders & Trauma in TNB Populations

Archive under `trans-nb-mental-health`.

### 4.1 Campbell et al. (2024) — Disordered Eating in TNB Youth

**PMID:** 37791928
**Why:** 26 articles. Formal ED diagnoses 2-18%; 42% endorsed disordered eating behaviors. Motivations often
tied to managing gender dysphoria (caloric restriction to suppress secondary sex characteristics).

```bash
uv run med-db --pmid 37791928 --validate
```

### 4.2 Heiden-Rootes et al. (2023) — Eating Disorders in TNB Youth Scoping Review

**PMID:** 37740228
**Why:** 49 studies. Body-gender congruence through gender-affirming interventions significantly alleviates
body image problems and facilitates ED treatment.

```bash
uv run med-db --pmid 37740228 --validate
```

### 4.3 Brewerton et al. (2021) — PTSD and Trauma in Sexual/Gender Minorities

**PMID:** 34057704
**Why:** LGBTQ+ individuals in ED treatment: 63% presumptive PTSD vs. 45% in non-LGBTQ+, more lifetime traumas,
greater severity of unwanted sexual experiences and physical assaults.

```bash
uv run med-db --pmid 34057704 --validate
```

---

## Phase 5: DOI-Only References

These papers may not have PMIDs (published in APA journals not always indexed in PubMed). Resolve via DOI
lookup first; fall back to Europe PMC search.

Archive under `gender-affirming-care`.

### 5.1 Lampe et al. (2025) — Trans Older Adults and Anti-Trans Legislation

**PMID:** 40929668
**Why:** Protective strategies: defining trans identity as life-affirming, cultivating trans-inclusive networks.

```bash
uv run med-db --pmid 40929668 --validate
```

### 5.2 Medina-Martinez et al. (2021) — LGBT Health Inequities and Intersectionality

**PMID:** 34831556
**Why:** 16 studies. Trans women of color in poverty/sex work at highest risk. Intersectionality modifies
minority stress impacts.

```bash
uv run med-db --pmid 34831556 --validate
```

### 5.3 Gender-affirming language systematic review (2025)

**PMID:** 41385937
**Why:** Core recommendations: follow client's lead with language, practice explicit allyship, periodic training.
Most impactful single change: correct names and pronouns.

```bash
uv run med-db --pmid 41385937 --validate
```

### 5.4 Non-binary healthcare experiences (2024)

**PMID:** 39247404
**Why:** Non-binary people less likely to feel respected, more likely misgendered, less likely to report
adequate provider knowledge. Identity-specific stigma distinct from binary trans experience.

```bash
uv run med-db --pmid 39247404 --validate
```

### 5.5 Mezzalira et al. (2025) — TNB Psychotherapeutic Experiences

**PMID:** 40019470
**Why:** Mixed-method systematic review. Negative experiences: micro/macroaggressions, inadequate trans-specific
knowledge, pathologization of TNB identities, reinforcement of cis/heteronormative stereotypes.

```bash
uv run med-db --pmid 40019470 --validate
```

---

## Phase 6: PubMed Search Queries

### 6.1 Gender-affirming care mental health outcomes

```bash
uv run med-db --query 'gender-affirming care mental health outcomes transgender adults systematic review' --archive-first 5 --validate
```

Archive under `gender-affirming-care`.

### 6.2 Non-binary mental health

```bash
uv run med-db --query 'non-binary gender diverse mental health depression anxiety systematic review' --archive-first 5 --validate
```

Archive under `trans-nb-mental-health`.

### 6.3 Transgender minority stress interventions

```bash
uv run med-db --query 'transgender minority stress intervention resilience psychotherapy affirmative' --archive-first 5 --validate
```

Archive under `gender-affirming-care`.

---

## Phase 7: Validation

```bash
uv run med-db-validate --med-db med-db
uv run med-db-query --list-topics
uv run med-db-query --topic gender-affirming-care
uv run med-db-query --topic trans-nb-mental-health
```
