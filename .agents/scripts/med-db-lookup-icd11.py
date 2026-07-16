"""Fast local ICD-11 lookup from downloaded WHO simple tabulation data.

Searches the ICD-11 MMS classification by code or keyword. Supports
English (2025-01, 2026-01) and German (2026-01) from cached TSV files
under med-db/guidelines/icd-11/. Returns JSON to stdout by default;
use --format text for human-readable output.

No network calls — everything is local.
"""

import argparse
import csv
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MED_DB = REPO_ROOT / "med-db"
ICD11_BASE = MED_DB / "guidelines" / "icd-11"


def _find_tabulation_file(release, language):
    """Return path to the extracted SimpleTabulation TSV for the given language."""
    candidate = (
        ICD11_BASE / release / "extracted" / language /
        f"SimpleTabulation-ICD-11-MMS-{language}.txt"
    )
    if candidate.exists():
        return candidate
    # Fallback: scan for any extracted SimpleTabulation .txt in this language dir
    extracted = ICD11_BASE / release / "extracted"
    if extracted.exists():
        for lang_dir in extracted.iterdir():
            if lang_dir.is_dir() and lang_dir.name == language:
                for f in lang_dir.glob("SimpleTabulation-ICD-11-MMS-*.txt"):
                    return f
    return None


def _build_column_map(header, language):
    """Map TSV column names → normalized dict keys for the tabulation loader.

    The EN file has: Foundation URI, Linearization URI, Code, BlockId,
    Title, ClassKind, DepthInKind, IsResidual, ChapterNo, BrowserLink,
    isLeaf, Primary tabulation, Grouping1..5, CodingNote, Parent

    The DE file has an extra Title column: TitleEN, Title between BlockId
    and ClassKind — the loader always stores the localised title as
    ``title`` and the English fallback as ``title_en``.
    """
    # Normalize header names: strip whitespace, BOM prefix, lowercase
    clean = [h.strip().lstrip("﻿").lower() for h in header]

    col_map = {}
    for idx, name in enumerate(clean):
        if name in ("foundation uri", "foundation_uri"):
            col_map["foundation_uri"] = idx
        elif name in ("linearization uri", "linearization (release) uri", "linearization_uri"):
            col_map["linearization_uri"] = idx
        elif name == "code":
            col_map["code"] = idx
        elif name in ("blockid", "block_id"):
            col_map["block_id"] = idx
        elif name == "title":
            # Title = localised title in DE files; only title column in EN files
            col_map["title"] = idx
        elif name == "titleen":
            col_map["title_en"] = idx
        elif name in ("classkind", "class_kind"):
            col_map["class_kind"] = idx
        elif name in ("depthinkind", "depth_in_kind"):
            col_map["depth_in_kind"] = idx
        elif name in ("isresidual", "is_residual"):
            col_map["is_residual"] = idx
        elif name in ("chapterno", "chapter_no"):
            col_map["chapter_no"] = idx
        elif name in ("browserlink", "browser_link"):
            col_map["browser_link"] = idx
        elif name == "isleaf":
            col_map["is_leaf"] = idx
        elif name in ("primary tabulation", "primary_tabulation"):
            col_map["primary_tabulation"] = idx
        elif name.startswith("grouping"):
            try:
                n = int(name.replace("grouping", ""))
                col_map[f"grouping{n}"] = idx
            except ValueError:
                pass
        elif name in ("codingnote", "coding_note"):
            col_map["coding_note"] = idx
        elif name == "parent":
            col_map["parent"] = idx

    return col_map


def _cell(row, col_map, key, default=""):
    """Safe cell access by mapped column index."""
    idx = col_map.get(key)
    if idx is not None and idx < len(row):
        return row[idx].strip()
    return default


def load_tabulation(release="2026-01", language="en"):
    """Load ICD-11 simple tabulation TSV into a list of dicts.

    Returns (entries, version_string).  Each entry dict has the
    normalised keys from _build_column_map, with ``title`` always
    holding the preferred-language title.  For bilingual files the
    English title is stored as ``title_en``; for monolingual EN files
    ``title_en`` is always empty.
    """
    path = _find_tabulation_file(release, language)
    if path is None:
        sys.stderr.write(
            f"ICD-11 data not found for {release}/{language}. "
            f"Run the download first.\n"
        )
        sys.exit(1)

    entries = []
    version_str = None
    with open(path, encoding="utf-8-sig") as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader, None)
        if header:
            version_str = header[-1] if "Version:" in (header[-1] or "") else None
        col_map = _build_column_map(header, language)

        # Determine how to populate title / title_en
        has_title_en = "title_en" in col_map

        for row in reader:
            if not row or all(c == "" for c in row):
                continue

            title = _cell(row, col_map, "title")

            entry = {
                "foundation_uri": _cell(row, col_map, "foundation_uri"),
                "linearization_uri": _cell(row, col_map, "linearization_uri"),
                "code": _cell(row, col_map, "code"),
                "block_id": _cell(row, col_map, "block_id"),
                "title": title,
                "title_en": _cell(row, col_map, "title_en") if has_title_en else title,
                "class_kind": _cell(row, col_map, "class_kind"),
                "depth_in_kind": _cell(row, col_map, "depth_in_kind"),
                "is_residual": _cell(row, col_map, "is_residual"),
                "chapter_no": _cell(row, col_map, "chapter_no"),
                "browser_link": _cell(row, col_map, "browser_link"),
                "is_leaf": _cell(row, col_map, "is_leaf"),
                "primary_tabulation": _cell(row, col_map, "primary_tabulation"),
                "grouping1": _cell(row, col_map, "grouping1"),
                "grouping2": _cell(row, col_map, "grouping2"),
                "grouping3": _cell(row, col_map, "grouping3"),
                "grouping4": _cell(row, col_map, "grouping4"),
                "grouping5": _cell(row, col_map, "grouping5"),
                "coding_note": _cell(row, col_map, "coding_note"),
                "parent": _cell(row, col_map, "parent"),
            }
            entries.append(entry)

    return entries, version_str


def _is_match(text: str, query: str) -> bool:
    """Case-insensitive substring match after normalizing dashes/quotes."""
    t = text.lower().replace('"', '').replace("'", "")
    q = query.lower().replace('"', '').replace("'", "")
    return q in t


def search_by_code(entries, code):
    """Exact case-insensitive code match. Returns matching entry or None."""
    code_upper = code.strip().upper().rstrip(".")
    # Exact match first
    for e in entries:
        if e["code"].upper() == code_upper:
            return e
    # Stem-code prefix match (e.g. "6A02" matches "6A02.0")
    for e in entries:
        if e["code"].upper().startswith(code_upper + "."):
            return e
    return None


def search_by_keyword(entries, keyword, class_kind=None, limit=50):
    """Find entries whose title (or title_en) contains the keyword.

    Searches both ``title`` and ``title_en`` so German queries can match
    the German title while English queries also work on a DE-loaded set.
    """
    keyword = keyword.strip()
    results = []
    for e in entries:
        if class_kind and e["class_kind"].lower() != class_kind.lower():
            continue
        match = _is_match(e["title"], keyword)
        if not match and e.get("title_en") and e["title_en"] != e["title"]:
            match = _is_match(e["title_en"], keyword)
        if match:
            results.append(e)
            if len(results) >= limit:
                break
    return results


def get_ancestors(entries, entry):
    """Follow parent URIs to build the ancestral chain (top-down)."""
    chain = []
    uri_to_entry = {}
    for e in entries:
        if e["foundation_uri"]:
            uri_to_entry[e["foundation_uri"]] = e

    current = entry
    visited = set()
    while current and current.get("parent") and current["parent"] not in visited:
        visited.add(current["parent"])
        parent = uri_to_entry.get(current["parent"])
        if parent is None:
            break
        chain.append(parent)
        current = parent

    chain.reverse()
    return chain


def get_children(entries, entry):
    """Return direct children of an entry by parent URI."""
    parent_uri = entry.get("linearization_uri") or entry.get("foundation_uri")
    if not parent_uri:
        return []
    return [e for e in entries if e.get("parent") == parent_uri]


# ── ICD-10 ↔ ICD-11 mapping ────────────────────────────────────────────


def load_icd10_to_icd11_mapping(release="2026-01"):
    """Load ICD-10 → ICD-11 mapping table (one-to-one).

    Returns a list of dicts with keys: icd10_code, icd10_title,
    icd10_chapter, icd11_code, icd11_title, icd11_chapter.
    """
    mapping_dir = ICD11_BASE / release / "extracted" / "mapping"
    path = mapping_dir / "10To11MapToOneCategory.txt"
    if not path.exists():
        return []

    mappings = []
    with open(path, encoding="utf-8-sig") as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader, None)
        if header is None:
            return []

        # Build column map from header
        clean = [h.strip().lower() for h in header]
        col = {}
        for idx, name in enumerate(clean):
            if name in ("icd10code",):
                col["icd10_code"] = idx
            elif name in ("icd10title",):
                col["icd10_title"] = idx
            elif name in ("icd10chapter",):
                col["icd10_chapter"] = idx
            elif name in ("icd11code",):
                col["icd11_code"] = idx
            elif name in ("icd11title",):
                col["icd11_title"] = idx
            elif name in ("icd11chapter",):
                col["icd11_chapter"] = idx

        for row in reader:
            if len(row) < max(col.values(), default=0) + 1:
                continue

            mappings.append({
                "icd10_code": row[col["icd10_code"]].strip() if "icd10_code" in col else "",
                "icd10_title": row[col["icd10_title"]].strip() if "icd10_title" in col else "",
                "icd10_chapter": row[col["icd10_chapter"]].strip() if "icd10_chapter" in col else "",
                "icd11_code": row[col["icd11_code"]].strip() if "icd11_code" in col else "",
                "icd11_title": row[col["icd11_title"]].strip() if "icd11_title" in col else "",
                "icd11_chapter": row[col["icd11_chapter"]].strip() if "icd11_chapter" in col else "",
            })
    return mappings


def _resolve_icd10_code(mappings, icd10_code):
    """Find ICD-11 code for a given ICD-10 code."""
    code = icd10_code.strip().upper()
    for m in mappings:
        if m["icd10_code"].upper() == code:
            return m
    return None


def _resolve_icd11_code(mappings, icd11_code):
    """Find ICD-10 code(s) for a given ICD-11 code.

    Matches exact ICD-11 codes first, then falls back to prefix matching
    (e.g. ``6A02`` matches ``6A02.0``, ``6A02.Z``, ``6A02.1``, etc.).
    """
    code = icd11_code.strip().upper()
    exact = [m for m in mappings if m["icd11_code"].upper() == code]
    if exact:
        return exact
    # Prefix match: stem code matches all subcodes
    prefix = code + "."
    return [m for m in mappings if m["icd11_code"].upper().startswith(prefix)]


# ── Output formatting ───────────────────────────────────────────────────


def _format_entry_text(entry, ancestors=None, children=None):
    lines = []
    lines.append(f"Code:        {entry['code'] or '(block — no code)'}")
    lines.append(f"Title:       {entry['title']}")
    if entry.get("title_en") and entry["title_en"] != entry["title"]:
        lines.append(f"Title (EN):  {entry['title_en']}")
    if entry.get("class_kind"):
        lines.append(f"Class:       {entry['class_kind']}")
    if entry.get("chapter_no"):
        lines.append(f"Chapter:     {entry['chapter_no']}")
    if entry.get("is_residual", "").lower() == "true":
        lines.append("Residual:    yes (other/unspecified)")
    if entry.get("coding_note"):
        lines.append(f"Coding note: {entry['coding_note']}")
    if entry.get("is_leaf", "").lower() == "true":
        lines.append("Leaf:        yes")
    fid = entry.get("foundation_uri", "").split("/")[-1]
    lines.append(f"Browser:     https://icd.who.int/browse/latestrelease/mms/en#{fid}")

    if ancestors:
        lines.append(f"\nHierarchy ({len(ancestors)} levels up):")
        indent = 0
        for a in ancestors:
            prefix = "  " * indent
            code_str = a["code"] if a["code"] else f"[{a.get('block_id', '')}]"
            lines.append(f"{prefix}→ {code_str}: {a['title']}")
            indent += 1
        prefix = "  " * indent
        code_str = entry["code"] if entry["code"] else f"[{entry.get('block_id', '')}]"
        lines.append(f"{prefix}→ {code_str}: {entry['title']}  ← current")

    if children is not None:
        lines.append(f"\nChildren ({len(children)}):")
        for c in children[:30]:
            c_code = c["code"] if c["code"] else f"[{c.get('block_id', '')}]"
            lines.append(f"  → {c_code}: {c['title']}")
        if len(children) > 30:
            lines.append(f"  ... and {len(children) - 30} more")

    return "\n".join(lines)


def _format_json_output(data):
    return json.dumps(data, indent=2, default=str, ensure_ascii=False)


# ── CLI ─────────────────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fast local ICD-11 MMS lookup from downloaded WHO data.",
    )
    parser.add_argument(
        "--code",
        help="Exact ICD-11 stem code to look up (e.g. 6A02, 1A00.0).",
    )
    parser.add_argument(
        "--keyword",
        help="Search ICD-11 titles by keyword (case-insensitive).",
    )
    parser.add_argument(
        "--class-kind",
        choices=("chapter", "block", "category"),
        help="Filter --keyword results by class kind.",
    )
    parser.add_argument(
        "--icd10-code",
        help="Look up equivalent ICD-11 code for an ICD-10 code.",
    )
    parser.add_argument(
        "--icd11-to-icd10",
        help="Find equivalent ICD-10 code(s) for an ICD-11 code.",
    )
    parser.add_argument(
        "--release",
        default="2026-01",
        help="ICD-11 release to use. Default: 2026-01.",
    )
    parser.add_argument(
        "--language",
        default="en",
        choices=("en", "de"),
        help="Language for title display. Default: en.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max keyword search results. Default: 50.",
    )
    parser.add_argument(
        "--hierarchy",
        action="store_true",
        default=True,
        help="Show full hierarchy for code lookups (default on). Use --no-hierarchy to disable.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format. Default: json.",
    )
    parser.add_argument(
        "--children",
        action="store_true",
        default=False,
        help="Include direct children in code lookup output.",
    )

    args = parser.parse_args()
    if not args.code and not args.keyword and not args.icd10_code and not args.icd11_to_icd10:
        parser.error(
            "provide at least one of --code, --keyword, --icd10-code, or --icd11-to-icd10"
        )
    return args


def main():
    args = parse_args()
    output = {}

    # ICD-10 → ICD-11 mapping
    if args.icd10_code:
        mappings = load_icd10_to_icd11_mapping(args.release)
        match = _resolve_icd10_code(mappings, args.icd10_code)
        output["icd10_to_icd11"] = match if match else {
            "error": f"no mapping found for ICD-10 code {args.icd10_code}"
        }

    # ICD-11 → ICD-10 mapping
    if args.icd11_to_icd10:
        mappings = load_icd10_to_icd11_mapping(args.release)
        matches = _resolve_icd11_code(mappings, args.icd11_to_icd10)
        output["icd11_to_icd10"] = matches if matches else {
            "error": f"no mapping found for ICD-11 code {args.icd11_to_icd10}"
        }

    # Code or keyword search — load tabulation once
    if args.code or args.keyword:
        entries, version = load_tabulation(args.release, args.language)
        output["release"] = args.release
        output["language"] = args.language
        output["version"] = version
        output["total_entries"] = len(entries)

    if args.code:
        entry = search_by_code(entries, args.code)
        if entry is None:
            output["code_lookup"] = {"error": f"code '{args.code}' not found"}
        else:
            result = dict(entry)
            if args.hierarchy:
                result["ancestors"] = get_ancestors(entries, entry)
            if args.children:
                result["children"] = get_children(entries, entry)
            output["code_lookup"] = result

    if args.keyword:
        results = search_by_keyword(
            entries, args.keyword, class_kind=args.class_kind, limit=args.limit
        )
        output["keyword_search"] = {
            "query": args.keyword,
            "class_kind_filter": args.class_kind,
            "count": len(results),
            "results": results,
        }

    if args.format == "text":
        lines = []
        if "code_lookup" in output:
            cl = output["code_lookup"]
            if "error" in cl:
                lines.append(f"Error: {cl['error']}")
                lines.append("")
            else:
                ancestors = cl.pop("ancestors", None)
                children = cl.pop("children", None)
                lines.append(_format_entry_text(cl, ancestors=ancestors, children=children))
                lines.append("")

        if "keyword_search" in output:
            ks = output["keyword_search"]
            lines.append(f'Keyword: "{ks["query"]}" — {ks["count"]} results')
            if ks.get("class_kind_filter"):
                lines.append(f"Filter: class_kind={ks['class_kind_filter']}")
            lines.append("")
            for r in ks["results"]:
                code_str = r["code"] if r["code"] else f"[{r.get('block_id', '')}]"
                lines.append(
                    f"  {code_str:<12} {r['title']}"
                    f"  ({r['class_kind']}, ch.{r.get('chapter_no', '?')})"
                )
            lines.append("")

        if "icd10_to_icd11" in output:
            m = output["icd10_to_icd11"]
            if "error" in m:
                lines.append(f"ICD-10 → ICD-11: {m['error']}")
            else:
                lines.append(
                    f"ICD-10 {m['icd10_code']}: {m['icd10_title']}"
                )
                lines.append(
                    f"  → ICD-11 {m['icd11_code']}: {m['icd11_title']}"
                )
            lines.append("")

        if "icd11_to_icd10" in output:
            matches = output["icd11_to_icd10"]
            if isinstance(matches, dict) and "error" in matches:
                lines.append(f"ICD-11 → ICD-10: {matches['error']}")
            else:
                lines.append(
                    f"ICD-11 {args.icd11_to_icd10} maps to {len(matches)} ICD-10 code(s):"
                )
                for m in matches:
                    lines.append(
                        f"  → ICD-10 {m['icd10_code']}: {m['icd10_title']}"
                    )
            lines.append("")

        print("\n".join(lines).strip())
    else:
        print(_format_json_output(output))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("cancelled", file=sys.stderr)
        raise SystemExit(130)
