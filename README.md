# med-researcher-agent

Reusable medical research agent configuration for Claude Code.

The repository includes a local `med-db/` workflow for archiving structured literature from PubMed, Europe PMC, and web
discovery sources (Google Scholar, DOAJ, Open Science Directory, Free Medical Journals, OpenMD, Trip Database).

## Skills

| Skill                    | Summary                                                                                            |
| ------------------------ | -------------------------------------------------------------------------------------------------- |
| `analyze-med-claims`     | Verify medical claims against literature; produce evidence reports.                                |
| `apply-fixes`            | Apply approved fixes from a `review-changeset` plan (caller-invoked).                              |
| `check-retraction`       | Check whether a paper is retracted (Crossref + PubMed APIs).                                       |
| `compress-skill`         | Compress instruction `.md` files to cut token cost, keeping meaning exact.                         |
| `create-diet-plan`       | Build a personalized, evidence-based dietary plan.                                                 |
| `create-med-agent`       | Add a new shared agent with harness wrappers.                                                      |
| `create-med-skill`       | Add a new shared skill with harness wrappers.                                                      |
| `create-workout-routine` | Build a personalized, science-backed workout routine.                                              |
| `define-terms`           | Complete glossary CSVs or define medical terms, backed by sources in med-db.                       |
| `end-therapy-session`    | Write post-session therapy documentation (invoked automatically by `start-therapy-session`).       |
| `end-voice-training`     | Write post-session voice-training documentation (invoked automatically by `start-voice-training`). |
| `evaluate-paper`         | Score scientific papers 0-100 for evidence-based quality.                                          |
| `fetch-paper`            | Download a paper's full text (PDF + source text) into the med-db archive.                          |
| `med-db`                 | Access the local `med-db` archive — search, query, archive, validate, ICD-11 lookup.               |
| `optimize-repo`          | Audit and clean up repo instruction files for source-of-truth hygiene.                             |
| `review-changeset`       | Review the current changeset for logic flaws, stale references, and wrapper misalignment.          |
| `start-therapy-session`  | Start a live AI therapy session with the psychotherapist agent.                                    |
| `start-voice-training`   | Start a live AI voice training session with the voice-trainer agent.                               |

### Agents

| Agent             | Summary                                                                                                                                                                           |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `med-researcher`  | Medical and dietological research specialist with mandatory evidence-quality standards.                                                                                           |
| `fitness-coach`   | Science-backed fitness coach for workout design, exercise selection, and programming.                                                                                             |
| `dietologist`     | Evidence-based nutrition specialist for dietary planning and supplementation assessment.                                                                                          |
| `psychotherapist` | AI psychotherapist grounded in Liberation/Critical Psychology. Diagnosis, case formulation, therapeutic dialogue. Bilingual DE/EN.                                                |
| `psychiatrist`    | AI psychiatrist and psychopharmacology specialist for ADHD, autism, anxiety disorders, and depression. Diagnosis, medication management, differential diagnosis. Bilingual DE/EN. |
| `voice-trainer`   | AI voice trainer for voice feminization (trans women and transfeminine people). Evidence-based pitch, resonance, and articulation coaching. Bilingual DE/EN.                      |

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager. Reads `.python-version` (3.12)
  and installs the correct Python automatically — no separate Python install needed.
- CSV tooling for the `define-terms` skill — the repo's bundled `csv-util`
  (`uv run csv-util`); no external install needed.

## Setup

```bash
# Clone and enter the repo
git clone https://github.com/lena-miyamoto/med-researcher-agent.git && cd med-researcher-agent

# uv reads .python-version and installs Python 3.12 automatically,
# then creates a venv and installs dependencies (pypdf, pytest, ruff, rumdl, pre-commit, playwright)
uv sync
```

Runtime dependencies: pypdf (PDF text extraction). Dev tooling: pytest, ruff, rumdl, pre-commit, playwright.

## CSV tooling

CSV/TSV work (glossary CSVs, archive tables) is handled by the repo's bundled
`csv-util` (`uv run csv-util stats|check|cut|head|drop-empty|dedupe|fill`).
No external install required.

## Session protocol extraction

Therapy-session protocols are extracted from Claude Code JSONL transcripts by the bundled
`session-protocol` tool (`uv run session-protocol --slug <slug> --session-number <N> --date <YYYY-MM-DD>`),
invoked automatically by the `end-therapy-session` skill. No manual use required.

## Usage

All tools are invoked via `uv run <entry-point>` from the repo root.

### Local archive (`med-db/`)

All med-db usage instructions are owned by the `med-db` skill. Invoke via `Skill: "med-db"` or
consult the skill file directly. Do not duplicate med-db commands
outside the skill — the skill is the single source of truth.

### Development

```bash
uv run test               # Run test suite
uv run lint               # Ruff check + format check (.claude/scripts, tests)
uv run lint --fix         # Ruff autofix
uv run format             # Apply ruff format
uv run lint-md            # Lint Markdown files
uv run lint-md --fix      # Auto-fix lint violations
uv run pre-commit install # One-time per clone: install git hooks
```

`uv run fetch-archive <url> -o tmp/out.txt` opens a headed browser to scrape a
paywalled article via archive.is (interactive CAPTCHA solve); ingest the result with
`uv run med-db-download-paper --reference '<doi>' --body-file tmp/out.txt --topic <topic>`.
Host prerequisite for the browser: `uvx playwright install chromium`.

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
export ANTHROPIC_AUTH_TOKEN="<your-key>"
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-flash"
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-flash"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_FABLE_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_MODEL="deepseek-flash"

export FORCE_HYPERLINK=1
export CLAUDE_CODE_NO_FLICKER=1
export CLAUDE_CODE_RETRY_WATCHDOG=1

export CLAUDE_CODE_DISABLE_1M_CONTEXT=1
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=200000
export CLAUDE_CODE_AUTO_COMPACT_WINDOW=193000
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1

claude
```

## Claude Code Usage

Start a session with the agent directly:

```bash
claude --agent med-researcher
claude --agent fitness-coach
claude --agent dietologist
claude --agent psychotherapist
claude --agent psychiatrist
claude --agent voice-trainer
```
