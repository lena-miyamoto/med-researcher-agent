"""Archive a medical term definition into the med-db dictionary category.

Writes ``dictionary/<term-slug>/source.md`` (YAML frontmatter + definition
body) and ``metadata.json`` (machine-readable mirror), syncs ``index.json``,
and runs the integrity check.  Used by the ``define-terms`` skill to store
evidence-backed term definitions.

No network calls — the caller supplies the definition and its authoritative
source reference.
"""

import argparse
import datetime
import importlib.util
import json
import sys
from pathlib import Path

import utils

SOURCE_TYPE_LABELS = {
    "icd11": "ICD-11",
    "dsm5": "DSM-5-TR",
    "mesh": "MeSH",
    "who": "WHO",
    "society": "Professional society",
    "dictionary": "Medical dictionary",
    "literature": "Peer-reviewed literature",
    "web": "Web",
    "other": "Other",
}


def load_med_db_module():
    """Load ``med-db.py`` as the ``med_db`` module.

    Tests pre-load it into ``sys.modules`` via conftest; in production the
    file is loaded from the scripts directory.
    """
    existing = sys.modules.get("med_db")
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(
        "med_db", Path(__file__).resolve().parent / "med-db.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load med-db.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["med_db"] = module
    spec.loader.exec_module(module)
    return module


def source_type_label(source_type):
    """Return the human-readable label for a source type."""
    return SOURCE_TYPE_LABELS.get(source_type, source_type)


def _is_url(value):
    return value.startswith("http://") or value.startswith("https://") or value.startswith("doi:")


def resolve_source_url(source_ref, source_url):
    """Return the canonical source URL, falling back to a URL-shaped source_ref."""
    if source_url:
        return source_url
    if source_ref and _is_url(source_ref):
        return source_ref
    return ""


def build_source_md(term, english, definition, source_type, source_ref, source_url, access_date, extraction_notes):
    """Build the ``source.md`` content with YAML frontmatter and a definition body."""
    fields = {
        "title": term,
        "english": english,
        "source_type": source_type,
        "source_ref": source_ref,
        "source": source_type_label(source_type),
        "source_url": source_url,
        "access_date": access_date,
        "language": "de",
        "extraction_notes": extraction_notes,
    }
    return utils.build_frontmatter(fields) + "\n" + definition.rstrip() + "\n"


def build_metadata(term, english, definition, source_type, source_ref, source_url, access_date, extraction_notes):
    """Build the machine-readable ``metadata.json`` mirror."""
    return {
        "term": term,
        "english": english,
        "definition": definition,
        "source_type": source_type,
        "source_ref": source_ref,
        "source_url": source_url,
        "access_date": access_date,
        "extraction_notes": extraction_notes,
    }


def archive_term(med_db, term, english, definition, source_type, source_ref, source_url, access_date, extraction_notes):
    """Write the term definition into ``dictionary/<term-slug>/`` and return the directory."""
    term_slug = utils.slugify(term, fallback="term")
    term_dir = med_db / "dictionary" / term_slug
    term_dir.mkdir(parents=True, exist_ok=True)

    source_md = build_source_md(
        term, english, definition, source_type, source_ref, source_url, access_date, extraction_notes
    )
    metadata = build_metadata(
        term, english, definition, source_type, source_ref, source_url, access_date, extraction_notes
    )
    utils.atomic_write(term_dir / "source.md", source_md)
    utils.atomic_write(
        term_dir / "metadata.json", json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
    )
    return term_dir


def _format_text(result):
    lines = [
        f"term:         {result['term']}",
        f"english:      {result['english'] or '(none)'}",
        f"source_type:  {result['source_type']}",
        f"source_ref:   {result['source_ref'] or '(none)'}",
        f"folder:       {result['folder']}",
    ]
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Archive a medical term definition into the med-db dictionary category.",
    )
    parser.add_argument("--term", required=True, help="German term to archive (e.g. Hypertonie).")
    parser.add_argument("--english", default="", help="English translation of the term.")
    parser.add_argument("--definition", required=True, help="German definition text.")
    parser.add_argument(
        "--source-type",
        choices=tuple(SOURCE_TYPE_LABELS),
        default="other",
        help="Kind of authoritative source backing the definition.",
    )
    parser.add_argument(
        "--source-ref",
        default="",
        help="Source reference: classification code, URL, or PMID/DOI.",
    )
    parser.add_argument(
        "--source-url",
        default="",
        help="Canonical source URL. Falls back to --source-ref when it is a URL.",
    )
    parser.add_argument(
        "--extraction-notes",
        default="",
        help="Provenance note recorded in the source.md frontmatter (e.g. non-authoritative community usage).",
    )
    parser.add_argument(
        "--med-db",
        default="med-db",
        help="Target med-db directory. Defaults to ./med-db.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format. Defaults to text.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    med_db_module = load_med_db_module()
    med_db = Path(args.med_db)

    med_db.mkdir(parents=True, exist_ok=True)
    med_db_module.ensure_med_db_structure(med_db)

    access_date = datetime.date.today().isoformat()
    source_url = resolve_source_url(args.source_ref, args.source_url)
    term_dir = archive_term(
        med_db,
        args.term,
        args.english,
        args.definition,
        args.source_type,
        args.source_ref,
        source_url,
        access_date,
        args.extraction_notes,
    )

    med_db_module.sync_index(med_db)

    result = {
        "term": args.term,
        "english": args.english,
        "source_type": args.source_type,
        "source_ref": args.source_ref,
        "folder": str(term_dir),
    }

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(_format_text(result))

    if utils.verify_and_report_integrity(med_db) != 0:
        return 1
    return 0


if __name__ == "__main__":
    utils.run_cli(main)
