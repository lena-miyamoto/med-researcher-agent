---
description: >
  Compact session note format for documenting therapy sessions in the client's
  history file. Referenced by SKILL.md Step 5.
---

# Session Note Format

When client ends session (naturally or signals done — e.g., "I'd like to end here," "that's all for today"),
session is over. Do NOT re-engage in post-session conversation. The session is over.

Produce compact session note using psychotherapist agent format. Write to client's history file.
Prepend below YAML frontmatter (newest at top):

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
- Therapist reflection: [what went well; what to improve; countertransference signal; pattern to watch]
```

Update `sessions` count in YAML frontmatter to incremented value if not already done.

Write updated file.
