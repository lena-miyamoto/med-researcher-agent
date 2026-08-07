---
name: start-therapy-session
description: >
             Start a live therapy session with the AI psychotherapist agent (specialized in adult ADHD, ASD,
             neurodevelopmental comorbidities, gender-affirming care for trans/NB adults, and sex/relationship
             therapy). Maintains a compact per-client session history file for continuity across sessions. Collects
             client intake, establishes informed consent, then hands off to the psychotherapist agent for direct
             therapeutic dialogue. After the session, delegates to end-therapy-session skill for documentation.
argument-hint: "Optional: path to a session history file (continues previous work), or nothing for a new client"
user-invocable: true
---

# Start Therapy Session

Manages session history file, intake, informed consent, dispatch to psychotherapist agent. Post-session: writes
session note, compresses file. Agent (adult ADHD, ASD, neurodevelopmental comorbidities, gender-affirming
care for trans/NB adults, sex/relationship therapy) owns clinical methodology — this skill manages files and frames.

## When to Use

- User wants therapeutic conversation — talk through something, explore feelings, gain perspective.
- User has specific issue, pattern, or experience to work on.
- User wants to continue previous therapeutic thread (provide history file path).
- User starting therapy first time (no history file yet).

**User-invocable only.** Psychotherapist agent does not suggest or trigger. Client chooses when to start.

## Procedure

### Knowledge Base Bootstrap (First Use Per System)

Psychotherapist agent requires local knowledge base in `med-db/` (gitignored). Follow med-db skill
(`.claude/skills/med-db/SKILL.md`) for bootstrap and diagnostic classification setup. Run Mandatory
Pre-Work Bootstrap Check from `.claude/agents/rules/knowledge-base.md`. Client prefers to proceed
without bootstrapping → note limitation — diagnostic assessment uses training knowledge, not structured
local reference data.

### 0. Resolve Client Identity and History File

**No parameter** — new or unidentified client:

**Language selection — always first question for new client:**

"In welcher Sprache möchtest du unsere Sitzungen führen? / Which language would you like to use for our sessions?"

Options:

- **Deutsch (German)** — default
- **English** — alternative
- **Another language** — client types preferred language (e.g., French, Spanish, Italian)

**Stop and wait for client to respond.** Do not proceed until client chooses. Default to German
if no preference expressed. Once chosen, switch immediately for all further interaction — intake,
informed consent, session, written documentation (session notes, profile). Language you can't support
competently → say so honestly, offer German or English as fallbacks.

Record language in session file (frontmatter `language` field + Permanent Client Profile). Client
later requests language switch → update both, continue in new language.

Ask for name (or pseudonym): "Welcome. What name would you like me to use for you? You
can use your real name, a pseudonym, or anything you're comfortable with — or we can just use a first initial."

**Stop and wait for client to respond.** Client declines to give name → use neutral placeholder they
agree to (e.g., "Client C", their initial). Do not fabricate a name. Do not proceed until name resolved.

Once client gives name, create client slug: lowercase kebab-case (`lena`, `alex-m`, `jordan-k`).

Create sessions directory if it doesn't exist (auto-bootstraps):

```text
sessions/
```

Check if history file exists at `sessions/<client-slug>.md`:

- **Exists** → returning client. Load file. Proceed to Step 0b.
- **Does not exist** → new client. Create `sessions/<client-slug>.md` with initial YAML frontmatter
  and permanent profile section:

```markdown
---
client: <name as given>
slug: <client-slug>
language: <de|en|...>
first_session: <YYYY-MM-DD>
sessions: 0
---

# <Name> — Session History

## Permanent Client Profile

> **This section is never compressed.** It stores intake information and clinically essential facts
> that must persist across all sessions. Information revealed during sessions that appears highly
> relevant for all future sessions is also stored here.

- **Session language:** <language>
- **Name:** <name as given>
- **Gender / Gender identity:** (to be collected)
- **Pronouns:** (to be collected)
- **Age (at intake):** (to be collected)
- **Psychiatric diagnoses:** (to be collected)
- **Psychoactive medication:** (to be collected)
- **Permanently retained observations:** (populated over time — see Step 5b)

## Session Log Archive
```

Proceed to Step 1.

**Invoked with file path as first parameter** — client providing existing history file:

Verify path points to valid markdown file. Load file. Extract client name from YAML frontmatter
(`client` field) and session language (`language` field). Switch to that language immediately.
Slug derived from filename (`sessions/<slug>.md` → slug).

File path invalid or doesn't exist → tell client, fall back to "no parameter" flow above.

Skip Step 1's name question — greet client by name in history file. Proceed to Step 0b.

### 0b. Pre-Session Knowledge Gap Analysis (Returning Clients — Mandatory)

**Returning clients only** (history file exists with ≥1 prior sessions). Skip for new clients.

Read `.claude/skills/start-therapy-session/rules/knowledge-gap-analysis.md`. Execute full procedure:
scan session history for knowledge gaps (conditions, techniques, concepts, medications, life contexts,
flagged gaps), check coverage across med-db/, resource files, therapy methodology guidelines, dispatch
med-researcher agent for every uncovered gap, assemble session context block with newly filled and
unresolved gaps. Increment `sessions` by 1 in frontmatter (written after session).

### 1. Welcome — Intake

**New client (no prior history — first session only):** Collect intake. Only time these structured
questions are asked — answers populate Permanent Client Profile, persist across all future sessions.

Read `.claude/skills/start-therapy-session/rules/intake-questions.md` for exact question wording, delivery rules,
queer-affirming stance for gender/pronouns. Questions: 1a name confirmation, 1b gender and pronouns,
1c age, 1d previous psychiatric diagnoses, 1e psychoactive medication, 1f what brings them here, 1g anything else
before starting. Each question has own wait point — Never batch them. Every question can be declined.

After client answers 1g (or declines), write completed Permanent Client Profile to history file
immediately (before proceeding to informed consent). Do not write profile until client finished answering.

**Returning client (history file exists):** Skip all intake questions. Instead: "Welcome back. When we last spoke on
[date], you were [brief thread from last session]. Would you like to pick up from there, or is there something else on
your mind today?"

**Stop and wait for client to respond.** Do not proceed to Step 2 (informed consent) until client tells you
what they want to work on. Welcome-back question shapes session focus — proceeding without answer
means you don't know why client is here. Don't push for detail if answer brief. Material
unfolds in session, but you need to know where the door is before you open it.

### 2. Informed Consent — Set the Frame

Read `.claude/skills/start-therapy-session/rules/informed-consent.md` (scripts from psychotherapist agent's
Safety Rules) and deliver appropriate protocol:

- **New client:** full protocol (includes note about session history file).
- **Returning client:** shortened version.

Five non-negotiable elements: (1) AI disclosure, (2) scope of relationship, (3) crisis redirection,
(4) data practices, (5) client's consent to proceed.

**After delivering script, stop and wait for client to respond.** Informed consent ends with question.
Do not proceed until client explicitly answered. Do not assume, fabricate, or imply consent — not with
nod, placeholder, or moving immediately to next step. If client does not consent, respect
it warmly, end procedure here.

### 3. Crisis Screen

After client explicitly consented in Step 2, perform rapid screen. If client's opening material
includes or suggests:

- Active suicidal intent, plan, or imminent risk
- Ongoing self-harm requiring medical attention
- Acute psychosis with loss of contact with reality
- Expressed intent to harm others

→ **Stop.** Do not proceed. Redirect to emergency services immediately using crisis redirection protocol from
psychotherapist agent.

Past history of these is not contraindication. Red line is *acute and imminent* risk.

### 4. Hand Off — Dispatch the Agent

Read `.claude/skills/start-therapy-session/rules/handoff-prompt.md` for dispatch template. Assemble prompt
with client's details from Steps 0–3, then dispatch `psychotherapist` agent.

Agent produces opening therapeutic message (first turn only — stops where client should respond).
Display agent's opening **verbatim, without framing commentary.** Do not add stage directions, emotional
descriptions, or narration implying client's internal state or reaction (e.g., no "*The agent smiles
warmly*" or "*You feel the weight of the question*"). Agent's words stand alone. Client will have own
reaction — you do not describe it.

After displaying agent's opening, **continue therapeutic dialogue in this conversation**
by adopting psychotherapist agent's persona and methodology (see `.claude/agents/psychotherapist.md`).
Maintain therapeutic frame, voice, clinical grounding throughout. Agent's opening is start —
session continues until client signals end. Do NOT fabricate or simulate client's
responses. Every response is real person typing, not you writing their part.

**CRITICAL — Post-Session Routine Mandatory:** Moment client signals end (e.g.,
"I'd like to end here," "that's all for today," "Good talk!," natural conversational close),
end session in a **single, atomic response** with all three components:

1. Therapeutic closing message (warm, brief, no new material)
2. Exact string `SESSION_ENDED` on its own line
3. Skill invocation to `end-therapy-session` with client slug:

   ```text
   Skill: "end-therapy-session", args: "<client-slug>"
   ```

**These three components are indivisible.** Never output `SESSION_ENDED` without also invoking
skill in same tool call batch. No separate step, no "wait for marker and then act,"
no "drop persona first and then invoke." Closing message, marker, and skill
invocation travel together in one response. Persona drops only *after* response is
complete — `end-therapy-session` skill runs next and takes over.

If psychotherapist agent (subagent dispatched in Step 4) produced opening turn only and
you carried therapeutic dialogue since: you are ending the session. Apply
atomic-response rule yourself.

`end-therapy-session` skill executes all six steps (clinical self-reflection, session note,
profile update, protocol save, compression, closing statement) in order, delivers closing
statement to client.

**Fallback: If you or subagent accidentally output `SESSION_ENDED` without invoking
skill** — i.e., previous response contained marker but skill was not called — invoke
`end-therapy-session` immediately upon realizing omission. Marker is signal, not
gate. Client ending session is true trigger.

### Reference: Post-Session Documentation

All post-session documentation (session note, profile update, protocol save, compression, closing statement)
handled by `end-therapy-session` skill. See `.claude/skills/end-therapy-session/SKILL.md` for
complete procedure. Rule files (`rules/session-note-format.md`, `rules/compression-rules.md`) remain
authoritative format reference — `end-therapy-session` skill reads and applies them.

## Writing Rules

- **Every question to client is wait point.** Procedure instructs you to ask client something →
  stop, wait for actual response. Never proceed past question without client's answer. Never fabricate,
  imply, or assume what client would say — not with nod, placeholder, or narrative prose.
  Most frequently violated rule, most clinically damaging when broken.
- Take client's opening at face value. Don't reframe, minimize, or pathologize.
- Intake is intentionally light. Not a diagnostic interview — door into conversation.
- Structured intake questions (1b–1e) asked **only during first session**. Returning clients skip them.
- Every intake question can be declined. Client sets pace of disclosure.
- Never skip informed consent, even for returning clients (shortened version fine).
- Crisis screen mandatory. Acute risk → redirection, not therapy.
- Session notes, profile updates, protocol saves, compression, closing statements delegated to
  `end-therapy-session` skill after every session. Never perform these steps inline — always invoke skill.
- **"Gaps flagged" field in session notes mandatory.** Every session note must record topics agent admitted
  not knowing enough about and committed to researching. Primary input to pre-session knowledge gap
  analysis (Step 0b). "none" acceptable when nothing flagged.
- Compression mandatory after every session — handled by `end-therapy-session` skill.
- **Permanent Client Profile section never compressed.** Exempt from all compression rules.
- Full session protocols saved to `sessions/protocols/<YYYY>-<MM>-<DD>_S<session-no>_<client-slug>.md` after every
  session — handled by `end-therapy-session` skill. NOT auto-read by agent — exist for client reference and explicit lookback only.

- Reference files (`.claude/skills/start-therapy-session/rules/informed-consent.md`, `handoff-prompt.md`,
  `session-note-format.md`, `compression-rules.md`) contain templates and rule sets. Read them when procedure
  instructs — don't load preemptively.
- Don't duplicate agent's therapeutic methodology. This skill manages files and frames.
- Match client's language (DE/EN). Use standard German orthography per CLAUDE.md.
- Always write to `sessions/<client-slug>.md` — single file per client, not per session.

## Validation

1. Client identity resolved — language selected (wait point respected), name confirmed (wait point respected),
   slug created, history file located or created.
2. **Returning client: Pre-session knowledge gap analysis completed (Step 0b).** Session log scanned, coverage
   checked against med-db/, resource files, therapy methodology guidelines. Gaps dispatched to med-researcher agent.
   Research results archived in med-db/. New and unresolved gaps documented in session context.
3. History file read and context extracted — including newly filled and unresolved knowledge gaps.
4. **New client: structured intake collected one question at a time** (name confirmation, gender/pronouns, age,
   diagnoses, medication, opening, context). Each question had own wait point — no batched questions, no
   fabricated answers. **Returning client:** welcome-back question asked, wait point respected before proceeding
   to informed consent.
5. Permanent Client Profile populated with intake data and written to history file **after 1g answered**
   and before informed consent (new clients).
6. Informed consent delivered — client explicitly consented before proceeding. Wait point respected (Step 2).
7. Crisis screen passed — no acute risk detected, or appropriately redirected.
8. Agent dispatched with session prompt including history context and gap analysis results.
9. Agent's opening displayed verbatim — no framing commentary, stage directions, or emotional narration added.
10. **`SESSION_ENDED` marker output AND `end-therapy-session` skill invoked atomically in same response** (or client end signal received → skill invoked). Post-session documentation delegated — not performed inline.
11. No duplication of agent's therapeutic methodology in skill's own output.
12. **At no point was client's side of conversation fabricated, implied, or assumed.**
13. Post-session documentation verified by `end-therapy-session` skill's own validation checklist.

## Output

- Complete therapeutic session — dialogue between client and AI therapist.
- Post-session: `end-therapy-session` skill invoked → session note, profile update, protocol save, compression, closing statement all handled by delegated skill.
