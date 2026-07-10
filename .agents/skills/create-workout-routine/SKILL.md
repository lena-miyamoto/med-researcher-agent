---
name: create-workout-routine
description: >
             Build a scientifically sound, personalized workout routine. Collects training goal, experience, equipment,
             schedule, and injury history; presents training split options with trade-offs; then dispatches the
             fitness-coach agent to design a full program with exercises, sets, reps, RPE targets, warm-up, cool-down,
             technique cues, and progression rules. Writes the completed plan to workouts/.
argument-hint: "Optional: training goal and constraints (e.g. 'hypertrophy, home gym, 3 days/week')"
user-invocable: true
---

# Create Workout Routine

Cross-harness source of truth for building evidence-based, personalized workout routines.

This skill collects client intake, presents split options, dispatches the `fitness-coach` agent
(`.agents/agents/fitness-coach.md`), and writes the completed plan to `workouts/`.

The agent owns all exercise science methodology: programming principles, RPE-based autoregulation, volume landmarks,
exercise selection, safety rules, and output format. This skill does not duplicate those. It collects inputs, frames the
programming brief, and hands it to the agent — the agent knows *how* to build the program.

## When to Use

- User wants a personalized workout plan from evidence-based principles.
- User wants to change or refresh their current routine.
- User has a specific goal (hypertrophy, strength, endurance, general health, athletic performance) and needs a
structured program.
- User is returning to training after a break or injury.

## How This Skill Works

Orchestrates the `fitness-coach` agent (`.agents/agents/fitness-coach.md`). Skill handles intake, validation, split
selection, and file output. Agent handles all programming: exercise selection, volume, intensity, progression,
warm-up/cool-down, technique cues, and safety modifications. Skill tells the agent *what* to build; agent knows *how*.

## Procedure

### 1. Intake — Collect Client Data

Collect these six fields. Ask for missing fields; don't assume. Skip fields already in the initial prompt.

| Field | Options / Examples | Notes |
|---|---|---|
| **Training goal** | Hypertrophy, general strength, maximal strength / powerlifting, muscular endurance, athletic performance / sport-specific, fat loss (preserve muscle), general health & fitness, rehab / return-to-training | Multiple goals → help prioritize. Programming for conflicting goals dilutes both. |
| **Experience level** | Beginner (≤6 months), intermediate (6 months–3 years), advanced (3+ years) | Resistance training experience specifically. Ask about general athletic background separately. |
| **Available equipment** | Full commercial gym, home gym (rack, barbell, dumbbells, cables, machines?), bodyweight only, resistance bands, dumbbells only, kettlebells, suspension trainer | Be specific. "Home gym" spans wide range — ask what's actually there. |
| **Days per week** | 1–6 | Realistic commitment. A sustainable 3-day program beats an abandoned 6-day program. |
| **Time per session** | 30, 45, 60, 75, 90+ minutes | Including warm-up and cool-down. Most hypertrophy/strength sessions need 45–75 min. |
| **Injuries & limitations** | Free text | Current and past. Known movement restrictions. Medical conditions affecting training (hypertension, asthma, diabetes, etc.). Problem joints. |

Flag unclear fields as assumptions in the plan output; let the client correct.

### 2. Validate — Catch Contradictions

Check for combinations making the goal infeasible or suboptimal. Flag and ask:

| Contradiction | Message |
|---|---|
| Strength/powerlifting + 1 day/week | Significant strength gains unlikely on one session/week. Can design a maintenance + work-capacity full-body session, but progress needs 2–3 sessions minimum. Offer best-possible 1-day plan or ask about more days. |
| Hypertrophy + 30 min sessions | Hypertrophy needs volume per muscle group — hard in 30 min including warm-up. Can use paired sets and minimal rest, but requires high efficiency. Offer to proceed or stretch to 45 min. |
| High-volume program + bodyweight only | Bodyweight builds muscle and strength, but lower-body progressive overload is challenging without external load. Use unilateral work, tempo changes, high rep ranges. Confirm approach is acceptable. |
| Advanced lifter + bodyweight only | Likely adapted to bodyweight loading. Can program maintenance, mobility, and skill work, but significant strength/size gains without external load are unlikely. Ask about equipment access or design around constraints. |

Don't refuse suboptimal inputs — make the trade-off transparent and let the client decide.

### 3. Split Design — Offer Options

Based on days/week, experience, and goal, propose 2–3 training split options. For each:

- **Split name** (e.g., "Upper/Lower 4-day", "Full-Body 3-day", "Push/Pull/Legs 6-day")
- **Schedule** (e.g., Mon/Thu upper, Tue/Fri lower)
- **Focus & trade-off** (1–2 sentences: what this split excels at and what it sacrifices)

Reference the Split Design table in `.agents/agents/fitness-coach.md`, adapt to client inputs.

Let the user pick. No preference → recommend the option best balancing stimulus, recovery, and schedule fit.

### 4. Dispatch — Brief the Agent

Assemble a structured prompt for the `fitness-coach` agent:

```text
Build a workout routine for [client context].

Intake summary:
- Goal: [goal]
- Experience: [experience level, relevant athletic background]
- Equipment: [detailed equipment list]
- Schedule: [N days/week, M minutes/session]
- Injuries/limitations: [list, or "none reported"]
- Selected split: [split name and schedule]

Requirements:
- RPE-based autoregulation (default)
- Include warm-up and cool-down for each session
- Include exercise technique cues (2–4 bullet points per exercise)
- Include a progression rule for each main exercise
- Include deload guidance
- Output in the full Fitness Coach format: quick-reference table, warm-up/cool-down, detailed session
  breakdowns, progression & periodization, and rationale
- Address any injury/limitation modifications needed
```

Dispatch the `fitness-coach` agent with this prompt.

### 5. Review — Verify the Output

Before writing to disk, verify the agent's output includes all required components:

- [ ] Quick-reference summary table
- [ ] Warm-up protocol per training day
- [ ] Cool-down protocol per training day
- [ ] Each exercise: sets × reps, RPE target, rest period, technique cues
- [ ] Progression rule for main exercises
- [ ] Deload guidance
- [ ] Regressions/substitutions for key exercises (especially if injuries noted)
- [ ] Rationale section explaining design decisions
- [ ] No nutrition or supplement advice (agent boundary — flag if violated)

Missing → follow-up to agent requesting the specific section.

### 6. Write — Save the Plan

Create `workouts/` if missing (auto-bootstraps, like med-db pattern).

Write to `workouts/<kebab-case-name>-<YYYY-MM-DD>.md`.

File structure:

```markdown
---
title: <Plan Title>
goal: <goal>
experience: <experience>
equipment: <equipment summary>
days_per_week: <N>
session_minutes: <M>
injuries: <list or "none">
split: <split name>
rpe_method: true
created_date: <YYYY-MM-DD>
---

# <Plan Title>

<Agent output — quick-reference table, warm-up/cool-down, detailed breakdowns, progression, rationale>
```

Agent produces the body. Skill adds the YAML frontmatter.

### 7. Summary — Present & Invite Iteration

After writing the file, present a brief summary:

- Split and schedule chosen
- Key exercises and focus areas
- Progression method
- When to expect the first deload
- Feedback invitation: "This is your starting point. After the first week or two, let me know how it's feeling —
recovery, exercise comfort, schedule fit — and we can adjust."

## Writing Rules

- Take client inputs at face value. Don't second-guess or push toward a different goal.
- Validate contradictions transparently (Step 2) but accept the client's final decision.
- Never duplicate the agent's programming rules. This skill collects inputs and writes files.
- Mid-intake programming questions → answer briefly or route to fitness-coach agent directly.
- Use client's stated name if provided; otherwise "you."

## Validation

1. All 6 intake fields collected or explicitly flagged as assumptions.
2. Contradictions checked and surfaced.
3. 2–3 split options presented with trade-offs; client selected one.
4. Agent output includes all required components (Step 5 checklist).
5. Plan file written to `workouts/<kebab-case-name>-<YYYY-MM-DD>.md` with valid YAML frontmatter.
6. `workouts/` directory exists and contains the plan.
7. No nutrition, supplement, or medical diagnosis content in the output (boundary check).

## Output

- `workouts/<plan-name>-<YYYY-MM-DD>.md` — complete personalized workout plan with YAML frontmatter.
- Summary message with key decisions and invitation to provide feedback.
