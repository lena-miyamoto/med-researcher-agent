# med-researcher-agent

Reusable medical research agent configuration for both GitHub Copilot and Claude Code.

The repository includes a local `med-db/` workflow for archiving structured literature from PubMed, Europe PMC, and web
discovery sources (Google Scholar, DOAJ, Open Science Directory, Free Medical Journals, OpenMD, Trip Database).

## Skill Surfaces

These are the main user-facing entry points in this repository.

| Skill                | What it does                                                                                                   |
| -------------------- | -------------------------------------------------------------------------------------------------------------- |
| `analyze-med-claims` | Verify medical claims against the scientific literature and produce structured evidence reports with verdicts. |
| `create-med-skill`   | Add a new shared skill with `.agents` as the source of truth plus `.github` and `.claude` wrappers.            |
| `create-med-agent`   | Add a new shared agent with `.agents` as the source of truth plus `.github` and `.claude` wrappers.            |
| `optimize-repo`      | Audit and clean up repo customization files for consistency and source-of-truth hygiene.                       |

All skills are defined under `.agents/skills/` and surfaced through thin `.github/skills/` and `.claude/skills/`
wrappers.

## Setup and Tests

The project uses [uv](https://docs.astral.sh/uv/) for Python dependency management and repo-standard command execution.
`uv` is required for running skills and repo tooling in this repository.

### Installing uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (WinGet)
winget install --id=astral-sh.uv -e

# Cross-platform via pip / pipx
pipx install uv
```

After installing `uv`, sync the local environment before running tests or repo tools:

```bash
uv sync
```

### Running tests

```bash
# Run the full suite via the project script
uv run test

# Or pass through specific pytest arguments
uv run test tests/test_med_db_validate.py -q
```

### Running med-db tools with uv

```bash
uv run med-db --help
uv run med-db --query 'endometriosis' --archive-first 5 --validate
uv run med-db-validate --med-db med-db
uv run med-db-lookup --pmid 12345678
uv run med-db-query --list-topics
```

These are the canonical repo commands. Use them instead of direct `python3 .agents/scripts/...` execution.

### Adding or extending Python scripts

```bash
# Add runtime dependencies to pyproject.toml, then:
uv sync              # sync lockfile and venv
uv run test          # re-run the full suite
```

## Instruction Layout

- `AGENTS.md`: repo-wide, tool-agnostic workflow.
- `CLAUDE.md`: Claude-specific routing.
- `.github/copilot-instructions.md`: Copilot-specific routing.
- `.agents/agents/med-researcher.md`: shared med-researcher role and output rules.
- `.github/agents/med-researcher.agent.md`, `.claude/agents/med-researcher.md`: thin med-researcher harness wrappers.
- `.agents/skills/<name>/SKILL.md`: shared cross-harness skill procedures.
- `.github/skills/`, `.claude/skills/`: thin harness wrappers pointing at the shared skill.
- `.agents/scripts/`: local archive tooling used by both agents.

Agent wrappers stay aligned; differences are limited to harness frontmatter, tool names, and model selection.

## Claude Code Usage

Start a session with the agent directly:

```bash
claude --agent med-researcher
```
