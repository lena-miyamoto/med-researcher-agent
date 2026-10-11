# Frontmatter Fields (Claude Code & Copilot)

Reference for the YAML frontmatter each harness accepts on skill and agent files. The `.github/`
wrappers exist only to give Copilot a thin entry point; the `.claude/` files are the source of truth.

## Hard Rules

Value semantics for `model` and `effort` — what each alias resolves to per service, per-model
capabilities, and the allowed effort levels — live in `.claude/references/model-capabilities.md`.

1. **Description sync.** A wrapper's `description` must be byte-identical to its `.claude/` source
   `description`. Any drift is a finding.
2. **Copilot-specific frontmatter.** A wrapper carries only Copilot-valid fields. Claude-only fields
   (invocation control, execution context, effort, model-override for skills, argument hint, etc.) must
   never be copied into a wrapper.
3. **Tool parity.** An agent wrapper's `tools` list is the exact Copilot-alias mapping of the source
   `tools` list — no tool added, none dropped. Capabilities must be identical across harnesses.

## Surfaces

| Harness | Kind  | Path                             |
| ------- | ----- | -------------------------------- |
| Claude  | skill | `.claude/skills/<name>/SKILL.md` |
| Claude  | agent | `.claude/agents/<name>.md`       |
| Copilot | skill | `.github/skills/<name>/SKILL.md` |
| Copilot | agent | `.github/agents/<name>.agent.md` |

## Copilot skill wrapper

Follows the Agent Skills open standard. Accepted fields:

| Field           | Required | Notes                                                     |
| --------------- | -------- | --------------------------------------------------------- |
| `name`          | yes      | Lowercase letters/digits/hyphens; must match folder name. |
| `description`   | yes      | 1–1024 chars; WHAT it does and WHEN to use it.            |
| `license`       | no       | License name or bundled `LICENSE.txt` reference.          |
| `compatibility` | no       | Environment requirements note.                            |
| `metadata`      | no       | Free-form key/value pairs.                                |
| `allowed-tools` | no       | Space-delimited pre-approved tools (experimental).        |

No invocation-control or execution fields exist here. `disable-model-invocation`, `user-invocable`,
`model`, `effort`, `context`, `background`, and `argument-hint` are **Claude-only** and must not appear.
Every skill wrapper in this repo therefore carries only `name` and `description`.

## Copilot agent wrapper

Follows GitHub custom-agents format. Accepted fields:

| Field                      | Required | Notes                                                          |
| -------------------------- | -------- | -------------------------------------------------------------- |
| `name`                     | no       | Display name; falls back to filename without `.agent.md`.      |
| `description`              | yes      | Shown in the agent picker; drives delegation.                  |
| `target`                   | no       | `vscode` or `github-copilot`; unset = both.                    |
| `tools`                    | no       | List/string of tool aliases; unset = all tools.                |
| `model`                    | no       | Model ID; unset inherits default. Claude `inherit` → omit.     |
| `disable-model-invocation` | no       | `true` forces manual selection.                                |
| `user-invocable`           | no       | `false` hides from the picker (subagent-only). Default `true`. |
| `argument-hint`            | no       | Placeholder prompt text; IDE-only, ignored on cloud.           |
| `handoffs`                 | no       | Handoff configs to other agents; IDE-only.                     |
| `infer`                    | no       | Retired; superseded by the two fields above.                   |
| `mcp-servers`              | no       | Not used in VS Code / IDE custom agents.                       |
| `metadata`                 | no       | Not used in VS Code / IDE custom agents.                       |

Tool aliases are case-insensitive. A wrapper's `tools` list must be the exact alias translation of the
source `tools` — no tool added, none dropped (Hard Rule 3):

| Alias     | Maps to (Claude)                             |
| --------- | -------------------------------------------- |
| `execute` | `Bash`                                       |
| `read`    | `Read`, `NotebookRead`                       |
| `edit`    | `Edit`, `Write`, `MultiEdit`, `NotebookEdit` |
| `search`  | `Grep`, `Glob`                               |
| `agent`   | `Agent`, `Task`                              |
| `web`     | `WebSearch`, `WebFetch`                      |
| `todo`    | `TodoWrite`                                  |

## Claude Code skill

`.claude/skills/<name>/SKILL.md` — accepted fields: `name`, `description`, `when_to_use`,
`argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `model`, `effort`,
`allowed-tools`, `disallowed-tools`, `context`, `background`, `agent`, `paths`, `shell`, `hooks` (plus the
open-standard `license`, `compatibility`, `metadata`).

## Claude Code agent

`.claude/agents/<name>.md` — accepted fields: `name`, `description`, `tools`, `disallowedTools`,
`model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`. This repo also uses
`argument-hint` and `user-invocable` on agents.

## Claude-only fields (must not appear in a wrapper)

| Surface       | Claude-only fields forbidden in a wrapper                                                                                                                                                     |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Skill wrapper | `disable-model-invocation`, `user-invocable`, `model`, `effort`, `context`, `background`, `argument-hint`, `when_to_use`, `arguments`, `disallowed-tools`, `agent`, `paths`, `shell`, `hooks` |
| Agent wrapper | `context`, `background`, `effort`, `permissionMode`, `maxTurns`, `skills`, `hooks`, `disallowedTools`, `allowed-tools`                                                                        |

## Pointer-line convention

- Skill wrapper body opens with: ``Wrapper. Source of truth: `.claude/skills/<name>/SKILL.md`.``
- Agent wrapper body opens with a one-line role summary, then:
  ``Wrapper for `.claude/agents/<name>.md`. Harness differences: <what differs>.``

The wrapper body is a thin pointer; substantive workflow lives only in the `.claude/` source.

## Sources

- GitHub Docs — Custom agents configuration: <https://docs.github.com/en/copilot/reference/custom-agents-configuration>
- Claude Code Docs — Skills: <https://code.claude.com/docs/en/skills>
- Claude Code Docs — Subagents: <https://code.claude.com/docs/en/sub-agents>
