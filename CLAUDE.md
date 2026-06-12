@AGENTS.md

<!-- Maintainer note: keep this file small and route specialized behavior into dedicated Claude subagents. -->

## Claude Code

- For every repo Python tool invocation, obey the AGENTS.md command invocation contract: use only `uv run ...` entry points from the repo root. Never call `.agents/scripts/*.py` through `python`, `python3`, direct paths, absolute paths, or shebang execution.
- Use the project subagent in `.claude/agents/med-researcher.md` for focused medical and dietological research.
- Use `.claude/skills/<name>/SKILL.md` when the user wants to create skills/agents, optimize the repo, or analyze medical claims. See AGENTS.md for the full skill layout.
