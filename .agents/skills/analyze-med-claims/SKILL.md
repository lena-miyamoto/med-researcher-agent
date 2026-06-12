---
name: analyze-med-claims
description: 'Analyze a medical claim or collection of claims for scientific accuracy. Takes a path to a text file or inline text; verifies each claim against the literature using the med-researcher agent and produces a structured evidence report with verdicts.'
argument-hint: 'Path to a text file containing claims, or inline claim text to analyze'
user-invocable: true
---

# Analyze Med Claims

Cross-harness source of truth for analyzing medical claims against the scientific literature.

Human lives may depend on the accuracy of these analyses. Every claim must be tested against the best available evidence, not just the first study found. Confirmation bias — searching only for supporting evidence — is a patient-safety risk and is prohibited by this procedure.

**Absence of evidence is not evidence of absence.** If no adequate studies exist on a claim, the verdict is "no evidence" — never "refuted." A claim is only refuted when high-quality evidence actively contradicts it.

## When to Use

- A text file or inline text contains one or more medical, nutritional, or health claims.
- Claims need evidence-backed verification, not just definition lookup.
- The output should cite sources and give a clear verdict per claim.

## Evidence Quality Standards

These standards are mandatory. A claim verdict is only as strong as the weakest study it rests on.

### Evidence Hierarchy

Prefer the highest available level. If a higher-level source exists and contradicts lower-level evidence, the higher level governs unless there is a specific, documented reason to deviate.

1. **Systematic review with meta-analysis of RCTs** — strongest; synthesizes multiple trials with pooled effect estimates.
2. **Systematic review without meta-analysis** — strong but less precise.
3. **Individual large, well-conducted RCT** — strong for causation if adequately powered and blinded.
4. **Systematic review of observational studies** — useful when RCTs are infeasible or unethical.
5. **Prospective cohort study** — association, not causation; prone to confounding.
6. **Case-control study** — retrospective, higher risk of bias.
7. **Case series / case reports** — hypothesis-generating only; never sufficient alone to support a claim.
8. **In-vitro / animal model** — mechanistic plausibility only; cannot establish clinical effect in humans.
9. **Expert opinion / narrative review** — weakest; use only when no higher-level evidence exists, and flag the limitation.

### Recency

- Studies must be from within the last 10 years (2016 onward at analysis time) unless no newer evidence exists. Older studies used as primary support must be flagged with an explicit justification.
- For fast-moving fields (pharmacology, infectious disease, nutrition, genetics), enforce a 5-year window. Studies older than 5 years in these fields are supporting only, not primary evidence.
- A landmark older study may be cited if it was foundational and no newer evidence supersedes it. Note its age explicitly and explain why it remains relevant. A single old study can never be the sole basis for a "supported" verdict.

### Mandatory Quality Assessment

Before citing any study as evidence, evaluate it against every applicable criterion below. Reject or downgrade studies that fail. Record the assessment in the quality justification.

| Criterion | Minimum bar | Reject or downgrade if |
|---|---|---|
| Study design | Must match or exceed the claim type (causation claims require at least cohort-level evidence) | Case report or weaker used to assert causation |
| Sample size and power | Must be adequate to detect a clinically meaningful effect; power calculation reported or estimable | Underpowered; no power calculation and small sample; flag as uncertain if power is indeterminate |
| Peer review | Must be published in a peer-reviewed venue | Preprint without peer review, predatory journal, conference abstract only |
| Pre-registration | For RCTs: must be registered before data collection began (ClinicalTrials.gov, WHO ICTRP, or equivalent). For systematic reviews: must have a PROSPERO registration or published protocol | Unregistered RCT or review; registered after data collection started; published outcomes differ from registered primary outcomes without explanation (outcome switching) |
| Conflicts of interest | Must be declared. Industry-funded studies are downgraded one confidence level unless an independent replication exists, even when funding is declared | Undisclosed relevant funding; sole evidence for a claim is industry-funded with no independent replication |
| Statistical rigor | Must account for multiple comparisons if multiple endpoints are tested; primary outcome must be pre-specified | No correction for multiple comparisons; p-hacking evident (many endpoints, selective reporting); HARKing (hypothesis created after results known) |
| Stopping rule | RCTs must report the stopping rule. Trials stopped early for benefit systematically overestimate treatment effects | RCT stopped early for benefit without a pre-specified stopping rule and adjustment; downgrade confidence |
| Effect size and clinical meaning | Statistically significant results must also be clinically meaningful. Report both absolute and relative risk (see Absolute vs. Relative Risk below) | p < 0.05 but absolute risk difference is clinically trivial (e.g., <1% ARR with no meaningful patient outcome) |
| Reproducibility | Single-study findings are tentative; single-group findings are unreliable | Only one study exists and has never been independently replicated; all positive evidence comes from a single research group without external replication |
| Publication bias | For meta-analyses: must assess publication bias (funnel plot, Egger's test, trim-and-fill). For individual studies: consider whether negative results are absent from the literature | Meta-analysis without publication bias assessment; all published studies are positive and small (suggesting publication bias); downgrade confidence |
| Retraction status | Must not be retracted or have an expression of concern | Retracted; expression of concern; indexed in Retraction Watch database |

### Absolute vs. Relative Risk

Both measures must be reported for any claim involving risk, efficacy, or harm. Relative risk alone is misleading.

- **Relative risk reduction (RRR)**: the proportional reduction. "50% reduction" sounds large.
- **Absolute risk reduction (ARR)**: the actual difference in event rates. 2% → 1% = 1% ARR.
- **Number Needed to Treat (NNT)**: 1 / ARR. NNT = 100 means 100 people must be treated for one to benefit.
- **Number Needed to Harm (NNH)**: 1 / absolute risk increase for adverse events.

Require both RRR and ARR (with NNT/NNH when calculable) for every intervention or risk claim. If a cited study reports only relative measures, note this as a limitation and compute absolute measures from the reported data when possible.

### Counter-Evidence Search (Mandatory)

For every claim, a dedicated search for evidence that **contradicts or refutes** the claim is required. This is not optional. Confirmation bias is a patient-safety hazard.

- Use the same databases and search rigor as the supporting-evidence search.
- Formulate an explicit counter-hypothesis and search for it ("X does NOT reduce Y," "X is NOT associated with Y").
- If no counter-evidence is found, note this in the report — but also note that negative studies are less likely to be published (publication bias).
- When counter-evidence of comparable quality exists, the verdict must be "mixed" and both sides presented with equal detail.
- When counter-evidence is weaker than supporting evidence, explain why the weaker studies do not overturn the conclusion.

### Harms and Safety Search (Mandatory)

Every claim that asserts or implies safety, or involves an intervention (supplement, drug, diet, device, procedure), requires a dedicated adverse-event investigation. Efficacy and safety are independent questions.

- Search for adverse event data: RCT safety outcomes, observational safety studies, case reports of harm, pharmacovigilance databases.
- Check regulatory sources: FDA Adverse Event Reporting System (FAERS), EMA EudraVigilance, WHO VigiBase.
- If no safety data exists, state this explicitly: "No safety data were found. Absence of safety evidence is not evidence of safety."
- When a claim asserts something is "safe," "natural," or "harmless," treat this with the same evidentiary rigor as an efficacy claim. "Natural" is not a safety guarantee.
- Report NNH alongside NNT when the data permits.

### Extraordinary Claims

A claim that contradicts well-established physiology, biochemistry, or a large body of consistent evidence must clear a higher bar. Such claims require **extraordinary evidence**.

Triggers for the extraordinary-claims bar:
- The claimed mechanism violates known laws of physics, chemistry, or physiology (e.g., "alkaline water neutralizes blood acidity," "detox foot pads extract toxins through skin," "homeopathic remedy at 200C dilution has biological effect").
- The claimed effect size is implausibly large relative to the best available treatments for the condition.
- The claim asserts a panacea: a single intervention that cures or prevents many unrelated diseases.
- The claim asserts that an established, evidence-backed treatment is ineffective or harmful without credible contradictory evidence.

When a claim triggers this bar:
- Require at least one large, independently replicated RCT or a meta-analysis of RCTs to consider the claim "supported."
- A single study, observational data, mechanistic speculation, or expert opinion is insufficient — the claim must be classified as "inconclusive" or "refuted" regardless of how many lower-level studies exist.
- Note in the report that the extraordinary-claims bar was applied and why.

### Searching for the Best Evidence

- Always search for the highest evidence level first. If a systematic review or meta-analysis exists on the exact question, it must be found and evaluated before any individual study.
- Do not stop at the first study. Search broadly enough to find conflicting evidence and negative results.
- Required search sources:
  - **PubMed** — Clinical Queries or systematic review filter.
  - **Europe PMC** — with the `SR` (systematic review) filter.
  - **Cochrane Library** — the gold standard for systematic reviews; must be checked for any intervention claim.
  - **ClinicalTrials.gov / WHO ICTRP** — for ongoing, completed-but-unpublished, and terminated trials. Unpublished or negative trials are essential for detecting publication bias.
  - **Retraction Watch** — check that no key cited study has been retracted.
- When no meta-analysis exists, retrieve at least 2–3 of the most relevant individual studies and compare their findings. A single study is never sufficient for a "supported" verdict unless it is a large, well-replicated RCT and no contradictory evidence exists.

## Procedure

1. **Triage claims**: acquire input (file path or inline text), extract individual claims, and triage each claim:
   - Does it trigger the extraordinary-claims bar? Mark it.
   - Does it involve an intervention that requires a mandatory harms search? Mark it.
   - Does it assert causation? Mark it — requires at least cohort-level evidence.

2. **Formulate research prompts**: for each claim, write three focused research prompts for the `med-researcher` agent (`.agents/agents/med-researcher.md`):
   - **Supporting-evidence prompt**: search for the highest-level evidence that could support the claim, with explicit instructions to retrieve multiple studies, prefer meta-analyses, and report quality criteria.
   - **Counter-evidence prompt**: search for evidence that contradicts or refutes the claim, with equal rigor.
   - **Harms prompt** (if applicable): search for adverse event data, safety outcomes, and case reports of harm.

3. **Dispatch agents**: dispatch all prompts for all claims in parallel where the number of claims permits. Each agent must return:
   - The highest-level evidence found, with quality assessment against the mandatory criteria.
   - Justification for why selected studies were chosen over alternatives.
   - For meta-analyses: heterogeneity (I²), publication bias assessment, and quality of included studies.

4. **Review agent findings** before accepting:
   - Did the agent find the highest evidence level available? If it returned an RCT but a meta-analysis exists, reject and re-search.
   - Did it check Cochrane? If the claim involves an intervention and Cochrane was not searched, reject and re-search.
   - Did the agent assess every applicable quality criterion? If criteria are missing or superficial, request a deeper assessment.
   - Are there conflicting studies the agent missed? Cross-check with a targeted search if the question is high-stakes.
   - Did the counter-evidence search find studies of comparable quality to the supporting evidence? If so, the verdict is "mixed."
   - Did the harms search find safety signals? Even if efficacy evidence is strong, safety concerns must be reflected in the verdict and summary.

5. **Apply the extraordinary-claims bar**: if a claim was marked in step 1, verify that the evidence meets the higher standard. If the best evidence is below the bar, the verdict is "inconclusive" at best.

6. **Compile findings** into the report for each claim:
   - **Verdict**:
     - **supported** — consistent high-quality evidence; ≥1 meta-analysis or ≥2 concordant large RCTs; counter-evidence absent or weak; harms assessed and acceptable.
     - **weakly supported** — some evidence exists but quality is limited; single moderate-quality study; or evidence is observational when an RCT would be feasible.
     - **refuted** — consistent high-quality evidence contradicts the claim.
     - **mixed** — supporting and refuting evidence of comparable quality exist; present both sides.
     - **inconclusive — insufficient quality** — studies exist but all fail the mandatory quality criteria; better research is needed.
     - **inconclusive — no evidence** — no adequate studies exist; absence of evidence must not be mistaken for evidence of absence.
   - **Evidence quality rating**: **high** (≥1 meta-analysis or ≥2 concordant large RCTs), **moderate** (one large RCT or multiple concordant cohort studies), **low** (only small/underpowered studies, case-control data, or single observational study), **very low** (case reports, expert opinion, animal/in-vitro only).
   - **Evidence summary** (4–8 sentences):
     - Best available studies: design, population, sample size, key results.
     - For intervention claims: ARR, RRR, NNT, NNH when calculable.
     - Counter-evidence found and its quality.
     - Harms/safety findings, or explicit statement that no safety data exist.
     - Limitations of the evidence.
   - **Quality justification**: which quality criteria each cited study passed, which it failed, and why it was selected despite any limitations.
   - **Applicability note**: what population, intervention/dose, comparator, and outcome the evidence applies to. Flag when the original claim is too vague to match a specific evidence base.
   - **Sources**: identifiers (PMID, DOI) for every cited study, plus trial registry IDs (NCT number) where applicable.

7. **Synthesize the report**:
   - Header: input source, analysis date, claim count, analyst.
   - Per claim: original text, extraordinary-claims flag (if applicable), verdict, evidence quality rating, evidence summary, quality justification, applicability note, sources.
   - Footer: evidence hierarchy used, quality criteria applied, date range of cited studies, search sources consulted, limitations of the analysis, re-evaluation recommendation.
   - **Re-evaluation interval**: for fast-moving fields, recommend re-evaluation within 12 months. For all claims, note that new evidence may change the conclusion.

8. Write the report to `tmp/analyze-med-claims.<timestamp>.md` with YAML frontmatter (`title`, `source`, `analysis_date`, `claim_count`, `verdicts`, `re-evaluation_recommended_by`).

9. When the input is a file, also write a brief inline summary to `<source-stem>.claims-verdicts.md`.

## Writing Rules

- Clinical and precise; no hedging unless the evidence genuinely is mixed or weak.
- Flag study types and distinguish risk, therapy, biomarker, and mechanistic evidence — these are not interchangeable.
- Prefer PMIDs and DOIs over bare URLs. Include trial registry IDs (NCT numbers) for RCTs.
- Never edit the source claims file.
- When evidence is weak or contradictory, say so plainly. Overstating weak evidence can cause harm.
- When a claim cannot be verified to a reasonable standard, the responsible verdict is "inconclusive." Do not manufacture confidence.
- Report both absolute and relative risk measures for all risk, efficacy, and harm claims. Relative risk alone is insufficient.
- Report NNT and NNH for intervention claims when the data permits.
- Specify the population, intervention, comparator, and outcome to which the evidence applies. Flag vague claims.
- When no safety data exist, state "no safety data were found" — do not imply safety from absence of evidence.

## Validation

1. Every claim receives a verdict, evidence quality rating, and applicability note.
2. Counter-evidence was actively searched for every claim with the same rigor as supporting evidence.
3. Harms/safety search was performed for every intervention or safety-asserting claim.
4. Every supported or refuted verdict rests on evidence at or above the quality floor for that claim type.
5. Extraordinary claims were identified and held to the higher evidence bar.
6. At least one systematic review or meta-analysis was searched for per claim. Cochrane was checked for every intervention claim. If none exists, the report notes this.
7. Every cited study passes the mandatory quality assessment criteria; justification is recorded.
8. The highest available evidence level was used. A lower-level study is never cited as primary evidence when a higher-level source exists and is accessible.
9. Absolute and relative risk measures are reported for all applicable claims.
10. Industry-funded studies are flagged; if they are the sole evidence and no independent replication exists, confidence is explicitly downgraded.
11. Report uses YAML frontmatter with all required fields including re-evaluation recommendation.
12. Output files written to agreed locations.

## Output

- `tmp/analyze-med-claims.<timestamp>.md` — the full structured report with quality justifications, safety findings, and re-evaluation interval.
- When input is a file: `<source-stem>.claims-verdicts.md` — brief inline verdict summary.
