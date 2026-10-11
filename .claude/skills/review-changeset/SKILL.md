---
name: review-changeset
description: >
             Review the current changeset for logical inconsistencies, obvious flaws, stale
             cross-file references, and wrapper/source misalignment. Auto-detects scope: staged changes if
             present, otherwise unstaged. Produces a structured findings report; returns a fix plan to the
             caller and hands off to `apply-fixes` when issues warrant it.
disable-model-invocation: false
user-invocable: true
model: haiku
effort: high
context: fork
background: true
---

# Review Changeset

Diff-driven review of instruction files in the current changeset. Analyzes for inconsistencies, stale
references, and contradictions that cause wrong behavior. Produces a findings report with severity
labels. When findings warrant fixes, returns a fix plan to the caller as text and instructs the
caller to invoke the `apply-fixes` skill.

## When to Use

- After editing agent, skill, or rule `.md` files, before committing.
- When refactoring a behavioral rule spanning multiple files (e.g., session ending, dispatch protocol).
- When unsure whether a change in one file breaks references or assumptions in another.
- After renames, moves, or file splits that may leave stale paths.

## Procedure

### 1. Determine Diff Scope

Auto-detect the changeset — no argument needed:

```bash
git diff --cached --name-only
```

If the command returns files → review **staged changes only**.
If the command returns nothing → fall back to **unstaged changes**:

```bash
git diff --name-only
```

Only one scope reviewed — never merge staged and unstaged. Review what the user is about to commit
(staged) or what they're still working on (unstaged).

### 2. Filter to Instruction Files

From the file list, keep only `.md` files under these directories:

- `.claude/agents/`
- `.claude/agents/references/`
- `.claude/references/`
- `.claude/skills/`
- `.github/agents/`
- `.github/skills/`

Exclude `README.md`, `CHANGELOG.md`, `DEVELOPER.md`, `CONTRIBUTING.md`, and any file outside the
directories above. If no instruction files remain, report "No instruction files in changeset" and stop.

### 3. Read Each Changed File

Read every file from step 2 in full (current on-disk version). For each file, extract:

- **Explicit file references** — any path in backticks matching `.claude/*` or `.github/*`, plus references
  introduced by `Read`, `See`, `Follow`, `per`, `defined in`, `owned by`, `source of truth`.
- **Cross-file behavioral rules** — rules restated or referenced across multiple files. Identify by
  matching shared topics: session ending, crisis redirection, dispatch protocol, command invocation
  contract, source-of-truth ownership, evidence hierarchy, compression rules.
- **Frontmatter fields** — note presence/absence of `name`, `description`, `user-invocable`,
  `argument-hint`, `disable-model-invocation`, `model`, `effort`, `context`, `background` (for skills);
  `name`, `description`, `tools`, `model` (for agents).

### 4. Stale-Reference Check

For every file reference extracted in step 3, resolve relative to the repository root and verify the
target exists on disk. Use `Bash: test -f <path>` for each. Flag every missing path as:

- **Error** — target referenced in a procedure step or mandatory file load. Missing it breaks execution.
- **Warning** — target mentioned in prose or as a non-critical reference.

Also flag references using a path convention that no longer matches the repo structure (e.g.,
referencing `.claude/agents/references/foo.md` when the file moved to
`.claude/skills/foo/references/foo.md`).

### 5. Cross-File Consistency Check

For each changed file, identify its **related files** — other instruction files it references, plus other
files that reference it. Also check known related pairs:

- Agent file + its rule files (e.g., `psychotherapist.md` ↔ `clinical-work-guides.md`)
- Skill file + its rule files (e.g., `start-therapy-session/SKILL.md` ↔ `references/handoff-prompt.md`)
- `.github/` wrapper ↔ `.claude/` source of truth
- `CLAUDE.md` ↔ any changed agent or skill it routes to

For each related pair where at least one file is in the diff, read both files and check:

- **Behavioral contradiction** — does file A's new instruction contradict file B's existing rule?
  Example: A says "two-step protocol, wait between steps" while B still says "single atomic response."
- **Orphaned reference** — does the changed file reference a section heading, step number, or list item
  that no longer exists in the target file?
- **Divergent restatement** — is the same rule stated differently across files in ways that could produce
  different behavior? (Same rule restated in multiple files is expected in this repo — the check is
  whether the restatements *agree*, not whether duplication exists.)

### 6. Wrapper Alignment

For each changed file under `.github/`, verify the pointer line matches this repo's wrapper convention.

Skill wrappers (`.github/skills/<name>/SKILL.md`) open their body with:

```text
Wrapper. Source of truth: `.claude/skills/<name>/SKILL.md`.
```

Agent wrappers (`.github/agents/<name>.agent.md`) open their body with a one-line role summary, then:

```text
Wrapper for `.claude/agents/<name>.md`. Harness differences: <what differs>.
```

Check that:

- The referenced `.claude/` file exists.
- The frontmatter `name` matches, and `description` is **byte-identical** between wrapper and source. Any
  description drift is a finding.
- Wrapper frontmatter carries only Copilot-valid fields, per
  `.claude/references/frontmatter-fields.md`. A Claude-only field in a wrapper is a finding — **Error** for
  skill wrappers (`disable-model-invocation`, `user-invocable`, `model`, `effort`, `context`,
  `background`, `argument-hint`, and the rest are ignored/rejected by Copilot), **Warning** for agent
  wrappers.
- Skill execution fields (`model`, `effort`, `context`, `background`, `disable-model-invocation`) live only
  in the `.claude/` source; their absence from the wrapper is expected, not a mismatch.
- Agent wrapper `tools` must be the exact Copilot-alias mapping of the source `tools` (`Read`→`read`,
  `Grep`/`Glob`→`search`, `Bash`→`execute`, `WebFetch`/`WebSearch`→`web`, `Agent`→`agent`,
  `Edit`/`Write`→`edit`). A tool present in the source but missing from the wrapper, or present in the
  wrapper but absent from the source, is a finding.

### 7. Model & Effort Appropriateness

For every changed `.claude/` skill or agent file carrying a `model` and/or `effort` field, read
`.claude/references/model-capabilities.md` and resolve the value there before judging it. Resolve
aliases against the service the session is pointed at — never the Claude model of the same alias
name. Under this repo's default DeepSeek wiring `haiku`/`sonnet` → `deepseek-flash` and `opus`/`fable`
→ `deepseek-v4-pro`; on an Anthropic session the aliases map to the Claude models of those names. Flag:

- **Error** — `model` is not one of `haiku`, `sonnet`, `opus`, `fable`, `best`, `opusplan`,
  `default`, `inherit`, or a full `claude-*` / `deepseek-*` model ID; or `effort` is not one of
  `low`, `medium`, `high`, `xhigh`, `max`.
- **Warning** — the `(model, effort)` pair mismatches the work the file's body and description say it
  does, per the Selection Guide. Examples: a deep-synthesis skill pinned to `haiku` + `low`; a
  mechanical extraction skill pinned to `sonnet` + `max`; an agent that should follow the caller but
  hard-codes a model instead of `inherit`.
- **Info** — `effort` is `medium` or `xhigh`: on the DeepSeek wiring both collapse to `high` and add
  no capability over `high`. Flag only when the file's prose implies they do.
- **Info** — `model` is `opus`: on the DeepSeek wiring it resolves to the same model as `fable`.

Cite `.claude/references/model-capabilities.md` in every finding from this step. This step never edits
frontmatter — corrections go into the fix plan like any other finding.

### 8. Internal Consistency

Within each changed file, flag:

- **Contradictory rules** — opposing instructions within the same file. Examples: "stop immediately, no
  extra question" vs. "invite final thoughts before closing"; "never batch questions" vs. "ask all at
  once."
- **Mismatched counts** — prose says "three components" but the list has 2 or 4 items; heading says
  "five elements" but only 4 are enumerated.
- **Broken placeholders** — `<placeholder>` syntax used but never defined in the file or its documented
  inputs.
- **Lost emphasis** — a rule previously marked `CRITICAL`, `IMPORTANT`, `YOU MUST`, or `NEVER`
  lost its emphasis marker in the new version. Check the diff: if a line containing these keywords
  was removed, verify the rule is still enforced elsewhere or flag it.
- **Missing steps** — numbered procedure steps where a number is skipped (1, 2, 4 — missing 3).

### 9. Assemble Findings Report

Produce a report organized by file. For each finding, include:

- **Severity**: `Error` (will cause wrong or undefined behavior), `Warning` (potential issue, needs
  judgment), `Info` (noted, no action required).
- **Location**: file path and section/line reference.
- **Description**: what the issue is, why it matters.
- **Related files**: if the issue spans multiple files, list all involved.

If no findings: report "No issues found in `N` instruction files." Include a summary line listing which
files were reviewed. Stop here — no handoff needed.

### 10. Hand Off the Fix Plan (When Findings Warrant It)

If the report contains any **Error** or **Warning** findings, append the fix plan to your final message
as text — do **not** write a file. The plan must:

- **Summarize each finding** — one bullet per finding with severity, file, and a one-line description.
- **Propose a fix** for each Error and Warning. Info findings are listed but fixes are optional.
- **Be concise** — a fix checklist, not a restatement of the review report.

End the message with this handoff line:

> Caller: present this plan to the user, wait for explicit approval, then invoke the `apply-fixes`
> skill with this plan as `args` to apply the fixes.

Do not apply any fix here. `apply-fixes` owns applying approved fixes and is not forked — the caller
runs it inline after approval.

If there are no Errors or Warnings, state that and stop — no plan, no handoff.

## Writing Rules

- Read-only always. This skill writes no files — including no plan file. The review summary and fix
  plan are returned as text to the caller.
- Never edit, move, or delete instruction files during review. Never run formatters, linters, or fix-up
  scripts during review.
- Never apply fixes. This skill stops at the handoff — `apply-fixes` owns applying approved fixes.
- If the diff includes `.py` files alongside instruction files, note their presence but do not review
  them — this skill reviews instruction files only.
- Treat `.gitignore` boundaries as out of scope. Skip any file excluded by `.gitignore`.
- Every flagged issue must cite the specific contradiction or missing reference. No vague findings.
- Cross-file consistency checks are the highest-value part of this skill — prioritize them over
  exhaustive internal checks when time is limited.
- Model/effort findings must cite `.claude/references/model-capabilities.md` and name the model the
  alias resolves to under the session's wiring — never call a value wrong based on the Claude model
  of the same alias name.

## Validation

1. Diff scope auto-detected correctly — staged if present, otherwise unstaged.
2. Every changed instruction file read in full.
3. Every extracted file reference verified against disk.
4. Cross-file checks completed for all related-file pairs where at least one side changed.
5. Wrapper alignment verified for every changed `.github/` file.
6. Internal consistency checked for every changed file.
7. Report includes severity, location, and description for every finding. "No issues found" is an
   acceptable result when the changeset is clean.
8. Every changed file carrying `model` or `effort` was checked against
   `.claude/references/model-capabilities.md`, and each such finding names the model the alias
   resolves to under the session's wiring.
9. If Errors or Warnings found: a fix plan was returned as text with concrete fixes, and the final
   message instructs the caller to invoke `apply-fixes` after user approval. No plan file was written.

## Output

- Findings report with severity labels (Error / Warning / Info), organized by file.
- Summary line: number of files reviewed, number of findings by severity.
- If Errors or Warnings present: a fix plan returned as text in the final message, plus an explicit
  handoff line instructing the caller to present it to the user and, on approval, invoke the
  `apply-fixes` skill with the plan.
- If no issues: confirmation that the changeset is clean; no handoff.
