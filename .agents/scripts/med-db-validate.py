import argparse
import json
import re
import sys
from pathlib import Path

import utils


# Re-export canonical slugify (replaces the old divergent copy)
slugify = utils.slugify


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate the local med-db structure and index consistency.",
    )
    parser.add_argument(
        "--med-db",
        default="med-db",
        help="Target med-db directory. Defaults to ./med-db.",
    )
    return parser.parse_args()


def read_text(path):
    return path.read_text(encoding="utf-8")


def validate_required_dirs(root, issues):
    for name in ("searches", "papers", "fulltext", "guidelines", "web"):
        path = root / name
        if not path.is_dir():
            issues.append(f"missing required directory: {path}")


def validate_non_empty_files(root, issues):
    for path in root.rglob("*"):
        if path.is_file() and path.stat().st_size == 0:
            issues.append(f"empty file: {path}")


def validate_search_json(root, issues):
    searches_dir = root / "searches"
    if not searches_dir.is_dir():
        return

    for path in sorted(searches_dir.rglob("*.json")):
        rel = str(path.relative_to(root))
        try:
            data = json.loads(read_text(path))
        except json.JSONDecodeError as error:
            issues.append(f"invalid search json: {rel}: {error}")
            continue

        pubmed_result = data.get("esearchresult", {})
        if data.get("header", {}).get("type") == "esearch" and pubmed_result:
            if "idlist" not in pubmed_result:
                issues.append(f"missing search idlist: {rel}")
            if "querytranslation" not in pubmed_result:
                issues.append(f"missing search querytranslation: {rel}")
            continue

        europe_pmc_request = data.get("request", {})
        europe_pmc_results = data.get("resultList", {})
        if europe_pmc_request and europe_pmc_results is not None:
            if not europe_pmc_request.get("queryString"):
                issues.append(f"missing Europe PMC queryString: {rel}")
            if "result" not in europe_pmc_results:
                issues.append(f"missing Europe PMC result list: {rel}")
            continue
        if europe_pmc_request:
            issues.append(f"Europe PMC response missing resultList: {rel}")
            continue

        issues.append(f"unrecognized search json format: {rel}")


def validate_papers(root, issues):
    papers_dir = root / "papers"
    if not papers_dir.is_dir():
        return

    for meta_file in sorted(papers_dir.rglob("metadata.json")):
        paper_dir = meta_file.parent

        abstract_file = paper_dir / "abstract.txt"
        if not abstract_file.is_file():
            issues.append(f"missing abstract.txt in paper folder: {paper_dir.relative_to(root)}")

        # Validate metadata.json structure
        try:
            data = json.loads(read_text(meta_file))
        except json.JSONDecodeError as error:
            issues.append(f"invalid metadata json: {paper_dir.relative_to(root)}/metadata.json: {error}")
            continue

        folder_name = paper_dir.name

        pmid_match = re.match(r"pmid-(\d+)-.+", folder_name)
        if pmid_match:
            expected_pmid = pmid_match.group(1)
            uids = data.get("result", {}).get("uids", [])
            if len(uids) != 1:
                issues.append(f"unexpected uid count in: {paper_dir.relative_to(root)}/metadata.json")
                continue
            if uids[0] != expected_pmid:
                issues.append(
                    f"pmid mismatch in: {paper_dir.relative_to(root)}/metadata.json: "
                    f"expected {expected_pmid}, got {uids[0]}"
                )
            continue

        epmc_match = re.match(r"epmc-([a-z0-9]+)-([a-z0-9]+)-.+", folder_name)
        if epmc_match:
            expected_source = epmc_match.group(1).upper()
            expected_id_slug = epmc_match.group(2)
            results = data.get("resultList", {}).get("result", [])
            if len(results) != 1:
                issues.append(
                    f"unexpected Europe PMC result count in: {paper_dir.relative_to(root)}/metadata.json"
                )
                continue
            record = results[0]
            source_name = str(record.get("source") or "").upper()
            record_id = str(record.get("id") or record.get("pmid") or "")
            if source_name != expected_source:
                issues.append(
                    f"Europe PMC source mismatch in: {paper_dir.relative_to(root)}/metadata.json: "
                    f"expected {expected_source}, got {source_name}"
                )
            if slugify(record_id) != expected_id_slug:
                issues.append(
                    f"Europe PMC id mismatch in: {paper_dir.relative_to(root)}/metadata.json: "
                    f"expected slug {expected_id_slug}, got {slugify(record_id)}"
                )
            continue

        issues.append(f"unrecognized paper folder name: {paper_dir.relative_to(root)}")

    # Check abstract content
    for path in sorted(papers_dir.rglob("abstract.txt")):
        if not read_text(path).strip():
            issues.append(f"empty abstract content: {path.relative_to(root)}")


def validate_web(root, issues):
    web_dir = root / "web"
    if not web_dir.is_dir():
        return
    for path in sorted(web_dir.rglob("*")):
        if not path.is_file():
            continue
        content = read_text(path)
        rel = str(path.relative_to(root))
        if not content.strip():
            issues.append(f"empty web file: {rel}")
        if path.suffix == ".html" and "<html" not in content.lower():
            issues.append(f"html file does not look like html: {rel}")


def validate_index(root, issues):
    index_path = root / "index.json"
    if not index_path.is_file():
        issues.append(f"missing index.json: {index_path}")
        return

    try:
        data = json.loads(read_text(index_path))
    except (json.JSONDecodeError, OSError) as exc:
        issues.append(f"invalid index.json: {exc}")
        return

    # Collect actual filesystem entries
    actual_searches = sorted(
        str(p.relative_to(root))
        for p in (root / "searches").rglob("*.json")
        if (root / "searches").is_dir()
    )
    actual_paper_dirs = sorted(
        str(p.parent.relative_to(root))
        for p in (root / "papers").rglob("metadata.json")
        if (root / "papers").is_dir()
    )
    actual_fulltext_dirs = sorted(
        str(p.parent.relative_to(root))
        for p in (root / "fulltext").rglob("metadata.json")
        if (root / "fulltext").is_dir()
    )
    actual_guideline_dirs = sorted(
        str(p.parent.relative_to(root))
        for p in (root / "guidelines").rglob("source.*.md")
        if (root / "guidelines").is_dir()
    )
    actual_web = sorted(
        str(p.relative_to(root))
        for p in (root / "web").rglob("*.html")
        if (root / "web").is_dir()
    )

    index_searches = _index_paths(data, "searches")
    index_papers = _index_paths(data, "papers")
    index_fulltext = _index_paths(data, "fulltext")
    index_guidelines = _index_paths(data, "guidelines")
    index_web = _index_paths(data, "web")

    for label, indexed, on_disk in (
        ("search index", index_searches, actual_searches),
        ("paper index", index_papers, actual_paper_dirs),
        ("fulltext index", index_fulltext, actual_fulltext_dirs),
        ("guideline index", index_guidelines, actual_guideline_dirs),
        ("web index", index_web, actual_web),
    ):
        missing = sorted(set(indexed) - set(on_disk))
        extra = sorted(set(on_disk) - set(indexed))
        for item in missing:
            issues.append(f"{label} references missing file: {item}")
        for item in extra:
            issues.append(f"{label} is missing existing entry: {item}")


def _index_paths(data, key):
    return sorted(entry["path"] for entry in data.get(key, []))


def validate_legacy_dirs(root, warnings):
    """Warn about old flat directories that should be cleaned up after migration."""
    for name in ("metadata", "abstracts"):
        legacy = root / name
        if legacy.is_dir():
            warnings.append(
                f"legacy flat directory still present (remove after verifying migration): {legacy}"
            )


def main():
    args = parse_args()
    root = Path(args.med_db)
    issues = []

    if not root.is_dir():
        print(f"med-db directory not found: {root}")
        return 1

    validate_required_dirs(root, issues)
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")
        return 1

    validate_non_empty_files(root, issues)
    validate_search_json(root, issues)
    validate_papers(root, issues)
    validate_web(root, issues)
    validate_index(root, issues)

    warnings = []
    validate_legacy_dirs(root, warnings)

    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")
        return 1

    for warning in warnings:
        print(f"WARNING: {warning}")

    search_count = len(list((root / "searches").rglob("*.json"))) if (root / "searches").is_dir() else 0
    paper_count = len(list((root / "papers").rglob("metadata.json"))) if (root / "papers").is_dir() else 0
    fulltext_count = len(list((root / "fulltext").rglob("metadata.json"))) if (root / "fulltext").is_dir() else 0
    guideline_count = len(list((root / "guidelines").rglob("source.*.md"))) if (root / "guidelines").is_dir() else 0
    web_count = len(list((root / "web").rglob("*.html"))) if (root / "web").is_dir() else 0

    print("med-db validation OK")
    print(f"searches: {search_count}")
    print(f"papers: {paper_count}")
    print(f"fulltext: {fulltext_count}")
    print(f"guidelines: {guideline_count}")
    print(f"web: {web_count}")
    if warnings:
        print(f"warnings: {len(warnings)} (see above)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("cancelled", file=sys.stderr)
        raise SystemExit(130)
