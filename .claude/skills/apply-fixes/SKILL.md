---
name: apply-fixes
description: >
             Apply the fixes from a `review-changeset` fix plan. Invoked by the caller after `review-changeset`
             returns findings that warrant fixes; never invoked directly by the user. Reads the review summary and
             fix plan from the caller's handoff and applies each approved fix.
argument-hint: 'The review summary and fix plan text returned by review-changeset'
disable-model-invocation: false
user-invocable: false
model: haiku
effort: high
background: false
---

# Apply Fixes

Cross-harness source of truth for the `apply-fixes` skill. Applies fixes from an approved `review-changeset` fix plan. Not forked and not user-invocable — only the handoff-receiving caller invokes it, after the user approves the plan.

## When to Use

- Called by the caller immediately after `review-changeset` returns a fix plan (Errors or Warnings).
- Only after the user has explicitly approved the plan. Never apply fixes on an unapproved plan.

## Input

- The review summary and fix plan produced by `review-changeset`, passed as `args`.
- If the handoff text is missing or empty → stop and ask the caller for it.

## Procedure

1. Confirm the handoff text carries a review summary and a fix plan. Missing → stop and ask the caller.
2. Confirm the plan was approved by the user. Approval unclear → stop and ask; never apply unprompted.
3. Apply each plan item, smallest local change first:
   - Re-read the target file with `Read` before each edit — sequential edits to one file need the current content, not the version from an earlier turn.
   - Make only the change the plan specifies; do not widen scope or invent extra fixes.
   - Ambiguous or unsafe item → skip it, note why, and continue.
   - **Mutation-verify every test-quality fix.** A fix that makes a test able to fail is not applied until proven: disable the covered branch, run that test alone, confirm it fails, restore the branch, confirm it passes. A fixture that still passes under the mutation is vacuous — rework the fixture to defeat the masker (see the masker list in `.claude/references/python-review.md`), keeping the plan's intent: the behavior the test names. A plan fix that cannot be made to fail goes back to the caller as unresolved rather than applied as-is.
4. Archive files: any fix touching `./med-db/` is delegated to the `med-db` skill via the Skill tool. Never edit archive files directly.
5. Validate: after any `*.md` edit run `uv run lint-md` (and `uv run lint-md --fix-source-md <PATH>` for archive Markdown); after any `*.py` edit run `uv run lint` and `uv run test`.
6. Report each plan item as applied or skipped.

## Writing Rules

- Follow the repo command contract: run repo tooling through `uv run` from the repo root.
- Smallest local change that works; re-read after edits.
- Preserve emphasis keywords, temporal framing, enumerated counts, and identity/consequence statements when editing instruction text.
- Never use `rm` — use `gio trash`.
- Never apply a fix that is not in the plan, and never apply without approval.
- Never leave a mutation in a source file. Revert it in the same step that introduced it, then confirm the revert against a baseline: capture `git diff <path>` before disabling the branch, and require byte-identical output after restoring it. `git status --short` does not prove this on its own — an unstaged modification shows `M` in the worktree column whether or not the mutation is still in place; only a staged file gives a signal, showing `MM` while the mutation is live.
- Do not re-review the changeset — that is `review-changeset`'s job. Mutation-verifying a test fix is not a re-review: it checks the fix does what the plan says, nothing else.

## Validation

1. The plan came from a `review-changeset` handoff.
2. User approval was confirmed before any edit.
3. Every applied fix matches a plan item; skipped items are reported with a reason.
4. Every test-quality fix was mutation-verified — it failed with the branch disabled and passed with it restored — or reported as unresolved with the reason. Any mutation was fully reverted.
5. Archive edits went through the `med-db` skill.
6. `uv run lint-md` was run after `*.md` edits; `uv run lint` and `uv run test` after `*.py` edits.
7. The caller receives a fix-by-fix report, including any deviation from the plan (e.g. a fixture tightened to make a mutation fail) and why.

## Output

- Each plan item: applied or skipped (with reason).
- Files changed, with the validation command run for each.
- For each mutation-verified test fix: the branch disabled, the assertion that failed, and the confirmation the branch was restored clean.
- Any item left unresolved and why.
