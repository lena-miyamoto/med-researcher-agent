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

### 0. Create Safety Backup

Before making **any** edit to `sessions/<client-slug>.md`, create a direct safety copy:

```bash
cp sessions/<client-slug>.md "sessions/~<client-slug>.md"
```

Verify the copy succeeded: confirm `sessions/~<client-slug>.md` exists and has the same file size as the original.
If the copy fails (disk full, permissions), **abort the entire procedure immediately** — the session file remains
untouched.

The backup is the rollback anchor. If any structural integrity check in Step 5b fails, restore from this copy.
It must not be used as a reference during editing — it exists only for recovery.

### Input

Read `sessions/<client-slug>.md`. Extract:

- Client name (`client` frontmatter field)
- Session language (`language` frontmatter field)
- Session count (`sessions` frontmatter field) — this is the **previous** session count; new session number = `sessions + 1`
- Date from the conversation context (today's date)

### 1. Clinical Self-Reflection

Before writing the session note, reflect on your therapeutic work. This produces the content
for the "Therapist reflection" field in the session note (Step 2). Brief audit:

1. **What went well?** A moment of genuine connection, an intervention that landed, a
   pattern you named accurately.
2. **What could have been better?** A missed cue, a question that landed wrong, a moment
   you should have challenged but didn't — or challenged but shouldn't have.
3. **Countertransference check.** Did you find yourself working too hard to "fix"
   something? Backing off when the clinical moment called for presence? Feeling irritated,
   helpless, or overly identified with the client? These are signals — note them.
4. **Pattern to watch.** One thing to be mindful of in the next session with this client.

This is not self-flagellation. The goal is continuous improvement — the same standard
you would expect from any therapist committed to getting better at their work.

Condense the reflection into a compact single line for the session note (Step 2). Example:
"Went well: naming the avoidance pattern landed. Improve: should have challenged the
self-dismissal at 0:20 instead of moving on. Countertransference: impulse to rescue —
caught it. Watch: client deflects praise with humor — pattern may be clinically relevant."

### 2. Write Session Note

Read `.claude/skills/start-therapy-session/rules/session-note-format.md` for the note template. Derive the note
contents from the therapeutic conversation that just ended — extract presenting issue, themes, interventions, key
quotes, patterns, gaps flagged, state at close, thread for next, and therapist reflection (from Step 1).

Write the session note to `sessions/<client-slug>.md`, prepended below the YAML frontmatter (newest sessions at top).
Update `sessions` count in frontmatter: increment by 1.

**Every session note must include the "Gaps flagged" field.** "none" is acceptable when the agent did not flag
anything for research.

### 3. Update Permanent Client Profile

Review the session for information belonging in the Permanent Client Profile:

- New or updated diagnoses, medications, gender identity, pronouns, or session language
- Life context so significant it will shape all future therapeutic work
- Metaphors, framings, or self-descriptions that capture something essential about how the client experiences the world
- Any other clinically essential information every future session needs to know

If any found, update the profile. Be judicious — routine session content stays in the session log. Test: "Would
missing this information in session 20 degrade therapeutic work?" If yes, it belongs here.

**Permanent Client Profile section is never compressed.**

### 4. Save Full Session Protocol

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

### 5. Compress History File

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
- **Therapist reflection field preserved.** Never drop the reflection entirely — at minimum, keep the
  "pattern to watch" portion so it transfers to future sessions. For sessions older than 5, compress to
  the pattern-to-watch line only.

Write the compressed file back to `sessions/<client-slug>.md`.

**After writing, pause.** Do not proceed to Step 6 yet. Run the structural integrity verification
in Step 5b first. The closing statement is only delivered after the file passes verification.

### 5b. Structural Integrity Verification

Read both files into context and compare:

1. Read `sessions/~<client-slug>.md` (backup — pre-edit state)
2. Read `sessions/<client-slug>.md` (modified — post-edit state)

Run each check below. Every check must pass. If any check produces an ERROR that cannot be
fixed in place, proceed to Rollback (Step 5b-R). If all checks pass with no remaining ERRORs,
proceed to Cleanup (Step 5b-C) then Step 6.

#### Check 1: YAML Frontmatter Integrity

Compare the frontmatter block (text between opening `---` and closing `---`) in both files:

- All required keys present in both files: `client`, `slug`, `language`, `first_session`, `sessions`
- `client`, `slug`, `language`, `first_session` — values identical to backup
- `sessions` in modified file == `sessions` in backup + 1
  - **If not:** ERROR. Fix by setting the correct value.
- No new frontmatter keys appeared that were not in the backup (removing stale keys per compression
  rules is acceptable; adding undocumented keys is not)

#### Check 2: Section Order and Presence

Identify the major structural sections by their `##` headings. Verify this exact sequence, in this
order, with no sections missing:

1. `# <Name> — Session History` heading (or equivalent level-1 heading)
2. Recent session notes block (one or more `### S<N>: <YYYY-MM-DD>` entries between the frontmatter
   and the Permanent Client Profile)
3. `## Permanent Client Profile`
4. `## Session Log`

- **Sections in wrong order:** ERROR. Most common: session notes appearing after or inside the
  Permanent Client Profile. Fix by reordering.
- **Section missing:** ERROR. Restore from backup, then re-apply edits.
- **Unexpected `##` or `###` heading inside Permanent Client Profile:** ERROR. The profile section
  must contain only bullet list items and blockquotes — no sub-headings. Remove the intruding heading.

#### Check 3: Session Note Boundaries — No Cross-Contamination

Verify that session note headings and profile content have not leaked across section boundaries:

- No `### S<N>: <YYYY-MM-DD>` heading appears inside the `## Permanent Client Profile` section
- No profile content (bullet list items, blockquotes with `>` prefix) appears inside `## Session Log`
  or among recent session notes

**If cross-contamination found:** ERROR. A session note was misplaced into the profile, or profile
content leaked into the log. Move the content back to its correct section.

#### Check 4: Field Completeness — Recent Session Notes

For each `### S<N>: <YYYY-MM-DD>` heading above `## Permanent Client Profile` (uncompressed recent
sessions), verify all 9 mandatory fields:

| Field | Label |
|---|---|
| Presenting | `- Presenting:` |
| Themes | `- Themes:` |
| Interventions | `- Interventions:` |
| Key quotes | `- Key quotes:` |
| Patterns | `- Patterns:` |
| Gaps flagged | `- Gaps flagged:` |
| State at close | `- State at close:` |
| Thread for next | `- Thread for next:` |
| Therapist reflection | `- Therapist reflection:` |

- **Any field missing from a recent session note:** ERROR. Identify which session and which field.
  Restore the missing field content from the backup, or if this is the newly written session note,
  verify it was written correctly.
- "Gaps flagged" must be present even if value is "none".
- "Therapist reflection" must contain content — never empty. For sessions older than 5, the
  reflection may be compressed to the pattern-to-watch portion only (per compression rules), but
  the field label must remain.

#### Check 5: Field Completeness — Compressed Session Log

For each `### S<N>: <YYYY-MM-DD>` heading under `## Session Log`:

- Every compressed entry has a non-empty body after its heading (not a bare heading with no content)
- **If compressed entry is empty (heading only, no body):** WARNING. Content was lost during
  compression. Restore the entry body from the backup.

#### Check 6: Permanent Client Profile — Untouched

Compare the `## Permanent Client Profile` section against the backup:

- Section heading `## Permanent Client Profile` present in both
- Profile content (everything between the heading and the next `##` heading or end of file) is
  identical to the backup, **except** for intentional additions made in Step 3 (new timestamped
  observations, updated fields)
- **If content was removed or altered that was NOT an intentional Step 3 addition:** ERROR.
  Compression has leaked into the protected section. Restore profile content from backup, then
  re-apply only the intentional additions.

#### Check 7: Session Count — Self-Consistency

Count the total number of unique `### S<N>:` headings across the entire file (both recent notes
and session log). This count must equal the `sessions` value in the YAML frontmatter.

- **Counts do not match:** ERROR. Either sessions were lost during compression, or the frontmatter
  count was not updated. Fix by reconciling: count actual headings, update frontmatter to match,
  or restore missing sessions from backup.

#### Check 8: Gate Before Closing Statement

All ERROR-level findings must be resolved before delivering the closing statement. WARNING-level
findings must be acknowledged but do not block.

- **Any ERROR remaining:** do NOT proceed to Step 6. Return to the failing check and fix, or
  initiate rollback (Step 5b-R).

#### 5b-C: Cleanup on Successful Verification

All checks passed with no remaining ERRORs:

1. Delete the backup file:

   ```bash
   rm "sessions/~<client-slug>.md"
   ```

2. Confirm deletion: `sessions/~<client-slug>.md` no longer exists.
3. Proceed to Step 6 (Deliver Closing Statement).

The backup file must not persist after a successful session. If deletion fails (file remains on
disk), log a WARNING but proceed — the file is harmless but should be removed manually.

#### 5b-R: Rollback on Verification Failure

If any structural integrity check produces an ERROR that cannot be fixed in place:

1. Restore the backup:

   ```bash
   cp "sessions/~<client-slug>.md" "sessions/<client-slug>.md"
   ```

2. Verify the restore: read the restored file and confirm it matches the backup (frontmatter
   `sessions` count matches, `## Permanent Client Profile` section present, session notes intact).
3. Delete the backup:

   ```bash
   rm "sessions/~<client-slug>.md"
   ```

4. Report the failure to the orchestrator:
   > "Session documentation failed integrity verification. The session file has been restored to
   > its pre-edit state. The full session protocol was saved to
   > `sessions/protocols/<date>_S<N>_<slug>.md` and is preserved. Manual documentation review is
   > needed before the next session."
5. **Do not deliver a closing statement.** The session is in an error state — closing normally
   would be misleading.
6. The `start-therapy-session` orchestrator must note this failure so the agent is aware before
   the next session that documentation for session `S<N>` is incomplete.

### 6. Deliver Closing Statement

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

All checks run in Step 5b (Structural Integrity Verification). This section summarizes what was verified
for traceability.

1. Clinical self-reflection completed (Step 1) — therapist reflection field populated in session note
2. YAML frontmatter intact, `sessions` incremented correctly, no spurious keys (Check 1)
3. Section structure in correct order: History header, recent notes, Permanent Client Profile, Session Log
   (Check 2)
4. No section cross-contamination — session notes not inside Profile, Profile content not inside Session Log
   (Check 3)
5. All 9 mandatory fields present in new session note and all recent session notes (Check 4)
6. Compressed session log entries have non-empty bodies (Check 5)
7. Permanent Client Profile untouched except for intentional Step 3 additions (Check 6)
8. Session count in frontmatter matches actual session entries in file (Check 7)
9. Full session protocol saved with correct filename format and speaker labels (Step 4)
10. Backup file deleted after successful verification (Step 5b-C)
11. Closing statement delivered as statement, not question; no therapeutic re-engagement after closing (Step 6)
12. If verification failed: session file restored from backup, failure reported to orchestrator, no closing
    statement delivered (Step 5b-R)

## Writing Rules

- Match client's language (DE/EN) from frontmatter `language` field
- Use standard German orthography (umlauts, ß) per CLAUDE.md
- All med-db access through med-db skill — never touch med-db/ files directly
- Session notes compact — clinical documentation, not narrative
- Permanent Client Profile never compressed
