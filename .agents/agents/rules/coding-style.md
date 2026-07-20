---
description: >
  Repo-wide Python coding style rules — naming (no abbreviations) and functional programming by default.
  Read before writing or editing any Python file in this repo. Applies to .agents/scripts/ and any other
  Python code in the repository.
---

# Coding Style

## Naming — no cryptic abbreviations

Variable, function, and parameter names must be self-explanatory. **No abbreviations** — spell words out in full.

**Allowed exceptions (only these two):**

- `i` (or `index`) for the index variable in loops
- `tmp` or `temp` for a temporary value scoped to a single short block (≤ 10 lines)

Everything else must be written out: `entry` not `e`, `disorder` not `d`, `category` not `cat`,
`record_id` not `rid`, `column_map` not `col_map`, `file_handle` not `fh`, `keyword_search` not `ks`,
`code_lookup` not `cl`, `relative_path` not `rel`, `abstract_lines` not `ab_lines`, etc.

Domain terms that are universally understood acronyms in the field (PMID, DOI, ICD, DSM, PMC) may be
used as-is.

## Functional programming by default

Stick to functional programming. Prefer pure functions, immutable data, and composing smaller functions
over mutation and shared state.

**Classes only when you can articulate a concrete reason why they are necessary.**
"Feels cleaner," "organizes the code," or "would be nice" are not valid justifications. Valid reasons:
state machines that truly benefit from encapsulation, resource managers where `__enter__`/`__exit__`
are the ergonomic API, or integration with a framework that requires classes.

Unit tests are the explicit exception — test frameworks (pytest, unittest) require classes for test
grouping. That is a framework mandate, not a design choice.

When in doubt: use a module with functions, not a class.
