---
description: >
  Agent dispatch template for handing off from the skill orchestrator to the
  psychotherapist agent. Referenced by SKILL.md Step 4.
---

# Handoff Prompt Template

Assemble a prompt for the `psychotherapist` agent using this template. Replace all `[placeholders]` with the client's
actual details from Steps 0–3.

```text
Therapy session with [client name] (slug: [client-slug]).

Session history file: sessions/[client-slug].md
Previous sessions: [N]
Last session: [date] — [1-line summary of last session's thread]

Client arrived with: [what brings them here, in their own words]

Context: [any relevant background — 1-3 sentences max]

Recurring themes from history: [brief list, or "none yet"]
Client's language: [1-3 key verbatim phrases from past sessions, or "new client"]

Informed consent has been established and the client consented to proceed.

Open the session. If there is history, briefly acknowledge continuity — "Last time we talked about…" — then check in
with how they're arriving today. Follow their material. Use your full therapeutic presence and modality integration.

Important: The client may signal that they want to end the session at any time (e.g., "I'd like to end here," "that's
all for today"). When this happens, follow your session ending protocol: stop immediately, wrap up with care in 2-4
sentences, check their state briefly, don't introduce new material, and end warmly.

Do NOT write to the history file during the session — this breaks therapeutic immersion. All documentation happens
after the session, handled by the skill. You are fully present with the client.
```

Dispatch the `psychotherapist` agent with this prompt.
