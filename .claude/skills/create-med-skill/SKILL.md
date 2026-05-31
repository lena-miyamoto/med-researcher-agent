---
name: create-med-skill
description: Use when you need to create a new shared repo skill for this workspace, with the source of truth in .agents/skills and thin .github/.claude wrappers.
argument-hint: Provide the new skill name and what it should do; include description keywords, optional argument hint, and any routing or doc updates needed
user-invocable: true
---

# Create Med Skill

Harness wrapper for the shared skill instructions in `.agents/skills/create-med-skill/SKILL.md`.

Follow `CLAUDE.md` and `AGENTS.md`, then load the shared skill file for the full procedure, writing rules, and validation. Keep this wrapper minimal so Copilot and Claude stay synchronized.
