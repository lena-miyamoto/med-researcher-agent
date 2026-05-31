# med-researcher-agent

Reusable medical research agent configuration for both GitHub Copilot and Claude Code.

The repository includes a local `med-db/` workflow that can archive structured literature data from PubMed and Europe PMC, plus reproducible discovery pages for broader sources such as Google Scholar, DOAJ, Open Science Directory, Free Medical Journals, OpenMD, and Trip Database.

## Instruction Layout

- `AGENTS.md`: repo-wide, tool-agnostic workflow.
- `CLAUDE.md`: Claude-specific routing.
- `.github/copilot-instructions.md`: Copilot-specific routing.
- `.github/agents/med-researcher.agent.md`, `.claude/agents/med-researcher.md`: paired med-research agents.
- `.agents/skills/<name>/SKILL.md`: shared cross-harness skill procedures.
- `.github/skills/`, `.claude/skills/`: thin harness wrappers pointing at the shared skill.
- `.agents/scripts/`: local archive tooling used by both agents.

## Skill Surfaces

- `create-med-skill`: add a new shared skill with `.agents` source-of-truth plus `.github` and `.claude` wrappers.
- `create-med-agent`: add a new paired Copilot/Claude agent.
- `optimize`: audit and clean up repo customization files.

Paired agents stay semantically aligned; differences are limited to harness frontmatter, tool names, and model selection. See `.agents/skills/create-med-agent/SKILL.md`.

## Claude Code Usage

- Start a session with the agent directly: `claude --agent med-researcher`
- Or invoke it inside an existing session with `@agent-med-researcher`
