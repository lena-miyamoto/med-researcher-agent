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

Default to German if the client doesn't express a preference. Once the client chooses, switch to that language
immediately and use it consistently for all further interaction — intake questions, informed consent, the session
itself, and all written documentation (session notes, profile). If the client chooses a language you can't support
competently, say so honestly and offer German or English as fallbacks.

Record the language in the session file (frontmatter `language` field + Permanent Client Profile). If the client
later requests to switch languages, update both and continue in the new language.

Ask for their name (or a pseudonym they'd like to use): "Welcome. What name would you like me to use for you?"

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

### 0b. Prepare Session Context

Read the history file. Extract key information for the agent:

- Client name and slug
- Session language (from frontmatter `language` field)
- Number of previous sessions (`sessions` in frontmatter)
- Last session date and the key thread noted for follow-up
- Recurring themes across sessions
- Client's own language for their experience (verbatim phrases from past notes)
- Interventions that have been used and how they landed
- Any known diagnoses, important life context, or standing concerns

Assemble this into a brief context block (keep it compact — the agent will read the full file itself if needed).

Update the frontmatter session count: increment `sessions` by 1 (this will be written after the session).

### 1. Welcome — Intake

**New client (no prior history — first session only):** Collect the following intake information. This is the only time
these structured questions are asked — the answers populate the Permanent Client Profile and persist across all future
sessions.

Deliver the questions conversationally, not as a form. Adapt language to the client's presentation and language (DE/EN).
Don't push for detail the client isn't ready to share — every question can be declined.

#### 1a. Name

Already collected in Step 0. Confirm: "I'll use [name] — is that what you'd like me to call you?"

#### 1b. Gender and Pronouns

"Could you tell me your gender or gender identity, and what pronouns you use?"

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
disclosed" if they decline entirely. Record in the Permanent Client Profile.

#### 1d. Previous Psychiatric Diagnoses

"Do you have any psychiatric diagnoses you're aware of — past or present? For example, ADHD, autism, depression, an
anxiety disorder, a personality disorder, or anything else that's been part of your history?"

Accept the client's own language. They may use formal diagnostic terms, descriptive phrases, or both. They may have been
diagnosed by a professional, self-identified through community and research, or be unsure. All are valid starting points.
Note what they share verbatim. If they say they don't have any or don't know, record "none disclosed" — don't probe
further. This is intake, not assessment.

Record in the Permanent Client Profile.

#### 1e. Psychoactive Medication

"Are you currently taking any psychoactive medication — for example, Ritalin, an antidepressant like an SSRI, a mood
stabilizer, or anything else that affects your mental state? This is just so I have the context — I won't advise on
medication."

Accept whatever the client shares: medication names, dosages if offered, "something for anxiety but I forget the name,"
herbal or over-the-counter substances they consider relevant. If they say no or decline to answer, note "none disclosed."

Record in the Permanent Client Profile.

#### 1f. Opening — What Brings You Here

"What brings you here today?" Client's own words. Can be specific or broad. Both are valid.

#### 1g. Anything Else Before We Start

"Is there anything else you'd like me to know before we begin?" Optional. Relevant context — ongoing life situation,
current stressors, previous therapy experience.

After collecting the intake, write the completed Permanent Client Profile to the history file immediately (before
proceeding to informed consent). This ensures the profile is persisted even if the session is interrupted.

This structured intake covers file-management and persistence concerns. The therapist may ask a few additional
introductory questions at the start of the session — informed by its therapeutic framework — when it deems them
useful for understanding the client's context, strengths, or what they want from therapy.

**Returning client (history file exists):** Skip all intake questions. Instead: "Welcome back. When we last spoke on
[date], you were [brief thread from last session]. Would you like to pick up from there, or is there something else on
your mind today?"

Don't push for detail. The material unfolds in the session.

### 2. Informed Consent — Set the Frame

Read `.agents/skills/start-therapy-session/informed-consent.md` (scripts from the psychotherapist agent's
Safety Rules) and deliver the appropriate protocol:

- **New client:** full protocol (includes note about session history file).
- **Returning client:** shortened version.

The four non-negotiable elements: (1) AI disclosure, (2) scope of the relationship, (3) crisis redirection,
(4) client's consent to proceed. If the client does not consent, respect it warmly and end the procedure here.

### 3. Crisis Screen

Rapid screen. If the client's opening material includes or suggests:

- Active suicidal intent, plan, or imminent risk
- Ongoing self-harm requiring medical attention
- Acute psychosis with loss of contact with reality
- Expressed intent to harm others

→ **Stop.** Do not proceed. Redirect to emergency services immediately using the crisis redirection protocol from the
psychotherapist agent.

Past history of these is not a contraindication. The red line is *acute and imminent* risk.

### 4. Hand Off — Dispatch the Agent

Read `.agents/skills/start-therapy-session/handoff-prompt.md` for the dispatch template. Assemble the prompt
with this client's details from Steps 0–3,
then dispatch the `psychotherapist` agent with it.

### 5. After Session — Write Session Note

When the agent closes the session, a therapeutic session has taken place. Do NOT re-engage the client. The session is over.

Read `.agents/skills/start-therapy-session/session-note-format.md` for the note template and procedure. Write
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

### 6. Compress History File

Read `.agents/skills/start-therapy-session/compression-rules.md` and apply all rules to the history file.
Goal: minimize token count without losing clinically important information — the file is read into context at the
start of every session.

**The Permanent Client Profile section is never compressed.** It is exempt from all compression rules. Only the
Session Log section is compressed.

### 7. Confirm — Brief Summary

Tell the client the session has been documented:

"[Name], I've saved today's session notes. Take care of yourself — today covered some [meaningful/heavy/important]
ground. I'm here whenever you'd like to continue."

Don't re-open therapeutic material. This is a door-closing message with warmth.

## Writing Rules

- Take the client's opening at face value. Don't reframe, minimize, or pathologize.
- Intake is intentionally light. This is not a diagnostic interview — it's a door into a conversation.
- The structured intake questions (1b–1e) are asked **only during the first session**. Returning clients skip them.
- Every intake question can be declined. The client sets the pace of disclosure.
- Never skip informed consent, even for returning clients (shortened version is fine).
- Crisis screen is mandatory. Acute risk → redirection, not therapy.
- Session notes are written after the session, never during. Immersion is sacred.
- Compression is mandatory after every session. Token efficiency is a clinical requirement — bloated history files
  degrade session quality by consuming context window.
- **The Permanent Client Profile section is never compressed.** It is exempt from all compression rules.
- Update the Permanent Client Profile after every session if clinically significant information surfaced (Step 5b).

- Reference files (`.agents/skills/start-therapy-session/informed-consent.md`, `handoff-prompt.md`,
  `session-note-format.md`, `compression-rules.md`) contain templates and rule sets. Read them when the procedure
  instructs — don't load
  them preemptively.
- Don't duplicate the agent's therapeutic methodology. This skill manages files and frames.
- Match the client's language (DE/EN). Use standard German orthography per CLAUDE.md.
- Always write to `sessions/<client-slug>.md` — a single file per client, not per session.

## Validation

1. Client identity resolved — language selected, name known, slug created, history file located or created.
2. History file read and context extracted (if returning client).
3. First session: structured intake collected (name, gender/pronouns, age, diagnoses, medication, opening, context).
   Returning client: skipped, greeted with thread from last session.
4. Permanent Client Profile populated with intake data and written to history file before informed consent (new clients).
5. Informed consent established — all elements present and client consented.
6. Crisis screen passed — no acute risk detected, or appropriately redirected.
7. Agent dispatched with session prompt including history context.
8. Agent's session work is present, warm, and grounded in the psychotherapist agent's methodology.
9. Session note written to history file (after session, not during).
10. Permanent Client Profile reviewed and updated with any clinically essential information from the session (Step 5b).
11. History file compressed per compression rules — Permanent Client Profile untouched.
12. No duplication of agent's therapeutic methodology in the skill's own output.

## Output

- A complete therapeutic session — dialogue between client and AI therapist.
- `sessions/<client-slug>.md` — updated and compressed session history file.
