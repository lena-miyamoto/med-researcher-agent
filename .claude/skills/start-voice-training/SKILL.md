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
disable-model-invocation: true
user-invocable: true
model: opus
effort: high
---

# Start Voice Training

Manages history file, intake, informed consent, agent dispatch. Agent owns coaching methodology; skill manages
files and frames.

## Model Guard — Run First, Before Anything Else

First action, before any other tool call: read and apply `.claude/references/session-model-guard.md`
(session directory: `sessions/voice/`). Guard fails → abort; no intake, no history file, no question, no
client-directory access.

## When to Use

- Voice training or voice feminization coaching — pitch, resonance, vocal weight, intonation, articulation,
  any other voice dimension.
- A voice that feels their own, with their own goals (not necessarily "passing").
- Continue a previous voice training thread (provide history file path).
- First voice training session (no history file).

**User-invocable only.** Voice-trainer agent does not suggest or trigger. Client chooses when to start.

## Procedure

### Knowledge Base Bootstrap (First Use Per System)

Voice-trainer agent requires local knowledge base in local archive (gitignored) — `voice-feminization` topic
with core evidence archive. Follow `med-db` skill to bootstrap. Run Mandatory Pre-Work Knowledge Check from
`.claude/agents/references/voice-training-knowledge-base.md`. Client proceeds without bootstrapping → note
limitation: technique guidance uses training knowledge, not archived evidence base.

### 0. Resolve Client Identity and History File

**No parameter** — new or unidentified client:

**Language selection — always first question for new client:**

"In welcher Sprache möchtest du unsere Sitzungen führen? / Which language would you like to use for our sessions?"

Options:

- **Deutsch (German)** — default
- **English** — alternative
- **Another language** — client types preferred language (e.g., French, Spanish, Italian)

**Stop and wait for client to respond.** Do not proceed until client chooses. No preference → default German.
Once chosen, switch immediately for all further interaction — intake, informed consent, session, written
documentation (session notes, profile). Language you can't support competently → say so, offer German or
English as fallbacks.

Record language in session file (frontmatter `language` field + Permanent Client Profile). Later
language-switch request → update both, continue in new language.

Ask for name (or pseudonym): "Welcome. What name would you like me to use for you? You
can use your real name, a pseudonym, or anything you're comfortable with — or we can just use a first initial."

**Stop and wait for client to respond.** Declines name → use neutral placeholder they agree to (e.g.,
"Client C", their initial). Never fabricate a name. Do not proceed until name resolved.

Once client gives name, create client slug: lowercase kebab-case (`sam`, `alex-m`, `jordan-k`).

Create sessions directory if it doesn't exist (auto-bootstraps):

```text
sessions/voice/
```

Check if history file exists at `sessions/voice/<client-slug>.md`:

- **Exists** → returning client. Load file. Proceed to Step 0b.
- **Does not exist** → new client. Create `sessions/voice/<client-slug>.md` with initial YAML frontmatter and
  permanent profile section:

```markdown
---
client: <name as given>
slug: <client-slug>
language: <de|en|...>
first_session: <YYYY-MM-DD>
sessions: 0
---

# <Name> — Voice Training History

## Permanent Client Profile

> **This section is never compressed.** It stores intake information and training-essential facts
> that must persist across all sessions. Information revealed during sessions that appears highly
> relevant for all future sessions is also stored here.

- **Session language:** <language>
- **Name:** <name as given>
- **Gender / Gender identity:** (to be collected)
- **Pronouns:** (to be collected)
- **Age (at intake):** (to be collected)
- **Phoniatric / HNO check:** (to be collected)
- **Voice surgery:** (to be collected)
- **GAHT status:** (to be collected)
- **Permanently retained observations:** (populated over time — see Step 3 of `end-voice-training`)

## Session Log Archive
```

Proceed to Step 1.

**Invoked with file path as first parameter** — client providing existing history file:

Verify path points to valid markdown file. Load file. Extract client name (`client` field) and session language
(`language` field) from YAML frontmatter. Switch to that language immediately. Slug derived from filename
(`sessions/voice/<slug>.md` → slug).

File path invalid or doesn't exist → tell client, fall back to "no parameter" flow above.

Skip Step 1's name question — greet client by name in history file. Proceed to Step 0b.

### 0b. Pre-Session Knowledge Gap Analysis (Returning Clients — Mandatory)

**Returning clients only** (history file exists with ≥1 prior sessions). Skip for new clients.

Read `.claude/skills/start-voice-training/references/knowledge-gap-analysis.md`. Execute full procedure: scan
session history for knowledge gaps (techniques, surgery types, anatomy, measurement tools, voice-affecting
conditions, singing), check coverage across local archive and resource files, dispatch med-researcher agent for
every uncovered gap, assemble session context block with newly filled and unresolved gaps. Session number for
this session = `sessions` + 1; the frontmatter increment is written by `end-voice-training` Step 2.

### 1. Welcome — Intake

**New client (no prior history — first session only):** Collect intake. Only time these structured questions
are asked — answers populate Permanent Client Profile, persist across all future sessions.

Read `.claude/skills/start-voice-training/references/intake-questions.md` for exact question wording, delivery
rules, affirming stance for gender/pronouns. Questions: 1a name confirmation, 1b gender and pronouns, 1c age,
1d phoniatric/HNO check, 1e voice complaints and dysphonia, 1f voice surgery history, 1g GAHT status, 1h voice
goals, 1i daily voice demands, 1j measurement access, 1k singing, 1l psychological context, 1m anything else
before starting. Each question has own wait point — Never batch them. Every question can be declined.

After 1m answered (or declined), write completed Permanent Client Profile to history file immediately, before
informed consent. Do not write profile until client finishes answering.

**Returning client (history file exists):** Skip all intake questions. Instead: "Welcome back. When we last
worked together on [date], you were [brief thread from last session]. Would you like to pick up from there, or
is there something else you'd like to work on today?"

**Stop and wait for client to respond.** Do not proceed to Step 2 (informed consent) until client says what
they want to work on. Welcome-back question shapes focus; skipping it means not knowing why client is here.
Don't push for detail if answer brief.

### 2. Informed Consent — Set the Frame

Read `.claude/skills/start-voice-training/references/informed-consent.md` (scripts from voice-trainer agent's
Safety Rules) and deliver appropriate protocol:

- **New client:** full protocol (includes note about session history file).
- **Returning client:** shortened version.

Seven non-negotiable elements: (1) AI disclosure, (2) AI cannot hear the client, (3) scope of relationship,
(4) vocal safety limits, (5) crisis redirection, (6) data practices, (7) client's consent to proceed.

**After delivering script, stop and wait for client to respond.** Informed consent ends with question. Do not
proceed until client explicitly answered. Do not assume, fabricate, or imply consent — not with nod,
placeholder, or moving immediately to next step. If client does not consent, respect it warmly, end procedure
here.

### 3. Crisis Screen

After client explicitly consented in Step 2, perform rapid screen. If client's opening material includes or
suggests:

- Active suicidal intent, plan, or imminent risk
- Ongoing self-harm requiring medical attention
- Acute psychosis with loss of contact with reality
- Expressed intent to harm others

→ **Stop.** Do not proceed. Redirect to emergency services immediately using crisis redirection protocol from
voice-trainer agent.

Past history of these is not contraindication. Red line is *acute and imminent* risk.

### 4. Hand Off — Dispatch the Agent

Read `.claude/skills/start-voice-training/references/handoff-prompt.md` for dispatch template. Assemble prompt
with client's details from Steps 0–3, then dispatch `voice-trainer` agent.

Agent produces opening coaching message (first turn only — stops where client should respond). Display opening
**verbatim, without framing commentary.** No stage directions, emotional descriptions, or narration implying
client's internal state or reaction (e.g., no "*The trainer smiles warmly*" or "*You feel the weight of the
question*"). Agent's words stand alone. Client has own reaction — you do not describe it.

After displaying opening, **continue coaching dialogue in this conversation** by adopting voice-trainer agent's
persona and methodology (see `.claude/agents/voice-trainer.md`). Maintain coaching frame, voice, evidence
grounding throughout. Opening is start — session continues until client signals end. Do NOT fabricate or
simulate client's responses. Every response is real person typing, not you writing their part.

**CRITICAL — Post-Session Routine (Two-Step):** When client signals they may want to end (e.g., "I'd like to
end here," "that's all for today," "Good session!," natural conversational close), follow the two-step session
ending protocol from the voice-trainer agent:

**Step 1 — Suggest ending, invite final thoughts.** Do NOT jump to closing message. Acknowledge signal, suggest
ending, explicitly invite anything client still wants to say — a question, a request for next session, anything
at all. Stop and wait for client to respond. Client may have more to add.

**Step 2 — Close and trigger documentation (only after client confirms).** Once client verbally agrees to end,
deliver response as **single, atomic unit** with all three components:

1. Coaching closing message (warm, brief, no new material)
2. Exact string `SESSION_ENDED` on its own line
3. Skill invocation to `end-voice-training` with client slug:

   ```text
   Skill: "end-voice-training", args: "<client-slug>"
   ```

**These three components are indivisible in Step 2.** Never output `SESSION_ENDED` without also invoking skill
in same tool call batch. No separate step, no "wait for marker and then act," no "drop persona first and then
invoke." Closing message, marker, and skill invocation travel together in one response. Persona drops only
*after* response is complete — `end-voice-training` skill runs next and takes over.

**Never combine Step 1 and Step 2 into one message.** The suggestion to end and the final closing message must
be separate turns — the client always gets space to respond between them.

If voice-trainer agent (subagent from Step 4) produced opening turn only and you carried coaching dialogue
since: you are ending the session. Apply atomic-response rule yourself.

`end-voice-training` skill executes all six steps (trainer self-reflection, session note, profile update,
protocol save, compression, closing statement) in order, delivers closing statement to client.

**Fallback: If you or subagent accidentally output `SESSION_ENDED` without invoking skill** — previous response
contained marker but skill not called — invoke `end-voice-training` immediately upon realizing omission. Marker
is signal, not gate. Client ending session is true trigger.

### Reference: Post-Session Documentation

All post-session documentation (session note, profile update, protocol save, compression, closing statement)
handled by `end-voice-training` skill. See it for complete procedure. Rule files
(`references/session-note-format.md`, `references/compression-rules.md`) remain authoritative format reference —
`end-voice-training` reads and applies them.

## Writing Rules

- **Every question to client is wait point.** Procedure instructs you to ask client something → stop, wait for
  actual response. Never proceed past question without client's answer. Never fabricate, imply, or assume what
  client would say — not with nod, placeholder, or narrative prose. Most frequently violated rule, most
  damaging when broken.
- Take client's opening at face value. Don't reframe, minimize, or pathologize.
- Intake is intentionally light. Not a diagnostic interview — door into conversation.
- Structured intake questions (1b–1l) asked **only during first session**. Returning clients skip them.
- Every intake question can be declined. Client sets pace of disclosure.
- Never skip informed consent, even for returning clients (shortened version fine).
- Crisis screen mandatory. Acute risk → redirection, not coaching.
- Session notes, profile updates, protocol saves, compression, closing statements delegated to
  `end-voice-training` skill after every session. Never perform these inline — always invoke skill.
- **"Gaps flagged" field in session notes mandatory.** Every session note must record topics agent admitted not
  knowing enough about and committed to researching. Primary input to pre-session knowledge gap analysis
  (Step 0b). "none" acceptable when nothing flagged.
- Compression mandatory after every session — handled by `end-voice-training` skill.
- **Permanent Client Profile section never compressed.** Exempt from all compression rules.
- Full session protocols saved to `sessions/voice/protocols/<YYYY>-<MM>-<DD>_S<session-no>_<client-slug>.md`
  after every session — handled by `end-voice-training` skill. NOT auto-read by agent — exist for client
  reference and explicit lookback only.
- Reference files (`.claude/skills/start-voice-training/references/informed-consent.md`, `handoff-prompt.md`,
  `session-note-format.md`, `compression-rules.md`) contain templates and rule sets. Read them when procedure
  instructs — don't load preemptively.
- Don't duplicate agent's coaching methodology. This skill manages files and frames.
- Match client's language (DE/EN). Use standard German orthography per CLAUDE.md.
- Always write to `sessions/voice/<client-slug>.md` — single file per client, not per session.

## Validation

1. Client identity resolved — language selected (wait point respected), name confirmed (wait point respected),
   slug created, history file at `sessions/voice/<client-slug>.md` located or created.
2. **Returning client: pre-session knowledge gap analysis completed (Step 0b).** Session log scanned, coverage
   checked against local archive and resource files. Gaps dispatched to med-researcher agent. Research results
   archived in local archive. New and unresolved gaps documented in session context.
3. History file read and context extracted — including newly filled and unresolved knowledge gaps.
4. **New client: structured intake collected one question at a time** (name confirmation, gender/pronouns, age,
   phoniatric/HNO check, voice complaints, surgery history, GAHT status, goals, daily voice demands, measurement
   access, singing, psychological context, context). Each question had own wait point — no batched questions, no
   fabricated answers. **Returning client:** welcome-back question asked, wait point respected before proceeding
   to informed consent.
5. Permanent Client Profile populated with intake data and written to history file **after 1m answered** and
   before informed consent (new clients).
6. Informed consent delivered — all seven elements covered, client explicitly consented before proceeding. Wait
   point respected (Step 2).
7. Crisis screen passed — no acute risk detected, or appropriately redirected.
8. Agent dispatched with session prompt including history context and gap analysis results.
9. Agent's opening displayed verbatim — no framing commentary, stage directions, or emotional narration added.
10. **`SESSION_ENDED` marker output AND `end-voice-training` skill invoked atomically in same response** (or
    client end signal received → skill invoked). Post-session documentation delegated — not performed inline.
11. No duplication of agent's coaching methodology in skill's own output.
12. **At no point was client's side of conversation fabricated, implied, or assumed.**
13. Post-session documentation verified by `end-voice-training` skill's own validation checklist.
14. Model guard passed per `.claude/references/session-model-guard.md` — accepted model id, effective `high` or
    above (`medium` accepted on `deepseek-v4-pro`), no `auto`/`unset` override.

## Output

- Complete voice training session — dialogue between client and AI voice trainer.
- Post-session: `end-voice-training` skill invoked → session note, profile update, protocol save, compression,
  closing statement all handled by delegated skill.
