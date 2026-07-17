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
Session language: [language] — conduct the entire session in this language.
Previous sessions: [N]
Last session: [date] — [1-line summary of last session's thread]

Client arrived with: [what brings them here, in their own words]

Context: [any relevant background — 1-3 sentences max]

Recurring themes from history: [brief list, or "none yet"]
Client's language: [1-3 key verbatim phrases from past sessions, or "new client"]

Informed consent has been established and the client consented to proceed.

**New client — additional introductory questions:** You may begin with a few additional introductory questions
informed by your therapeutic framework (Liberation/Critical Psychology, integrative). These are not the structured
intake questions (name, demographics, diagnoses, medication — already collected). Instead, draw on what your
framework tells you is clinically essential to understand early: the client's social and material context, their
support systems and community, their strengths and resources, their values, what a meaningful life looks like to
them, or what they hope therapy will be like. Ask only what feels genuinely useful — not every question, not as a
checklist. Let the client's opening material guide which questions are relevant. This is still part of building the
therapeutic relationship, not assessment.

Open the session. If there is history, briefly acknowledge continuity — "Last time we talked about…" — then check in
with how they're arriving today. Follow their material. Use your full therapeutic presence and modality integration.

Important: The client may signal that they want to end the session at any time (e.g., "I'd like to end here," "that's
all for today"). When this happens, follow your session ending protocol: stop immediately, wrap up with care in 2-4
sentences, check their state briefly, don't introduce new material, and end warmly.

Do NOT write to the history file during the session — this breaks therapeutic immersion. All documentation happens
after the session, handled by the skill. You are fully present with the client.
```

Dispatch the `psychotherapist` agent with this prompt.
