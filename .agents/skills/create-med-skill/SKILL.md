---
name: create-med-skill
description: >
             Create a new shared repo skill for this workspace, with the source of truth in .agents/skills and thin
             .github/.claude wrappers. Use when adding a new skill that must work cleanly in both Copilot and Claude.
argument-hint: >
               Provide the new skill name and what it should do; include description keywords, optional argument hint,
               and any routing or doc updates needed
user-invocable: true
---

# Create Med Skill

## When to Use

- User wants to add a skill available through both Copilot and Claude.
- Follow the architecture in `CLAUDE.md`: shared procedure in `.agents/skills/`, thin wrappers in `.github/skills/` and
  `.claude/skills/`.
- If the request is an agent, not a skill, stop and route to `create-med-agent`.

## Procedure

1. Clarify contract: lowercase kebab-case name, what it does and when to use, discovery description, optional argument
   hint, `user-invocable` value.
2. Write the shared source of truth at `.agents/skills/<name>/SKILL.md`:
   - Frontmatter `name` matches folder; `description` is keyword-rich.
   - Body is self-contained. Use sections: `When to Use`, `Procedure`, `Writing Rules` (when needed), `Validation`,
     `Output`.
   - Don't restate the multi-agent architecture — `CLAUDE.md` covers that. Don't repeat "this skill does not duplicate"
     — it's implicit in the repo pattern.
3. Write the Copilot wrapper at `.github/skills/<name>/SKILL.md`: mirror discovery frontmatter, point body at the shared
file.
4. Write the Claude wrapper at `.claude/skills/<name>/SKILL.md`: same as Copilot wrapper.
5. Never duplicate procedure across `.agents`, `.github`, `.claude`. Wrappers only discover and redirect.
6. Reuse repo tooling: `.agents/scripts/` and the `med-db/` workflow. Keep medical-research workflow in `CLAUDE.md` and
the `med-researcher` agents, not in generic skills.
7. Update `README.md` only if the skill should be advertised. Update `CLAUDE.md` or `.github/copilot-instructions.md`
only when routing boundaries change.

## Writing Rules

- ASCII unless the file already needs non-ASCII.
- Descriptions concrete and keyword-rich.
- Direct, procedural tone. No padding.
- Single source of truth: `.agents/skills/<name>/SKILL.md`.

## Validation

1. All three files exist: `.agents/`, `.github/`, `.claude/` `skills/<name>/SKILL.md`.
2. Frontmatter parses in each.
3. Shared file holds the procedure; wrappers do not duplicate it.
4. Wrapper bodies cite the shared file path exactly.
5. Run `uv run lint-md` on every changed file; diagnostics must be clean.
6. Repo doc references match created paths.

## Output

- Files created or updated.
- Repo doc or routing changes, if any.
- Unresolved decisions left to the user.
