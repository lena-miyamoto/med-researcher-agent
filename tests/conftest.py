import importlib.util
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"


def _load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    assert spec is not None, f"Could not find {SCRIPTS_DIR / filename}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def pytest_configure():
    """Load med_db, med_db_validate, med_db_lookup, med_db_query, and utils
    as importable modules."""
    _load_module("med_db", "med-db.py")
    _load_module("med_db_validate", "med-db-validate.py")
    _load_module("med_db_lookup", "med-db-lookup.py")
    _load_module("med_db_query", "med-db-query.py")
    _load_module("med_db_lookup_icd11", "med-db-lookup-icd11.py")
    _load_module("med_db_lookup_dsm5", "med-db-lookup-dsm5.py")
    _load_module("utils", "utils.py")
