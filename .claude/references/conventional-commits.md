# Conventional Commits

Source of truth for commit message format. Spec: Conventional Commits v1.0.0 —
<https://www.conventionalcommits.org/en/v1.0.0/#specification>.

Read on demand — before composing a commit message, not at session start.

## Structure

```text
<type>[(scope)][!]: <description>

[optional body]

[optional footer(s)]
```

- `type` and `description` mandatory; `scope` optional.
- Body and each footer separated from previous part by one blank line.

## Rules

- `scope` is a noun in parentheses naming affected section, e.g. `feat(med-db):`.
- `type` is a noun: `feat`, `fix`, or any other permitted type (`docs`, `refactor`, `chore`, `test`,
  `ci`, `perf`, `build`).
- Breaking change: `!` before the `:`, or `BREAKING CHANGE: <explanation>` footer. `BREAKING CHANGE`
  stays uppercase; `BREAKING-CHANGE` is equivalent as footer token.
- Footer token: `Token: value` or `Token #value`. Tokens replace whitespace with `-` (e.g. `Acked-by`).

## Examples

```text
feat(med-db): add --stats query
fix: correct ICD-11 lookup for degenerate codes
docs: document source-of-truth ownership

BREAKING CHANGE: drop the med-db-validate entry point
```
