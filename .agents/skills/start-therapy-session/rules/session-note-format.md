---
description: >
  Compact session note format for documenting therapy sessions in the client's
  history file. Referenced by SKILL.md Step 5.
---

# Session Note Format

When the client has ended the session (either naturally or by signalling they're done — e.g., "I'd like to end here,"
"that's all for today"), the therapeutic session is over. Do NOT re-engage the client in a post-session conversation.
The session is over.

Produce a compact session note using the format from the psychotherapist agent. Write it to the client's
history file. Prepend it below the YAML frontmatter (newest sessions at top):

```markdown
### Session [N]: [YYYY-MM-DD]

- Presenting: [1-line reason]
- Themes: [key themes — 3-6 bullet points]
- Interventions: [modality:technique, e.g. "ACT:values clarification"]
- Key client language: [1-3 short verbatim quotes]
- Patterns: [recurring themes across sessions, if observed]
- Gaps flagged: [topics the agent admitted not knowing enough about and committed to researching — list each one so the
  pre-session gap analysis can dispatch med-researcher to fill them. "none" if nothing was flagged]
- State at close: [grounded / emotional but contained / activated / etc.]
- Thread for next: [1 line]
```

Update the `sessions` count in the YAML frontmatter to the incremented value if you haven't already.

Write the updated file.
