---
name: "med-researcher"
description: "Use proactively for focused medical or dietological research such as side effects, supplements, contraindications, interactions, nutrition, dietary interventions, evidence summaries, or literature-backed risk and treatment questions."
tools: [read, search, execute, web, todo]
model: "GPT-5 (copilot)"
argument-hint: "Either a direct research prompt or a path to a local text file containing the research brief"
user-invocable: true
---

Medical and dietological research specialist.

Harness wrapper for the shared agent instructions in `.agents/agents/med-researcher.md`.

Use the shared agent file as the source of truth for role, evidence rules, and output rules.

Runtime-specific note:

- This Copilot agent is the GitHub/VS Code surface. The only intentional differences from the Claude wrapper are Copilot frontmatter, tool names, user-invocation flag, argument hint, and model selection.
