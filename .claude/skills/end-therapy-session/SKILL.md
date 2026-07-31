---
name: end-therapy-session
description: >
  Post-session documentation for therapy sessions. Writes compact session note, updates Permanent Client Profile,
  saves full session protocol, compresses history file, and delivers closing statement. Invoked automatically by
  start-therapy-session skill when the therapeutic session ends (client signals end + SESSION_ENDED marker detected).
  Never invoked manually by the user.
argument-hint: "<client-slug>"
user-invocable: false
---

# End Therapy Session

Invoked by `start-therapy-session` skill orchestrator the moment the therapeutic session ends. Handles all
post-session documentation. Not user-invocable — the orchestrator calls it automatically.

## When This Skill Runs

Triggered when:

1. The client signals they want to end the session (e.g., "I'd like to end here," "that's all for today," natural
   conversational close).
2. The psychotherapist agent outputs the `SESSION_ENDED` marker after its closing message.

The `start-therapy-session` skill orchestrator detects the marker and immediately invokes this skill with the
client slug. This skill must not be called during active therapeutic dialogue.

## Procedure

### Input

Read `sessions/<client-slug>.md`. Extract:

- Client name (`client` frontmatter field)
- Session language (`language` frontmatter field)
- Session count (`sessions` frontmatter field) — this is the **previous** session count; new session number = `sessions + 1`
- Date from the conversation context (today's date)

### 1. Write Session Note

Read `.claude/skills/start-therapy-session/rules/session-note-format.md` for the note template. Derive the note
contents from the therapeutic conversation that just ended — extract presenting issue, themes, interventions, key
quotes, patterns, gaps flagged, state at close, and thread for next.

Write the session note to `sessions/<client-slug>.md`, prepended below the YAML frontmatter (newest sessions at top).
Update `sessions` count in frontmatter: increment by 1.

**Every session note must include the "Gaps flagged" field.** "none" is acceptable when the agent did not flag
anything for research.

### 2. Update Permanent Client Profile

Review the session for information belonging in the Permanent Client Profile:

- New or updated diagnoses, medications, gender identity, pronouns, or session language
- Life context so significant it will shape all future therapeutic work
- Metaphors, framings, or self-descriptions that capture something essential about how the client experiences the world
- Any other clinically essential information every future session needs to know

If any found, update the profile. Be judicious — routine session content stays in the session log. Test: "Would
missing this information in session 20 degrade therapeutic work?" If yes, it belongs here.

**Permanent Client Profile section is never compressed.**

### 3. Save Full Session Protocol

Create `sessions/protocols/` if it does not exist. Save the complete therapeutic dialogue to:

```text
sessions/protocols/<YYYY>-<MM>-<DD>_S<session-no>_<client-slug>.md
```

Format:

- Heading: `# S<session-no>: <YYYY-MM-DD> — <Client Name>`
- `**Session language:** <de|en|...>`
- Bold speaker labels: **Therapeutin:** / **Client:** (DE) or **Therapist:** / **Client:** (EN)
- Separate turns with blank lines
- Capture every client response and every therapist message verbatim
- Exclude skill orchestrator output (intake questions, informed consent delivery, crisis screen, research dispatches,
  meta-commentary)

Protocol files are NOT auto-read by the agent at session start. They exist for client reference and explicit
lookback only.

### 4. Compress History File

Read `.claude/skills/start-therapy-session/rules/compression-rules.md` and apply all rules to the Session Log
section only.

**Permanent Client Profile section never compressed.** Exempt from all compression rules.

Key compression rules:

- Remove filler words that carry no clinical information
- Use sentence fragments, not full grammatical sentences
- Keep all verbatim quotes — they are high-signal
- Drop dead information (one-time events processed and closed, resolved transient circumstances)
- Collapse sessions older than 10 sessions ago to 1-2 lines each
- No narrative connective tissue
- Remove frontmatter fields that have grown stale

Write the compressed file back to `sessions/<client-slug>.md`.

### 5. Deliver Closing Statement

Tell the client the session is documented. Use the client's language (DE/EN). Statement, not a question. Door
closed warmly, no invitation to re-engage.

Template (DE):
> "[Name], ich habe die heutigen Notizen gespeichert. [Brief thematic acknowledgment — 1 sentence]. Pass auf dich
> auf. Ich bin da, wenn du weitermachen willst."

Template (EN):
> "[Name], I've saved today's session notes. [Brief thematic acknowledgment — 1 sentence]. Take care of yourself.
> I'm here whenever you'd like to continue."

After delivering, the session is over. Do not add "How are you feeling now?" or any follow-up question.

## Validation

1. Session note written to history file in correct position (below frontmatter, newest first)
2. `sessions` count in frontmatter incremented
3. "Gaps flagged" field present in session note
4. Permanent Client Profile reviewed and updated if clinically essential information surfaced
5. Full session protocol saved with correct filename format and speaker labels
6. History file compressed — Session Log only, Permanent Client Profile untouched
7. Closing statement delivered as statement, not question
8. No therapeutic re-engagement after closing

## Writing Rules

- Match client's language (DE/EN) from frontmatter `language` field
- Use standard German orthography (umlauts, ß) per CLAUDE.md
- All med-db access through med-db skill — never touch med-db/ files directly
- Session notes compact — clinical documentation, not narrative
- Permanent Client Profile never compressed
