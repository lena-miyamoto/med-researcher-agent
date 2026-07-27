---
description: >
  Research brief for the med-researcher agent. Archives the core evidence base on sex therapy (Sensate Focus,
  PLISSIT, CBST), kink-positive/BDSM-affirming practice, polyamory/consensual non-monogamy, LGBTQI+ affirmative
  therapy, relationship diversity, and the neurodivergence-sexuality intersection. Run once per system to
  bootstrap the psychotherapist agent's sex and relationship therapy knowledge base.
topics:
  - sex-therapy
  - relationship-diversity
version: 1.0.0
last_updated: 2026-07-15
---

# Sex Therapy & Relationship Diversity — Knowledge Base Bootstrap

This brief tells the med-researcher agent exactly what to archive in `med-db/` so the psychotherapist agent has a
local evidence base for sex therapy, kink-positive practice, and LGBTQI+/polyamory-affirming relationship therapy.
Treat this brief as read-only.

## Pre-flight

Verify `med-db/` exists and check existing topics:

```bash
uv run med-db-query --list-topics
```

If `sex-therapy` and `relationship-diversity` both have papers, the knowledge base may already be bootstrapped.
Check each:

```bash
uv run med-db-query --topic sex-therapy
uv run med-db-query --topic relationship-diversity
```

If both are populated, skip to the report. Otherwise, proceed through the phases.

---

## Phase 1: Core PMIDs — Sex Therapy Foundations

Archive under `sex-therapy`.

### 1.1 Ramirez-Santos et al. (2024) — Sexual Dysfunction Prevalence Meta-Analysis

**PMID:** 38336366
**Why:** 58,849 men, 73,379 women. Prevalence: men 31%, women 41% (44.3% with validated instruments). Provides
the population baseline for sexual dysfunction — essential for normalizing and contextualizing client concerns.

```bash
uv run med-db --pmid 38336366 --validate
```

### 1.2 Ozdemir et al. (2024) — PLISSIT Model Meta-Analysis

**PMID:** 38890226
**Why:** 18 studies. PLISSIT significantly improved sexual function (SMD 1.68) and communication satisfaction
(SMD 0.75). Evidence for the graduated intervention model used in sex therapy.

```bash
uv run med-db --pmid 38890226 --validate
```

### 1.3 Sharifipour et al. (2024) — CBT for Female Sexual Dysfunction

**PMID:** 39148917
**Why:** 7 clinical trials (448 women). CBT significantly improved overall sexual function (SMD 1.34), desire,
orgasm, satisfaction, lubrication, and assertiveness. Foundation for CBST efficacy.

```bash
uv run med-db --pmid 39148917 --validate
```

### 1.4 Liu et al. (2025) — CBT Meta-Analysis for Female Sexual Dysfunction

**PMID:** 40151032
**Why:** 10 RCTs (837 patients). CBT showed greater FSFI score increases vs. routine care (MD 7.63) and waitlist
(MD 3.13). More recent meta-analysis confirming CBST efficacy.

```bash
uv run med-db --pmid 40151032 --validate
```

---

## Phase 2: Core PMIDs — Kink-Positive / BDSM-Affirming Practice

Archive under `sex-therapy`.

### 2.1 Brown et al. (2019) — BDSM Prevalence Scoping Review

**PMID:** 31617765
**Why:** 60 studies. BDSM fantasies in 40-70% of people; ~20% engage in BDSM behaviors; 7.6% self-identify as
BDSM practitioners. Establishes that BDSM interests are common, not rare or pathological.

```bash
uv run med-db --pmid 31617765 --validate
```

### 2.2 Dunkley & Brotto (2018) — BDSM Clinical Considerations

**PMID:** 29543573
**Why:** Exhaustive review: BDSM practitioners differ minimally from general population in psychopathology —
same rates of mental illness, psychological adjustment, and distress. Less neurotic, more extraverted, more
conscientious, less rejection-sensitive. Foundation for depathologizing BDSM in clinical practice.

```bash
uv run med-db --pmid 29543573 --validate
```

### 2.3 Kolmes, Stock & Moser (2006) — Psychotherapy Bias with BDSM Clients

**PMID:** 16803769
**Why:** Survey of 175 BDSM-identified therapy clients. Documented biased care: pathologization of practices,
misinterpretation as abuse or personality disorder, assumptions about unfit parenting, empathic failures.
Foundation for the "common mistakes" guidance.

```bash
uv run med-db --pmid 16803769 --validate
```

### 2.4 Waldura et al. (2016) — Fifty Shades of Stigma

**PMID:** 28340946
**Why:** Focus groups with 115 kink-oriented patients. Anticipated stigma most common barrier to disclosure;
fewer than half had disclosed. Patients feared clinicians would confuse consensual BDSM with IPV.

```bash
uv run med-db --pmid 28340946 --validate
```

---

## Phase 3: Core PMIDs — Polyamory / CNM

Archive under `relationship-diversity`.

### 3.1 Haupert et al. (2017) — CNM Prevalence

**PMID:** 27096488
**Why:** Two US Census-based quota samples (n=8,718). 21.9% and 21.2% reported lifetime CNM engagement. Constant
across demographics. Foundation for normalizing CNM as a common relationship structure.

```bash
uv run med-db --pmid 27096488 --validate
```

### 3.2 Schechinger, Sakaluk & Moors (2018) — CNM Therapy Practices

**PMID:** 30335421
**Why:** 249 CNM individuals. Both exemplary practices (affirming, knowledgeable) and inappropriate practices
(biased, uninformed) significantly predicted therapist helpfulness ratings and premature termination. Foundation
for the do's and don'ts of CNM-affirming therapy.

```bash
uv run med-db --pmid 30335421 --validate
```

### 3.3 Campbell et al. (2024) — CNM Sexual Health Care Experiences

**PMID:** 37641450
**Why:** 67 CNM individuals. Significantly lower trust in healthcare professionals. 37% sometimes or never
disclosed relationship status. Experiences ranged from accepting to withholding treatment.

```bash
uv run med-db --pmid 37641450 --validate
```

### 3.4 Vaughan et al. (2019) — CNM Healthcare Experiences

**PMID:** 30621924
**Why:** 20 CNM adults in focus groups. Documented lack of provider knowledge, inadequate screenings, stigmatizing
behaviors. Foundation for understanding systemic barriers CNM clients face.

```bash
uv run med-db --pmid 30621924 --validate
```

---

## Phase 4: Core PMIDs — LGBTQI+ Affirmative Therapy

Archive under `relationship-diversity`.

### 4.1 Nakamura et al. (2022) — APA Guidelines for Sexual Minority Persons

**PMID:** 35143229
**Why:** Executive summary of APA Guidelines. Three lenses: affirmative practice, minority stress theory,
intersectionality. Foundation for what constitutes truly affirming (vs. merely tolerant) care.

```bash
uv run med-db --pmid 35143229 --validate
```

---

## Phase 5: Core PMIDs — Neurodivergence & Sexuality Intersection

Archive under `sex-therapy`.

### 5.1 Young & Cocallis (2023) — Neurodiversity and Psychosexual Functioning

**PMID:** 37287894
**Why:** 17 ASD studies, 19 ADHD studies. Poorer psychosexual functioning for both groups: less satisfaction,
more dysfunction, more risky behaviors, more victimization — especially females. Non-heterosexual orientation
more common in ASD. Foundation for the neurodivergence-sexuality clinical guidance.

```bash
uv run med-db --pmid 37287894 --validate
```

---

## Phase 6: DOI-Only and Key References Without PMIDs

Some key references come from APA journals or clinical publications not always indexed in PubMed. Resolve via DOI
lookup first, then fall back to Europe PMC search. Archive under `sex-therapy`.

### 6.1 Moser & Kleinplatz (2005) — DSM Paraphilias Critique

**DOI:** 10.1300/J082v50n02_15 (same as Kolmes et al., PMID 16803769 above)
The foundational critique arguing paraphilias do not meet DSM's own definition of mental disorder. This paper
and Kleinplatz & Moser (2006) *Sadomasochism: Powerful Pleasures* (Routledge, ISBN 9781560236405) are the
intellectual foundation for the DSM-5 paraphilic disorders distinction.

### 6.2 Kink Clinical Practice Guidelines

**URL:** <https://www.kinkguidelines.com>
2019 original, 2026 revision. 23 aspirational guidelines for clinicians working with kink-identified clients.
Archived as a web source:

```bash
uv run med-db --source doaj --query 'kink clinical practice guidelines sprott' --search-slug 'kink-guidelines' --validate
```

### 6.3 TASHRA Kink Core Competencies

**URL:** <https://www.tashra.org>
Progressive competency levels (0.5 through 3) for clinicians working with kink-identified clients. Search and
archive:

```bash
uv run med-db --source google-scholar --query 'TASHRA kink core competencies clinical training' --search-slug 'tashra-competencies' --validate
```

---

## Phase 7: PubMed Search Queries

### 7.1 Sex therapy modalities efficacy

```bash
uv run med-db --query 'sex therapy cognitive behavioral sensate focus efficacy systematic review meta-analysis' --archive-first 5 --validate
```

Archive under `sex-therapy`.

### 7.2 Consensual non-monogamy mental health

```bash
uv run med-db --query 'consensual non-monogamy polyamory mental health relationship satisfaction systematic review' --archive-first 5 --validate
```

Archive under `relationship-diversity`.

### 7.3 Kink BDSM mental health

```bash
uv run med-db --query 'BDSM kink mental health psychotherapy stigma clinical guidelines' --archive-first 5 --validate
```

Archive under `sex-therapy`.

### 7.4 LGBTQ affirmative therapy outcomes

```bash
uv run med-db --query 'LGBTQ affirmative therapy outcomes mental health cognitive behavioral minority stress' --archive-first 5 --validate
```

Archive under `relationship-diversity`.

---

## Phase 8: Validation

```bash
uv run med-db-integrity-check --med-db med-db
uv run med-db-query --list-topics
uv run med-db-query --topic sex-therapy
uv run med-db-query --topic relationship-diversity
```
