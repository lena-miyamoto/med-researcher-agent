@AGENTS.md

## Architecture

Follow `AGENTS.md` for repo architecture. Claude-specific: when a skill says "dispatch the X agent," invoke via the
Agent tool with `subagent_type: "X"`. The agent name is the `name` field in the shared agent file's YAML frontmatter
(e.g., `med-researcher`, `fitness-coach`, `dietologist`, `psychotherapist`). Agents inherit `CLAUDE.md` and `AGENTS.md`
— don't restate repo conventions in agent files.

## Agents

| Agent | Shared file | Purpose |
|-------|-------------|---------|
| `med-researcher` | `.agents/agents/med-researcher.md` | Medical/dietological research: evidence hierarchy, counter-evidence, harms search, literature review |
| `fitness-coach` | `.agents/agents/fitness-coach.md` | Workout design: exercise selection, programming, RPE autoregulation, technique |
| `dietologist` | `.agents/agents/dietologist.md` | Dietary planning: macronutrients, meal composition, supplementation, ED screening |
| `psychotherapist` | `.agents/agents/psychotherapist.md` | Therapeutic dialogue, DSM/ICD diagnosis, case formulation, psychoeducation. Specialized in adult ADHD, ASD, neurodevelopmental comorbidities, gender-affirming care (trans/NB), and sex/relationship therapy. Bilingual DE/EN |

## Skills

| Skill | Agent used | Purpose |
|-------|-----------|---------|
| `analyze-med-claims` | `med-researcher` | Verify medical claims against literature; produce evidence report with verdicts |
| `create-workout-routine` | `fitness-coach` | Collect training intake, present split options, dispatch agent, write plan to `workouts/` |
| `create-diet-plan` | `dietologist` | Collect nutrition intake, screen for ED, present approach options, dispatch agent, write plan to `diet-plans/` |
| `start-therapy-session` | `psychotherapist` | Manage session history, collect intake, establish informed consent, dispatch agent, write session note |
| `create-med-agent` | — | Add new shared agent + `.github`/`.claude` wrappers |
| `create-med-skill` | — | Add new shared skill + `.github`/`.claude` wrappers |
| `optimize-repo` | — | Audit and clean up repo instruction, skill, and agent files |

## Command Contract

Follow `AGENTS.md` (Shared section). All repo Python tools must run via `uv run <entry-point>` from repo root.
