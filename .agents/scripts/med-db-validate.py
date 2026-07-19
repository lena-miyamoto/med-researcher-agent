"""Validate the local med-db structure and index consistency.

Legacy wrapper — delegates to the canonical integrity checks in ``utils.py``.
Prefer ``med-db-integrity-check`` for new workflows; this entry point is kept
for backward compatibility and returns flat string issues in the original format.
"""

import argparse
import json
import sys
from pathlib import Path

import utils


# Re-export canonical slugify (replaces the old divergent copy)
slugify = utils.slugify


def _findings_to_strings(findings, prefix=""):
    """Convert structured finding dicts to flat string messages."""
    strings = []
    for f in findings:
        msg = f"{f['category']}: {f['location']} — {f['description']}"
        if prefix:
            msg = f"{prefix}: {msg}"
        strings.append(msg)
    return strings


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


def validate_required_dirs(root, issues):
    findings = []
    utils.check_required_dirs(Path(root), findings)
    issues.extend(_findings_to_strings(findings, "missing required directory"))


def validate_non_empty_files(root, issues):
    findings = []
    utils.check_empty_files(Path(root), findings)
    issues.extend(_findings_to_strings(findings, "empty file"))


def validate_search_json(root, issues):
    findings = []
    utils.check_search_json(Path(root), findings)
    issues.extend(_findings_to_strings(findings, "invalid search json"))


def validate_papers(root, issues):
    findings = []
    utils.check_paper_integrity(Path(root), findings)
    issues.extend(_findings_to_strings(findings, "paper issue"))


def validate_web(root, issues):
    findings = []
    utils.check_web_files(Path(root), findings)
    issues.extend(_findings_to_strings(findings, "web issue"))


def validate_index(root, issues):
    findings = []
    data = utils.check_index_valid(Path(root), findings)
    if data is not None:
        utils.check_index_crossref(Path(root), data, findings)
    issues.extend(_findings_to_strings(findings, "index issue"))


def validate_legacy_dirs(root, warnings):
    """Warn about old flat directories that should be cleaned up after migration."""
    findings = []
    utils.check_legacy_dirs(Path(root), findings)
    warnings.extend(
        f"legacy flat directory still present (remove after verifying migration): {f['location']}"
        for f in findings
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
    guideline_count = len(set(
        p.parent for pattern in ("source.md", "source.*.md")
        for p in (root / "guidelines").rglob(pattern)
    )) if (root / "guidelines").is_dir() else 0
    web_count = len([p for p in (root / "web").rglob("*") if p.is_file()]) if (root / "web").is_dir() else 0

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
    utils.run_cli(main)
