---
name: apply-fixes
description: >
             Apply the fixes from a `review-changeset` fix plan. Invoked by the caller after `review-changeset`
             returns findings that warrant fixes; never invoked directly by the user. Reads the review summary and
             fix plan from the caller's handoff and applies each approved fix.
---

# Apply Fixes

Wrapper. Source of truth: `.claude/skills/apply-fixes/SKILL.md`.
