# Copilot Repository Instructions

This file only covers Copilot-specific routing. Shared repo workflow belongs in `AGENTS.md`, and shared cross-harness skill procedure belongs in `.agents/skills/`.

## Instruction Boundaries

- Keep only Copilot-specific routing and discovery notes in this file.
- Keep shared repo workflow in `AGENTS.md`.
- Keep shared skill procedure in `.agents/skills/<name>/SKILL.md`.
- Keep shared agent behavior in `.agents/agents/<name>.md`.
- Keep Copilot skill wrappers in `.github/skills/<name>/SKILL.md`.
- Keep Copilot agent wrappers in `.github/agents/<name>.agent.md`.
- Keep shared skill creation workflow in `.agents/skills/create-med-skill/SKILL.md`, shared agent creation workflow in `.agents/skills/create-med-agent/SKILL.md`, and shared instruction cleanup workflow in `.agents/skills/optimize-repo/SKILL.md`.
- Keep Medical DB baseline workflow in `AGENTS.md`; keep med-researcher agent-specific behavior in `.agents/agents/med-researcher.md`.
- Avoid duplicating the same domain workflow across `AGENTS.md`, `CLAUDE.md`, and agent prompts.
