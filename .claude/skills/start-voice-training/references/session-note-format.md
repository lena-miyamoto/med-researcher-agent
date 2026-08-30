---
description: >
  Compact session note format for documenting voice training sessions in the client's
  history file. Referenced by SKILL.md Step 5.
---

# Session Note Format

When client ends session (naturally or signals done — e.g., "I'd like to end here," "that's all for today"),
session is over. Do NOT re-engage in post-session conversation. The session is over.

Produce compact session note using voice-trainer agent format. Write to client's history file.
Prepend below YAML frontmatter (newest at top):

```markdown
### Session [N]: [YYYY-MM-DD]

- Presenting: [1-line reason]
- Themes: [key themes — 3-6 bullet points]
- Exercises done: [techniques worked in session, e.g. "SOVTE:straw phonation glides", "pitch:220 Hz sustains"]
- Measurements: [self-reported or app readings taken this session — F0 values in Hz, sensations, or "none taken"]
- Home practice: [exercises assigned for between sessions, with dosage]
- Adherence: [how last session's plan was followed — consistent / partial / none, with reason if known]
- Gaps flagged: [topics the agent admitted not knowing enough about and committed to researching — list each one so the
  pre-session gap analysis can dispatch med-researcher to fill them. "none" if nothing was flagged]
- State at close: [voice: rested / slightly strained / energized; mood: grounded / frustrated / activated / etc.]
- Thread for next: [1 line]
- Trainer reflection: [what went well; what to improve; pattern to watch in client's technique or adherence]
```

Update `sessions` count in YAML frontmatter to incremented value if not already done.

Write updated file.
