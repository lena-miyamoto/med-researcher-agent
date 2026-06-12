# med-researcher-agent

Reusable medical research agent configuration for both GitHub Copilot and Claude Code.

The repository includes a local `med-db/` workflow that can archive structured literature data from PubMed and Europe PMC, plus reproducible discovery pages for broader sources such as Google Scholar, DOAJ, Open Science Directory, Free Medical Journals, OpenMD, and Trip Database.

## Setup and Tests

The project uses [uv](https://docs.astral.sh/uv/) for Python dependency management. uv is **entirely optional** — Python scripts under `.agents/scripts/` have no runtime dependencies and work with a plain `python3` (≥ 3.12) installation. uv is only needed when you want to extend those scripts or run the test suite.

### Installing uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip / pipx
pipx install uv
```

### Running tests

```bash
# Install dev dependencies and run the full suite
uv sync
uv run pytest tests/ -v

# Or with a plain venv (no uv needed for tests either — it just automates the venv)
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
pytest tests/ -v
```

### Adding or extending Python scripts

```bash
# Add runtime dependencies to pyproject.toml, then:
uv sync              # sync lockfile and venv
uv run pytest -v     # re-run tests
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

## Skill Surfaces

- `create-med-skill`: add a new shared skill with `.agents` source-of-truth plus `.github` and `.claude` wrappers.
- `create-med-agent`: add a new shared agent with `.agents` source-of-truth plus `.github` and `.claude` wrappers.
- `optimize-repo`: audit and clean up repo customization files.
- `analyze-med-claims`: verify medical claims against the scientific literature, producing structured evidence reports with verdicts.

Agent wrappers stay semantically aligned; differences are limited to harness frontmatter, tool names, and model selection. See `.agents/skills/create-med-agent/SKILL.md`.

## Claude Code Usage

- Start a session with the agent directly: `claude --agent med-researcher`
- Or invoke it inside an existing session with `@agent-med-researcher`
