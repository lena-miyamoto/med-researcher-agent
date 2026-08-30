---
description: >
  Research brief for the med-researcher agent. Archives the core evidence base on voice feminization for
  trans women and transfeminine people — WPATH SOC-8 voice chapter, Schwarz 2023 meta-analysis, Leyns et
  al. RCTs, TWVQ validation, German consensus guidance, and foundational source-filter perception
  studies. Run once per system to bootstrap the voice-trainer agent's knowledge base.
topics:
  - voice-feminization
version: 1.0.0
last_updated: 2026-08-30
---

# Voice Feminization — Knowledge Base Bootstrap

Directs med-researcher agent what to archive in `med-db/` for voice-trainer agent's local evidence base:
voice feminization research and guidelines. Read-only.

## Archive access

All archive and query operations go through the `med-db` skill. Archive each PMID under the topic named
in its phase heading.

## Pre-flight

Verify `med-db/` exists, check existing topics via the `med-db` skill (`med-db-query --list-topics`).

If `voice-feminization` has papers, the knowledge base may already be bootstrapped. Check via
`med-db-query --topic voice-feminization`. Populated → skip to report. Otherwise proceed through phases.

---

## Phase 1: Core PMIDs — Guidelines and Outcomes

Archive under `voice-feminization`.

### 1.1 Coleman et al. (2022) — WPATH Standards of Care Version 8, Voice Chapter

**PMID:** 36238954
**Why:** International clinical guideline. Voice chapter covers: assessment, individualized voice
intervention, referral pathways, pre-/post-operative voice support, and the fact that estrogen does
not change the adult voice. Foundation for all coaching practice.

### 1.2 Schwarz et al. (2023) — Voice Therapy Systematic Review / Meta-Analysis

**PMID:** 37481572
**Why:** Meta-analysis of voice therapy outcomes for trans women. Mean F0 gains: +27 Hz (sustained
vowel), +39 Hz (reading), +25 Hz (spontaneous speech). The standard effect-size reference for
program design and client expectation-setting.

### 1.3 Leyns et al. (2024) — Sham-Controlled Crossover RCT (Short Term)

**PMID:** 39465090
**Why:** Ghent RCT, 14-week program with pitch-elevating (PET) and articulation-resonance (ART)
blocks. Speaking F0 +49 Hz; combination of both dimensions beat single-dimension work. The strongest
controlled-trial evidence for multi-dimensional programs; also the source of the "as high as
possible without strain" pitch rule.

### 1.4 Leyns et al. (2024) — Long-Term Acoustic Effects

**PMID:** 38704279
**Why:** Follow-up of the Ghent cohort: gains largely stable at 1 year; lower F0 limit unchanged.
Evidence for durability of trained gains.

### 1.5 Dacakis et al. (2013) — TWVQ Development and Validation

**PMID:** 23415146
**Why:** The Trans Woman Voice Questionnaire — validated 30-item voice-related quality-of-life
measure for trans women. The standard client-reported outcome instrument in this literature.

### 1.6 Heydrich & Rustemeier-Holtwick (2022) — German Consensus Guidance

**PMID:** 36328187
**Why:** German-language consensus: conservative voice therapy first line, phoniatric/HNO check
recommended first, voice therapy covered under GKV Heilmittelverordnung (ST1). Fills the German
guideline gap (no dedicated AWMF guideline exists).

---

## Phase 2: Core PMIDs — Delivery, Measures, and Surgery Outcomes

Archive under `voice-feminization`.

### 2.1 Hawley et al. (2024) — Hybrid Clinic + App Delivery

**PMID:** 34706847
**Why:** Hybrid in-person-plus-app voice training: 3 of 4 participants reached the 170–220 Hz range.
Evidence for app-supported delivery models (relevant when coaching includes app-based feedback).

### 2.2 Park et al. — TWVQ Outcomes After Glottoplasty

**PMID:** 34565626
**Why:** TWVQ (voice-related quality of life) outcomes after Wendler glottoplasty. Reference for
discussing surgery outcomes and the role of voice work around surgical pathways.

---

## Phase 3: Foundational Perception Studies (Older, High-Citation)

Archive under `voice-feminization`. These are foundational physiology/perception papers — cite with
year, flag as foundational.

### 3.1 Hillenbrand & Clark (2009) — F0 and Formants in Sex Perception

**PMID:** 19525544
**Why:** Source-filter synthesizer study: shifting F0 + formants together changed perceived speaker
sex ~82% of the time; shifting either alone usually failed; F0 somewhat more important. Core
evidence that resonance must be trained alongside pitch.

### 3.2 Gelfer & Mikos (2005) — F0 vs. Formants in Gender Identification

**PMID:** 16301101
**Why:** With trans women speakers: gender identifications followed F0 in all cases, even when F0
contradicted formant information. Pitch primacy evidence.

### 3.3 Wolfe et al. (1990) — Intonation and F0 in Male-to-Female Transsexuals

**PMID:** 2299839
**Why:** Classic study: F0–femininity rating correlation r = .89; lowest average F0 identified as
female was 155 Hz; intonation patterns (upward contours, fewer level shifts) distinguished
female-categorized speakers. Basis for the 155–220 Hz target band and intonation work.

### 3.4 Gelfer & Schofield (2000) — Acoustic vs. Perceptual Measures

**PMID:** 10764114
**Why:** Trans women perceived as female had higher mean and upper-limit speaking F0 than those
perceived as male; upper F0 limit correlated with femininity ratings. Supports range work, not just
average-pitch work.

---

## Phase 4: PubMed Search Queries

Run each query via the `med-db` skill, archive the most relevant results under `voice-feminization`.

### 4.1 Voice feminization outcomes

Search PubMed via the `med-db` skill for `voice feminization transgender outcomes therapy`, archive
first 5 under `voice-feminization`.

### 4.2 Resonance and vocal weight

Search PubMed via the `med-db` skill for `transgender voice resonance formant vocal weight training`,
archive first 5 under `voice-feminization`.

### 4.3 Voice surgery outcomes

Search PubMed via the `med-db` skill for `glottoplasty Wendler outcomes transsexual voice`,
archive first 5 under `voice-feminization`.

---

## Phase 5: Validation

Run validation via the `med-db` skill (`med-db-integrity-check`), then verify the topic is populated
via `med-db-query --list-topics` and `med-db-query --topic voice-feminization`. Check retraction
status of all newly archived papers via `uv run check-retraction`.
