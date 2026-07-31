---
name: end-therapy-session
description: >
  Post-session documentation for therapy sessions. Writes compact session note, updates Permanent Client Profile,
  saves full session protocol, compresses history file, and delivers closing statement. Invoked automatically by
  start-therapy-session skill when the therapeutic session ends (client signals end + SESSION_ENDED marker detected).
  Never invoked manually by the user.
argument-hint: "<client-slug>"
user-invocable: false
---

# End Therapy Session

Wrapper. Source of truth: `.claude/skills/end-therapy-session/SKILL.md`.
