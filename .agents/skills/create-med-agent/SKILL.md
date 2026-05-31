---
name: create-med-agent
description: 'Create a new repo agent for this workspace, with paired .github and .claude agent files that stay aligned while keeping shared workflow in AGENTS.md and shared skills. Use when adding a new agent for both Copilot and Claude.'
argument-hint: 'Provide the new agent name, role, trigger description, tool scope, and whether it should be user-invocable or subagent-only'
user-invocable: true
---

# Create Med Agent

This shared skill file is the cross-harness source of truth for creating new repo agents that work in both Copilot and Claude.

## When to Use

- The user wants to add a new custom agent to this repository.
- The new agent must exist for both Copilot and Claude.
- The new agent should follow this repo's established agent convention: paired harness-specific files with only minimal, justified differences.

## Procedure

1. Clarify the agent contract before writing files:
   - Confirm the agent name and role.
   - Confirm the discovery description and trigger phrases.
   - Confirm whether the agent is user-invocable, subagent-only, or both.
   - Confirm the minimal tool set the agent actually needs.
   - Capture any argument hint, routing expectations, handoff behavior, or model constraints.
   - If the request is really for a skill rather than an agent, stop and route to `create-med-skill` instead of guessing.
2. Create the Copilot agent file at `.github/agents/<name>.agent.md`:
   - Use valid Copilot agent frontmatter.
   - Keep the description specific enough for agent picker and delegation discovery.
   - Use the minimal Copilot tool aliases needed for the role.
3. Create the Claude agent file at `.claude/agents/<name>.md`:
   - Keep the same role and discovery intent as the Copilot version.
   - Use the Claude-compatible tool list and model behavior appropriate for that harness.
4. Keep the paired agents aligned:
   - The purpose, routing boundaries, and output expectations should match across both files.
   - Differences should be limited to harness-specific frontmatter, tool names, model settings, and brief runtime notes.
   - Do not fork the substantive workflow unless a real harness constraint requires it.
5. Keep stable workflow out of the agents when possible:
   - Put repo-wide behavior in `AGENTS.md`.
   - Put reusable procedural workflow in shared skills under `.agents/skills/`.
   - Keep agent prompts short and role-focused instead of re-embedding long procedures.
6. Adapt the new agent to this repo's medical-research conventions when needed:
   - Prefer the existing `med-db/` archive workflow and `.agents/scripts/` helpers instead of inventing parallel archive tooling.
   - Keep evidence and safety rules in repo-level instructions unless the new agent truly needs specialized additions.
7. Update repo docs or routing only when needed:
   - Update `README.md` when the new agent should be advertised to repo users.
   - Update `CLAUDE.md` or `.github/copilot-instructions.md` only when the new agent changes routing boundaries.
   - Avoid duplicating the same routing rule in multiple files unless the harness actually needs it.

## Writing Rules

- Prefer one focused role per agent.
- Prefer the smallest tool set that lets the agent do its job.
- Keep descriptions keyword-rich and concrete.
- Keep agent bodies short; push shared workflow into `AGENTS.md` and shared skills.
- Do not invent a fake shared `.agents/agents/` source of truth; for agents in this repo, the convention is a paired `.github` and `.claude` file kept intentionally aligned.

## Validation

1. Confirm both harness files exist:
   - `.github/agents/<name>.agent.md`
   - `.claude/agents/<name>.md`
2. Confirm both files have valid frontmatter for their harness.
3. Confirm the descriptions, role boundaries, and routing intent are aligned.
4. Confirm differences between the two files are only harness-specific differences that are actually needed.
5. Run markdown diagnostics on every changed instruction file.
6. If repo docs were updated, confirm their references match the created agent paths.

## Output

- State which agent files were created or updated.
- State whether any repo docs or routing files were updated.
- Call out any unresolved choice about tools, invocation mode, or routing.
