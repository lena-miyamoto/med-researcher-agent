---
description: >
  Repo-wide Python coding style rules — naming (no abbreviations) and functional programming by default.
  Read before writing or editing any Python file in this repo. Applies to .claude/scripts/ and any other
  Python code in the repository.
---

# Coding Style

## Naming — no cryptic abbreviations

Names must be self-explanatory. **No abbreviations** — spell out in full.

**Allowed exceptions (only these two):**

- `i` (or `index`) for the index variable in loops
- `tmp` or `temp` for a temporary value scoped to a single short block (≤ 10 lines)

All else must be spelled out: `entry` not `e`, `disorder` not `d`, `category` not `cat`,
`record_id` not `rid`, `column_map` not `col_map`, `file_handle` not `fh`, `keyword_search` not `ks`,
`code_lookup` not `cl`, `relative_path` not `rel`, `abstract_lines` not `ab_lines`, etc.

Universally understood domain acronyms (PMID, DOI, ICD, DSM, PMC) may be used as-is.

## Functional programming by default

Stick to functional programming: pure functions, immutable data, composing smaller functions
over mutation and shared state.

**Classes only when you can articulate a concrete reason why they are necessary.**
Not valid: "feels cleaner," "organizes the code," "would be nice." Valid: state machines
benefiting from encapsulation, resource managers where `__enter__`/`__exit__` is the ergonomic API,
framework integration requiring classes.

Unit tests are the explicit exception — test frameworks (pytest, unittest) require classes for grouping.
Framework mandate, not design choice.

When in doubt: use a module with functions, not a class.

## No backwards-compat shims

Scripts do not have versions — they only exist in their current form. The agent has no memory
of previous CLI interfaces. Never add:

- Deprecated aliases for renamed flags (e.g., `--json` alongside `--format json`)
- Deprecation warnings printed to stderr
- `[DEPRECATED]` markers in help text
- Shims that translate old flag names to new ones

If a flag name is wrong, change it. If an interface needs improvement, improve it. The old
form simply ceases to exist. No transitional period, no compatibility layer, no dead code.
