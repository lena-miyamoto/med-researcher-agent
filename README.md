# med-researcher-agent

Reusable medical research agent configuration for both GitHub Copilot and Claude Code.

The repository includes a local `med-db/` workflow that can archive structured literature data from PubMed and Europe PMC, plus reproducible discovery pages for broader sources such as Google Scholar, DOAJ, Open Science Directory, Free Medical Journals, OpenMD, and Trip Database.

## Agent Files

- GitHub Copilot repository instructions: `.github/copilot-instructions.md`
- GitHub Copilot / VS Code custom agent: `.github/agents/med-researcher.agent.md`
- Claude Code subagent: `.claude/agents/med-researcher.md`
- Shared repo context: `AGENTS.md` and `CLAUDE.md`

## Instruction Layout

- `AGENTS.md` is repo-wide and tool-agnostic.
- `.github/copilot-instructions.md` contains GitHub Copilot repository onboarding.
- `.github/agents/med-researcher.agent.md` contains the Copilot-specific med-research agent prompt.
- `.claude/agents/med-researcher.md` contains the Claude Code med-research subagent prompt.
- `.agents/skills/` contains shared cross-harness skill procedures.
- `.github/skills/` and `.claude/skills/` contain thin harness-specific skill wrappers.
- `.agents/scripts/` contains the local archive tooling used by both agent variants.

Specialized workflow text lives in the documented agent surfaces for each runtime.

## Skill Surfaces

This repo also exposes shared repo-maintenance skills:

- `create-med-skill`: creates a new shared skill with `.agents` source-of-truth plus `.github` and `.claude` wrappers
- `create-med-agent`: creates a new paired Copilot and Claude agent that stays aligned with repo conventions
- `optimize`: audits and cleans up repo customization files to remove redundancy and restore a clear source of truth

## Agent Differences

The Copilot and Claude med-research agents should stay semantically aligned, but they are not meant to be byte-identical.

- Shared behavior should live in repo-level instruction surfaces: `AGENTS.md`, `.github/copilot-instructions.md`, and Claude's root `CLAUDE.md` routing.
- The Copilot agent should only add what is specific to the GitHub Copilot custom-agent surface: Copilot frontmatter, tool names, model choice, and a short reminder to use the repo instructions.
- The Claude agent should only add what is specific to Claude Code subagents: Claude tool access, inherited `CLAUDE.md` context, and any Claude-only execution behavior.
- If a workflow rule applies equally to both runtimes, prefer moving it upward into a repo-level instruction surface instead of repeating it in both agent prompts.

## Claude Code Usage

- Start a session with the agent directly: `claude --agent med-researcher`
- Or invoke it inside an existing session with `@agent-med-researcher`
