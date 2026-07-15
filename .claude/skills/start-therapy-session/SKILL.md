---
name: start-therapy-session
description: >
             Start a live therapy session with the AI psychotherapist agent. Maintains a compact per-client session
             history file for continuity across sessions. Collects client intake, establishes informed consent, then
             hands off to the psychotherapist agent for direct therapeutic dialogue. After the session, writes a
             compressed session note to the history file.
argument-hint: "Optional: path to a session history file (continues previous work), or nothing for a new client"
user-invocable: true
---

# Start Therapy Session

Wrapper. Source of truth: `.agents/skills/start-therapy-session/SKILL.md`.
