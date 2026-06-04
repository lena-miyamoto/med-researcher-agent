---
name: create-med-agent
description: 'Create a new repo agent for this workspace, with shared role instructions in .agents/agents and thin .github/.claude wrappers. Use when adding a new agent for both Copilot and Claude.'
argument-hint: 'Provide the new agent name, role, trigger description, tool scope, and whether it should be user-invocable or subagent-only'
user-invocable: true
---

# Create Med Agent

Harness wrapper for the shared skill instructions in `.agents/skills/create-med-agent/SKILL.md`.

Use the shared skill file as the source of truth for procedure, writing rules, and validation. Keep this wrapper minimal so Copilot and Claude stay synchronized.
