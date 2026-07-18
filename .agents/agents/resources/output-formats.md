---
description: >
  Output format templates for the psychotherapist agent — therapeutic sessions,
  diagnostic assessment, case formulation, treatment plan, psychoeducation, and
  technique selection. Read the relevant template for the current task. Session notes
  use the format in `.agents/skills/start-therapy-session/session-note-format.md`.
---

## Output Format

Adapt output structure to the task:

### For Therapeutic Sessions

Therapy sessions are fluid, not structured documents. Your output is the dialogue itself — what you say to the client.
No formal template constrains the conversation. However, these markers guide the session arc:

```text
## Session: [Date] — [Client name or pseudonym]

### Opening
[Check-in, arriving, setting focus]

### Session Work
[The therapeutic dialogue — exploration, deepening, working. This is the
body of the session. It follows the client's material, not a template.]

### Closing
[Summary of key themes, check on client's state, take-away reflection,
warm closing. No cliffhangers — leave the client held.]
```

After the session, when documenting, the skill orchestrator writes a compact entry to the client's session history
file. The format is token-efficient — every word earns its place:

```text
### Session Note: [YYYY-MM-DD]

- Presenting: [1-line reason for session]
- Themes: [key themes, brief — 3-6 bullet points max]
- Interventions: [modality:technique, e.g. "ACT:values clarification", "narrative:externalizing"]
- Key client language: [verbatim phrases that capture the client's voice — 1-3 short quotes]
- Patterns noted: [recurring themes across sessions, if any]
- Gaps flagged: [topics the agent admitted not knowing enough about and committed to researching. "none" if nothing]
- State at close: [grounded / emotional but contained / activated / etc.]
- Thread for next: [1 line — what to pick up]
```

This goes into `sessions/<client-slug>.md` — a single file per client containing all session notes, newest at top.
The file is the client's complete session history and is read by the therapist at the start of each subsequent session.
After each write, the file is compressed for token efficiency (see the skill procedure for compression rules).

The session history file is never written to during the session — only after the session has fully ended.

### For Diagnostic Assessment

```text
## Diagnostic Assessment: [Client ID or pseudonym]

### Referral Question
[Why a diagnostic assessment was sought]

### Symptom Review
[Systematic mapping of reported experiences against DSM-5-TR / ICD-11 criteria]

### Differential Diagnosis
[Conditions considered and ruled out, with reasoning]

### Diagnostic Formulation

| Diagnosis | Criteria Met | Specifiers | Confidence |
|---|---|---|---|
| ... | ... | ... | provisional / confirmed |

### Comorbidity
[Co-occurring conditions and their relationships]

### Cultural Formulation
[Cultural context of symptom expression, help-seeking, and diagnostic meaning]

### Critical Placement
[What the diagnosis captures and obscures. Social/structural contributors.]

### Treatment Implications
[What follows diagnostically for treatment direction]
```

### For Case Conceptualization

```text
## Case Formulation: [Client ID or pseudonym]

### 1. Presenting Concerns
[In client's own language where possible]

### 2. Social and Structural Context
[Material conditions, social location, relevant histories, systemic factors]

### 3. Developmental and Relational Context
[Key relationships, attachment patterns, developmental events]

### 4. Strengths, Resources, and Resistance
[Individual and community resources, coping strategies, histories of resilience]

### 5. Pattern Analysis
[Recurring themes, relational cycles, functional analysis of current patterns]

### 6. Critical Discourse Analysis
[Dominant narratives, internalized oppression, cultural expectations at play]

### 7. Formulation Summary
[Concise, de-pathologizing integration — working understanding, not diagnosis]

### 8. Treatment Implications
[Clinical direction from this formulation]

### 9. Limitations
[What is unknown, assumptions made, information gaps]
```

### For Intervention Planning

```text
## Treatment Plan

### Formulation Anchor
[Brief restatement of the relevant part of the formulation this plan addresses]

### Goals
[In client's terms; process goals as well as outcome goals]

### Recommended Approaches

| Approach | Modality | Evidence Quality | Cultural Fit | Rationale |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

### Detailed Intervention Outline
[Per approach: session structure, key techniques, adaptations for this client]

### Progress Markers
[How therapist and client will know the intervention is working]

### Risks and Limitations
[What could go wrong, evidence gaps, assumptions]
```

### For Psychoeducation

```text
## [Topic]: What You Need to Know

### In Brief
[2–3 sentence accessible summary]

### Understanding [Topic]
[Explanatory content in accessible language, with social context]

### What the Research Says
[Honest evidence summary with populations, effect sizes, limitations]

### Practical Strategies
[Actionable framework — empower, don't prescribe]

### When to Seek Additional Support
[Signs that more intensive or in-person care may be needed]

### Further Reading
[Accessible resources with language and reading-level notes]
```

### For Technique Selection

```text
## Technique Evaluation: [Technique Name] for [Clinical Presentation]

### Description
[What the technique is, proposed mechanism, theoretical basis]

### Evidence Summary

| Evidence Level | Studies | Populations | Key Findings | Limitations |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

### Critical Appraisal
[Who was studied and excluded, whose interests the research serves, allegiance
effects, cultural assumptions embedded in the technique]

### Clinical Fit Assessment
[Suitability for this specific client/context, adaptations needed]

### Recommendation
[Provisional recommendation with reasoning and caveats]
```
