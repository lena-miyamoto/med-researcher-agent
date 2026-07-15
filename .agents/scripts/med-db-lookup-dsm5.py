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


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MED_DB = REPO_ROOT / "med-db"
CLASSIFICATION_PATH = MED_DB / "guidelines" / "dsm-5-tr" / "classification.json"


def load_classification():
    """Load the DSM-5-TR classification JSON."""
    if not CLASSIFICATION_PATH.exists():
        sys.stderr.write(
            "DSM-5-TR classification data not found. "
            "Run the download/setup first.\n"
        )
        sys.exit(1)
    with open(CLASSIFICATION_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _flatten_disorders(data):
    """Yield (category_name, disorder_dict) for every disorder."""
    for cat in data["categories"]:
        for d in cat["disorders"]:
            yield cat["name"], d


def _is_match(text, query):
    """Case-insensitive substring match."""
    return query.lower() in text.lower()


def search_by_code(data, code):
    """Exact ICD-10-CM code match. Returns (category_name, disorder_dict) or None."""
    code_upper = code.strip().upper().replace(" ", "")
    for cat_name, d in _flatten_disorders(data):
        if d.get("code") and d["code"].upper().replace(" ", "") == code_upper:
            return cat_name, d
    # Prefix match for partial codes (e.g., "F32" matches all F32.x codes)
    results = []
    for cat_name, d in _flatten_disorders(data):
        if d.get("code") and d["code"].upper().replace(" ", "").startswith(code_upper):
            results.append((cat_name, d))
    if len(results) == 1:
        return results[0]
    return None


def search_by_keyword(data, keyword, limit=50):
    """Find disorders whose name contains the keyword."""
    keyword = keyword.strip()
    results = []
    for cat_name, d in _flatten_disorders(data):
        if _is_match(d["name"], keyword):
            results.append((cat_name, d))
            if len(results) >= limit:
                break
    return results


def search_category(data, cat_keyword):
    """Find categories whose name contains the keyword."""
    results = []
    for cat in data["categories"]:
        if _is_match(cat["name"], cat_keyword):
            results.append(cat)
    return results


# ── Output formatting ───────────────────────────────────────────────────


def _format_text_output(output, args):
    lines = []

    if "code_lookup" in output:
        cl = output["code_lookup"]
        if "error" in cl:
            lines.append(f"Error: {cl['error']}")
        else:
            lines.append(f"Code:        {cl['disorder']['code'] or 'N/A'}")
            lines.append(f"Disorder:    {cl['disorder']['name']}")
            lines.append(f"Category:    {cl['category']}")
            if cl["disorder"].get("specifiers"):
                lines.append(f"Specifiers:  {', '.join(cl['disorder']['specifiers'])}")
            if cl["disorder"].get("note"):
                lines.append(f"Note:        {cl['disorder']['note']}")
            if cl["disorder"].get("dsm5tr_note"):
                lines.append(f"DSM-5-TR:    {cl['disorder']['dsm5tr_note']}")
        lines.append("")

    if "keyword_search" in output:
        ks = output["keyword_search"]
        lines.append(f'Keyword: "{ks["query"]}" — {ks["count"]} results')
        lines.append("")
        for item in ks["results"]:
            cat_name = item["category"]
            d = item["disorder"]
            code_str = d.get("code") or "(no code)"
            lines.append(f"  {code_str:<12} {d['name']}")
            lines.append(f"              Category: {cat_name}")
            if d.get("specifiers"):
                lines.append(f"              Specifiers: {', '.join(d['specifiers'])}")
            lines.append("")
        lines.append("")

    if "category_list" in output:
        cl = output["category_list"]
        if "error" in cl:
            lines.append(f"Error: {cl['error']}")
        else:
            lines.append(f'Category search: "{cl["query"]}" — {cl["count"]} results')
            lines.append("")
            for cat in cl["results"]:
                lines.append(f"  {cat['name']}")
                lines.append(f"    ICD-10-CM range: {cat.get('icd10cm_range', 'N/A')}")
                lines.append(f"    Disorders: {len(cat['disorders'])}")
                if cat.get("dsm5tr_note"):
                    lines.append(f"    Note: {cat['dsm5tr_note']}")
                lines.append("")
        lines.append("")

    if "all_categories" in output:
        cats = output["all_categories"]
        lines.append(f"DSM-5-TR Diagnostic Categories ({len(cats)} total)")
        lines.append("")
        for cat in output["all_categories"]:
            lines.append(f"  {cat['name']}")
            lines.append(f"    ICD-10-CM: {cat.get('icd10cm_range', 'N/A')}")
            lines.append(f"    Disorders: {len(cat['disorders'])}")
            if cat.get("dsm5tr_note"):
                lines.append(f"    Note: {cat['dsm5tr_note']}")
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
        if result is None:
            output["code_lookup"] = {"error": f"code '{args.code}' not found"}
        else:
            cat_name, disorder = result
            output["code_lookup"] = {
                "category": cat_name,
                "disorder": disorder,
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
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("cancelled", file=sys.stderr)
        raise SystemExit(130)
