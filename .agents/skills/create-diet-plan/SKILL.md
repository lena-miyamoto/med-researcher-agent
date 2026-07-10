---
name: create-diet-plan
description: >
             Build an evidence-based, personalized dietary plan. Collects nutrition goal, dietary pattern, allergies,
             health conditions, cooking capacity, meal schedule, budget, and current supplements; screens for disordered
             eating red flags; presents dietary approach options with trade-offs; then dispatches the dietologist agent
             to design a full plan with meal structure, macronutrient guidance, food-group recommendations,
             supplementation notes, and education. Writes the completed plan to diet-plans/.
argument-hint: "Optional: nutrition goal and dietary preferences (e.g. 'plant-based, support endurance training, 4 meals/day')"
user-invocable: true
---

# Create Diet Plan

Cross-harness source of truth for building evidence-based, personalized dietary plans.

This skill collects client intake, screens for disordered eating, presents dietary approach options, dispatches the
`dietologist` agent (`.agents/agents/dietologist.md`), and writes the completed plan to `diet-plans/`.

The agent owns all nutrition science methodology: evidence quality assessment, macronutrient targeting, dietary pattern
selection, food-group guidance, supplementation policy, safety boundaries, and output format. This skill does not
duplicate those. It collects inputs, frames the dietary brief, and hands it to the agent — the agent knows *how* to
build the plan.

## When to Use

- User wants a personalized dietary plan from evidence-based nutrition principles.
- User wants to adjust their eating pattern for a specific goal (body composition, athletic performance, health
condition management, general health).
- User needs practical meal structure and food-group guidance, not just abstract principles.
- User wants evidence-based assessment of current supplements or is considering new ones.

## How This Skill Works

Orchestrates the `dietologist` agent (`.agents/agents/dietologist.md`). Skill handles intake, validation, ED screening,
dietary approach selection, and file output. Agent handles all nutrition planning: macronutrient targets, meal
composition, food-group guidance, supplementation assessment, safety modifications, and education. Skill tells the agent
*what* to build; agent knows *how*.

For deep literature review questions (e.g., "does supplement X improve outcome Y?"), the dietologist agent routes to
`med-researcher` internally — this skill does not manage that handoff.

## Procedure

### 1. Intake — Collect Client Data

Collect these fields. Ask for missing fields; don't assume. Skip fields already in the initial prompt.

| Field | Options / Examples | Notes |
|---|---|---|
| **Nutrition goal** | Weight management (loss/gain/maintenance preserving muscle), athletic performance/fueling, general health & longevity, managing a health condition, improving relationship with food, supporting training | Multiple goals → help prioritize. Simultaneous weight loss + muscle gain requires careful protein and energy-balance targeting — flag the trade-off. |
| **Dietary pattern** | Omnivorous, vegetarian (lacto-ovo/lacto/ovo), vegan, pescatarian, halal, kosher, low-carb/ketogenic, gluten-free, low-FODMAP, Mediterranean-style, DASH-style, no specific pattern / flexible | No pattern → default Mediterranean-style as strongest evidence base. |
| **Allergies & intolerances** | Free text | Distinguish diagnosed IgE-mediated allergies (strict exclusion, anaphylaxis risk) from intolerances (lactose, FODMAP sensitivity — may be dose-dependent). |
| **Health conditions** | Free text | Diagnosed conditions affecting dietary needs: diabetes, hypertension, CKD, IBD/IBS, liver disease, celiac, PCOS, endometriosis, thyroid disorders, gout, GERD, etc. Also: history of eating disorders. |
| **Cooking capacity** | Time available, skill level, kitchen access, cooking for self vs. family | "I can cook" spans boiling pasta to multi-component meals. Ask: meals from scratch per week? Time per meal? |
| **Meals per day** | 2–6 | Realistic eating occasions including snacks. Consider work/school schedule. |
| **Food budget** | Low / moderate / flexible | Relative. Affects protein source recs (lentils/eggs/canned fish vs. fresh salmon), organic vs. conventional, specialty products. |
| **Current supplements** | Free text | Everything: protein powder, creatine, vitamins, minerals, herbals, pre-workouts, other dietary supplements. Include doses if known. |

Flag unclear fields as assumptions in the plan output; let the client correct.

### 2. Validate — Catch Contradictions

Check for combinations making the goal infeasible or suboptimal. Flag and ask:

| Contradiction | Message |
|---|---|
| Vegan + no supplementation | B12 supplementation is non-negotiable for vegans. Vitamin D, omega-3 (DHA/EPA), iodine, iron, zinc, and calcium may need attention. Design with food-first sources; flag where supplementation is indicated. |
| Weight loss + history of eating disorder | Recommend a registered dietitian specializing in eating disorders. Will provide general evidence-based principles, but won't create a prescriptive calorie-restricted plan. Offer principles-only guidance instead. |
| Very low calorie + high activity | Intake below estimated BMR risks muscle loss, metabolic adaptation, nutrient deficiencies, impaired performance. Won't design a plan below [X] kcal/day. Offer a moderate deficit approach. |
| Ketogenic + high-intensity training | Ketogenic diets can impair high-intensity performance, especially during adaptation (first several weeks). Performance may recover for steady-state work but remain compromised for glycolytic efforts. Confirm compatibility or offer moderate-carb alternative. |
| CKD + high protein | Protein intake must be individualized by CKD stage and lab values. General principles only; specific targets require nephrologist or renal dietitian coordination. |

Don't refuse suboptimal inputs — make the trade-off transparent. Exceptions: ED red flags (Step 3), <BMR calorie
targets, and conditions requiring clinical nutrition therapy.

### 3. ED Screening — Red-Flag Check

Before creating any meal plan with calorie or macronutrient targets, screen for red-flag behaviors. This is a screening
step, not a diagnostic assessment.

Ask indirectly: "Before I build this plan — can you tell me a bit about your current relationship with food? Any
patterns or behaviors you're concerned about?"

**Red flags triggering redirection (do not create a calorie/macro-prescriptive plan):**

- Compensatory behaviors (purging, laxative misuse, excessive exercise to "earn" or "burn off" food)
- Self-imposed intake consistently below 1200 kcal/day without medical supervision
- Binge-eating episodes with loss of control
- Obsessive weighing, measuring, or tracking causing distress
- Self-induced vomiting or diuretic/diet-pill misuse
- Significant preoccupation with food, weight, or body shape interfering with daily life

**If red flags are present:**

- Do not create a prescriptive meal plan with calorie/macro targets.
- State: "Some of what you're describing suggests your relationship with food may benefit from professional support. A
meal plan with specific calorie or macro targets could make things worse. I recommend working with a registered
dietitian who specializes in eating disorders. I'm happy to provide general evidence-based nutrition education without
numbers, if that would be helpful."
- Offer principles-only guidance (food groups, meal regularity, nutrient density) if the client wants it. No calorie
counts, macro targets, or portion prescriptions.

### 4. Dietary Approach — Offer Options

Based on goal, dietary pattern, cooking capacity, and preferences, propose 2–3 approaches. For each:

- **Approach name** (e.g., "Flexible Macro-Based", "Structured Meal Template", "Pattern-Based Guidelines")
- **What it looks like in practice** (1–2 sentences)
- **Best for** (who this suits)
- **Trade-off** (demands vs. benefits)

| Approach | Description | Best for | Trade-off |
|---|---|---|---|
| Flexible Macro-Based | Approximate macro targets, client chooses foods within targets. Higher autonomy. | Experienced with food tracking, comfortable estimating portions, wants flexibility. | Requires tracking literacy. Less structure — easier to drift off-target. |
| Structured Meal Template | Specific meal suggestions with portion guidance. "Eat this, roughly this much, at roughly this time." | New to nutrition planning, wants clear direction, limited tracking time. | Less flexibility. Can feel repetitive. Needs template updates as needs change. |
| Pattern-Based Guidelines | "Eat more X, eat less Y" with practical food-group guidance and plate method. No numbers. | ED history (numbers can trigger), wants freedom, cooking skills allow self-direction. | Least precision. Progress harder to track. Best for health maintenance, less suited for body-comp goals. |

ED history or red flags → default to Pattern-Based Guidelines. Do not offer calorie/macro-prescriptive approaches.

Let the user pick. No preference → recommend based on goal precision needs and tracking willingness.

### 5. Dispatch — Brief the Agent

Assemble a structured prompt for the `dietologist` agent:

```text
Build a dietary plan for [client context].

Intake summary:
- Goal: [goal]
- Dietary pattern: [pattern]
- Allergies/intolerances: [list, or "none reported"]
- Health conditions: [list, or "none reported"]
- Cooking capacity: [time, skill, kitchen, solo vs. family]
- Meals per day: [N meals, approximate timing]
- Budget: [low / moderate / flexible]
- Current supplements: [list with doses, or "none"]
- Selected approach: [approach name]
- ED screening: [passed / flagged — if flagged, no calorie or macro targets]

Requirements:
- Food-first philosophy; supplements only when indicated with evidence quality noted
- Default to Mediterranean-style pattern unless client specified otherwise
- Include quick-reference summary table, daily macronutrient overview (ranges, not exact grams),
  meal-by-meal breakdown with practical preparation notes, food group guidance,
  supplementation notes (if applicable), and principles & education section
- Address any health condition modifications needed; flag where clinical dietitian coordination is recommended
- If ED screening was flagged: pattern-based guidance only, no numbers
- Output in the full Dietologist format per the agent's Output Format specification
```

Dispatch the `dietologist` agent with this prompt.

### 6. Review — Verify the Output

Before writing to disk, verify the agent's output includes all required components:

- [ ] Quick-reference summary table
- [ ] Daily macronutrient overview (ranges, unless ED-flagged)
- [ ] Meal-by-meal breakdown with practical preparation notes
- [ ] Food group guidance ("eat more / eat less")
- [ ] Supplementation notes with evidence quality ratings (if applicable)
- [ ] Principles & education section
- [ ] Clinical condition modifications addressed (if applicable)
- [ ] No aesthetic framing, no "good food / bad food" dichotomies
- [ ] No aggressive calorie deficits (<BMR)
- [ ] No supplement recommendations for proprietary blends or extraordinary claims without evidence
- [ ] If ED-flagged: no calorie counts, no macro targets, no prescriptive portions

Missing → follow-up to agent requesting the specific section.

### 7. Write — Save the Plan

Create `diet-plans/` if missing.

Write to `diet-plans/<kebab-case-name>-<YYYY-MM-DD>.md`.

File structure:

```markdown
---
title: <Plan Title>
goal: <goal>
dietary_pattern: <pattern>
allergies: <list or "none">
health_conditions: <list or "none">
meals_per_day: <N>
budget: <low / moderate / flexible>
approach: <approach name>
ed_screened: true
created_date: <YYYY-MM-DD>
---

# <Plan Title>

<Agent output — summary table, macronutrient overview, meal breakdowns, food group guidance,
 supplementation notes, principles & education>
```

Agent produces the body. Skill adds the YAML frontmatter.

### 8. Summary — Present & Invite Iteration

After writing the file, present a brief summary:

- Dietary approach chosen
- Key macronutrient and food-group priorities
- Supplementation recommendations (if any) with evidence confidence level
- Monitoring guidance: what to track and when to adjust
- Feedback invitation: "This is your starting point. Dietary plans typically need adjustment after 2–4 weeks based on
how you feel, perform, and progress. Let me know what's working and what isn't, and we can refine."

## Writing Rules

- Take client inputs at face value. Don't second-guess their dietary pattern or push toward a different one.
- Validate contradictions and clinical risks transparently (Steps 2, 3). Accept client's decision except ED red flags
— those are a hard stop on prescriptive plans.
- Never duplicate the agent's nutrition methodology. This skill collects inputs and writes files.
- Mid-intake nutrition questions → answer briefly or route to dietologist agent directly.
- Use client's stated name if provided; otherwise "you."

## Validation

1. All 8 intake fields collected or explicitly flagged as assumptions.
2. Contradictions checked and surfaced.
3. ED screening performed; red flags handled with redirection, not accommodation.
4. 2–3 dietary approach options presented with trade-offs; client selected one.
5. Agent output includes all required components (Step 6 checklist).
6. Plan file written to `diet-plans/<kebab-case-name>-<YYYY-MM-DD>.md` with valid YAML frontmatter.
7. `diet-plans/` directory exists and contains the plan.
8. No aesthetic body framing, no food moralizing, no aggressive restriction in the output.
9. Clinical conditions flagged with provider coordination notes where applicable.

## Output

- `diet-plans/<plan-name>-<YYYY-MM-DD>.md` — complete personalized dietary plan with YAML frontmatter.
- Summary message with key decisions, monitoring guidance, and invitation to provide feedback.
