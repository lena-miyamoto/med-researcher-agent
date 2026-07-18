# med-researcher-agent

Reusable medical research agent configuration for both GitHub Copilot and Claude Code.

The repository includes a local `med-db/` workflow for archiving structured literature from PubMed, Europe PMC, and web
discovery sources (Google Scholar, DOAJ, Open Science Directory, Free Medical Journals, OpenMD, Trip Database).

## Skills

| Skill                    | Summary                                                              |
| ------------------------ | -------------------------------------------------------------------- |
| `analyze-med-claims`     | Verify medical claims against literature; produce evidence reports.  |
| `create-med-skill`       | Add a new shared skill with harness wrappers.                        |
| `create-med-agent`       | Add a new shared agent with harness wrappers.                        |
| `create-workout-routine` | Build a personalized, science-backed workout routine.                |
| `create-diet-plan`       | Build a personalized, evidence-based dietary plan.                   |
| `start-therapy-session`  | Start a live AI therapy session with the psychotherapist agent.      |
| `optimize-repo`          | Audit and clean up repo instruction files for source-of-truth hygiene. |

### Agents

| Agent             | Summary                                                                                      |
| ----------------- | -------------------------------------------------------------------------------------------- |
| `med-researcher`  | Medical and dietological research specialist with mandatory evidence-quality standards.      |
| `fitness-coach`   | Science-backed fitness coach for workout design, exercise selection, and programming.        |
| `dietologist`     | Evidence-based nutrition specialist for dietary planning and supplementation assessment.     |
| `psychotherapist` | AI psychotherapist grounded in Liberation/Critical Psychology. Diagnosis, case formulation, therapeutic dialogue. Bilingual DE/EN. |

## Setup

[Install uv](https://docs.astral.sh/uv/getting-started/installation/), then sync:

```bash
uv sync
uv run test
```

All commands use `uv run <entry-point>` from the repo root. The full command reference (archival, lookup, query,
diagnostic classification) is in `CLAUDE.md` (Medical DB section).

## Instruction Layout

| File                                                               | Purpose                                                    |
| ------------------------------------------------------------------ | ---------------------------------------------------------- |
| `CLAUDE.md`                                                        | Repo-wide workflow, command contract, Medical DB reference |
| `AGENTS.md`                                                        | Copilot-specific instructions, thin pointer to `CLAUDE.md`  |
| `.github/copilot-instructions.md`                                  | Copilot-specific routing                                   |
| `.agents/agents/<name>.md`                                         | Shared agent behavior (source of truth)                    |
| `.github/agents/<name>.agent.md`, `.claude/agents/<name>.md`       | Thin harness wrappers                                      |
| `.agents/skills/<name>/SKILL.md`                                   | Shared skill procedure (source of truth)                   |
| `.github/skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md` | Thin harness wrappers                                      |
| `.agents/scripts/`                                                 | Local tooling used by both harnesses                       |

Wrappers stay aligned; differences are limited to harness frontmatter, tool names, and model selection.

## Claude Code Usage

Start a session with the agent directly:

```bash
claude --agent med-researcher
claude --agent fitness-coach
claude --agent dietologist
claude --agent psychotherapist
```
