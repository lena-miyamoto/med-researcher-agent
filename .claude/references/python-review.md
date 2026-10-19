# Python Review Rules

Source of truth for Python review in `review-changeset` — rulebook for `.claude/scripts/**/*.py` and `tests/**/*.py`.

Repo floor: Python ≥3.12, ruff `line-length = 100`, `target-version = "py312"`, select = `E4`, `E7`, `E9`, `F`, `I`, `UP`, `B`, `SIM`, `N`, `C4`, `RUF`. Ruff enforces style, import order, modernization, bugbear, simplification — never re-derive by eye. Run it.

## Evidence Order

Always in this order; earlier evidence outranks later judgment.

1. Read the diff hunk **and** the full current file. Hunk alone hides the contract the change sits in.
2. Run `uv run lint <changed paths>`. Every violation is an **Error**, with ruff rule ID (`B006`, `RUF012`) and ruff's message. Never report a suspected lint issue from memory.
3. Run `uv run test <matching test files>`. Failing test is an **Error**, quoted. Changed behavior with no covering test is a **Warning** (coverage gap).
4. Only then apply the judgment rules below — they cover what the tools cannot see.

Both commands are allow-listed read-only checks. Never pass `--fix`; never run `uv run format`, `ruff format`, or any command that rewrites a source file. This skill stays text-only.

## Repo Contract Rules

Violation is an **Error** unless stated otherwise.

- `main()` returns an `int` exit code. `sys.exit()` inside `main()` or any library function is an Error; only `utils.run_cli(main)` under the `__main__` guard may raise `SystemExit`.
- Errors print to stderr, results to stdout. A traceback reaching the agent is an Error.
- All repo tooling runs through `uv run` from repo root. `python3 -c`, `python path/script.py`, absolute interpreter paths, shebang execution are Errors.
- New script wired in **both** `[project.scripts]` (`pyproject.toml`) and `entrypoints.py`. Missing either is an Error.
- Script basenames hyphenated (`med-db-query.py`); test module names use underscores (`test_med_db_query.py`). Both loaded through `importlib` — `entrypoints.py` and `tests/conftest.py` respectively.
- Text/JSON API fetches go through the `utils` fetch helpers — `fetch_text`, `fetch_pubmed`, `fetch_europe_pmc`, `fetch_crossref_work` (all wrappers over `_fetch_url`). A script hand-rolling `urllib`/`requests` for an API/text fetch is an Error. Binary PDF download is the sanctioned exception: `med-db-download-paper.py` builds `urllib.request.Request` directly in `download_binary` and `fetch_publisher_pdf`, both routed through `utils._request_with_retry`.
- Integrity findings use `utils` severity (`SEVERITY_ERROR`, `SEVERITY_WARNING`) and category (`CATEGORY_*`) constants plus the `finding` model. Inline string severity is a Warning.
- Machine-parseable output: read-only and archival scripts emit JSON to stdout (`json.dumps`/`json.dump`) — there is no `--format` flag in this repo. `med-db`, `med-db-lookup`, `med-db-query`, the `med-db-term-*` family, `check-retraction`, and `csv-util` all follow it. A new script in that class emitting only human prose is a Warning.
- Line length 100, enforced by ruff. Do not restate it as a finding.

## Correctness Rules

**Error** — wrong behavior, data loss, or security exposure:

- Mutable default argument (`def f(x=[])`) — ruff `B006` supplies the message.
- Bare `except:` or bare `except Exception` that swallows (`pass`, no re-raise, no log).
- Re-raise without `raise ... from` — ruff `B904`.
- Untrusted input reaching `eval`, `exec`, `pickle.loads`, `yaml.load` without `SafeLoader`, or `subprocess` with `shell=True`. This repo fetches HTML and PDFs from the open web, so fetched bytes are untrusted by definition.
- Regex with nested quantifiers over unbounded fetched HTML (catastrophic backtracking / ReDoS).
- Resource leak: file, socket, or subprocess opened without `with` or explicit close.
- Docstring or comment claiming behavior the code does not implement. Where the claim is a contract, the mismatch is an Error, not a nit — check every new comment against the code it describes.
- Silent fallback that hides a real failure — broad `except` returning a default, heuristic reverting without a trace.
- `== None`, `is` on strings or numbers, `type(x) == T` in place of `isinstance`.
- Off-by-one in slices, ranges, loop bounds; mutating a list while iterating it.
- Shadowing a builtin (`id`, `type`, `input`, `list`). Builtin-shadowing rules (`A001`, `A002`) are **not** enabled here, so this one is manual.

**Warning** — cost, maintainability, or hidden state:

- Work proportional to archive size: regex recompiled inside a loop or per item, quadratic string building, repeated full-file reads.
- Mutable module-level state instead of a returned or passed value.
- Duplicated logic a helper in `utils.py` already provides.
- Returning `None` for failure where an exception or described result value would be clearer.
- Nesting deeper than 3 levels where an early return flattens it.

## Modern Python (3.12) Rules

- `X | None` over `Optional[X]`; builtin generics (`list[str]`, `dict[str, int]`) over `typing.List`/`Dict`; `collections.abc` (`Iterable`, `Callable`, `Sequence`) over the `typing` equivalents. Ruff `UP` enforces most of this — quote its output instead of restating the rule.
- `pathlib.Path` over `os.path`. `os` acceptable only where `Path` has no equivalent, as with `os.path.lexists` in `utils.py` (it inspects the link itself, not the target).
- f-strings over `%` and `.str.format()`; `str.removeprefix`/`removesuffix` over slicing; `zip(..., strict=True)`; `enumerate` over a manual index counter.
- Timezone-aware datetimes for anything persisted or user-visible: `datetime.UTC`. Not `datetime.utcnow()`, and not `timezone.utc` — the alias is the 3.12 form.
- `@dataclass(frozen=True, slots=True)` for value objects. Mutable class attribute left unannotated is ruff `RUF012`.
- This repo is synchronous. Introducing `asyncio` or `async def` into a sync script or CLI path is a Warning — flag it, do not assume it is an upgrade.
- `from __future__ import annotations` unnecessary on 3.12 and absent repo-wide. Adding it is **Info**.
- New third-party dependency for something the stdlib already does is a Warning.

## Test Rules (pytest)

- Tests live in `tests/`, named `test_<module>.py`, one file per script module.
- One behavior per test; the name states the behavior. `test_1`, `test_works`, and names carrying no expectation are a Warning.
- `@pytest.mark.parametrize` over copy-pasted near-identical tests; pass `ids=` for readable names. Parametrizing unrelated behaviors is a Warning.
- Fixtures default to function scope. A session-scoped fixture holding mutable state makes test order a hidden input — Warning.
- `yield` fixtures for teardown, asserting the teardown ran where it matters.
- Mock the boundary (network, clock, third-party, module-level I/O), not repo-owned code. Mock assertions must be signature-safe (`autospec=True`) — a typo'd mock assertion passes silently.
- Patch where the name is **looked up**, not where it is defined. Patching the wrong target is an Error: the test passes without exercising the code.
- Prefer a real object (`tmp_path`, a local fake) over mocking a repo-owned function.
- A bug fix without a regression test that fails before and passes after is an Error — this repo's bug-diagnosis contract runs through the test harness.
- A regression test asserting on resolved, extracted, or post-processed output is only as strong as the last stage that can undo the guard. Before calling a test sound, name the masker that would keep it green with the guard deleted. Known maskers in this repo:
  - `_strip_html` (utils.py) — the general `<[^>]+>` tag removal plus `_html.unescape` strips *every* tag, so a test asserting "no `<script>`/`<iframe>` content" passes whether or not a tag-specific guard exists.
  - `extract_pdf_text` (med-db-download-paper.py) — `page.extract_text() or ""` per page and the trailing `.strip()` drop empty-page text, so a guard that filtered content on a page whose `extract_text()` already returns empty is masked; the final `raise ValueError` only fires when *all* pages are empty.
  - `slugify(..., fallback=...)` (utils.py) — empty or symbol-only input collapses to the fallback slug, so a test on slug output passes via the fallback even when the real slugging logic is broken.
  - `resolve_metadata` / `metadata_from_doi` (med-db-download-paper.py) — each source's `except (RuntimeError, json.JSONDecodeError, KeyError, IndexError)` falls through to the next source (PubMed → Crossref → Europe PMC, or title search), so a test asserting metadata provenance/fields can pass via the fallback source when the primary source's guard is removed.
  - `fetch_text` 404 handling (utils.py) — with `not_found_message` set, a 404 raises `LookupError` rather than the underlying error, so a "not found" test can pass through that branch without exercising the guard under test.
- A fix for a "cannot fail" test names its mutation: the exact branch whose removal makes the test fail, and the fixture change that defeats every masker on the path. Say which masker applies. A proposed fixture that still passes under its own mutation is not a fix — rework it, do not hand it off. `apply-fixes` performs the mutation and reports a fixture that cannot be made to fail.
- Ban: `assert True`, `time.sleep` for synchronization, dependence on execution order or on another test's side effects, assertions on private attributes or on message wording that is not a documented contract.
- Tests must not require network access.

## Severity Mapping

- **Error** — wrong behavior, contract violation, security exposure, failing lint or test, a test that cannot fail — including one that stays green only because a fallback, a later conversion stage, or a nesting/adjacency effect restores or keeps the guarded text.
- **Warning** — cost at archive scale, coverage gap, idiom deviation with no stated reason, maintainability.
- **Info** — style preference, unnecessary import, a note with no action required.

## Valid Patterns — Do NOT Flag

Every entry below is an accepted repo pattern; flagging it is a false positive.

- **Missing type annotations.** `.claude/scripts` and `tests` are unannotated and `ANN` is not in the ruff select list. Report an annotation finding only inside a module that already annotates, and only where the annotation is wrong or inconsistent with the ones around it.
- **`print()` to stdout or stderr.** That is the CLI contract, not a debugging leftover. `logging` is not this repo's idiom for CLI output.
- **`_strip_html` regex-based tag stripping.** The conversion is documented as a deterministic pure-Python strip. Recommending `BeautifulSoup`, `lxml`, or `HTMLParser` is out of scope unless the change introduces a correctness bug in the existing approach.
- **`os` calls with no `pathlib` equivalent**, including `os.path.lexists`.
- **`urllib.parse` for URL building** — `quote`, `urlencode`, `urljoin`. Established in `utils.py` (`fetch_pubmed`, `fetch_europe_pmc`, `fetch_crossref_work`) and `med-db-download-paper.py` (`fetch_scihub_pdf_url`). The `urllib` Error targets hand-rolled *fetching* for text/JSON (`urlopen`, `requests`) — not URL string assembly, and not the sanctioned binary-PDF downloaders.
- **Heavy `monkeypatch`/`unittest.mock` use in tests.** Boundary mocking is the repo's strategy, including at module level. Judge *what* is patched, not how much.
- **Leading-underscore helpers and module-private names.**
- **Documented guards and fallbacks** — for example `extract_pdf_text` raising `ValueError` when a PDF yields no text, `slugify`'s `fallback` parameter, `fetch_text`'s 404 → `LookupError` branch. A safety net with a comment is not dead code.
- **Anything ruff already checks and the diff passes.**
- **`# noqa: <rule>`** carrying a reason.
- **`if TYPE_CHECKING:` imports**, `__all__`, and `__main__` guards.

## Sources

- Ruff — linter and rule selection: <https://docs.astral.sh/ruff/linter/>
- Ruff 0.16 default rule expansion: <https://pydevtools.com/blog/ruff-0-16-0-default-rules/>
- PEP 8 — Style Guide for Python Code: <https://peps.python.org/pep-0008/>
- Python 3.12 release notes (PEP 695, `type` statement): <https://docs.python.org/3.12/whatsnew/3.12.html>
- pytest — good integration practices: <https://docs.pytest.org/en/stable/explanation/goodpractices.html>
- pytest — monkeypatch reference: <https://docs.pytest.org/en/stable/how-to/monkeypatch.html>
- pytest patterns for maintainable tests (2026): <https://dev.to/datanestdigital/pytest-patterns-that-make-tests-actually-maintainable-2026-5heo>
- Mock boundary discipline and `autospec` guidance: <https://github.com/ludo-technologies/python-best-practices/commit/73634efa99daa01a8f2956f361d01312c3e7a06f>
- Python code review checklist: <https://pullpanda.io/blog/python-code-review-checklist>
- Modern Python 3.12+ patterns: <https://github.com/ofershap/python-best-practices>
