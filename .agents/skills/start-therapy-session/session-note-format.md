---
description: >
  Compact session note format for documenting therapy sessions in the client's
  history file. Referenced by SKILL.md Step 5.
---

# Session Note Format

When the agent closes the session (either naturally or via client-initiated ending), a therapeutic session has taken
place. Do NOT re-engage the client in a post-session conversation. The session is over.

Instead, produce a compact session note using the format from the psychotherapist agent. Write it to the client's
history file. Prepend it below the YAML frontmatter (newest sessions at top):

```markdown
### Session [N]: [YYYY-MM-DD]

- Presenting: [1-line reason]
- Themes: [key themes — 3-6 bullet points]
- Interventions: [modality:technique, e.g. "ACT:values clarification"]
- Key client language: [1-3 short verbatim quotes]
- Patterns: [recurring themes across sessions, if observed]
- State at close: [grounded / emotional but contained / activated / etc.]
- Thread for next: [1 line]
```

Update the `sessions` count in the YAML frontmatter to the incremented value if you haven't already.

Write the updated file.
