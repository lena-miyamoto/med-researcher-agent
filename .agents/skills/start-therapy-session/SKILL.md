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

Ask for their name (or a pseudonym they'd like to use): "Welcome. What name would you like me to use for you?"

Once the client gives a name, create a client slug: lowercase kebab-case (`lena`, `alex-m`, `jordan-k`).

Create the sessions directory if it doesn't exist (auto-bootstraps, like the med-db pattern):

```text
sessions/
```

Check if a history file already exists at `sessions/<client-slug>.md`:

- **Exists** → this is a returning client. Load the file. Proceed to Step 0b.
- **Does not exist** → this is a new client. Create `sessions/<client-slug>.md` with initial YAML frontmatter:

```markdown
---
client: <name as given>
slug: <client-slug>
first_session: <YYYY-MM-DD>
sessions: 0
---

# <Name> — Session History
```

Proceed to Step 1.

**If invoked with a file path as the first parameter** — the client is providing their existing history file:

Verify the path points to a valid markdown file. If it does, this is the client's session history. Load the file.
Extract the client name from the YAML frontmatter (`client` field). The slug is derived from the filename
(`sessions/<slug>.md` → slug).

If the file path is invalid or doesn't exist, tell the client and fall back to the "no parameter" flow above.

Skip Step 1's name question — greet the client by the name in the history file. Proceed to Step 0b.

### 0b. Prepare Session Context

Read the history file. Extract key information for the agent:

- Client name and slug
- Number of previous sessions (`sessions` in frontmatter)
- Last session date and the key thread noted for follow-up
- Recurring themes across sessions
- Client's own language for their experience (verbatim phrases from past notes)
- Interventions that have been used and how they landed
- Any known diagnoses, important life context, or standing concerns

Assemble this into a brief context block (keep it compact — the agent will read the full file itself if needed).

Update the frontmatter session count: increment `sessions` by 1 (this will be written after the session).

### 1. Welcome — Brief Intake

**New client (no prior history):** Collect minimal context:

| Field | Notes |
|---|---|
| **What brings you here today?** | Client's own words. Can be specific or broad. Both are valid. |
| **Anything I should know before we start?** | Optional. Relevant context — ongoing life situation, known diagnoses, current stressors, previous therapy experience. |

**Returning client (history file exists):** Skip the intake questions. Instead: "Welcome back. When we last spoke on
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

### 6. Compress History File

Read `.agents/skills/start-therapy-session/compression-rules.md` and apply all rules to the history file.
Goal: minimize token count without losing
clinically important information — the file is read into context at the start of every session.

### 7. Confirm — Brief Summary

Tell the client the session has been documented:

"[Name], I've saved today's session notes. Take care of yourself — today covered some [meaningful/heavy/important]
ground. I'm here whenever you'd like to continue."

Don't re-open therapeutic material. This is a door-closing message with warmth.

## Writing Rules

- Take the client's opening at face value. Don't reframe, minimize, or pathologize.
- Intake is intentionally light. This is not a diagnostic interview — it's a door into a conversation.
- Never skip informed consent, even for returning clients (shortened version is fine).
- Crisis screen is mandatory. Acute risk → redirection, not therapy.
- Session notes are written after the session, never during. Immersion is sacred.
- Compression is mandatory after every session. Token efficiency is a clinical requirement — bloated history files
  degrade session quality by consuming context window.

- Reference files (`.agents/skills/start-therapy-session/informed-consent.md`, `handoff-prompt.md`,
  `session-note-format.md`, `compression-rules.md`) contain templates and rule sets. Read them when the procedure
  instructs — don't load
  them preemptively.
- Don't duplicate the agent's therapeutic methodology. This skill manages files and frames.
- Match the client's language (DE/EN). Use standard German orthography per CLAUDE.md.
- Always write to `sessions/<client-slug>.md` — a single file per client, not per session.

## Validation

1. Client identity resolved — name known, slug created, history file located or created.
2. History file read and context extracted (if returning client).
3. Brief intake collected (reason for session, any relevant context).
4. Informed consent established — all elements present and client consented.
5. Crisis screen passed — no acute risk detected, or appropriately redirected.
6. Agent dispatched with session prompt including history context.
7. Agent's session work is present, warm, and grounded in the psychotherapist agent's methodology.
8. Session note written to history file (after session, not during).
9. History file compressed per compression rules.
10. No duplication of agent's therapeutic methodology in the skill's own output.

## Output

- A complete therapeutic session — dialogue between client and AI therapist.
- `sessions/<client-slug>.md` — updated and compressed session history file.
