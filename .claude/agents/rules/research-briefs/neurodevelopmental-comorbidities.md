---
description: >
  Research brief for the med-researcher agent. Archives the core evidence base on adult ADHD, ASD, AuDHD
  (co-occurring ADHD+ASD), and common psychiatric comorbidities (depression, bipolar disorder, anxiety disorders,
  OCD, PTSD, substance use disorders, sleep disorders, eating disorders, personality disorders) into med-db/.
  Run once per system to bootstrap the psychotherapist agent's local knowledge base.
topics:
  - adhd-comorbidity
  - asd-comorbidity
  - neurodevelopmental-overlap
version: 1.0.0
last_updated: 2026-07-15
---

# Neurodevelopmental Comorbidities — Knowledge Base Bootstrap

Directs med-researcher agent what to archive in `med-db/` for psychotherapist agent's local, reproducible evidence base on adult ADHD, ASD, AuDHD, and common comorbidities. Same papers used to build psychotherapist's Neurodevelopmental Specialization. Read-only. Never edit. Archive under topics in frontmatter.

## Pre-flight

Verify `med-db/` exists. If not, any archival command auto-creates directory tree and `index.json`. No manual setup.

Check existing archives:

```bash
uv run med-db-query --list-topics
```

If `adhd-comorbidity`, `asd-comorbidity`, and `neurodevelopmental-overlap` all have papers, knowledge base may already be bootstrapped. Check each:

```bash
uv run med-db-query --topic adhd-comorbidity
uv run med-db-query --topic asd-comorbidity
uv run med-db-query --topic neurodevelopmental-overlap
```

All three populated → bootstrap complete. Stop, report to psychotherapist agent. Otherwise proceed, skipping populated topics.

---

## Phase 1: Core PMIDs — ADHD Comorbidity

Archive under `adhd-comorbidity`. Foundation for ADHD comorbidity prevalence and clinical management.

### 1.1 Katzman et al. (2017) — Adult ADHD and comorbid disorders

**PMID:** 28830387
**Why:** Comprehensive review of adult ADHD comorbidity prevalence, clinical implications. Covers mood, anxiety, substance use, and personality disorder comorbidity. Foundational reference for psychotherapist's ADHD specialization.

```bash
uv run med-db --pmid 28830387 --validate
```

### 1.2 Schiweck et al. (2021) — ADHD and adult bipolar disorder

**PMID:** 33515606
**Why:** Pooled BD prevalence in adults with ADHD (~7.95%), pooled OR 8.7, BD onset ~4 years earlier with comorbid ADHD. 17.11% of BD adults have ADHD. Critical for bipolar differential diagnosis guidance.

```bash
uv run med-db --pmid 33515606 --validate
```

### 1.3 Nazar et al. (2016) — Eating disorders comorbid with ADHD

**PMID:** 27859581
**Why:** Pooled OR 3.82 for any ED in ADHD, bulimia OR 5.71, BED OR 4.13. Bidirectional relationship. Foundation for psychotherapist's eating disorder screening recommendations.

```bash
uv run med-db --pmid 27859581 --validate
```

### 1.4 Bond et al. (2012) — CANMAT task force: mood disorders and comorbid ADHD

**PMID:** 22303520
**Why:** Clinical guidelines for treating ADHD in bipolar disorder. "Stabilize mood first" principle, bupropion as first-line ADHD treatment in BD, stimulant precautions. Referenced in bipolar differential and treatment sequencing.

```bash
uv run med-db --pmid 22303520 --validate
```

### 1.5 Diaz-Roman et al. (2018) — Sleep in adults with ADHD

**PMID:** 29604351
**Why:** Adults with ADHD show longer sleep onset latency, reduced sleep efficiency, elevated subjective insomnia. Foundation for psychotherapist's sleep disorder guidance (43–80% prevalence).

```bash
uv run med-db --pmid 29604351 --validate
```

### 1.6 Choi et al. (2025) — Personality disorders in adults with ADHD: meta-analysis

**DOI:** 10.1016/j.jad.2025.01.013
**Why:** Pooled 57% any PD prevalence in adults with ADHD. High BPD overlap (~22%). Foundation for personality disorder differential diagnosis guidance.

Resolve the DOI first:

```bash
uv run med-db-lookup --doi 10.1016/j.jad.2025.01.013
```

Then archive by PMID from lookup, or if no PMID, via Europe PMC:

```bash
uv run med-db --source europe-pmc --query "Choi 2025 personality disorders ADHD adult meta-analysis" --archive-first 1 --validate
```

### 1.7 Magdi et al. (2025) — ADHD and PTSD adult comorbidity: systematic review

**DOI:** 10.1186/s13643-025-02774-7
**Why:** Pooled PTSD prevalence in ADHD ~36%, ADHD in PTSD ~28%, up to 4× PTSD risk. Genetic correlation rg = 0.66. Foundation for psychotherapist's trauma screening recommendations.

Resolve DOI and archive as above.

---

## Phase 2: Core PMIDs — ASD Comorbidity

Archive under `asd-comorbidity`.

### 2.1 Micai et al. (2023) — Prevalence of co-occurring conditions in ASD

**PMID:** 37913872
**Why:** 340 studies, ~590,000 participants. Pooled point-prevalence for 38 conditions in ASD. Adult-specific estimates: depression 34%, anxiety 28%, ADHD 22%, OCD 10%, bipolar 9%. Single most important reference for ASD comorbidity prevalence.

```bash
uv run med-db --pmid 37913872 --validate
```

### 2.2 Lugo-Marin et al. (2019) — Psychiatric disorders in adults with ASD

**PMID:** 30903940
**Why:** 54.8% of adults with ASD have ≥1 psychiatric disorder. ADHD most prevalent, then mood and anxiety disorders. Key reference for psychotherapist's ASD specialization.

```bash
uv run med-db --pmid 30903940 --validate
```

### 2.3 McDougle et al. (2025) — Pharmacological treatment in autism

**DOI:** 10.1186/s12916-024-03814-0
**Why:** Lurie Center consensus guidelines. First-line recommendations differ from non-autistic SOC: buspirone and mirtazapine over SSRIs for anxiety; duloxetine, mirtazapine, bupropion, vortioxetine over SSRIs for depression. "Start low, go slow." Foundation for psychotherapist's ASD treatment guidance.

Resolve DOI and archive as above.

---

## Phase 3: Core PMIDs — ADHD + ASD Overlap

Archive under `neurodevelopmental-overlap`.

### 3.1 Xenaki et al. (2020) — Lifetime comorbidity in adults with ADHD or/and ASD

**PMID:** 32873239
**Why:** 336 newly diagnosed adults. ADHD+ASD group: 72.4% had ≥1 additional disorder. ADHD-only: 72.8%, ASD-only: 50%. Depressive disorder most common across all groups. Foundation for AuDHD profile.

```bash
uv run med-db --pmid 32873239 --validate
```

---

## Phase 4: PubMed Search Queries

Broaden evidence base beyond core PMIDs. Run each query, archive most relevant results, note findings.

### 4.1 ADHD comorbidity in adults — systematic reviews

```bash
uv run med-db --query 'adult ADHD comorbidity prevalence systematic review meta-analysis' --archive-first 5 --validate
```

Archive results under `adhd-comorbidity`.

### 4.2 ASD psychiatric comorbidity in adults

```bash
uv run med-db --query 'adult autism spectrum disorder psychiatric comorbidity prevalence systematic review' --archive-first 5 --validate
```

Archive results under `asd-comorbidity`.

### 4.3 ADHD bipolar disorder treatment guidelines

```bash
uv run med-db --query 'ADHD bipolar disorder treatment guidelines adults comorbidity management' --archive-first 3 --validate
```

Archive results under `adhd-comorbidity`.

### 4.4 ASD pharmacological treatment comorbid psychiatric symptoms

```bash
uv run med-db --query 'autism spectrum disorder pharmacological treatment comorbid anxiety depression guidelines adults' --archive-first 5 --validate
```

Archive results under `asd-comorbidity`.

### 4.5 ADHD PTSD comorbidity neurobiological overlap

```bash
uv run med-db --query 'ADHD PTSD comorbidity adult prevalence neurobiological overlap treatment' --archive-first 5 --validate
```

Archive results under `adhd-comorbidity`.

### 4.6 AuDHD (ADHD + autism combined) psychiatric comorbidity

```bash
uv run med-db --query 'ADHD autism combined comorbidity adults AuDHD psychiatric disorders prevalence' --archive-first 5 --validate
```

Archive results under `neurodevelopmental-overlap`.

---

## Phase 5: Validation

After all phases, run comprehensive validation:

```bash
uv run med-db-integrity-check --med-db med-db
```

Then verify the topics are populated:

```bash
uv run med-db-query --list-topics
```

Expected topics: `adhd-comorbidity`, `asd-comorbidity`, `neurodevelopmental-overlap`. If queries returned papers on additional topics, those appear as well.

Check each topic has papers:

```bash
uv run med-db-query --topic adhd-comorbidity
uv run med-db-query --topic asd-comorbidity
uv run med-db-query --topic neurodevelopmental-overlap
```

---

## Psychotherapist Agent Usage

Once archived, psychotherapist agent queries med-db/ for evidence-backed comorbidity data:

```bash
# List all comorbidity papers
uv run med-db-query --topic adhd-comorbidity
uv run med-db-query --topic asd-comorbidity
uv run med-db-query --topic neurodevelopmental-overlap

# Look up a specific reference
uv run med-db-lookup --pmid 28830387

# Keyword search across all topics
uv run med-db-query --search-keyword lisdexamfetamine

# Read full metadata for a paper
uv run med-db-query --read-metadata papers/adhd-comorbidity/pmid-28830387-katzman-adult-adhd-comorbid-disorders
```

Read-only queries — work without knowledge of archive layout. Only need topic slugs and PMID lookup.

---

## Notes

- **Recency window:** Med-researcher enforces 10-year window (5 years for pharmacology). Most references within window. Older papers (e.g., Bond 2012) flagged as foundational, not superseded.
- **Counter-evidence:** Med-researcher searches for contradicting evidence per mandatory counter-evidence protocol. Expected and valuable — higher-quality contradicting evidence surfaced to psychotherapist.
- **Updates:** Re-run every 12 months to capture new systematic reviews and meta-analyses. Review psychotherapist agent's specialization section at same cadence.
- **DOI-only references:** Choi (2025), Magdi (2025), McDougle (2025) are recent, may lack PMIDs. Resolve via DOI lookup first, fall back to Europe PMC search. May not be PubMed-indexed yet.
