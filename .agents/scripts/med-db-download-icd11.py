"""Download ICD-11 MMS simple tabulation data from WHO CDN into med-db/.

Idempotent — skips files that already exist.  Downloads SimpleTabulation
(EN + DE), ICD-10 ↔ ICD-11 mapping tables, mortality/morbidity tabulation
lists, and print PDF for the specified release.  Extracts the ZIPs to
med-db/guidelines/icd-11/<release>/extracted/.

Usage:
    uv run med-db-download-icd11                  # default: 2026-01 EN+DE
    uv run med-db-download-icd11 --release 2025-01  # specific release
    uv run med-db-download-icd11 --language en      # EN only
    uv run med-db-download-icd11 --force             # re-download
"""

import argparse
import sys
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MED_DB = REPO_ROOT / "med-db"
ICD11_BASE = MED_DB / "guidelines" / "icd-11"

WHO_CDN = "https://icdcdn.who.int/static/releasefiles"

# Files to download per release.  Language-specific entries use {lang}
# substitution; language-independent files are listed as-is.
RELEASE_FILES = [
    # (remote_path_template, local_name_template, description)
    ("SimpleTabulation-ICD-11-MMS-{lang}.zip",
     "SimpleTabulation-{lang}.zip",
     "SimpleTabulation"),
    ("print-ICD-11-MMS-{lang}.zip",
     "print-{lang}.zip",
     "Print PDF"),
    ("MortalityTabulationList_{lang}.zip",
     "MortalityTabulationList_{lang}.zip",
     "Mortality tabulation list"),
    ("MorbidityTabulationList_{lang}.zip",
     "MorbidityTabulationList_{lang}.zip",
     "Morbidity tabulation list"),
]

LANG_INDEPENDENT = [
    ("mapping.zip", "mapping.zip", "ICD-10 ↔ ICD-11 mapping tables"),
]


def _build_url(release, filename):
    return f"{WHO_CDN}/{release}/{filename}"


def _download_file(url, dest, force=False):
    """Download *url* to *dest*.  Returns True if downloaded, False if skipped."""
    if dest.exists() and not force:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, dest)
    return True


def _extract_zip(zip_path, dest_dir):
    """Extract a ZIP archive to *dest_dir*."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)


def download_release(release, languages, force=False):
    """Download and extract all ICD-11 files for a release.

    Args:
        release: e.g. "2026-01".
        languages: list of language codes, e.g. ["en", "de"].
        force: re-download even if files exist.

    Returns:
        tuple (downloaded_count, skipped_count, errors).
    """
    release_dir = ICD11_BASE / release
    release_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped = 0
    errors = []

    # Language-specific files
    for remote_tmpl, local_tmpl, desc in RELEASE_FILES:
        for lang in languages:
            remote_name = remote_tmpl.format(lang=lang)
            local_name = local_tmpl.format(lang=lang)
            url = _build_url(release, remote_name)
            dest = release_dir / local_name

            try:
                if _download_file(url, dest, force=force):
                    print(f"  Downloaded: {desc} ({lang})")
                    downloaded += 1
                else:
                    print(f"  Already present: {desc} ({lang})")
                    skipped += 1
            except Exception as exc:
                msg = f"  ERROR downloading {desc} ({lang}): {exc}"
                print(msg, file=sys.stderr)
                errors.append(msg)
                continue

            # Extract
            if dest.exists():
                extract_dir = release_dir / "extracted" / lang
                try:
                    _extract_zip(dest, extract_dir)
                except Exception as exc:
                    msg = f"  ERROR extracting {local_name}: {exc}"
                    print(msg, file=sys.stderr)
                    errors.append(msg)

    # Language-independent files
    for remote_name, local_name, desc in LANG_INDEPENDENT:
        url = _build_url(release, remote_name)
        dest = release_dir / local_name
        try:
            if _download_file(url, dest, force=force):
                print(f"  Downloaded: {desc}")
                downloaded += 1
            else:
                print(f"  Already present: {desc}")
                skipped += 1
        except Exception as exc:
            msg = f"  ERROR downloading {desc}: {exc}"
            print(msg, file=sys.stderr)
            errors.append(msg)
            continue

        if dest.exists():
            extract_dir = release_dir / "extracted" / "mapping"
            try:
                _extract_zip(dest, extract_dir)
            except Exception as exc:
                msg = f"  ERROR extracting {local_name}: {exc}"
                print(msg, file=sys.stderr)
                errors.append(msg)

    return downloaded, skipped, errors


def verify_quick(release, language):
    """Quick smoke test — try loading the tabulation.

    Returns (entry_count, None) on success, or (0, error_message) on failure.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from importlib import import_module
        mod = import_module("med-db-lookup-icd11")
        entries, version = mod.load_tabulation(release, language)
        if entries:
            return len(entries), None
        return 0, "loaded 0 entries — file may be empty"
    except SystemExit:
        return 0, "lookup tool exited (data not found or unreadable)"
    except Exception as exc:
        return 0, str(exc)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download ICD-11 MMS data from WHO CDN into med-db/"
    )
    parser.add_argument(
        "--release",
        default="2026-01",
        help="ICD-11 release to download. Default: 2026-01.",
    )
    parser.add_argument(
        "--language",
        action="append",
        default=[],
        help="Language code to download (may be passed multiple times). "
             "Default: en, de for 2026-01; en for earlier releases.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Re-download even if files already exist.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        default=True,
        help="Run a quick smoke test after downloading (default on). "
             "Use --no-verify to skip.",
    )

    args = parser.parse_args()

    if not args.language:
        # 2026-01 has DE; earlier releases typically EN-only
        if args.release >= "2026-01":
            args.language = ["en", "de"]
        else:
            args.language = ["en"]

    return args


def main():
    args = parse_args()

    print(f"ICD-11 Download — Release {args.release}, languages: {', '.join(args.language)}")
    print(f"Target: {ICD11_BASE / args.release}")
    print()

    downloaded, skipped, errors = download_release(
        args.release, args.language, force=args.force
    )

    print()
    print(f"Done: {downloaded} downloaded, {skipped} skipped, {len(errors)} errors")

    if errors:
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    if args.verify:
        print()
        ok = True
        for lang in args.language:
            count, err = verify_quick(args.release, lang)
            if err:
                print(f"  Verify {lang}: ERROR — {err}")
                ok = False
            else:
                print(f"  Verify {lang}: {count} entries loaded")
        if not ok:
            return 1

    # Ensure source.md exists
    source_md = ICD11_BASE / "source.md"
    if not source_md.exists():
        print()
        print("  source.md not found — it should be created separately "
              "(it ships with the repo under med-db/guidelines/icd-11/source.md)")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("cancelled", file=sys.stderr)
        raise SystemExit(130)
