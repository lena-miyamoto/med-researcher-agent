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

The psychotherapist agent requires a local knowledge base in `med-db/` (gitignored — not shipped with the repo)
with three components: research evidence (7 topics), ICD-11 classification, and DSM-5-TR classification.

Run the bootstrap check from `.agents/agents/psychotherapist.md` (Knowledge Base section, Mandatory Pre-Work
Bootstrap Check). If any component is missing:

- **Research evidence:** dispatch `med-researcher` agent with all three research briefs from `.agents/research-briefs/`.
- **ICD-11:** `uv run med-db-download-icd11 --release 2026-01`
- **DSM-5-TR:** `uv run med-db-setup-dsm5`

Follow `.agents/agents/psychotherapist.md` (Knowledge Base section) for the full bootstrap procedure. If the
client prefers to proceed without bootstrapping, note the limitation and continue — diagnostic assessment will
use training knowledge rather than structured local reference data.

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

Establish informed consent using the protocol from the psychotherapist agent's Safety Rules (Informed Consent &
Therapeutic Frame).

**New client — full protocol.** The core message:

> "Before we go further, I want to be transparent about what this is. I'm an AI, not a licensed human therapist. I can
> listen, reflect, explore, and work through things with you — and I take that seriously. But I can't provide emergency
> support, hold the frame between sessions, or take clinical-legal responsibility the way a human therapist can.
>
> If at any point I think what you're describing goes beyond what I can safely hold, I'll say so and help you think
> about what kind of support might serve you better. And if you're ever in crisis — feeling like you might hurt yourself
> or someone else — please reach out to emergency services immediately. I can give you those numbers if you need them.
>
> I keep session notes in a file under `sessions/<your-name>.md` to help me remember our conversations across sessions.
> These notes are compact and stored locally.
>
> Does that make sense? And are you okay to continue?"

**Returning client — shortened.** "As before — I'm an AI therapist, not a human one, and I can't provide crisis
support. If anything feels beyond what I can hold, I'll say so. I'll note today's session in your history file
afterwards. We good to continue?"

The four non-negotiable elements: (1) AI disclosure, (2) scope of the relationship, (3) crisis redirection,
(4) client's consent to proceed. Plus for new clients: (5) note about session history file.

If the client does not consent, respect it warmly and end the procedure here.

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

Assemble a prompt for the `psychotherapist` agent:

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

### 5. After Session — Write Session Note

When the agent closes the session (either naturally or via client-initiated ending), a therapeutic session has taken
place. Do NOT re-engage the client in a post-session conversation. The session is over.

Instead, produce a compact session note using the format from the psychotherapist agent. Write it to the
client's history file. Prepend it below the YAML frontmatter (newest sessions at top):

```markdown
### Session [N]: [YYYY-MM-DD]

- Presenting: [1-line reason]
- Themes: [key themes — 3-6 bullet points]
- Interventions: [modality:technique, e.g. "ACT:values clarification"]
- Key client language: [1-3 short verbatim quotes]
- Patterns: [recurring themes across sessions, if observed]
- State at close: [grounded / emotional but contained / activated / etc.]
- Thread for next: [1 line]
```

Update the `sessions` count in the YAML frontmatter to the incremented value if you haven't already.

Write the updated file.

### 6. Compress History File

After writing, run a compression pass on the entire history file. Goal: minimize token count without losing any
clinically important information. The file is read into context at the start of every session — every token matters.

**Compression rules:**

- **Remove filler.** Cut words that don't carry information: "the client discussed," "we explored," "it was noted that."
  Replace with direct, compact phrasing. "Discussed work stress — feels overwhelmed by new manager's expectations."

- **Use sentence fragments.** Full grammatical sentences cost tokens. Bullet-point style is preferred throughout.
- **Abbreviate consistently.** Establish abbreviations in the frontmatter and reuse: `CBT` (cognitive-behavioral
  therapy), `SI` (suicidal ideation), `SH` (self-harm), `RCT` (rational emotive behavior therapy), `GAD` (generalized
  anxiety disorder), `MDD` (major depressive disorder), `ACT` (acceptance and commitment therapy), `EMDR` (eye
  movement desensitization and reprocessing). Use standard clinical abbreviations only — never invent ambiguous ones.

- **Merge redundant entries.** If the same theme appears across multiple sessions, consolidate rather than repeating:
  "Sessions 3–5: ongoing pattern of self-criticism after work conflicts." Don't lose the timeline — note when a theme
  first appeared and whether it's active or resolved.

- **Keep verbatim quotes.** Client language is high-signal. Preserve short verbatim quotes that capture their voice,
  framing, or key metaphors. These are worth the tokens.

- **Drop dead information.** Remove anything that is no longer clinically relevant: one-time events that were processed
  and closed, transient circumstances that resolved, topics the client explicitly said they were done with. If unsure,
  keep it — losing information is worse than spending tokens.

- **Collapse old sessions.** Sessions older than 10 sessions ago can be compressed more aggressively: reduce to 1-2
  lines each ("S1: [date] — intake. Key themes: X, Y. Client uses [metaphor] for anxiety.") unless they contain
  information that is still clinically active.

- **Frontmatter hygiene.** Keep the YAML frontmatter minimal: `client`, `slug`, `first_session`, `sessions`, and any
  standing abbreviations legend. Remove any frontmatter fields that have grown stale.

- **No narrative.** The file is clinical documentation, not a story. Zero narrative connective tissue. Adjacent bullet
  points that belong together don't need transition sentences — proximity is enough.

After compression, write the final compressed file back to `sessions/<client-slug>.md`.

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

- Don't duplicate the agent's therapeutic methodology. This skill manages files and frames.
- Match the client's language (DE/EN). Use standard German orthography per AGENTS.md.
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
