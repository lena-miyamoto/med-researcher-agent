---
name: review-changeset
description: >
             Review the current instruction-file changeset for logical inconsistencies, obvious flaws, stale
             cross-file references, and wrapper/source misalignment. Auto-detects scope: staged changes if
             present, otherwise unstaged. Produces a structured findings report; creates a fix plan file when
             issues warrant it.
user-invocable: true
---

# Review Changeset

Diff-driven review of instruction files in the current changeset. Analyzes changes for inconsistencies,
stale references, and contradictions that would cause wrong behavior. Produces a findings report with
severity labels. When findings warrant fixes, creates a plan file and offers it for execution.

## When to Use

- After editing agent, skill, or rule `.md` files and before committing.
- When refactoring a behavioral rule that spans multiple files (e.g., session ending, dispatch protocol).
- When unsure whether a change in one file breaks references or assumptions in another.
- After renames, moves, or file splits that may have left stale paths behind.

**User-invocable.** Run manually after making instruction-file changes — not auto-triggered.

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

Only one scope is reviewed — never merge staged and unstaged into a combined review. The goal is to
review what the user is about to commit (staged) or what they're still working on (unstaged).

### 2. Filter to Instruction Files

From the file list, keep only `.md` files under these directories:

- `.claude/agents/`
- `.claude/agents/rules/`
- `.claude/skills/`
- `.github/agents/`
- `.github/skills/`

Exclude `README.md`, `CHANGELOG.md`, `DEVELOPER.md`, `CONTRIBUTING.md`, and any file outside the
directories above. If no instruction files remain, report "No instruction files in changeset" and stop.

### 3. Read Each Changed File

Read every file from step 2 in full (current on-disk version). For each file, extract:

- **Explicit file references** — any path in backticks matching `.claude/*` or `.github/*`, plus references
  introduced by `Read`, `See`, `Follow`, `per`, `defined in`, `owned by`, `source of truth`.
- **Cross-file behavioral rules** — rules that are restated or referenced across multiple files. Identify
  these by matching shared topics: session ending, crisis redirection, dispatch protocol, command
  invocation contract, source-of-truth ownership, evidence hierarchy, compression rules.
- **Frontmatter fields** — note presence/absence of `name`, `description`, `user-invocable`,
  `argument-hint` (for skills); `name`, `description`, `tools`, `model` (for agents).

### 4. Stale-Reference Check

For every file reference extracted in step 3, resolve it relative to the repository root and verify the
target exists on disk. Use `Bash: test -f <path>` for each. Flag every missing path as:

- **Error** — target is referenced in a procedure step or mandatory file load. Missing it breaks
  execution.
- **Warning** — target is mentioned in prose or as a non-critical reference.

Also flag references that use a path convention that no longer matches the repo structure (e.g.,
referencing `.claude/agents/rules/foo.md` when the file was moved to
`.claude/skills/foo/rules/foo.md`).

### 5. Cross-File Consistency Check

For each changed file, identify its **related files** — other instruction files it references, plus other
files that reference it. Also check known related pairs:

- Agent file + its rule files (e.g., `psychotherapist.md` ↔ `clinical-work-guides.md`)
- Skill file + its rule files (e.g., `start-therapy-session/SKILL.md` ↔ `rules/handoff-prompt.md`)
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

For each changed file under `.github/`, verify the pointer line matches the repo's wrapper convention:

```text
Wrapper. Source of truth: `.claude/<agents|skills>/<name>.<md|SKILL.md>`.
```

Check that:

- The referenced `.claude/` file exists.
- The frontmatter `name` and `description` match between wrapper and source (they must be identical).

### 7. Internal Consistency

Within each changed file, flag:

- **Contradictory rules** — opposing instructions within the same file. Examples: "stop immediately, no
  extra question" vs. "invite final thoughts before closing"; "never batch questions" vs. "ask all at
  once."
- **Mismatched counts** — prose says "three components" but the list has 2 or 4 items; heading says
  "five elements" but only 4 are enumerated.
- **Broken placeholders** — `<placeholder>` syntax used but never defined in the file or its documented
  inputs.
- **Lost emphasis** — a rule that was previously marked `CRITICAL`, `IMPORTANT`, `YOU MUST`, or `NEVER`
  lost its emphasis marker in the new version. Check the diff: if a line was removed that contained
  these keywords, verify the rule is still enforced elsewhere or flag it.
- **Missing steps** — numbered procedure steps where a number is skipped (1, 2, 4 — missing 3).

### 8. Assemble Findings Report

Produce a report organized by file. For each finding, include:

- **Severity**: `Error` (will cause wrong or undefined behavior), `Warning` (potential issue, needs
  judgment), `Info` (noted, no action required).
- **Location**: file path and section/line reference.
- **Description**: what the issue is, why it matters.
- **Related files**: if the issue spans multiple files, list all involved.

If no findings: report "No issues found in `N` instruction files." Include a summary line listing which
files were reviewed. Stop here — no plan file needed.

### 9. Create Fix Plan (When Findings Warrant It)

If the report contains any **Error** or **Warning** findings, create a plan file at
`.claude/plans/fix-review-findings-<slug>.md` that proposes concrete fixes for each actionable finding.

The plan file must:

- **Summarize each finding** — one bullet per finding with severity, file, and a one-line description.
- **Propose a fix** for each Error and Warning. Info findings are listed but fixes are optional.
- **Be concise** — the plan is a fix checklist, not a restatement of the review report.
- **End with a question** asking the user whether to execute the plan.

After writing the plan file, present it to the user:

> Review found `N` issue(s) that warrant fixes. Fix plan written to `.claude/plans/fix-review-findings-<slug>.md`.
> Execute the plan?

**Stop and wait for the user to respond.** Do not apply fixes without explicit approval — the plan is an
offer, not an auto-execute. If the user approves, follow the plan and apply each fix.

Info-only findings (no Errors or Warnings) → mention them in the report but skip the plan file. The user
can act on them or not.

## Writing Rules

- Read-only during review (steps 1–8). Plan file creation (step 9) is the only write allowed.
- Never edit, move, or delete instruction files during review. Never run formatters, linters, or fix-up
  scripts during review.
- If the diff includes `.py` files alongside instruction files, note their presence but do not review
  them — this skill reviews instruction files only.
- Treat `.gitignore` boundaries as out of scope. Skip any file excluded by `.gitignore`.
- Every flagged issue must cite the specific contradiction or missing reference. No vague findings.
- Cross-file consistency checks are the highest-value part of this skill — prioritize them over
  exhaustive internal checks when time is limited.
- The fix plan is an offer — never apply fixes without user approval.

## Validation

1. Diff scope auto-detected correctly — staged if present, otherwise unstaged.
2. Every changed instruction file was read in full.
3. Every extracted file reference was verified against disk.
4. Cross-file checks completed for all related-file pairs where at least one side changed.
5. Wrapper alignment verified for every changed `.github/` file.
6. Internal consistency checked for every changed file.
7. Report includes severity, location, and description for every finding. "No issues found" is an
   acceptable result when the changeset is clean.
8. If Errors or Warnings found: fix plan file created with concrete fixes, presented to user for approval.

## Output

- Findings report with severity labels (Error / Warning / Info), organized by file.
- Summary line: number of files reviewed, number of findings by severity.
- If Errors or Warnings present: fix plan file at `.claude/plans/fix-review-findings-<slug>.md`, offered
  for user approval.
- If no issues: confirmation that the changeset is clean.
