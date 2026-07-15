---
name: create-med-agent
description: >
             Create a new repo agent for this workspace, with shared role instructions in .agents/agents and thin
             .github/.claude wrappers. Use when adding a new agent for both Copilot and Claude.
argument-hint: >
               Provide the new agent name, role, trigger description, tool scope, and whether it should be
               user-invocable or subagent-only
user-invocable: true
---

# Create Med Agent

## When to Use

- User wants a custom agent available in both Copilot and Claude.
- Follow the architecture in `CLAUDE.md`: shared behavior in `.agents/agents/`, thin wrappers in `.github/agents/` and
  `.claude/agents/`.
- If the request is a skill, not an agent, stop and route to `create-med-skill`.

## Procedure

1. Clarify contract: name, role, discovery description, trigger phrases, invocation mode (user-invocable, subagent-only,
   or both), minimal tool set, argument hint, model constraints, handoff behavior.
2. Use the same ownership pattern as skills: stable instructions in `.agents/`, harness files are wrappers. See
   `CLAUDE.md` and `AGENTS.md` for the full architecture.
3. Write the shared agent instructions at `.agents/agents/<name>.md`: mirror discovery frontmatter where useful, then
put the role, stable behavior, and output expectations here. Don't restate the multi-agent architecture — `CLAUDE.md`
covers that. Don't add "this file is the shared source of truth" boilerplate — it's implicit in where the file lives.
4. Write the Copilot wrapper at `.github/agents/<name>.agent.md` with valid Copilot frontmatter and minimal Copilot tool
aliases. Point the body at the shared agent file.
5. Write the Claude wrapper at `.claude/agents/<name>.md` with Claude-compatible tools and model behavior. Point the
body at the shared agent file.
6. Keep wrappers aligned. Differences are limited to harness frontmatter, tool names, model settings, invocation fields,
and brief runtime notes.
7. Push broader workflow out of the agent: repo-wide behavior into `AGENTS.md`, reusable procedure into
`.agents/skills/`. Agent wrappers stay short.
8. Reuse repo tooling: `med-db/` workflow and `.agents/scripts/`. Keep evidence and safety rules in repo-level
instructions unless the shared agent file needs specialization.
9. Update `README.md` only if the agent should be advertised. Update `CLAUDE.md` or `.github/copilot-instructions.md`
only when routing boundaries change.

## Writing Rules

- One focused role per agent.
- Smallest tool set that works.
- Descriptions concrete and keyword-rich.
- Shared agent behavior lives in `.agents/agents/<name>.md`. Don't add "this file is the shared source of truth"
  boilerplate — it's implicit in where the file lives.
- Harness agent bodies are wrappers; do not duplicate stable role or output rules there.

## Validation

1. All three files exist: `.agents/agents/<name>.md`, `.github/agents/<name>.agent.md`, `.claude/agents/<name>.md`.
2. Frontmatter valid in each file.
3. Shared file holds stable role boundaries and output expectations.
4. Wrappers point at the shared file and do not duplicate its procedure.
5. Differences are only the harness differences that are actually needed.
6. Run `uv run lint-md` on every changed file; diagnostics must be clean.
7. Repo doc references match created paths.

## Output

- Files created or updated.
- Repo doc or routing changes, if any.
- Unresolved decisions on tools, invocation mode, or routing.
