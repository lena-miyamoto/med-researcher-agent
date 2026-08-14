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

Directs med-researcher agent what to archive in `med-db/` for psychotherapist agent's local evidence base on gender-affirming care and TNB mental health. Read-only.

## Archive access

All archive and query operations go through the `med-db` skill. Archive each PMID/DOI under the topic named in its phase heading.

## Pre-flight

Verify `med-db/` exists, check existing topics via the `med-db` skill (`med-db-query --list-topics`).

If `gender-affirming-care` and `trans-nb-mental-health` both have papers, knowledge base may already be bootstrapped. Check each via `med-db-query --topic <slug>`.

Both populated → skip to report. Otherwise proceed through phases.

---

## Phase 1: Core PMIDs — Clinical Guidelines & Minority Stress

Archive under `gender-affirming-care`.

### 1.1 WPATH Standards of Care Version 8 (2022)

**PMID:** 36238954
**Why:** International clinical guideline for TNB healthcare. First WPATH version with formal evidence-based methodology. One referral letter for adults, no mandatory psychotherapy, explicit prohibition of conversion therapy, first-time detransition guidance. Foundation for gender-affirming therapy principles.

### 1.2 Meyer (2003) — Minority Stress Model

**PMID:** 12956539
**Why:** Foundational conceptual framework. Distal stressors (discrimination, violence) → proximal stressors (expectations of rejection, concealment, internalized stigma) → mental health disparities. Theoretical basis for TNB mental health disparities.

### 1.3 Hendricks & Testa (2012) — Gender Minority Stress Adaptation

**DOI:** 10.1037/a0029597
**Why:** Landmark adaptation of Meyer's minority stress model for TGNC populations. Maps distal and proximal stressors specific to gender minority experience. Adds nonaffirmation as TNB-specific distal stressor.

Resolve the DOI via the `med-db` skill (`med-db-lookup`), then archive under `gender-affirming-care`.

### 1.4 Testa et al. (2015) — Gender Minority Stress and Resilience Measure

**DOI:** 10.1037/sgd0000081
**Why:** Validated 58-item GMSR measure (n=844). Nine constructs: discrimination, rejection, victimization, nonaffirmation, internalized transphobia, negative expectations, nondisclosure, community connectedness, pride. Clinical and research tool for assessing minority stress in TNB clients.

Resolve the DOI and archive as 1.3.

---

## Phase 2: Core PMIDs — TNB Mental Health

Archive under `trans-nb-mental-health`.

### 2.1 Hainey et al. (2025) — Umbrella Review of TNB Mental Health

**PMID:** 40768163
**Why:** 24 systematic reviews synthesized. Pooled prevalence: suicidal ideation 50%, suicide attempts 29%, NSSI 47%, eating disorders 18%, ASD 11%. OR vs. cisgender: suicidal ideation 3.48, suicide attempts 3.45. Critical for evidence-backed prevalence data.

### 2.2 Polidori et al. (2024) — Suicide Attempt Meta-Analysis

**PMID:** 38320410
**Why:** 35 reports, 37,563 gender-diverse individuals. Suicide attempt rate 20.1% vs. cisgender 1.90% — 10.6-fold difference. Most cited statistic for TNB suicide risk.

### 2.3 Pinna et al. (2022) — Mental Health in Transgender Individuals

**PMID:** 36151828
**Why:** Systematic review of 165 articles. Extensive evidence for elevated depression, anxiety, substance use disorders, and trauma-related disorders in TNB populations.

### 2.4 Klinger et al. (2024) — Non-Binary Youth Mental Health Meta-Analysis

**PMID:** 39385290
**Why:** 21 studies, 16,114 non-binary participants. Non-binary vs. cisgender: worse general mental health (d=0.48), elevated depression (d=0.52), elevated anxiety (d=0.44). Non-binary vs. binary trans: worse general mental health (d=0.24).

### 2.5 Kallstrom et al. (2022) — Finnish Population Study

**PMID:** 36327285
**Why:** Population-based (n=8,589). Non-binary individuals reported highest rates of anxiety and depression among all sexual and gender minority subgroups. Key evidence for non-binary-specific mental health disparities.

---

## Phase 3: Core PMIDs — Intersection with Neurodivergence

Archive under `gender-affirming-care`.

### 3.1 Kallitsounaki et al. (2023) — ASD and Gender Dysphoria Meta-Analysis

**PMID:** 35596023
**Why:** Pooled prevalence of ASD diagnoses in GD populations: 11%. Effect size for ASD traits in GD vs. controls: g=0.67. Concludes chances of no link between ASD and GD are "negligible."

### 3.2 Bouzy et al. (2023) — Transidentities and ASD Systematic Review

**PMID:** 36996732
**Why:** 77 articles. Five themes: sex ratio, explanatory theories, sexual orientation, clinical/social consequences, care implications. Explicitly states autism is NOT a contraindication for gender-affirming treatment.

### 3.3 Thrower et al. (2020) — ASD and ADHD in Gender Dysphoria

**PMID:** 31732891
**Why:** 30 studies. ASD prevalence in transgender populations: 6-26% using formal diagnostic criteria. Evidence for ADHD rates insufficient but elevated.

---

## Phase 4: Core PMIDs — Eating Disorders & Trauma in TNB Populations

Archive under `trans-nb-mental-health`.

### 4.1 Campbell et al. (2024) — Disordered Eating in TNB Youth

**PMID:** 37791928
**Why:** 26 articles. Formal ED diagnoses 2-18%; 42% endorsed disordered eating behaviors. Motivations often tied to managing gender dysphoria (caloric restriction to suppress secondary sex characteristics).

### 4.2 Heiden-Rootes et al. (2023) — Eating Disorders in TNB Youth Scoping Review

**PMID:** 37740228
**Why:** 49 studies. Body-gender congruence through gender-affirming interventions significantly alleviates body image problems and facilitates ED treatment.

### 4.3 Brewerton et al. (2021) — PTSD and Trauma in Sexual/Gender Minorities

**PMID:** 34057704
**Why:** LGBTQ+ individuals in ED treatment: 63% presumptive PTSD vs. 45% in non-LGBTQ+, more lifetime traumas, greater severity of unwanted sexual experiences and physical assaults.

---

## Phase 5: DOI-Only References

May lack PMIDs (APA journals not always indexed in PubMed). Resolve via DOI lookup first; fall back to Europe PMC search.

Archive under `gender-affirming-care`.

### 5.1 Lampe et al. (2025) — Trans Older Adults and Anti-Trans Legislation

**PMID:** 40929668
**Why:** Protective strategies: defining trans identity as life-affirming, cultivating trans-inclusive networks.

### 5.2 Medina-Martinez et al. (2021) — LGBT Health Inequities and Intersectionality

**PMID:** 34831556
**Why:** 16 studies. Trans women of color in poverty/sex work at highest risk. Intersectionality modifies minority stress impacts.

### 5.3 Gender-affirming language systematic review (2025)

**PMID:** 41385937
**Why:** Core recommendations: follow client's lead with language, practice explicit allyship, periodic training. Most impactful single change: correct names and pronouns.

### 5.4 Non-binary healthcare experiences (2024)

**PMID:** 39247404
**Why:** Non-binary people less likely to feel respected, more likely misgendered, less likely to report adequate provider knowledge. Identity-specific stigma distinct from binary trans experience.

### 5.5 Mezzalira et al. (2025) — TNB Psychotherapeutic Experiences

**PMID:** 40019470
**Why:** Mixed-method systematic review. Negative experiences: micro/macroaggressions, inadequate trans-specific knowledge, pathologization of TNB identities, reinforcement of cis/heteronormative stereotypes.

---

## Phase 6: PubMed Search Queries

Run each query via the `med-db` skill, archive the most relevant results under the stated topic.

### 6.1 Gender-affirming care mental health outcomes

Search PubMed via the `med-db` skill for `gender-affirming care mental health outcomes transgender adults systematic review`, archive first 5 under `gender-affirming-care`.

### 6.2 Non-binary mental health

Search PubMed via the `med-db` skill for `non-binary gender diverse mental health depression anxiety systematic review`, archive first 5 under `trans-nb-mental-health`.

### 6.3 Transgender minority stress interventions

Search PubMed via the `med-db` skill for `transgender minority stress intervention resilience psychotherapy affirmative`, archive first 5 under `gender-affirming-care`.

---

## Phase 7: Validation

Run validation via the `med-db` skill (`med-db-integrity-check`), then verify topics are populated via `med-db-query --list-topics` and `--topic <slug>` for `gender-affirming-care` and `trans-nb-mental-health`.
