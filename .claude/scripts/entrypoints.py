import importlib.util
import subprocess
import sys
from pathlib import Path

import utils

SCRIPTS_DIR = Path(__file__).resolve().parent


def _load_script(module_name: str, filename: str):
    script_path = SCRIPTS_DIR / filename
    if not script_path.is_file():
        raise FileNotFoundError(f"missing script entrypoint target: {script_path}")

    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load script spec for {script_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def med_db():
    return _load_script("med_db", "med-db.py").main()


def med_db_lookup():
    return _load_script("med_db_lookup", "med-db-lookup.py").main()


def med_db_query():
    return _load_script("med_db_query", "med-db-query.py").main()


def med_db_lookup_icd11():
    return _load_script("med_db_lookup_icd11", "med-db-lookup-icd11.py").main()


def med_db_lookup_dsm5():
    return _load_script("med_db_lookup_dsm5", "med-db-lookup-dsm5.py").main()


def med_db_download_icd11():
    return _load_script("med_db_download_icd11", "med-db-download-icd11.py").main()


def med_db_download_paper():
    return _load_script("med_db_download_paper", "med-db-download-paper.py").main()


def med_db_setup_dsm5():
    return _load_script("med_db_setup_dsm5", "med-db-setup-dsm5.py").main()


def med_db_setup_therapy_methods():
    return _load_script("med_db_setup_therapy_methods", "med-db-setup-therapy-methods.py").main()


def med_db_integrity_check():
    return _load_script("med_db_integrity_check", "med-db-integrity-check.py").main()


def med_db_term():
    return _load_script("med_db_term", "med-db-term.py").main()


def med_db_term_lookup():
    return _load_script("med_db_term_lookup", "med-db-term-lookup.py").main()


def med_db_term_wikipedia():
    return _load_script("med_db_term_wikipedia", "med-db-term-wikipedia.py").main()


def med_db_term_mesh():
    return _load_script("med_db_term_mesh", "med-db-term-mesh.py").main()


def check_retraction():
    return _load_script("check_retraction", "check-retraction.py").main()


def csv_util():
    return _load_script("csv_util", "csv-util.py").main()


def session_protocol():
    return _load_script("session_protocol", "session-protocol.py").main()


def fetch_archive():
    return _load_script("fetch_archive", "fetch-archive.py").main()


def lint_md(args=None):
    """Run rumdl on repo markdown files.

    Delegates to utils.lint_source_md when --check-source-md or
    --fix-source-md is passed.  Otherwise scans AGENTS.md, README.md,
    CLAUDE.md, .github, and .claude by default.  Pass --fix to auto-fix
    violations.  rumdl reads its rule set from .rumdl.toml.
    """
    if args is None:
        args = sys.argv[1:]
    args = list(args)

    source_md_result = utils.lint_source_md(args)
    if source_md_result != -1:
        return source_md_result

    fix_mode = False
    if "--fix" in args:
        fix_mode = True
        args = [a for a in args if a != "--fix"]

    if not args:
        repo_root = Path(__file__).resolve().parent.parent.parent
        args = [
            str(repo_root / "AGENTS.md"),
            str(repo_root / "README.md"),
            str(repo_root / "CLAUDE.md"),
            str(repo_root / ".github"),
            str(repo_root / ".claude"),
        ]

    if fix_mode:
        subprocess.run(["rumdl", "fmt", *args], check=False)

    # Always check afterward so remaining violations are visible even when
    # --fix rewrote files: `check` reports them and sets the exit code.
    return subprocess.run(["rumdl", "check", *args], check=False).returncode


def test(args=None):
    """Run pytest on the test suite. Passes ``tests/ -v`` by default."""
    try:
        from pytest import main as pytest_main
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pytest is not installed; run 'uv sync' to install the dev dependencies"
        ) from exc

    if args is None:
        args = sys.argv[1:] or ["tests/", "-v"]
    return pytest_main(args)


def lint():
    """Run ruff check and ruff format --check on repo Python code.

    Targets .claude/scripts and tests by default.  Pass --fix to apply
    safe autofixes before checking, or pass explicit paths to override
    the defaults.
    """
    args = list(sys.argv[1:])
    fix_mode = "--fix" in args
    if fix_mode:
        args = [a for a in args if a != "--fix"]

    targets = [a for a in args if not a.startswith("-")] or [".claude/scripts", "tests"]

    if fix_mode:
        subprocess.run(["ruff", "check", "--fix", *targets], check=False)

    status = 0
    status |= subprocess.run(["ruff", "check", *targets], check=False).returncode
    status |= subprocess.run(["ruff", "format", "--check", *targets], check=False).returncode
    return status


def format():
    """Format repo Python code with ruff format.

    Targets .claude/scripts and tests by default; pass paths to override.
    """
    args = sys.argv[1:]
    flags = [a for a in args if a.startswith("-")]
    targets = [a for a in args if not a.startswith("-")] or [".claude/scripts", "tests"]
    return subprocess.run(["ruff", "format", *flags, *targets], check=False).returncode
