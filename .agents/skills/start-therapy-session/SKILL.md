---
name: start-therapy-session
description: >
             Start a live therapy session with the AI psychotherapist agent (specialized in adult ADHD, ASD,
             neurodevelopmental comorbidities, gender-affirming care for trans/NB adults, and sex/relationship
             therapy). Maintains a compact per-client session history file for continuity across sessions. Collects
             client intake, establishes informed consent, then hands off to the psychotherapist agent for direct
             therapeutic dialogue. After the session, writes a compressed session note to the history file.
argument-hint: "Optional: path to a session history file (continues previous work), or nothing for a new client"
user-invocable: true
---

# Start Therapy Session

This skill manages the client's session history file, collects intake, establishes informed consent, then dispatches the
psychotherapist agent for direct therapeutic dialogue. After the session, it writes a compact session note and compresses
the file. The agent (specialized in adult ADHD, ASD, neurodevelopmental comorbidities, gender-affirming
care for trans/NB adults, and sex/relationship therapy) owns all clinical methodology — this skill manages
files and frames.

## When to Use

- User wants a therapeutic conversation — to talk through something, explore feelings, gain perspective.
- User has a specific issue, pattern, or experience they want to work on.
- User wants to continue a previous therapeutic thread (provide the history file path).
- User is starting therapy for the first time (no history file yet).

This skill is **user-invocable only**. The psychotherapist agent does not suggest or trigger it. The client chooses
when to start a session.

## Procedure

### Knowledge Base Bootstrap (First Use Per System)

The psychotherapist agent requires a local knowledge base in `med-db/` (gitignored) with three components:
research evidence, ICD-11 classification, and DSM-5-TR classification. Run the Mandatory Pre-Work Bootstrap
Check from `.agents/agents/psychotherapist.md` (Knowledge Base section). If the client prefers to proceed
without bootstrapping, note the limitation — diagnostic assessment will use training knowledge rather than
structured local reference data.

### 0. Resolve Client Identity and History File

**If invoked with no parameter** — this is a new or unidentified client:

**Language selection — always the first question for a new client:**

"In welcher Sprache möchtest du unsere Sitzungen führen? / Which language would you like to use for our sessions?"

Present the options clearly:

- **Deutsch (German)** — default
- **English** — alternative
- **Another language** — the client types their preferred language (e.g., French, Spanish, Italian, etc.)

**Stop and wait for the client to respond.** Do not proceed until the client has chosen a language. Default to German
if the client doesn't express a preference. Once the client chooses, switch to that language immediately and use it
consistently for all further interaction — intake questions, informed consent, the session itself, and all written
documentation (session notes, profile). If the client chooses a language you can't support competently, say so
honestly and offer German or English as fallbacks.

Record the language in the session file (frontmatter `language` field + Permanent Client Profile). If the client
later requests to switch languages, update both and continue in the new language.

Ask for their name (or a pseudonym they'd like to use): "Welcome. What name would you like me to use for you? You
can use your real name, a pseudonym, or anything you're comfortable with — or we can just use a first initial."

**Stop and wait for the client to respond.** If the client declines to give a name, use a neutral placeholder they
agree to (e.g., "Client C", their initial). Do not fabricate a name. Do not proceed until the name question is
resolved.

Once the client gives a name, create a client slug: lowercase kebab-case (`lena`, `alex-m`, `jordan-k`).

Create the sessions directory if it doesn't exist (auto-bootstraps, like the med-db pattern):

```text
sessions/
```

Check if a history file already exists at `sessions/<client-slug>.md`:

- **Exists** → this is a returning client. Load the file. Proceed to Step 0b.
- **Does not exist** → this is a new client. Create `sessions/<client-slug>.md` with initial YAML frontmatter
and a permanent profile section:

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

## Session Log
```

Proceed to Step 1.

**If invoked with a file path as the first parameter** — the client is providing their existing history file:

Verify the path points to a valid markdown file. If it does, this is the client's session history. Load the file.
Extract the client name from the YAML frontmatter (`client` field) and the session language (`language` field).
Switch to that language immediately. The slug is derived from the filename (`sessions/<slug>.md` → slug).

If the file path is invalid or doesn't exist, tell the client and fall back to the "no parameter" flow above.

Skip Step 1's name question — greet the client by the name in the history file. Proceed to Step 0b.

### 0b. Pre-Session Knowledge Gap Analysis (Returning Clients — Mandatory)

**For returning clients only** (history file exists with ≥1 prior sessions). Skip this step for new clients.

Before the session begins, the agent must fill any knowledge gaps identified in previous sessions. This is not optional —
a therapist who never learns from their clients is a deteriorating one. Each client should leave the knowledge base broader
than it was before.

#### 0b-i. Scan for Knowledge Gaps

Read the full session history. For every session note, identify:

- **Conditions mentioned** — any diagnosis, symptom cluster, or clinical presentation discussed
- **Techniques and modalities referenced** — any therapeutic approach named or applied
- **Concepts and terminology** — any clinical concept, framework, or specialized term that appeared
- **Medications named** — any psychopharmacological agent the client mentioned (even in passing)
- **Life experiences and contexts** — any social, cultural, or experiential domain that is clinically relevant (e.g.,
  a specific form of discrimination, a cultural practice, a health condition, a relationship structure)
- **Topics flagged in "Gaps flagged" fields** — anything the agent explicitly admitted it didn't know enough about
  during a previous session and committed to researching

#### 0b-ii. Check Coverage

For each identified item, check whether the knowledge base has adequate coverage:

1. **med-db/ coverage**: Is there at least one relevant paper archived under a matching topic? Query with
   `uv run med-db-query --search-keyword "<term>"` or `uv run med-db-query --list-topics` to check topic presence.
2. **Resource file coverage**: Do the agent's resource files (`neurodevelopmental-specialization`,
   `gender-affirming-care`, `sex-relationship-therapy`, `knowledge-base`) cover this? Read the relevant file and check.
3. **Therapy methodology coverage**: Do the bootstrapped therapy methodology guidelines
   (`med-db/guidelines/therapy-methodologies/`) cover techniques or modalities mentioned?

An item has **adequate coverage** if at least one of these three sources provides substantive clinical information —
not just a passing mention, but enough to inform competent therapeutic work.

#### 0b-iii. Dispatch Research for Gaps

For every item with inadequate coverage, dispatch the `med-researcher` agent with a focused, well-scoped prompt. Examples:

> "Research and archive evidence on [condition X] in adults. Focus on: prevalence, diagnostic criteria, evidence-based
> treatments, and any relevant clinical practice guidelines. Archive the top 3–5 most relevant papers in med-db/ under a
> new or existing topic."
>
> "Research and archive evidence on [technique Y] for [population Z]. What is the evidence base, effect sizes,
> limitations, and adaptations needed? Archive key papers."
>
> "Client mentioned [medication M]. Research and archive: mechanism of action, indications, common side effects, evidence
> quality, and interactions relevant to [client's other conditions/medications]."

Run these research dispatches **before proceeding to Step 1**. The med-researcher agent archives papers in med-db/,
populating the knowledge base for this and all future sessions. This takes a few minutes — the client is not waiting yet;
this is pre-session preparation.

If the med-researcher agent cannot find adequate evidence on a topic, note this honestly: "Research was attempted on [X]
but no high-quality evidence was found. This limitation should be disclosed to the client if the topic arises."

#### 0b-iv. Prepare Session Context

After the gap analysis is complete (or if skipped for a new client), extract key information for the session:

- Client name and slug
- Session language (from frontmatter `language` field)
- Number of previous sessions (`sessions` in frontmatter)
- Last session date and the key thread noted for follow-up
- Recurring themes across sessions
- Client's own language for their experience (verbatim phrases from past notes)
- Interventions that have been used and how they landed
- Any known diagnoses, important life context, or standing concerns
- **Knowledge gaps newly filled** — brief summary of what was researched and archived this cycle (so the agent knows what
  new knowledge is available)
- **Unresolved gaps** — topics flagged in previous sessions that still lack coverage (so the agent can be honest with the
  client if they come up)

Assemble this into a brief context block (keep it compact — the agent will read the full file itself if needed).

Update the frontmatter session count: increment `sessions` by 1 (this will be written after the session).

### 1. Welcome — Intake

**New client (no prior history — first session only):** Collect the following intake information. This is the only time
these structured questions are asked — the answers populate the Permanent Client Profile and persist across all future
sessions.

Deliver the questions conversationally, one at a time, not as a form. **After each question, stop and wait for the
client to respond.** Do not batch multiple questions in one message. Do not anticipate, assume, or fabricate the
client's answer. Adapt language to the client's presentation and language (DE/EN). Don't push for detail the client
isn't ready to share — every question can be declined. If a question is declined, note it and move to the next without
probing.

#### 1a. Name

Already collected in Step 0. Confirm with the client: "I'll use [name] — is that what you'd like me to call you?"
**Wait for confirmation** before proceeding to 1b.

#### 1b. Gender and Pronouns

"Could you tell me your gender or gender identity, and what pronouns you use?"
**Wait for the client's response** before proceeding to 1c.

**Queer-affirming stance.** This question is asked warmly and without assumption. Accept and normalize all responses:

- Binary cis or trans identities with corresponding pronouns (she/her, he/him)
- Non-binary identities with they/them, a combination (she/they, he/they), or any other pronoun set
- Neo-pronouns (ze/zir, xe/xem, ey/em, etc.) — use them consistently and without comment
- No pronouns — the client prefers to be referred to by name only. Honor this.
- The client does not wish to disclose their gender/gender identity — note "not disclosed" and move on without
  further inquiry. Never pressure for disclosure.
- The client is questioning or unsure — note "questioning" or "exploring" in their own words.

Record the client's exact response in the Permanent Client Profile. Use the client's pronouns correctly and consistently
from this point forward. If the client later shares that their gender identity or pronouns have changed, update the
profile immediately — this is not a "preference," it is who they are.

#### 1c. Age

"May I ask how old you are?" If the client prefers not to share their exact age, an age range is fine. Note "not
disclosed" if they decline entirely. **Wait for the client's response.** Record in the Permanent Client Profile.

#### 1d. Previous Psychiatric Diagnoses

"Do you have any psychiatric diagnoses you're aware of — past or present? For example, ADHD, autism, depression, an
anxiety disorder, a personality disorder, or anything else that's been part of your history?"

Accept the client's own language. They may use formal diagnostic terms, descriptive phrases, or both. They may have been
diagnosed by a professional, self-identified through community and research, or be unsure. All are valid starting points.
Note what they share verbatim. If they say they don't have any or don't know, record "none disclosed" — don't probe
further. This is intake, not assessment. **Wait for the client's response.**

Record in the Permanent Client Profile.

#### 1e. Psychoactive Medication

"Are you currently taking any psychoactive medication — for example, Ritalin, an antidepressant like an SSRI, a mood
stabilizer, or anything else that affects your mental state? This is just so I have the context — I won't advise on
medication."

Accept whatever the client shares: medication names, dosages if offered, "something for anxiety but I forget the name,"
herbal or over-the-counter substances they consider relevant. If they say no or decline to answer, note "none disclosed."
**Wait for the client's response.**

Record in the Permanent Client Profile.

#### 1f. Opening — What Brings You Here

"What brings you here today?" Client's own words. Can be specific or broad. Both are valid.
**Wait for the client's response.**

#### 1g. Anything Else Before We Start

"Is there anything else you'd like me to know before we begin?" Optional. Relevant context — ongoing life situation,
current stressors, previous therapy experience.
**Wait for the client's response.**

After the client has answered 1g (or declined), write the completed Permanent Client Profile to the history file
immediately (before proceeding to informed consent). This ensures the profile is persisted even if the session is
interrupted. Do not write the profile until the client has finished answering the intake questions.

This structured intake covers file-management and persistence concerns. The therapist may ask a few additional
introductory questions at the start of the session — informed by its therapeutic framework — when it deems them
useful for understanding the client's context, strengths, or what they want from therapy.

**Returning client (history file exists):** Skip all intake questions. Instead: "Welcome back. When we last spoke on
[date], you were [brief thread from last session]. Would you like to pick up from there, or is there something else on
your mind today?"

**Stop and wait for the client to respond.** Do not proceed to Step 2 (informed consent) until the client has told you
what they want to work on today. The welcome-back question shapes the session focus — proceeding without the answer
means you don't know why the client is here. Don't push for detail if the client's answer is brief. The material
unfolds in the session, but you need to know where the door is before you open it.

### 2. Informed Consent — Set the Frame

Read `.agents/skills/start-therapy-session/resources/informed-consent.md` (scripts from the psychotherapist agent's
Safety Rules) and deliver the appropriate protocol:

- **New client:** full protocol (includes note about session history file).
- **Returning client:** shortened version.

The four non-negotiable elements: (1) AI disclosure, (2) scope of the relationship, (3) crisis redirection,
(4) client's consent to proceed.

**After delivering the script, stop and wait for the client to respond.** The informed consent ends with a question.
Do not proceed until the client has explicitly answered. Do not assume, fabricate, or imply their consent — not with
a nod, not with a placeholder, not by moving immediately to the next step. If the client does not consent, respect
it warmly and end the procedure here.

### 3. Crisis Screen

After the client has explicitly consented in Step 2, perform a rapid screen. If the client's opening material
includes or suggests:

- Active suicidal intent, plan, or imminent risk
- Ongoing self-harm requiring medical attention
- Acute psychosis with loss of contact with reality
- Expressed intent to harm others

→ **Stop.** Do not proceed. Redirect to emergency services immediately using the crisis redirection protocol from the
psychotherapist agent.

Past history of these is not a contraindication. The red line is *acute and imminent* risk.

### 4. Hand Off — Dispatch the Agent

Read `.agents/skills/start-therapy-session/resources/handoff-prompt.md` for the dispatch template. Assemble the prompt
with this client's details from Steps 0–3,
then dispatch the `psychotherapist` agent with it.

The agent produces its opening therapeutic message (first turn only — it stops where the client should respond).
Display the agent's opening **verbatim, without framing commentary.** Do not add stage directions, emotional
descriptions, or narration that implies the client's internal state or reaction (e.g., no "*The agent smiles
warmly*" or "*You feel the weight of the question*"). The agent's words stand alone. The client will have their
own reaction — you do not describe it.

After displaying the agent's opening, **continue the therapeutic dialogue in this conversation**
by adopting the psychotherapist agent's persona and methodology (see `.agents/agents/psychotherapist.md`).
Maintain the therapeutic frame, voice, and clinical grounding throughout. The agent's opening is the start —
the session continues here until the client signals they want to end. Do NOT fabricate or simulate the client's
responses at any point. Every client response in the dialogue is the real person typing, not you writing their part.

Proceed to Step 5 only after the client has ended the session (naturally or by signalling they're done).

### 5. After Session — Write Session Note

The client has signalled they want to end the session (e.g., "I'd like to end here," "that's all for today," or a
natural conversational close). **The session is over.** Do NOT add a closing reflection, a final therapeutic
observation, or "one more thought" after the client has ended. Do NOT re-engage the client in a post-session
conversation. The client's signal to end is a boundary — respect it immediately.

Read `.agents/skills/start-therapy-session/resources/session-note-format.md` for the note template and procedure. Write
a compact session note to the client's history
file, prepended below the YAML frontmatter (newest sessions at top). Update the `sessions` count in the frontmatter.

### 5b. Update Permanent Client Profile

After writing the session note, review the session for information that belongs in the Permanent Client Profile:

- Did the client disclose or update their gender identity or pronouns?
- Did they request a change of session language?
- Did they reveal a previously undisclosed diagnosis or receive a new one?
- Did they start, stop, or change psychoactive medication?
- Did they share life context so significant it will shape all future therapeutic work (e.g., a major loss, a
  trauma history that becomes clinically central, a chronic health condition, immigration or displacement history,
  experiences of systemic oppression that are core to their presentation)?
- Did they use a metaphor, framing, or self-description that captures something essential about how they experience
  the world — something you'd want every future session to know?

If yes, update the relevant field in the Permanent Client Profile. For observations that don't fit an existing field,
append them under **Permanently retained observations** as concise bullet points with the session date:

```markdown
- **Permanently retained observations:**
  - [2026-07-17] Client describes their anxiety as "a radio that never turns off" — central metaphor for their experience.
  - [2026-07-17] Disclosed history of workplace discrimination related to neurodivergence — key context for career-related distress.
```

Be judicious. This section should stay compact — it's the distilled essence of what every future session needs to know.
Routine session content stays in the session log. When in doubt, ask: "Would missing this information in session 20
degrade the therapeutic work?" If yes, it belongs here.

### 5c. Save Full Session Protocol

After the session note and profile update are written, save the complete session dialog as a standalone protocol file
for long-term traceability. This is separate from the compact session note — the protocol preserves every word of the
therapeutic dialogue.

Create the protocols directory if it doesn't exist (auto-bootstraps):

```text
sessions/protocols/
```

Save the full transcript as a markdown file:

```text
sessions/protocols/<YYYY>-<MM>-<DD>_S<session-no>_<client-slug>.md
```

Example: `sessions/protocols/2026-07-19_S4_lena.md`

**Format:**

```markdown
# S<session-no>: <YYYY-MM-DD> — <Client Name>

**Session language:** <de|en|...>

---

**Therapist:** [first message]

**Client:** [response]

**Therapist:** [next message]

...
```

- Use bold speaker labels: **Therapeutin:** / **Client:** (in DE sessions) or **Therapist:** / **Client:** (in EN sessions).
- Separate turns with blank lines.
- Capture the complete dialog — every client response and every therapist message, verbatim.
- Include the agent's opening message (from Step 4) as the first **Therapeutin:** entry.
- Do not include the skill orchestrator's non-therapeutic output (intake questions, informed consent delivery, crisis
  screen, research dispatches, meta-commentary).

**These protocol files are NOT automatically read by the agent at session start.** The agent reads only the compact
history file (`sessions/<client-slug>.md`). Protocol files exist for the client's reference and for explicit lookback
when the user asks the agent to review a specific prior session. They consume significant token budget and must not
be loaded into context unless the user explicitly requests it.

### 6. Compress History File

Read `.agents/skills/start-therapy-session/resources/compression-rules.md` and apply all rules to the history file.
Goal: minimize token count without losing clinically important information — the file is read into context at the
start of every session.

**The Permanent Client Profile section is never compressed.** It is exempt from all compression rules. Only the
Session Log section is compressed.

### 7. Confirm — Brief Summary

Tell the client the session has been documented:

"[Name], I've saved today's session notes. Take care of yourself — today covered some [meaningful/heavy/important]
ground. I'm here whenever you'd like to continue."

This is a door-closing statement, not a question. Do not invite a response or re-open therapeutic material. After
delivering it, the session is over. Do not add "How are you feeling now?" or any follow-up question. Warmth, closure,
boundary — all three.

## Writing Rules

- **Every question to the client is a wait point.** When the procedure instructs you to ask the client something,
  stop and wait for their actual response. Never proceed past a question without the client's answer. Never fabricate,
  imply, or assume what the client would say — not with a nod, not with a placeholder, not with narrative prose.
  This is the most frequently violated rule and the most clinically damaging when broken.
- Take the client's opening at face value. Don't reframe, minimize, or pathologize.
- Intake is intentionally light. This is not a diagnostic interview — it's a door into a conversation.
- The structured intake questions (1b–1e) are asked **only during the first session**. Returning clients skip them.
- Every intake question can be declined. The client sets the pace of disclosure.
- Never skip informed consent, even for returning clients (shortened version is fine).
- Crisis screen is mandatory. Acute risk → redirection, not therapy.
- Session notes are written after the session, never during. Immersion is sacred.
- **The "Gaps flagged" field in session notes is mandatory.** Every session note must record topics the agent admitted
  not knowing enough about and committed to researching. These are the primary input to the pre-session knowledge gap
  analysis (Step 0b). "none" is acceptable when nothing was flagged.
- Compression is mandatory after every session. Token efficiency is a clinical requirement — bloated history files
  degrade session quality by consuming context window.
- **The Permanent Client Profile section is never compressed.** It is exempt from all compression rules.
- Update the Permanent Client Profile after every session if clinically significant information surfaced (Step 5b).
- Full session protocols are saved to `sessions/protocols/<YYYY>-<MM>-<DD>_S<session-no>_<client-slug>.md` after every
  session (Step 5c). These are NOT auto-read by the agent — they exist for client reference and explicit lookback only.

- Reference files (`.agents/skills/start-therapy-session/resources/informed-consent.md`, `handoff-prompt.md`,
  `session-note-format.md`, `compression-rules.md`) contain templates and rule sets. Read them when the procedure
  instructs — don't load
  them preemptively.
- Don't duplicate the agent's therapeutic methodology. This skill manages files and frames.
- Match the client's language (DE/EN). Use standard German orthography per CLAUDE.md.
- Always write to `sessions/<client-slug>.md` — a single file per client, not per session.

## Validation

1. Client identity resolved — language selected (wait point respected), name confirmed (wait point respected),
   slug created, history file located or created.
2. **Returning client: Pre-session knowledge gap analysis completed (Step 0b-i–iii).** Session log scanned, coverage
   checked against med-db/, resource files, and therapy methodology guidelines. Gaps dispatched to med-researcher agent.
   Research results archived in med-db/. New and unresolved gaps documented in session context (Step 0b-iv).
3. History file read and context extracted — including newly filled and unresolved knowledge gaps.
4. **New client: structured intake collected one question at a time** (name confirmation, gender/pronouns, age,
   diagnoses, medication, opening, context). Each question had its own wait point — no batched questions, no
   fabricated answers. **Returning client:** welcome-back question asked, wait point respected before proceeding
   to informed consent.
5. Permanent Client Profile populated with intake data and written to history file **after 1g was answered**
   and before informed consent (new clients).
6. Informed consent delivered — client explicitly consented before proceeding. Wait point respected (Step 2).
7. Crisis screen passed — no acute risk detected, or appropriately redirected.
8. Agent dispatched with session prompt including history context and gap analysis results.
9. Agent's opening displayed verbatim — no framing commentary, stage directions, or emotional narration added.
10. Session note written to history file (after session, not during — no closing reflection added after client's
    end signal) — includes "Gaps flagged" field.
11. Permanent Client Profile reviewed and updated with any clinically essential information from the session (Step 5b).
12. History file compressed per compression rules — Permanent Client Profile untouched.
13. Closing message delivered as a statement, not a question. Door closed warmly, no invitation to re-engage.
14. No duplication of agent's therapeutic methodology in the skill's own output.
15. **At no point was the client's side of the conversation fabricated, implied, or assumed.**
16. Full session protocol saved to `sessions/protocols/` with correct filename format (Step 5c).

## Output

- A complete therapeutic session — dialogue between client and AI therapist.
- `sessions/<client-slug>.md` — updated and compressed session history file.
- `sessions/protocols/<YYYY>-<MM>-<DD>_S<session-no>_<client-slug>.md` — full transcript of the therapeutic dialogue.
