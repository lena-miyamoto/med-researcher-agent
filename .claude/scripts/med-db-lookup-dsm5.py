"""Fast local DSM-5-TR lookup from curated classification data.

Searches the DSM-5-TR diagnostic classification by ICD-10-CM code or
keyword.  Data lives under med-db/guidelines/dsm-5-tr/classification.json.
Returns JSON to stdout by default; use --format text for human-readable
output.

No network calls — everything is local.
"""

import argparse
import json
import sys
from pathlib import Path

import utils
from utils import MED_DB
CLASSIFICATION_PATH = MED_DB / "guidelines" / "dsm-5-tr" / "classification.json"


def load_classification():
    """Load the DSM-5-TR classification JSON."""
    if not CLASSIFICATION_PATH.exists():
        sys.stderr.write(
            "DSM-5-TR classification data not found. "
            "Run the download/setup first.\n"
        )
        sys.exit(1)
    try:
        with open(CLASSIFICATION_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        sys.stderr.write(
            f"DSM-5-TR classification data is corrupt: {exc}\n"
            "Run 'uv run med-db-setup-dsm5 --force' to regenerate.\n"
        )
        sys.exit(1)


def _flatten_disorders(data):
    """Yield (category_name, disorder_dict) for every disorder."""
    for category in data["categories"]:
        for disorder in category["disorders"]:
            yield category["name"], disorder


def _is_match(text, query):
    """Case-insensitive substring match."""
    return query.lower() in text.lower()


def search_by_code(data, code):
    """Search by ICD-10-CM code.

    Returns a list of ``(category_name, disorder_dict)`` tuples — always a
    list, even for single or no matches.  Exact matches take priority over
    prefix matches (e.g. ``"F32"`` matches ``F32.0``, ``F32.1``, etc.).
    """
    code_upper = code.strip().upper().replace(" ", "")
    # Exact match
    for category_name, disorder in _flatten_disorders(data):
        if disorder.get("code") and disorder["code"].upper().replace(" ", "") == code_upper:
            return [(category_name, disorder)]
    # Prefix match for partial codes (e.g., "F32" matches all F32.x codes)
    results = []
    for category_name, disorder in _flatten_disorders(data):
        if disorder.get("code") and disorder["code"].upper().replace(" ", "").startswith(code_upper):
            results.append((category_name, disorder))
    return results


def search_by_keyword(data, keyword, limit=50):
    """Find disorders whose name contains the keyword.

    Args:
        data: classification data dict.
        keyword: search term (case-insensitive).
        limit: maximum number of results (default 50).

    Returns:
        list of ``(category_name, disorder_dict)`` tuples.
    """
    keyword = keyword.strip()
    results = []
    for category_name, disorder in _flatten_disorders(data):
        if _is_match(disorder["name"], keyword):
            results.append((category_name, disorder))
            if len(results) >= limit:
                break
    return results


def search_category(data, cat_keyword):
    """Find categories whose name contains the keyword."""
    results = []
    for category in data["categories"]:
        if _is_match(category["name"], cat_keyword):
            results.append(category)
    return results


# ── Output formatting ───────────────────────────────────────────────────


def _format_text_output(output, args):
    """Format lookup results as human-readable text and print to stdout.

    Args:
        output: result dict from main().
        args: parsed CLI arguments (reserved for future use).
    """
    lines = []

    if "code_lookup" in output:
        code_lookup = output["code_lookup"]
        if "error" in code_lookup:
            lines.append(f"Error: {code_lookup['error']}")
        elif code_lookup.get("partial_match"):
            lines.append(f"Code '{code_lookup['query']}' matches {code_lookup['count']} disorders:")
            lines.append("")
            for item in code_lookup["results"]:
                disorder = item["disorder"]
                code_str = disorder.get("code") or "(no code)"
                lines.append(f"  {code_str:<12} {disorder['name']}")
                lines.append(f"              Category: {item['category']}")
                if disorder.get("specifiers"):
                    lines.append(f"              Specifiers: {', '.join(disorder['specifiers'])}")
                lines.append("")
        else:
            lines.append(f"Code:        {code_lookup['disorder']['code'] or 'N/A'}")
            lines.append(f"Disorder:    {code_lookup['disorder']['name']}")
            lines.append(f"Category:    {code_lookup['category']}")
            if code_lookup["disorder"].get("specifiers"):
                lines.append(f"Specifiers:  {', '.join(code_lookup['disorder']['specifiers'])}")
            if code_lookup["disorder"].get("note"):
                lines.append(f"Note:        {code_lookup['disorder']['note']}")
            if code_lookup["disorder"].get("dsm5tr_note"):
                lines.append(f"DSM-5-TR:    {code_lookup['disorder']['dsm5tr_note']}")
        lines.append("")

    if "keyword_search" in output:
        keyword_search = output["keyword_search"]
        lines.append(f'Keyword: "{keyword_search["query"]}" — {keyword_search["count"]} results')
        lines.append("")
        for item in keyword_search["results"]:
            category_name = item["category"]
            disorder = item["disorder"]
            code_str = disorder.get("code") or "(no code)"
            lines.append(f"  {code_str:<12} {disorder['name']}")
            lines.append(f"              Category: {category_name}")
            if disorder.get("specifiers"):
                lines.append(f"              Specifiers: {', '.join(disorder['specifiers'])}")
            lines.append("")
        lines.append("")

    if "category_list" in output:
        category_list = output["category_list"]
        if "error" in category_list:
            lines.append(f"Error: {category_list['error']}")
        else:
            lines.append(f'Category search: "{category_list["query"]}" — {category_list["count"]} results')
            lines.append("")
            for category in category_list["results"]:
                lines.append(f"  {category['name']}")
                lines.append(f"    ICD-10-CM range: {category.get('icd10cm_range', 'N/A')}")
                lines.append(f"    Disorders: {len(category['disorders'])}")
                if category.get("dsm5tr_note"):
                    lines.append(f"    Note: {category['dsm5tr_note']}")
                lines.append("")
        lines.append("")

    if "all_categories" in output:
        categories = output["all_categories"]
        lines.append(f"DSM-5-TR Diagnostic Categories ({len(categories)} total)")
        lines.append("")
        for category in categories:
            lines.append(f"  {category['name']}")
            lines.append(f"    ICD-10-CM: {category.get('icd10cm_range', 'N/A')}")
            lines.append(f"    Disorders: {len(category['disorders'])}")
            if category.get("dsm5tr_note"):
                lines.append(f"    Note: {category['dsm5tr_note']}")
        lines.append("")

    print("\n".join(lines).strip())


# ── CLI ─────────────────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fast local DSM-5-TR classification lookup.",
    )
    parser.add_argument(
        "--code",
        help="ICD-10-CM code to look up (e.g. F32.0, F90.2).",
    )
    parser.add_argument(
        "--keyword",
        help="Search disorder names by keyword (case-insensitive).",
    )
    parser.add_argument(
        "--category",
        help="Search diagnostic categories by keyword.",
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        default=False,
        help="List all DSM-5-TR diagnostic categories.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max keyword search results. Default: 50.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format. Default: json.",
    )

    args = parser.parse_args()
    if not args.code and not args.keyword and not args.category and not args.list_categories:
        parser.error(
            "provide at least one of --code, --keyword, --category, or --list-categories"
        )
    return args


def main():
    args = parse_args()
    data = load_classification()
    output = {}

    if args.code:
        result = search_by_code(data, args.code)
        if not result:
            output["code_lookup"] = {"error": f"code '{args.code}' not found"}
        elif len(result) == 1:
            cat_name, disorder = result[0]
            output["code_lookup"] = {
                "category": cat_name,
                "disorder": disorder,
            }
        else:
            output["code_lookup"] = {
                "partial_match": True,
                "query": args.code,
                "count": len(result),
                "results": [{"category": c, "disorder": d} for c, d in result],
            }

    if args.keyword:
        results = search_by_keyword(data, args.keyword, limit=args.limit)
        output["keyword_search"] = {
            "query": args.keyword,
            "count": len(results),
            "results": [{"category": c, "disorder": d} for c, d in results],
        }

    if args.category:
        results = search_category(data, args.category)
        if not results:
            output["category_list"] = {"error": f"no category matching '{args.category}'"}
        else:
            output["category_list"] = {
                "query": args.category,
                "count": len(results),
                "results": results,
            }

    if args.list_categories:
        output["all_categories"] = data["categories"]

    if args.format == "text":
        _format_text_output(output, args)
    else:
        print(json.dumps(output, indent=2, default=str, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    utils.run_cli(main)
