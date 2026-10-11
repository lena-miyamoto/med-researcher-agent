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
---

# Apply Fixes

Cross-harness source of truth for the `apply-fixes` skill. Applies the fixes from an approved
`review-changeset` fix plan. Not forked and not user-invocable — only the caller that received the
handoff invokes it, after the user approves the plan.

## When to Use

- Called by the caller immediately after `review-changeset` returns a fix plan (Errors or Warnings).
- Only after the user has explicitly approved the plan. Never apply fixes on an unapproved plan.
- User-invocable is `false`: the user routes through `review-changeset`, which hands off to this skill.

## Input

- The review summary and fix plan produced by `review-changeset`, passed as `args`.
- If the handoff text is missing or empty → stop and ask the caller for it.

## Procedure

1. Confirm the handoff text carries a review summary and a fix plan. Missing → stop and ask the caller.
2. Confirm the plan was approved by the user. Approval unclear → stop and ask; never apply unprompted.
3. Apply each plan item, smallest local change first:
   - Re-read the target file with `Read` before each edit — sequential edits to one file need the current
     content, not the version from an earlier turn.
   - Make only the change the plan specifies; do not widen scope or invent extra fixes.
   - If an item is ambiguous or unsafe to apply → skip it, note why, and continue.
4. Archive files: any fix touching the `med-db` archive is delegated to the `med-db` skill via the Skill
   tool. Never edit archive files directly.
5. Validate: after any `*.md` edit run `uv run lint-md` (and `uv run lint-md --fix-source-md <PATH>` for
   archive Markdown); after any `*.py` edit run `uv run test`.
6. Report each plan item as applied or skipped.

## Writing Rules

- Follow the repo command contract: run repo tooling through `uv run` from the repo root.
- Smallest local change that works; re-read after edits.
- Preserve emphasis keywords, temporal framing, enumerated counts, and identity/consequence statements
  when editing instruction text.
- Never use `rm` — use `gio trash`.
- Never apply a fix that is not in the plan, and never apply without approval.
- Do not re-review the changeset — that is `review-changeset`'s job.

## Validation

1. The plan came from a `review-changeset` handoff.
2. User approval was confirmed before any edit.
3. Every applied fix matches a plan item; skipped items are reported with a reason.
4. Archive edits went through the `med-db` skill.
5. `uv run lint-md` was run after `*.md` edits; `uv run test` after `*.py` edits.
6. The caller receives a fix-by-fix report.

## Output

- Each plan item: applied or skipped (with reason).
- Files changed, with the validation command run for each.
- Any item left unresolved and why.
