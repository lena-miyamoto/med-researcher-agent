---
name: evaluate-paper
description: >
             Evaluate a scientific paper or article for evidence-based research quality. Scores it 0-100 weighted by
             study type, rates retracted papers 0, and lists strengths and weaknesses with reasons for the grade.
argument-hint: 'Path to a paper file, DOI/URL, or inline paper text'
user-invocable: true
---

# Evaluate Paper

Grades one scientific paper or article for evidence-based quality. Scale 0-100: 0 = worthless, 100 = aspirational
landmark — virtually no paper reaches it. Every grade must be justified: strengths and weaknesses.

## When to Use

- A paper, preprint, or scientific article needs a quality grade before being cited, trusted, or acted on.
- Input is a file path, DOI/URL, or inline text.
- Grading the paper itself — not verifying its claims against the literature.

## Procedure

### 1. Acquire the paper

- File path → read it.
- DOI/URL → retrieve the paper with the `fetch-paper` skill. Abstract-only
  allowed but provisional — see Writing Rules.

### 2. Retraction gate — mandatory, before any reading

Check retraction status via the `check-retraction` skill before any
reading.

- **Retracted → score 0. Stop. No further analysis.** Report is the retraction record: status, retraction date
  and reason if findable, source (PubMed / Crossref). Verify with at least two sources.
- Outstanding Expression of Concern → continue; cap score at 20; state it in the report.
- Journal legitimacy (separate from retraction): check indexing (MEDLINE, Scopus) and DOAJ (https://doaj.org)
  before scoring. Predatory or unverifiable journal → cap at 15. OpenAlex
  (`https://api.openalex.org/works/doi:<DOI>`) reports OA status, venue, and identifiers without an API key or
  email; use it when DOAJ returns 403.

### 3. Classify the study design

Design sets base weight and score ceiling. Read the methods enough to classify — 1-2 sentences.

| Design | Base | Ceiling |
|---|---|---|
| SR/MA of RCTs | 30 | 95 |
| RCT | 28 | 95 |
| Prospective cohort, confounder-adjusted | 20 | 75 |
| Non-randomized intervention (ITS, before-after) | 15 | 70 |
| Case-control | 15 | 65 |
| Cross-sectional | 10 | 55 |
| Case series | 5 | 30 |
| Expert opinion / narrative review | 3 | 20 |

- **Study type dominates sample size.** A meta-analysis of three small trials outranks a single n>1000 trial; an
  unadjusted n=2000 cohort never beats a well-run RCT.
- **Reclassification rule** (GRADE: execution can override design label). Paper fails the defining feature of its
  design → reclassify one tier down before scoring:
  - RCT without proper randomization or allocation concealment → non-randomized intervention study.
  - SR/MA without systematic search or registered protocol → narrative review.
  - Cohort without defined exposure and follow-up → cross-sectional or case series.

### 4. Quick red-flag scan — the token-cheap pass

Scan abstract, methods, results tables, COI/funding statement. Most bad papers fail here; go deep only where a
flag needs confirmation. Deduct per flag:

| Red flag | − | Spot it |
|---|---|---|
| No control group (intervention claim) | 15 | pre-post only + causal wording |
| No/improper randomization or concealment (RCT) | 15 | methods; baseline imbalance |
| Selective outcome reporting | 15 | registry (ClinicalTrials.gov / PROSPERO / OSF) vs paper: swapped or dropped primary |
| p-hacking signals | 12 | p-values clustering at 0.03-0.049; many flexible analyses |
| No blinding where feasible, subjective outcome | 10 | unblinded, patient-reported outcome (objective outcome: −3) |
| Spin | 10 | abstract claims benefit; primary outcome non-significant |
| Post-hoc subgroup sold as primary claim | 10 | "post hoc" in limitations; no interaction test |
| Registered trial, no results posted | 10 | registry record vs FDAAA |
| Not peer-reviewed / unindexed | 10 | no MEDLINE/Scopus indexing |
| No a priori sample-size or power justification | 8 | methods lack a sample-size sentence |
| Multiple comparisons uncorrected | 8 | count endpoints vs stated corrections |
| HARKing | 8 | no prereg; hypothesis matches results too neatly |
| Surrogate endpoint sold as clinical outcome | 8 | biomarker/lab change, no mortality/morbidity/QoL |
| Baseline imbalance unadjusted | 8 | Table 1 vs adjustment list |
| Missing data mishandled | 8 | >20% attrition, complete-case only, no sensitivity analysis |
| No ITT in RCT | 8 | per-protocol-only analysis |
| Undisclosed / industry COI with favorable results | 8 | COI statement, funding line, registry sponsor |
| Effect sizes / CIs missing (p only) | 6 | results tables |
| Relative risk without absolute risk or NNT | 6 | no baseline risk given |
| Unreported attrition / no flow diagram | 5 | no CONSORT flow |

### 5. Quality checklist per design — deep pass only where a flag appeared

Apply the most discriminating criteria of the matching tool. Shared criteria (preregistration, COI, stopping rules,
statistical rigor) follow the med-researcher agent's Mandatory Quality Assessment
(`.claude/agents/med-researcher.md`) — do not restate them here.

- RCT → Cochrane RoB 2 domains: randomization and concealment; deviations (blinding, ITT); missing outcome data;
  outcome measurement; selection of reported result.
- Non-randomized intervention → ROBINS-I: confounding adjustment is make-or-break.
- Observational exposure → ROBINS-E (2024).
- SR/MA → AMSTAR 2 critical domains: protocol registered; comprehensive search; excluded-studies list; RoB of
  included studies; MA methods; RoB in interpretation; publication-bias assessment (funnel/Egger); COI. Plus PRISMA
  2020: search strategy per database; registration; certainty assessment.
- Reporting-proxy: CONSORT (RCTs), STROBE (observational). Checklist adherence correlates inversely with spin.

Deduct for statistical misuses found here:

| Misuse | − |
|---|---|
| Post-hoc power as justification (it is a 1:1 function of p — worthless) | 5 |
| Post-hoc outlier exclusion ("non-compliers" removed after seeing data) | 5 |
| Unit-of-analysis errors (paired/repeated measures as independent) | 5 |
| Median-vs-mean games; mean±SD on skewed data | 4 |
| CI barely excluding null sold as strong evidence | 4 |

### 6. Score

score = design ceiling − deductions + bonuses, floor 0, never above ceiling. Reclassified designs use the lower
ceiling.

Bonuses (max +5 total): Registered Report +3; preregistered with registry-outcome match +2; open data and code +2;
independent replication exists +2; estimand-consistent methods (ICH E9(R1)) +1.

Caps: retracted = 0 (stop). Expression of Concern ≤ 20. Predatory/unindexed journal ≤ 15.

| Band | Meaning |
|---|---|
| 90-100 | landmark — 100 needs ceiling 95 plus the full +5 bonus; in practice near-unreachable |
| 70-89 | strong — minor issues; credible for practice |
| 50-69 | moderate — real limitations; effects likely overestimated |
| 30-49 | weak — major flaws; hypothesis-generating only |
| <30 | severely flawed — ignore or cite as a negative example |

### 7. Report

Every result must state:

- Score (integer 0-100) and band.
- Retraction status — always: "retracted — score 0" (with record) or "not retracted (checked: sources)".
- Study design, ceiling, and any reclassification.
- Strengths: what the paper does right (checklist passes, bonuses).
- Weaknesses: every deduction, naming the flag and citing the paper's section — no unexplained point math.
- Verdict: one paragraph on what this paper is good for at this score.

Write full report to `tmp/evaluate-paper.<timestamp>.md` with YAML frontmatter (`title`, `score`, `band`,
`study_design`, `retraction_status`, `evaluation_date`). When input is a file, also write
`<source-stem>.evaluation.md` next to it.

## Writing Rules

- Never edit the source paper file.
- Abstract-only → items that cannot be verified are noted, not deducted; score marked provisional.
- The score is an ordinal judgment, not a measurement — don't defend a 1-point difference.
- Weak evidence of quality: when in doubt between two bands, take the lower one.

## Validation

1. Retraction checked via the `check-retraction` skill before any scoring; retracted papers scored 0 and stopped.
2. Study design classified; ceiling stated; reclassification applied where the defining feature failed.
3. Every deduction maps to a named flag.
4. Strengths and weaknesses both present.
5. Score respects design ceiling and caps.
6. Report files written to agreed locations with required frontmatter.

## Output

- `tmp/evaluate-paper.<timestamp>.md` — full report.
- `<source-stem>.evaluation.md` — sibling summary when input is a file.
