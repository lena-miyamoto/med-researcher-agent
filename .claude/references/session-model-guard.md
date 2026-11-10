# Session Model Guard

Run first, before any other tool call. Shared by `start-therapy-session` and `start-voice-training`. Fail →
abort before any session action.

## 1. Model

System prompt names the model: `You are powered by the model <id>`. Accept only:

- `deepseek-v4-pro`
- `claude-opus-5-5`
- `claude-fable-5-2`
- `claude-fable-5-1`

Each optionally suffixed `[1m]`. Reject everything else — `deepseek-flash`, `claude-sonnet-5-5`,
`claude-haiku-5-5`, any id containing `-flash`, `sonnet`, or `haiku`. Model line missing → fail; unverifiable
is not a pass.

## 2. Effort Probe

Two exact, attributable, allowlisted calls:

- `printenv CLAUDE_EFFORT` — the running level.
- `printenv CLAUDE_CODE_EFFORT_LEVEL` — the override. Exit 1 with no output means unset.

## 3. `auto` / `unset` Override

`CLAUDE_CODE_EFFORT_LEVEL` equal to `auto` or `unset` → fail for any Anthropic id: either value suppresses the
skill's `effort: high`, so the session runs at the API default and is unverifiable. On `deepseek-v4-pro`
(suffix stripped per §1) → accept: no effort parameter is sent, so DeepSeek's default `high` applies (see
`model-capabilities.md`).

## 4. Accept Rules

- Accept `high`, `xhigh`, `max`.
- Accept `medium` when the model is `deepseek-v4-pro` (strip an optional `[1m]` suffix before comparing) —
  DeepSeek maps `medium`, `high`, `xhigh` to the same request.
- Reject `medium` for any Anthropic id — `medium < high`.
- Reject `low`.
- `CLAUDE_CODE_EFFORT_LEVEL` set to a level → it wins and governs the check; otherwise judge `CLAUDE_EFFORT`.
- Both probes unset → unverifiable: unset `CLAUDE_EFFORT` can also mean the active model does not support the
  effort parameter, so it does not prove the `effort: high` frontmatter applied. Unverifiable is not a pass.

## Failure Path

Abort immediately: no intake, no history file read or create, no question, no touch of the session directory
(`sessions/` for therapy, `sessions/voice/` for voice training). Name the failed check, show the observed
value.

- **Model check failed** → tell the client to run `/model opus` (resolves to `deepseek-v4-pro` on DeepSeek
  wiring, `claude-opus-5-5` on Anthropic), then re-invoke the skill. If `/model opus` does not resolve to an
  accepted id (provider pin or org `availableModels` allowlist), report that limitation instead of looping the
  same remediation.
- **Effort check failed, `CLAUDE_CODE_EFFORT_LEVEL` set** (any value, including `auto` / `unset`) → tell the
  client to remove or unset it in the shell or in settings, then restart the session. Do not loop `/effort high`
  while the env var is set.
- **Effort check failed, `CLAUDE_CODE_EFFORT_LEVEL` unset** → tell the client to run `/effort high`, then
  re-invoke the skill.

Alias and effort rules: `.claude/references/model-capabilities.md`; `/effort`:
<https://code.claude.com/docs/en/model-config>.
