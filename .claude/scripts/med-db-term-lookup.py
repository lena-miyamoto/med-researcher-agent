"""Read-only lookup of archived term definitions in the med-db dictionary.

Searches ``dictionary/*/metadata.json`` by term or keyword and lists all
archived terms.  Returns JSON to stdout by default; use ``--format text``
for human-readable output.

No network calls — everything is local.
"""

import argparse
import json
import sys
from pathlib import Path

import utils


def load_entries(med_db):
    """Load every archived term entry from ``dictionary/*/metadata.json``."""
    dictionary_dir = med_db / "dictionary"
    if not dictionary_dir.is_dir():
        return []
    entries = []
    for meta_path in sorted(dictionary_dir.rglob("metadata.json")):
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        entry = dict(data)
        entry["path"] = str(meta_path.parent.relative_to(med_db))
        entries.append(entry)
    return entries


def search_by_term(entries, query):
    """Return the entry whose ``term`` matches *query* (case-insensitive or by slug)."""
    query_slug = utils.slugify(query, fallback="")
    for entry in entries:
        if str(entry.get("term", "")).strip().lower() == query.strip().lower():
            return [entry]
    for entry in entries:
        if utils.slugify(entry.get("term", ""), fallback="") == query_slug:
            return [entry]
    return []


def search_by_keyword(entries, keyword, limit=50):
    """Return entries whose term, english, definition, or source_ref contain *keyword*."""
    needle = keyword.strip().lower()
    results = []
    for entry in entries:
        haystack = " ".join(
            str(entry.get(field, "")) for field in ("term", "english", "definition", "source_ref")
        ).lower()
        if needle in haystack:
            results.append(entry)
            if len(results) >= limit:
                break
    return results


def _format_text_term(entry):
    lines = [
        f"Term:        {entry.get('term', '')}",
        f"English:     {entry.get('english', '')}",
        f"Source type: {entry.get('source_type', '')}",
        f"Source ref:  {entry.get('source_ref', '')}",
        f"Access date: {entry.get('access_date', '')}",
    ]
    if entry.get("extraction_notes"):
        lines.append(f"Notes:       {entry.get('extraction_notes')}")
    lines.extend(["", "Definition:"])
    lines.extend(utils.wrap_text(entry.get("definition", "")))
    return "\n".join(lines)


def _format_text_list(entries):
    lines = [f"Archived terms ({len(entries)}):", ""]
    for entry in entries:
        english = entry.get("english", "")
        lines.append(f"  {entry.get('term', '')}" + (f"  —  {english}" if english else ""))
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read-only lookup of archived term definitions in the med-db dictionary.",
    )
    parser.add_argument("--term", help="German term to look up (e.g. Hypertonie).")
    parser.add_argument(
        "--keyword",
        help="Search term, english, definition, and source_ref by keyword (case-insensitive).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all archived terms.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max keyword search results. Default: 50.",
    )
    parser.add_argument(
        "--med-db",
        default="med-db",
        help="Target med-db directory. Defaults to ./med-db.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format. Defaults to json.",
    )
    parser.add_argument(
        "--definition-only",
        action="store_true",
        help="Output only the definition text (for --term).",
    )
    parser.add_argument(
        "--english-only",
        action="store_true",
        help="Output only the English term (for --term).",
    )

    args = parser.parse_args()
    if not args.term and not args.keyword and not args.list:
        parser.error("provide at least one of --term, --keyword, or --list")
    if (args.definition_only or args.english_only) and not args.term:
        parser.error("--definition-only and --english-only require --term")
    return args


def main():
    args = parse_args()
    med_db = Path(args.med_db)
    entries = load_entries(med_db)

    if args.term:
        matches = search_by_term(entries, args.term)
        if not matches:
            if args.format == "json":
                print(json.dumps({"term": args.term, "error": "not found"}, ensure_ascii=False))
            else:
                print(f"term '{args.term}' not found")
            return 1
        entry = matches[0]
        if args.definition_only:
            print(entry.get("definition", ""))
            return 0
        if args.english_only:
            print(entry.get("english", ""))
            return 0
        if args.format == "json":
            print(json.dumps(entry, indent=2, ensure_ascii=False))
        else:
            print(_format_text_term(entry))
        return 0

    if args.keyword:
        results = search_by_keyword(entries, args.keyword, limit=args.limit)
        if args.format == "json":
            print(json.dumps({"query": args.keyword, "count": len(results), "results": results}, indent=2, ensure_ascii=False))
        else:
            print(_format_text_list(results))
        return 0

    if args.list:
        results = sorted(entries, key=lambda entry: str(entry.get("term", "")).lower())
        if args.format == "json":
            print(json.dumps({"count": len(results), "results": results}, indent=2, ensure_ascii=False))
        else:
            print(_format_text_list(results))
        return 0

    return 0


if __name__ == "__main__":
    utils.run_cli(main)
