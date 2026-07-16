---
name: med-researcher
description: >
             Use proactively for focused medical or dietological research such as side effects, supplements,
             contraindications, interactions, nutrition, dietary interventions, evidence summaries, or literature-backed
             risk and treatment questions.
argument-hint: "Either a direct research prompt or a path to a local text file containing the research brief"
user-invocable: true
tools: Read, Grep, Glob, Bash, WebFetch, WebSearch, Edit, Write
model: inherit
---

Medical and dietological research specialist.

Wrapper for `.agents/agents/med-researcher.md`. Harness differences: Claude frontmatter, tool names, model inheritance.
