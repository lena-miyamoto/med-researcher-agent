# med-researcher-agent

Reusable medical research agent configuration for both GitHub Copilot and Claude Code.

## Agent Files

- GitHub Copilot / VS Code custom agent: `.github/agents/med-researcher.agent.md`
- Claude Code subagent: `.claude/agents/med-researcher.md`
- Shared workflow text: `.agents/med-researcher.instructions.md`

## Shared Instruction Layout

The reusable medical-research workflow lives in `.agents/med-researcher.instructions.md`.

- The Copilot agent keeps a thin wrapper and references that shared file from `.github/agents/med-researcher.agent.md`.
- Claude Code loads the same shared workflow through `CLAUDE.md`, which imports both `AGENTS.md` and `.agents/med-researcher.instructions.md`.

## Claude Code Usage

- Start a session with the agent directly: `claude --agent med-researcher`
- Or invoke it inside an existing session with `@agent-med-researcher`
