---
name: start-voice-training
description: >
             Start a live voice training session with the AI voice trainer agent (voice feminization
             coaching for trans women and transfeminine people, grounded in WPATH SOC-8 and current voice
             science). Maintains a compact per-client session history file for continuity across sessions.
             Collects client intake, establishes informed consent, then hands off to the voice-trainer
             agent for direct coaching dialogue. After the session, delegates to `end-voice-training`
             skill for documentation.
argument-hint: "Optional: path to a session history file (continues previous work), or nothing for a new client"
user-invocable: true
---

# Start Voice Training

Wrapper. Source of truth: `.claude/skills/start-voice-training/SKILL.md`.
