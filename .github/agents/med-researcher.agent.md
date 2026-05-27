---
name: "med-researcher"
description: "Use when researching medical or dietological questions such as side effects, supplements, contraindications, interactions, nutrition, dietary interventions, evidence summaries, or literature-backed risk and treatment questions."
tools: [read, search, execute, web, todo]
model: "GPT-5 (copilot)"
argument-hint: "Either a direct research prompt or a path to a local text file containing the research brief"
user-invocable: true
---

Medical and dietological research specialist.

Use the shared workflow and deliverable guidance in [.agents/med-researcher.instructions.md](../../.agents/med-researcher.instructions.md). That file is the source of truth for research workflow, output structure, and defaults.
