# med-researcher-agent

Reusable medical research agent configuration for Claude Code.

The repository includes a local `med-db/` workflow for archiving structured literature from PubMed, Europe PMC, and web
discovery sources (Google Scholar, DOAJ, Open Science Directory, Free Medical Journals, OpenMD, Trip Database).

## Skills

| Skill                    | Summary                                                                      |
| ------------------------ | ---------------------------------------------------------------------------- |
| `analyze-med-claims`     | Verify medical claims against literature; produce evidence reports.          |
| `evaluate-paper`         | Score scientific papers 0-100 for evidence-based quality.                    |
| `check-retraction`       | Check whether a paper is retracted (Crossref + PubMed APIs).                 |
| `create-med-skill`       | Add a new shared skill with harness wrappers.                                |
| `create-med-agent`       | Add a new shared agent with harness wrappers.                                |
| `create-workout-routine` | Build a personalized, science-backed workout routine.                        |
| `create-diet-plan`       | Build a personalized, evidence-based dietary plan.                           |
| `start-therapy-session`  | Start a live AI therapy session with the psychotherapist agent.              |
| `optimize-repo`          | Audit and clean up repo instruction files for source-of-truth hygiene.       |
| `fetch-paper`            | Download a paper's full text (PDF + source text) into the med-db archive.    |
| `define-terms`           | Complete glossary CSVs or define medical terms, backed by sources in med-db. |

### Agents

| Agent             | Summary                                                                                                                            |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `med-researcher`  | Medical and dietological research specialist with mandatory evidence-quality standards.                                            |
| `fitness-coach`   | Science-backed fitness coach for workout design, exercise selection, and programming.                                              |
| `dietologist`     | Evidence-based nutrition specialist for dietary planning and supplementation assessment.                                           |
| `psychotherapist` | AI psychotherapist grounded in Liberation/Critical Psychology. Diagnosis, case formulation, therapeutic dialogue. Bilingual DE/EN. |

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager. Reads `.python-version` (3.12)
  and installs the correct Python automatically — no separate Python install needed.
- CSV tooling for the `define-terms` skill — `mlr` (Miller) and `csvkit`
  (`csvcut`, `csvlook`, `csvstat`, `csvjson`). Install with the platform commands in
  [System tools](#system-tools).

## Setup

```bash
# Clone and enter the repo
git clone https://github.com/lena-miyamoto/med-researcher-agent.git && cd med-researcher-agent

# uv reads .python-version and installs Python 3.12 automatically,
# then creates a venv and installs dependencies (pypdf, pytest, pymarkdownlnt)
uv sync
```

Runtime dependencies: pypdf (PDF text extraction). Dev tooling: pytest, pymarkdownlnt.

## System tools

The `define-terms` skill needs two CSV tools beyond `uv`:

- `mlr` — the Miller binary; inspect and transform CSV/TSV.
- `csvkit` — provides `csvcut`, `csvlook`, `csvstat`, `csvjson` (no top-level `csvkit` binary).

Install on your platform:

| Platform             | Command                                                              |
| -------------------- | -------------------------------------------------------------------- |
| Debian/Ubuntu        | `sudo apt install -y miller csvkit`                                  |
| macOS                | `brew install miller csvkit`                                         |
| Windows (PowerShell) | `winget install -e --id JohnKerl.Miller`<br>`uv tool install csvkit` |

## Usage

All tools are invoked via `uv run <entry-point>` from the repo root.

### Local archive (`med-db/`)

All med-db usage instructions are owned by the `med-db` skill. Invoke via `Skill: "med-db"` or
consult the skill file directly. Do not duplicate med-db commands
outside the skill — the skill is the single source of truth.

### Development

```bash
uv run test          # Run test suite
uv run lint-md       # Lint Markdown files
uv run lint-md --fix # Auto-fix lint violations
```

## Environment setup

This repo is a Claude Code agent configuration. You need Claude Code, uv, and a
model provider. Python is managed automatically by uv via `.python-version`.

### 1. Claude Code

| Platform             | Command                                           |
| -------------------- | ------------------------------------------------- |
| macOS, Linux         | `curl -fsSL https://claude.ai/install.sh \| bash` |
| Windows (PowerShell) | `irm https://claude.ai/install.ps1 \| iex`        |

Native installs auto-update in the background. Verify with `claude --version`.

### 2. uv

| Platform | Command                                            |
| -------- | -------------------------------------------------- |
| Windows  | `winget install --id=astral-sh.uv -e`              |
| macOS    | `brew install uv`                                  |
| Linux    | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

### 3. Python (via uv)

The repo ships a `.python-version` file pinning Python 3.12. `uv` reads it and
installs the correct version on first use — no manual Python install needed.

```bash
uv python install   # one-time: install Python 3.12
uv sync             # create venv + install dependencies
```

### 4. Model provider (DeepSeek)

#### Create an account

Sign up at [platform.deepseek.com/sign_up](https://platform.deepseek.com/sign_up).
You can register with an email address, a Google account, or a GitHub account.

#### Get an API key

After signing in, go to [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys)
and click **"Create new API key"**. Give it a name and copy the key — it is shown
only once. Do not share the key or commit it to version control.

DeepSeek's API is pay-as-you-go. New accounts typically receive free credits to
start. Top up on the [billing page](https://platform.deepseek.com/top_up) if needed.

#### Configure Claude Code

Set the base URL and API key. Replace `<your-key>` with the key from the step above.

```bash
export DEEPSEEK_API_KEY="<your-key>"
export DEEPSEEK_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_DEFAULT_FABLE_MODEL="deepseek-v4-pro[1m]"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro[1m]"
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro[1m]"
export ANTHROPIC_MODEL="deepseek-v4-pro[1m]"
export CLAUDE_CODE_DISABLE_1M_CONTEXT=1
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export DISABLE_GROWTHBOOK=1

claude
```

## Claude Code Usage

Start a session with the agent directly:

```bash
claude --agent med-researcher
claude --agent fitness-coach
claude --agent dietologist
claude --agent psychotherapist
```
