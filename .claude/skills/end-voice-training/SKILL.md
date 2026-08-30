---
name: end-voice-training
description: >
  Post-session documentation for voice training sessions. Writes compact session note, updates Permanent Client
  Profile, saves full session protocol, compresses history file, and delivers closing statement. Invoked
  automatically by `start-voice-training` skill when the voice training session ends (client signals end +
  SESSION_ENDED marker detected). Never invoked manually by the user.
argument-hint: "<client-slug>"
user-invocable: false
---

# End Voice Training

Invoked by `start-voice-training` skill orchestrator when voice training session ends. Handles all
post-session documentation. Not user-invocable — orchestrator calls it automatically.

## When This Skill Runs

Triggered when:

1. Client signals session end (e.g., "I'd like to end here," "that's all for today," natural conversational close).
2. Voice-trainer agent outputs `SESSION_ENDED` marker after closing message.

Orchestrator detects marker, immediately invokes this skill with client slug. Must not be called during active coaching dialogue.

## Procedure

### 0. Create Safety Backup

Before **any** edit to `sessions/voice/<client-slug>.md`, create a direct safety copy:

```bash
cp sessions/voice/<client-slug>.md "sessions/voice/~<client-slug>.md"
```

Verify copy: confirm `sessions/voice/~<client-slug>.md` exists, same file size as original. Copy fails →
**abort entire procedure immediately** — session file remains untouched.

Backup is rollback anchor. If any Step 5b structural integrity check fails, restore from this copy.
Not a reference during editing — exists only for recovery.

### Input

Read `sessions/voice/<client-slug>.md`. Extract:

- Client name (`client` frontmatter field)
- Session language (`language` frontmatter field)
- Session count (`sessions` frontmatter field) — **previous** count; new session number = `sessions + 1`
- Date from conversation context (today's date)

### 1. Trainer Self-Reflection

Before writing session note, reflect on coaching work. Produces "Trainer reflection" field content (Step 2).
Brief audit:

1. **What went well?** A moment of genuine connection, an exercise that landed, a pattern you named accurately.
2. **What could have been better?** A missed cue, an instruction that landed wrong, a moment you should have
   slowed down but didn't — or pushed when you shouldn't have.
3. **Signal check.** Working too hard to "fix" the voice? Backing off when the coaching moment called for
   presence? Feeling impatient, helpless, or overly identified with the client's dysphoria? These are
   signals — note them.
4. **Pattern to watch.** One thing to be mindful of in the next session with this client.

Not self-flagellation. Goal: continuous improvement — standard expected of any trainer committed to getting better.

Condense reflection into a compact single line for session note (Step 2). Example:
"Went well: 220 Hz anchor clicks — client held sustains without strain. Improve: rushed the resonance
explanation; client needed the mouth-open analogy first. Signal: urge to push harder when progress is
slow — caught it. Watch: client consistently undersells home practice."

### 2. Write Session Note

Read `.claude/skills/start-voice-training/references/session-note-format.md` for template. Derive note from
coaching conversation — extract presenting, themes, exercises done, measurements, home practice, adherence,
gaps flagged, state at close, thread for next, trainer reflection (from Step 1).

Write note to `sessions/voice/<client-slug>.md`, prepended below YAML frontmatter (newest at top).
Increment `sessions` count in frontmatter by 1.

**Every session note must include "Gaps flagged" field.** "none" acceptable when agent flagged nothing for research.

### 3. Update Permanent Client Profile

Review session for information belonging in Permanent Client Profile:

- New or updated voice conditions, surgery history, GAHT status, gender identity, pronouns, or session language
- Baseline measurements that become the client's reference points (resting F0, comfortable range)
- Voice-use context significant enough to shape all future training work
- Metaphors, framings, or self-descriptions capturing something essential about how client experiences their voice
- Any other training-essential information every future session needs to know

If any found, update profile. Be judicious — routine session content stays in session log. Test: "Would
missing this in session n+20 degrade coaching work?" If yes, it belongs here.

**Permanent Client Profile section is never compressed.**

### 4. Save Full Session Protocol

Run the protocol extraction script from the repository root:

```bash
uv run session-protocol --session-kind voice --slug <client-slug> --session-number <session-no> --date <YYYY-MM-DD>
```

- `<session-no>`: session number computed at Input (previous `sessions` count + 1).
- `<YYYY-MM-DD>`: today's date.

The script reads client name and language from `sessions/voice/<client-slug>.md` frontmatter, locates the
session transcript automatically (newest JSONL under `~/.claude/projects/` containing both the
`SESSION_ENDED` marker and the `end-voice-training` Skill call), and writes
`sessions/voice/protocols/<YYYY>-<MM>-<DD>_S<session-no>_<client-slug>.md` (directory created if needed).

**Verify the written protocol:**

1. Read `sessions/voice/protocols/<YYYY>-<MM>-<DD>_S<session-no>_<client-slug>.md`.
2. Heading is `# S<session-no>: <YYYY-MM-DD> — <Client Name>`; `**Session language:**` matches frontmatter.
3. First turn is the trainer opening; last trainer turn is the closing message.
4. No `SESSION_ENDED` marker, tool calls, skill instructions, or intake/consent text anywhere.
5. Speaker labels correct and alternating: **Trainerin:** / **Client:** (DE), **Trainer:** / **Client:** (EN).
6. Turn count (printed by the script) plausible vs. the session as you witnessed it.
7. Spot-check verbatim: 2–3 client messages and 2–3 trainer messages — compare against the
   conversation in context; fix any mismatch directly in the file (never regenerate the whole
   protocol token-by-token).

Script fails (non-zero exit) → manual fallback: construct the protocol yourself from the
conversation in context with the same format:

- Heading: `# S<session-no>: <YYYY-MM-DD> — <Client Name>`
- `**Session language:** <de|en|...>`
- Bold speaker labels: **Trainerin:** / **Client:** (DE) or **Trainer:** / **Client:** (EN)
- Separate turns with blank lines
- Capture every client response and every trainer message verbatim
- Exclude skill orchestrator output (intake questions, informed consent delivery, crisis screen,
  research dispatches, meta-commentary)

If the script selected the wrong transcript (rare), re-run with the explicit file:

```bash
uv run session-protocol --session-kind voice --slug <client-slug> --session-number <session-no> --date <YYYY-MM-DD> --session-file <path-to-jsonl>
```

Protocol files NOT auto-read at session start. Exist for client reference and explicit lookback only.

### 5. Compress History File

Read `.claude/skills/start-voice-training/references/compression-rules.md`. Apply all rules to Session Log Archive
section only.

**Permanent Client Profile section never compressed.** Exempt from all compression rules.

Key compression rules:

- Remove filler words carrying no training information
- Use sentence fragments, not full grammatical sentences
- Keep all verbatim quotes — high-signal
- Drop dead information (one-time events processed and closed, resolved transient circumstances)
- Collapse sessions older than 10 sessions ago to 1-2 lines each
- No narrative connective tissue
- Remove frontmatter fields grown stale
- **Trainer reflection field preserved.** Never drop entirely — at minimum, keep "pattern to watch" portion
  so it transfers to future sessions. For sessions older than 5, compress to pattern-to-watch line only.

Write compressed file back to `sessions/voice/<client-slug>.md`.

**After writing, pause.** Do not proceed to Step 6. Run Step 5b structural integrity verification first.
Closing statement only delivered after file passes verification.

### 5b. Structural Integrity Verification

Read both files into context and compare:

1. Read `sessions/voice/~<client-slug>.md` (backup — pre-edit state)
2. Read `sessions/voice/<client-slug>.md` (modified — post-edit state)

Run each check below. All must pass. ERROR that cannot be fixed in place → Rollback (Step 5b-R).
All pass with no remaining ERRORs → Cleanup (Step 5b-C) then Step 6.

#### Check 1: YAML Frontmatter Integrity

Compare frontmatter block (text between opening `---` and closing `---`) in both files:

- All required keys present in both: `client`, `slug`, `language`, `first_session`, `sessions`
- `client`, `slug`, `language`, `first_session` — values identical to backup
- `sessions` in modified file == `sessions` in backup + 1
  - **If not:** ERROR. Fix by setting correct value.
- No new frontmatter keys appeared that were not in backup (removing stale keys per compression
  rules acceptable; adding undocumented keys is not)

#### Check 2: Section Order and Presence

Identify major structural sections by `##` headings. Verify exact sequence, in order, no sections missing:

1. `# <Name> — Voice Training History` heading (or equivalent level-1 heading)
2. Recent session notes block (one or more `### S<N>: <YYYY-MM-DD>` entries between frontmatter
   and Permanent Client Profile)
3. `## Permanent Client Profile`
4. `## Session Log Archive`

- **Sections in wrong order:** ERROR. Most common: session notes after or inside Permanent Client Profile.
  Fix by reordering.
- **Section missing:** ERROR. Restore from backup, re-apply edits.
- **Unexpected `##` or `###` heading inside Permanent Client Profile:** ERROR. Profile section must contain
  only bullet list items and blockquotes — no sub-headings. Remove intruding heading.

#### Check 3: Session Note Boundaries — No Cross-Contamination

Verify no cross-contamination across section boundaries:

- No `### S<N>: <YYYY-MM-DD>` heading inside `## Permanent Client Profile` section
- No profile content (bullet list items, blockquotes with `>` prefix) inside `## Session Log Archive`
  or among recent session notes

**Cross-contamination found:** ERROR. Session note misplaced into profile, or profile content leaked
into log. Move content back to correct section.

#### Check 4: Field Completeness — Recent Session Notes

For each `### S<N>: <YYYY-MM-DD>` heading above `## Permanent Client Profile` (uncompressed recent
sessions), verify all 10 mandatory fields:

| Field | Label |
|---|---|
| Presenting | `- Presenting:` |
| Themes | `- Themes:` |
| Exercises done | `- Exercises done:` |
| Measurements | `- Measurements:` |
| Home practice | `- Home practice:` |
| Adherence | `- Adherence:` |
| Gaps flagged | `- Gaps flagged:` |
| State at close | `- State at close:` |
| Thread for next | `- Thread for next:` |
| Trainer reflection | `- Trainer reflection:` |

- **Any field missing from recent session note:** ERROR. Identify session and field. Restore missing
  field from backup, or verify newly written session note was written correctly.
- "Gaps flagged" must be present even if value is "none".
- "Trainer reflection" must contain content — never empty. For sessions older than 5, may be
  compressed to pattern-to-watch portion only (per compression rules), but field label must remain.

#### Check 5: Field Completeness — Compressed Session Log Archive

For each `### S<N>: <YYYY-MM-DD>` heading under `## Session Log Archive`:

- Every compressed entry has non-empty body after heading (not a bare heading with no content)
- **Compressed entry empty (heading only, no body):** WARNING. Content lost during compression.
  Restore entry body from backup.

#### Check 6: Permanent Client Profile — Untouched

Compare `## Permanent Client Profile` section against backup:

- Section heading `## Permanent Client Profile` present in both
- Profile content (everything between heading and next `##` heading or end of file) identical
  to backup, **except** for intentional additions made in Step 3 (new timestamped observations,
  updated fields)
- **Content removed or altered that was NOT intentional Step 3 addition:** ERROR. Compression
  leaked into protected section. Restore profile from backup, re-apply only intentional additions.

#### Check 7: Session Count — Self-Consistency

Count unique `### S<N>:` headings across entire file (recent notes + session log). Must equal
`sessions` value in YAML frontmatter.

- **Counts do not match:** ERROR. Sessions lost during compression, or frontmatter count not updated.
  Reconcile: count actual headings, update frontmatter to match, or restore missing sessions from backup.

#### Check 8: Gate Before Closing Statement

All ERROR-level findings must be resolved before closing statement. WARNING-level findings must
be acknowledged but do not block.

- **Any ERROR remaining:** do NOT proceed to Step 6. Return to failing check and fix, or initiate
  rollback (Step 5b-R).

#### 5b-C: Cleanup on Successful Verification

All checks passed with no remaining ERRORs:

1. Delete backup file:

   ```bash
   rm "sessions/voice/~<client-slug>.md"
   ```

2. Confirm deletion: `sessions/voice/~<client-slug>.md` no longer exists.
3. Proceed to Step 6 (Deliver Closing Statement).

Backup must not persist after successful session. Deletion fails (file remains on disk) → log
WARNING, proceed — file harmless but should be removed manually.

#### 5b-R: Rollback on Verification Failure

If any structural integrity check produces an ERROR that cannot be fixed in place:

1. Restore backup:

   ```bash
   cp "sessions/voice/~<client-slug>.md" "sessions/voice/<client-slug>.md"
   ```

2. Verify restore: read restored file, confirm it matches backup (frontmatter `sessions` count
   matches, `## Permanent Client Profile` section present, session notes intact).
3. Delete backup:

   ```bash
   rm "sessions/voice/~<client-slug>.md"
   ```

4. Report failure to orchestrator:
   > "Session documentation failed integrity verification. The session file has been restored to
   > its pre-edit state. The full session protocol was saved to
   > `sessions/voice/protocols/<date>_S<N>_<slug>.md` and is preserved. Manual documentation review is
   > needed before the next session."
5. **Do not deliver a closing statement.** Session in error state — closing normally would be misleading.
6. `start-voice-training` orchestrator must note failure so agent is aware before next session that
   documentation for `S<N>` is incomplete.

### 6. Deliver Closing Statement

Tell client session is documented. Use client's language (DE/EN). Statement, not question. Door
closed warmly, no invitation to re-engage.

Template (DE):
> "[Name], ich habe die heutigen Notizen gespeichert. [Brief thematic acknowledgment — 1 sentence]. Bleib dran
> an deiner Übungsroutine — und gönn deiner Stimme Ruhe, wenn sie sie braucht. Ich bin da, wenn du
> weitermachen willst."

Template (EN):
> "[Name], I've saved today's session notes. [Brief thematic acknowledgment — 1 sentence]. Keep up your
> practice routine — and rest your voice when it needs it. I'm here whenever you'd like to continue."

After delivering, session is over. Do not add "How is your voice feeling now?" or any follow-up question.

## Validation

All checks run in Step 5b. Summarizes what was verified for traceability.

1. Trainer self-reflection completed (Step 1) — trainer reflection field populated in session note
2. YAML frontmatter intact, `sessions` incremented correctly, no spurious keys (Check 1)
3. Section structure in correct order: History header, recent notes, Permanent Client Profile, Session Log Archive
   (Check 2)
4. No section cross-contamination — session notes not inside Profile, Profile content not inside Session Log Archive
   (Check 3)
5. All 10 mandatory fields present in new session note and all recent session notes (Check 4)
6. Compressed session log entries have non-empty bodies (Check 5)
7. Permanent Client Profile untouched except for intentional Step 3 additions (Check 6)
8. Session count in frontmatter matches actual session entries in file (Check 7)
9. Full session protocol saved via `uv run session-protocol --session-kind voice`; filename format and speaker
   labels correct; protocol verified (start/end turns, no marker or tool text, verbatim spot checks,
   turn count) (Step 4)
10. Backup file deleted after successful verification (Step 5b-C)
11. Closing statement delivered as statement, not question; no coaching re-engagement after closing (Step 6)
12. If verification failed: session file restored from backup, failure reported to orchestrator, no closing
    statement delivered (Step 5b-R)

## Writing Rules

- Match client's language (DE/EN) from frontmatter `language` field
- Use standard German orthography (umlauts, ß) per CLAUDE.md
- All med-db access through `med-db` skill — never touch med-db/ files directly
- Session notes compact — training documentation, not narrative
- Permanent Client Profile never compressed
