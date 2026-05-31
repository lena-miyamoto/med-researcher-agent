---
name: create-med-agent
description: 'Create a new repo agent for this workspace, with paired .github and .claude agent files that stay aligned while keeping shared workflow in AGENTS.md and shared skills. Use when adding a new agent for both Copilot and Claude.'
argument-hint: 'Provide the new agent name, role, trigger description, tool scope, and whether it should be user-invocable or subagent-only'
user-invocable: true
---

# Create Med Agent

This shared skill file is the cross-harness source of truth for creating new repo agents that work in both Copilot and Claude.

## When to Use

- User wants a custom agent available in both Copilot and Claude.
- New agent follows the repo convention: paired harness files with only justified differences.
- If the request is really a skill, stop and route to `create-med-skill`.

## Procedure

1. Clarify contract: name, role, discovery description, trigger phrases, invocation mode (user-invocable, subagent-only, or both), minimal tool set, argument hint, model constraints, handoff behavior.
2. Write the Copilot agent at `.github/agents/<name>.agent.md` with valid Copilot frontmatter and the minimal Copilot tool aliases.
3. Write the Claude agent at `.claude/agents/<name>.md` with Claude-compatible tools and model behavior. Match the Copilot agent's role and discovery intent.
4. Keep the pair aligned: purpose, routing, and output expectations match. Differences limited to harness frontmatter, tool names, model settings, brief runtime notes.
5. Push stable workflow out of the agent: repo-wide behavior into `AGENTS.md`, reusable procedure into `.agents/skills/`. Agent prompts stay short and role-focused.
6. Reuse repo tooling: `med-db/` workflow and `.agents/scripts/`. Keep evidence and safety rules in repo-level instructions unless the agent truly needs specialization.
7. Update `README.md` only if the agent should be advertised. Update `CLAUDE.md` or `.github/copilot-instructions.md` only when routing boundaries change.

## Writing Rules

- One focused role per agent.
- Smallest tool set that works.
- Descriptions concrete and keyword-rich.
- Agent bodies short; shared workflow lives in `AGENTS.md` and `.agents/skills/`.
- No fake shared `.agents/agents/` source of truth; the convention is a paired `.github`/`.claude` file kept aligned.

## Validation

1. Both files exist: `.github/agents/<name>.agent.md`, `.claude/agents/<name>.md`.
2. Frontmatter valid in each harness.
3. Descriptions, role boundaries, routing intent aligned.
4. Differences are only the harness differences that are actually needed.
5. Markdown diagnostics clean on every changed file.
6. Repo doc references match created paths.

## Output

- Files created or updated.
- Repo doc or routing changes, if any.
- Unresolved decisions on tools, invocation mode, or routing.
