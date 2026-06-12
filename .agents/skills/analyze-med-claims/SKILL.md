---
name: analyze-med-claims
description: 'Analyze a medical claim or collection of claims for scientific accuracy. Takes a path to a text file or inline text; verifies each claim against the literature using the med-researcher agent and produces a structured evidence report with verdicts.'
argument-hint: 'Path to a text file containing claims, or inline claim text to analyze'
user-invocable: true
---

# Analyze Med Claims

Cross-harness source of truth for analyzing medical claims against the scientific literature.

Human lives may depend on the accuracy of these analyses. Every claim must be tested against the best available evidence, not just the first study found.

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

- Prefer studies published within the last 10 years (2016 onward at analysis time).
- For fast-moving fields (pharmacology, infectious disease, nutrition), prefer the last 5 years.
- A landmark older study may be cited if it was foundational and no newer evidence supersedes it, but explicitly note its age and why it is still relevant.

### Mandatory Quality Assessment

Before citing any study as evidence, evaluate it against these criteria. Reject or downgrade studies that fail.

| Criterion | Minimum bar | Reject if |
|---|---|---|
| Study design | Must match or exceed the claim type (e.g., causation claims require at least cohort-level evidence) | Case report or weaker used to assert causation |
| Sample size | Must be adequate to detect a clinically meaningful effect | Underpowered (check if a power calculation is reported; if absent, flag as uncertain) |
| Peer review | Must be published in a peer-reviewed venue | Preprint without peer review, predatory journal, conference abstract only |
| Conflicts of interest | Must be declared | Undisclosed industry funding clearly relevant to the result; funding by a party with a direct financial stake in the outcome, without independent replication |
| Reproducibility | Single-study findings are tentative | Only one small study exists and it has never been replicated; flag as preliminary |
| Effect size | Statistically significant results must also be clinically meaningful | p < 0.05 but effect size is trivial (e.g., <1% absolute risk difference with no clinical consequence) |
| Publication bias | For meta-analyses, check whether publication bias was assessed (funnel plot, Egger's test) | Meta-analysis that did not assess publication bias; downgrade confidence |
| Retraction status | Must not be retracted or have an expression of concern | Retracted, or indexed in Retraction Watch database |

### Searching for the Best Evidence

- Always search for the highest evidence level first. If a systematic review or meta-analysis exists on the exact question, it must be found and evaluated before any individual study is considered.
- Do not stop at the first study that appears to answer the question. Search broadly enough to find conflicting evidence.
- Use PubMed Clinical Queries or systematic review filters. Search Europe PMC with the `SR` (systematic review) filter.
- When no meta-analysis exists, retrieve at least 2–3 of the most relevant individual studies and compare their findings. A single study is never sufficient to declare a claim "supported" unless it is a large, well-replicated RCT and no contradictory evidence exists.

## Procedure

1. Acquire input: if the argument is a readable file path, load it; otherwise treat the full argument as the claims text.
2. Extract individual claims from the text. A claim is a factual assertion about health, disease, treatment, nutrition, or biology that can be tested against evidence. Keep enough surrounding context so each claim is self-contained.
3. For each claim, formulate a focused research question and dispatch a `med-researcher` agent (`.agents/agents/med-researcher.md`) with explicit instructions:
   - Search for the highest-level evidence first (systematic reviews, meta-analyses).
   - Retrieve multiple studies, not just the first result.
   - For each candidate study, report the quality assessment criteria from the table above.
   - Return the best-quality studies with justification for why they were selected over alternatives.
4. Run claims in parallel where the number of claims permits.
5. Review each agent's findings before accepting them:
   - Did the agent find the highest evidence level available? If it returned an RCT but a meta-analysis exists, reject the finding and re-search.
   - Did the agent assess study quality? If quality criteria are missing, request them.
   - Are there conflicting studies the agent didn't find? Cross-check with a second targeted search if the question is high-stakes.
6. Collect each agent's findings into the report:
   - **Verdict**: **supported** (consistent high-quality evidence), **weakly supported** (some evidence but quality is limited), **refuted** (consistent high-quality evidence contradicts), **mixed** (conflicting evidence of comparable quality), or **inconclusive** (insufficient or consistently low-quality evidence).
   - **Evidence quality rating**: **high** (≥1 meta-analysis or ≥2 concordant large RCTs), **moderate** (one large RCT or multiple concordant cohort studies), **low** (only small/underpowered studies, case-control data, or single observational study), **very low** (case reports, expert opinion, animal/in-vitro only).
   - **Evidence summary**: 3–6 sentences describing the best available studies, their design, quality assessment, key results, and limitations. When the evidence is mixed, present both sides with equal rigor.
   - **Quality justification**: explicit statement of why the cited studies meet the quality bar — sample size, study design, replication status, and any noted limitations.
   - **Sources**: identifiers (PMID, DOI) or URLs for every cited study.
7. Synthesize a single report:
   - Header: input source (file path or "inline text"), analysis date, claim count.
   - Per claim: original text, verdict, evidence quality rating, evidence summary, quality justification, sources.
   - Footer: evidence hierarchy and quality criteria used, date range of cited studies, limitations of the analysis.
8. Write the report to `tmp/analyze-med-claims.<timestamp>.md` with YAML frontmatter (`title`, `source`, `analysis_date`, `claim_count`, `verdicts`).
9. When the input is a file, also write a brief inline summary of verdicts to the same directory as `<source-stem>.claims-verdicts.md`.

## Writing Rules

- Keep the output clinical and precise; no hedging unless the evidence genuinely is mixed or weak.
- Flag study types (RCT, systematic review, meta-analysis, cohort, case report, in-vitro, animal model) and distinguish risk, therapy, biomarker, and mechanistic evidence.
- Prefer PMIDs and DOIs over bare URLs.
- Never edit the source claims file.
- When evidence is weak or contradictory, say so plainly. Overstating weak evidence can cause harm.
- If a claim cannot be verified to a reasonable standard, "inconclusive" is a valid and responsible verdict. Do not manufacture confidence.

## Validation

1. Every claim in the input gets a verdict and an evidence quality rating.
2. Every supported or refuted verdict rests on evidence at or above the quality floor for that claim type.
3. At least one systematic review or meta-analysis was searched for per claim. If none exists, the report notes this.
4. Every cited study passes the mandatory quality assessment criteria, with justification recorded.
5. The highest available evidence level was used. A lower-level study is never cited when a higher-level source exists and is accessible.
6. Report uses YAML frontmatter with all required fields.
7. Output files written to agreed locations.

## Output

- `tmp/analyze-med-claims.<timestamp>.md` — the full structured report with quality justifications.
- When input is a file: `<source-stem>.claims-verdicts.md` — brief inline verdict summary.
