# Model Aliases, Capabilities, and Effort

Source of truth for the `model` and `effort` frontmatter fields in `.claude/` skills and agents.

The harness reads `model` / `effort` at runtime, and what an alias resolves to depends on the
**service the session is pointed at**, not on the alias name. A session pointed at Anthropic's API
resolves `haiku` / `sonnet` to the Claude models of those names; one pointed at the DeepSeek
Anthropic-compatible endpoint resolves them to DeepSeek models. Never assume an alias means the
Claude model of its name — check the session's wiring.

This repo is **optimized** for the DeepSeek endpoint (the maintainer's default wiring), not bound to
it: Anthropic models are fully supported, and GitHub Copilot is supported best-effort. A rule below
that holds only under the DeepSeek wiring is labeled as such and never asserts that every session
runs on DeepSeek. This doc records the alias pins, what each resolved model is good at, and which
`(model, effort)` pair fits which task.

## Hard Rules

1. **Aliases are service-relative.** `model: haiku` resolves to whatever
   `ANTHROPIC_DEFAULT_HAIKU_MODEL` points at. Under this repo's default DeepSeek wiring that is
   `deepseek-flash`; under Anthropic wiring it is `claude-haiku-5-5`. Never judge a `model` value
   by the Claude model of the same alias name — resolve it against the session's service.
2. **`effort` levels collapse on DeepSeek.** The Claude Code scale is `low` / `medium` / `high` /
   `xhigh` / `max`, but the DeepSeek endpoint maps `medium`, `high`, and `xhigh` all to the same
   `high` level. Only `low` and `max` change behavior there. Do not treat `xhigh` as "more than
   `high`" unless the service is Anthropic.
3. **Effort is calibrated per model.** The same level name is not the same reasoning budget across
   models. A change that is right on one service may be a no-op or an overthink on the other.
4. **Available tiers depend on the service.** Under the DeepSeek wiring `haiku`/`sonnet` are the
   only practical tiers — `opus` resolves to the same model as `sonnet` and adds nothing. Under
   Anthropic wiring `opus` and `fable` are distinct, stronger tiers. On either service use `haiku`
   for cheap/mechanical work and a reasoning tier (`sonnet` or above) for reasoning-heavy work.
5. **`inherit` means the session model.** Agents that should follow the caller use `model: inherit`
   (this is what every agent in `.claude/agents/` does).

## Alias Resolution

| Alias     | Anthropic service   | DeepSeek wiring (repo default)         | Pinned by                        |
| --------- | ------------------- | -------------------------------------- | -------------------------------- |
| `haiku`   | `claude-haiku-5-5`  | `deepseek-flash` (DeepSeek-V4.1-Flash) | `ANTHROPIC_DEFAULT_HAIKU_MODEL`  |
| `sonnet`  | `claude-sonnet-5-5` | `deepseek-v4-pro` (DeepSeek V4 Pro)    | `ANTHROPIC_DEFAULT_SONNET_MODEL` |
| `opus`    | `claude-opus-5-5`   | `deepseek-v4-pro` (same as `sonnet`)   | `ANTHROPIC_DEFAULT_OPUS_MODEL`   |
| `fable`   | `claude-fable-5-1`  | `deepseek-v4-pro` (same as `sonnet`)   | `ANTHROPIC_DEFAULT_FABLE_MODEL`  |
| `inherit` | session model       | session model                          | —                                |
| full ID   | pinned snapshot     | pinned snapshot                        | —                                |

**Default session wiring** — machine-level, in `~/.claude/settings.json`. This is how the
maintainer's sessions are configured, not a repo guarantee; a session pointed elsewhere resolves the
aliases differently:

- `ANTHROPIC_BASE_URL = https://api.deepseek.com/anthropic` — the DeepSeek endpoint.
- `ANTHROPIC_DEFAULT_MODEL = sonnet` — new sessions start on `sonnet`.

Everything labeled "DeepSeek wiring" below describes this default setup. On a session pointed at
Anthropic, use the Anthropic column instead.

Notes on the other aliases: `default` clears an override and reverts to the account default;
`best` resolves to `fable` where available, else `opus`; `opusplan` runs `opus` in Plan Mode and
`sonnet` otherwise. A full ID such as `claude-sonnet-5-5` or `deepseek-v4-pro` pins an exact
snapshot and bypasses the alias pins above.

**Wiring divergence (DeepSeek wiring only):** DeepSeek's own Claude Code guide recommends mapping
both `claude-haiku` and `claude-sonnet` to `deepseek-flash` and `claude-opus` to `deepseek-v4-pro`.
The default wiring here instead pins `sonnet` to `deepseek-v4-pro`, so under it `sonnet` is a real
step up from `haiku` (Pro vs Flash) while `opus` is a no-op. None of this applies to an Anthropic
session, and the DeepSeek guide's default mapping should not be assumed either.

## Model Profiles

Profiles are listed per model, not per alias. Each heading names the alias that resolves to that
model under the DeepSeek wiring.

### DeepSeek-V4.1-Flash (`deepseek-flash`, alias `haiku`)

- ~552B-parameter MoE with ~8B active at prefill and ~16B at decode plus a ~196B conditional
  "Engram" memory; natively multimodal (text + image in); MIT-licensed.
- 1M-token context, up to ~384K output. Cheap and fast.
- Strong for its class on agentic/coding tasks (Terminal-Bench 2.1 ≈ 90.6, DeepSWE v1.1 ≈ 74.2).
- **Weakness:** at `max` effort it is prone to long, low-density reasoning and can keep re-arguing
  settled points rather than converging.
- **Use for:** high-volume mechanical work — extraction, text conversion, transcription, archive
  queries, and parallel subagent fan-out where per-item cost and latency dominate.

### DeepSeek V4 Pro (`deepseek-v4-pro`, aliases `sonnet` and `opus`)

- Large MoE (~49B active parameters; the HF card lists ~1.7T total). 1M-token context, up to ~384K
  output. Text-first (image input reported for the GA release). Strongest DeepSeek tier.
- Large gains over the Flash tier on agentic/coding and hard reasoning (Terminal-Bench 2.1 ≈ 87.9,
  DeepSWE ≈ 62.7, HLE ≈ 60.0 with tools).
- **Weakness:** verbose; `max` effort over-reasons and can balloon token spend for marginal gain.
- **Use for:** long-horizon agentic work, multi-source synthesis, hard reasoning, anything where a
  wrong answer costs more than the extra tokens.

### Claude Haiku 5.5 (`claude-haiku-5-5`, Anthropic-side `haiku`)

- Anthropic's fastest/cheapest model; 1M-token context, 128K output; $0.10/$0.50 per MTok for
  prompts up to 100K tokens, $0.50/$2.50 above that. Default effort `medium`.
- Best for narrow, high-volume, checkable work: classification, extraction, routing, summarisation,
  per-turn subagent work.

### Claude Sonnet 5.5 (`claude-sonnet-5-5`, Anthropic-side `sonnet`)

- Anthropic's "best combination of speed and intelligence"; 1M-token context, 128K output; $2/$10
  per MTok. Default effort `high`.
- Best for long-horizon agentic work, computer use, code that must compile, and other unverifiable
  tasks where a wrong answer costs more than the call.

Opus 5.5 (`claude-opus-5-5`, $4/$20) and Fable 5.1 (`claude-fable-5-1`, $10/$50) sit above Sonnet on
the Anthropic side. On Anthropic wiring the `opus` and `fable` aliases reach these models; under the
DeepSeek wiring both resolve to `deepseek-v4-pro` (the same model as `sonnet`), so neither reaches
its Claude namesake.

## Effort Semantics

Claude Code accepts `low`, `medium`, `high`, `xhigh`, and `max`. On the Anthropic models every level
is distinct. On the DeepSeek endpoint the scale collapses:

| Claude Code `effort` | DeepSeek `reasoning_effort` |
| -------------------- | --------------------------- |
| `low`                | `low`                       |
| `medium`             | `high`                      |
| `high`               | `high`                      |
| `xhigh`              | `high`                      |
| `max`                | `max`                       |

Consequences under the DeepSeek wiring:

- `medium`, `high`, and `xhigh` are **the same request** on DeepSeek. Picking `xhigh` over `high`
  changes nothing, and picking `medium` over `high` does not lower cost — it is still `high`.
- Only `low` and `max` are meaningfully different from `high`.
- DeepSeek's default is `high`, so omitting `effort` is equivalent to `medium`/`high`/`xhigh`.
- `max` is the only level above `high`. Use it for genuinely hard problems and expect overthinking on
  Flash; prefer `high` unless a task demonstrably needs `max`.

General effort guidance (holds on both services):

- `low` — mechanical, checkable steps: renames, formatting, extraction, yes/no checks.
- `high` — normal agentic work where verification matters: multi-step procedures, fixes, reviews.
- `max` — hard problems worked through autonomously (deep analysis, security-style audits). Test
  before adopting broadly; diminishing returns and overthinking are real.

Precedence: `CLAUDE_CODE_EFFORT_LEVEL` and `--effort` override a file's `effort` frontmatter, and a
skill's frontmatter overrides the session level but **not** the environment variable.

## Selection Guide

Pick the cheapest tier that reliably does the task at `high` effort; reserve `max` and `sonnet` for
work that fails at the cheaper setting. The aliases below resolve on either service, and the tier
ordering (`haiku` < `sonnet`) holds on both.

| Task class                                                                          | Model    | Effort         | Rationale                                                                |
| ----------------------------------------------------------------------------------- | -------- | -------------- | ------------------------------------------------------------------------ |
| Extraction, conversion, transcription, archive queries                              | `haiku`  | `low` / `high` | Mechanical and checkable; `low` for clean text, `high` for messy parsing |
| Summaries, fetch/archive, review, apply-fixes                                       | `haiku`  | `high`         | Multi-step but bounded; verification catches slips                       |
| Synthesis, definitions, therapy/voice sessions, plan generation, repo optimization  | `sonnet` | `high`         | Reasoning-heavy; weak answers are costly to detect                       |
| Hardest long-horizon reasoning or adversarial analysis                              | `sonnet` | `max`          | Only when `high` demonstrably falls short                                |

Under the DeepSeek wiring do not set `opus` (same model as `sonnet` there) and do not rely on `xhigh`
or `medium` to differentiate from `high`; on Anthropic those levels are distinct. Agents that should
follow whatever model the caller uses keep `model: inherit`.

## Sources

- DeepSeek — Integrate with Claude Code: <https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code/>
- DeepSeek — Thinking Mode (effort mapping): <https://api-docs.deepseek.com/guides/thinking_mode/>
- DeepSeek-V4.1-Flash model card: <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash>
- DeepSeek-V4-Pro-0813 model card: <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813>
- Anthropic — Models overview: <https://platform.claude.com/docs/en/models/overview>
- Claude Code — Model configuration (aliases, effort levels, precedence): <https://code.claude.com/docs/en/model-config>
