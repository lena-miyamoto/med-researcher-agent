import importlib.util
import sys
from pathlib import Path


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


def med_db_validate():
    return _load_script("med_db_validate", "med-db-validate.py").main()


def med_db_lookup():
    return _load_script("med_db_lookup", "med-db-lookup.py").main()


def med_db_query():
    return _load_script("med_db_query", "med-db-query.py").main()


def lint_md():
    """Run pymarkdownlnt on repo markdown files.

    Falls back to scanning AGENTS.md, README.md, CLAUDE.md, .agents, .github,
    and .claude when no paths are given.  Pass --fix to auto-fix violations.
    """
    import subprocess

    args = sys.argv[1:]
    fix_mode = False
    if "--fix" in args:
        args.remove("--fix")
        fix_mode = True

    if not args:
        args = [
            "AGENTS.md",
            "README.md",
            "CLAUDE.md",
            ".agents",
            ".github",
            ".claude",
        ]

    base_cmd = ["pymarkdownlnt", "--config", ".pymarkdown.yaml"]

    if fix_mode:
        subprocess.run([*base_cmd, "fix", "-r", *args], check=False)
        # Always scan afterward so the user sees remaining violations.
        # pymarkdownlnt fix is silent when it finds nothing to fix (e.g.
        # only violations whose autofix hasn't shipped yet or rules without
        # autofix support), which makes --fix look like a no-op.
        return subprocess.run(
            [*base_cmd, "scan", "-r", *args], check=False
        ).returncode

    return subprocess.run(
        [*base_cmd, "scan", "-r", *args], check=False
    ).returncode


def test():
    try:
        from pytest import main as pytest_main
    except ModuleNotFoundError as exc:
        raise RuntimeError("pytest is not installed; run 'uv sync' to install the dev dependencies") from exc

    args = sys.argv[1:] or ["tests/", "-v"]
    return pytest_main(args)
