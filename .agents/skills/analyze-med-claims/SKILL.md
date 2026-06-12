---
name: analyze-med-claims
description: 'Analyze a medical claim or collection of claims for scientific accuracy. Takes a path to a text file or inline text; verifies each claim against the literature using the med-researcher agent and produces a structured evidence report with verdicts.'
argument-hint: 'Path to a text file containing claims, or inline claim text to analyze'
user-invocable: true
---

# Analyze Med Claims

Cross-harness source of truth for analyzing medical claims against the scientific literature.

Human lives may depend on the accuracy of these analyses. Every claim must be tested against the best available evidence, not just the first study found. Confirmation bias — searching only for supporting evidence — is a patient-safety risk and is prohibited by this procedure.

## When to Use

- A text file or inline text contains one or more medical, nutritional, or health claims.
- Claims need evidence-backed verification, not just definition lookup.
- The output should cite sources and give a clear verdict per claim.

## How This Skill Works

This skill orchestrates the `med-researcher` agent (`.agents/agents/med-researcher.md`). The agent owns all evidence-quality methodology: the evidence hierarchy, mandatory quality assessment criteria, recency rules, counter-evidence and harms search requirements, absolute vs. relative risk reporting, search protocol, and research output format. This skill does not duplicate those instructions. It tells the agent *what* to research; the agent knows *how* to do it rigorously.

## Extraordinary Claims

A claim that contradicts well-established physiology, biochemistry, or a large body of consistent evidence must clear a higher evidence bar. Such claims must be flagged for the agent so it applies its extraordinary-claims enforcement.

Triggers — a claim is extraordinary if any of these apply:
- The claimed mechanism violates known laws of physics, chemistry, or physiology (e.g., "alkaline water neutralizes blood acidity," "detox foot pads extract toxins through skin," "homeopathic remedy at 200C dilution has biological effect").
- The claimed effect size is implausibly large relative to the best available treatments for the condition.
- The claim asserts a panacea: a single intervention that cures or prevents many unrelated diseases.
- The claim asserts that an established, evidence-backed treatment is ineffective or harmful without credible contradictory evidence.

When a claim triggers this bar, mark it with `extraordinary: true` in the research prompt. The agent enforces the higher standard.

## Procedure

1. **Acquire and extract claims**: load input (file path or inline text). Extract individual claims — a claim is a factual assertion about health, disease, treatment, nutrition, or biology that can be tested against evidence. Keep enough surrounding context so each claim is self-contained.

2. **Triage each claim**:
   - Extraordinary? Mark it for the agent.
   - Involves an intervention? The agent will automatically perform a harms search.
   - Asserts causation? The agent will require at least cohort-level evidence.

3. **Dispatch research agents**: for each claim, dispatch a `med-researcher` agent (`.agents/agents/med-researcher.md`) with a focused prompt. The prompt specifies *what* to research and any flags (e.g., `extraordinary: true`). The agent applies all evidence-quality standards from its own instructions. Dispatch three prompts per claim where applicable:
   - **Supporting evidence**: "Research whether evidence supports the claim: [claim text]."
   - **Counter-evidence**: "Research whether evidence contradicts the claim: [claim text]."
   - **Harms** (for intervention or safety-asserting claims): "Research adverse events and safety data for: [intervention]."
   Run claims in parallel where the number permits.

4. **Review agent findings**: each agent returns structured findings per the agent's Research Output Format (evidence quality rating, supporting evidence with quality assessment, risk measures, counter-evidence, harms, quality justification, applicability note, sources). Before accepting:
   - Did the agent find the highest evidence level available? If the quality rating seems too low for the claim type, re-dispatch with a refined prompt.
   - Are there obvious gaps or conflicting studies not addressed? Cross-check with a targeted re-search if the question is high-stakes.
   - Did the harms search find safety signals that change the overall assessment?

5. **Compile the report** — assign a verdict for each claim by weighing the supporting, counter, and harms evidence streams:

   | Verdict | Criteria |
   |---|---|
   | **supported** | Consistent high-quality evidence (quality rating: high); counter-evidence absent or weak; harms assessed and acceptable |
   | **weakly supported** | Some evidence exists but quality is limited (quality rating: moderate or low); single moderate-quality study; or evidence is observational when an RCT would be feasible |
   | **refuted** | Consistent high-quality evidence contradicts the claim |
   | **mixed** | Supporting and refuting evidence of comparable quality exist; present both sides |
   | **inconclusive — insufficient quality** | Studies exist but all fail the mandatory quality criteria; better research is needed |
   | **inconclusive — no evidence** | No adequate studies exist; absence of evidence must not be mistaken for evidence of absence |

   Each verdict entry in the report must include:
   - Original claim text
   - Extraordinary-claims flag (if applicable)
   - Verdict
   - Evidence quality rating (from the agent)
   - Evidence summary: 4–8 sentences synthesizing the agent's supporting evidence, counter-evidence, and harms findings
   - Quality justification (from the agent)
   - Applicability note (from the agent)
   - Sources: PMIDs, DOIs, NCT numbers (from the agent)

6. **Synthesize the final report**:
   - **Header**: input source, analysis date, claim count.
   - **Body**: per-claim entries as above.
   - **Footer**: summary of the evidence-quality standards applied (reference the agent's Evidence Quality Standards), date range of cited studies, re-evaluation recommendation.
   - **Re-evaluation interval**: for fast-moving fields, recommend re-evaluation within 12 months. For all claims, note that new evidence may change the conclusion.

7. Write the report to `tmp/analyze-med-claims.<timestamp>.md` with YAML frontmatter (`title`, `source`, `analysis_date`, `claim_count`, `verdicts`, `re-evaluation_recommended_by`).

8. When the input is a file, also write a brief inline verdict summary to `<source-stem>.claims-verdicts.md`.

## Writing Rules

- Never edit the source claims file.
- When generating reusable markdown from a source file, always write sibling output files in the same directory. Use `<source-stem>.leitfaden.md` for the clinical/medical guide and `<source-stem>.patienten.md` for the patient-facing guide. Example: `tmp/diet-plan.md` → `tmp/diet-plan.leitfaden.md` and `tmp/diet-plan.patienten.md`.
- If an output file already exists, update only that output file; do not fold changes back into the original source brief.
- When evidence is weak or contradictory, say so plainly. Overstating weak evidence can cause harm.
- When a claim cannot be verified to a reasonable standard, the responsible verdict is "inconclusive." Do not manufacture confidence.
- The agent handles evidence-level writing rules (ARR/RRR, NNT/NNH, study type flags, PICO specificity, PMIDs/DOIs). Do not override or soften the agent's findings.

## Validation

1. Every claim receives a verdict and references the agent's evidence quality rating.
2. Every claim was researched with three prompts (supporting, counter, harms where applicable).
3. Extraordinary claims were identified and flagged for the agent.
4. Every verdict rests on the agent's quality-assessed evidence — no study is cited without passing the agent's mandatory criteria.
5. Report uses YAML frontmatter with all required fields including re-evaluation recommendation.
6. Output files written to agreed locations.

## Output

**Claims analysis mode** (this skill's primary workflow):
- `tmp/analyze-med-claims.<timestamp>.md` — full structured report with quality justifications, safety findings, and re-evaluation interval.
- When input is a file: `<source-stem>.claims-verdicts.md` — brief inline verdict summary.

**Source file analysis mode** (when the agent is given a general medical source file to analyze):
- `<source-stem>.leitfaden.md` — clinical/medical guide.
- `<source-stem>.patienten.md` — patient-facing guide.
