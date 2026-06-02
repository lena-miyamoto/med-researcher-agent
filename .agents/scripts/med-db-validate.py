#!/usr/bin/python3
import argparse
import json
import re
import sys
from pathlib import Path


def slugify(text):
	text = str(text).lower()
	text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
	return text or "record"


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


def collect_files(directory, pattern):
	return sorted(path.name for path in directory.glob(pattern) if path.is_file())


def read_text(path):
	return path.read_text(encoding="utf-8")


def validate_required_dirs(root, issues):
	for name in ("searches", "metadata", "abstracts", "web"):
		path = root / name
		if not path.is_dir():
			issues.append(f"missing required directory: {path}")


def validate_non_empty_files(root, issues):
	for path in root.rglob("*"):
		if path.is_file() and path.stat().st_size == 0:
			issues.append(f"empty file: {path}")


def validate_search_json(root, issues):
	search_dir = root / "searches"
	actual_numbers = []

	def sort_key(path):
		match = re.match(r"s(\d+)-.+\.json$", path.name)
		return (0, int(match.group(1))) if match else (1, path.name)

	for path in sorted(search_dir.glob("*.json"), key=sort_key):
		match = re.match(r"s(\d+)-.+\.json$", path.name)
		if not match:
			issues.append(f"bad search filename: {path.name}")
			continue
		actual_numbers.append(int(match.group(1)))
		try:
			data = json.loads(read_text(path))
		except json.JSONDecodeError as error:
			issues.append(f"invalid search json: {path.name}: {error}")
			continue

		pubmed_result = data.get("esearchresult", {})
		if data.get("header", {}).get("type") == "esearch" and pubmed_result:
			if "idlist" not in pubmed_result:
				issues.append(f"missing search idlist: {path.name}")
			if "querytranslation" not in pubmed_result:
				issues.append(f"missing search querytranslation: {path.name}")
			continue

		europe_pmc_request = data.get("request", {})
		europe_pmc_results = data.get("resultList", {})
		if europe_pmc_request and europe_pmc_results is not None:
			if not europe_pmc_request.get("queryString"):
				issues.append(f"missing Europe PMC queryString: {path.name}")
			if "result" not in europe_pmc_results:
				issues.append(f"missing Europe PMC result list: {path.name}")
			continue

		issues.append(f"unrecognized search json format: {path.name}")

	if actual_numbers:
		expected_numbers = list(range(1, len(actual_numbers) + 1))
		if actual_numbers != expected_numbers:
			issues.append(
				f"search numbering is not contiguous: expected {expected_numbers}, got {actual_numbers}"
			)


def validate_metadata_and_abstracts(root, issues):
	metadata_dir = root / "metadata"
	abstracts_dir = root / "abstracts"
	metadata_files = collect_files(metadata_dir, "*.json")
	abstract_files = collect_files(abstracts_dir, "*.txt")

	metadata_stems = {name[:-5] for name in metadata_files}
	abstract_stems = {name[:-4] for name in abstract_files}

	for stem in sorted(metadata_stems - abstract_stems):
		issues.append(f"missing abstract for metadata record: {stem}")
	for stem in sorted(abstract_stems - metadata_stems):
		issues.append(f"missing metadata for abstract record: {stem}")

	for name in metadata_files:
		path = metadata_dir / name
		match = re.match(r"pmid-(\d+)-.+\.json$", name)
		try:
			data = json.loads(read_text(path))
		except json.JSONDecodeError as error:
			issues.append(f"invalid metadata json: {name}: {error}")
			continue

		if match:
			expected_pmid = match.group(1)
			uids = data.get("result", {}).get("uids", [])
			if len(uids) != 1:
				issues.append(f"unexpected uid count in metadata: {name}")
				continue
			if uids[0] != expected_pmid:
				issues.append(f"pmid mismatch in metadata: {name}: expected {expected_pmid}, got {uids[0]}")
			continue

		epmc_match = re.match(r"epmc-([a-z0-9]+)-([a-z0-9]+)-.+\.json$", name)
		if not epmc_match:
			issues.append(f"bad metadata filename: {name}")
			continue

		expected_source = epmc_match.group(1).upper()
		expected_id_slug = epmc_match.group(2)
		results = data.get("resultList", {}).get("result", [])
		if len(results) != 1:
			issues.append(f"unexpected Europe PMC result count in metadata: {name}")
			continue
		record = results[0]
		source_name = str(record.get("source") or "").upper()
		record_id = str(record.get("id") or record.get("pmid") or "")
		if source_name != expected_source:
			issues.append(f"Europe PMC source mismatch in metadata: {name}: expected {expected_source}, got {source_name}")
		if slugify(record_id) != expected_id_slug:
			issues.append(f"Europe PMC id mismatch in metadata: {name}: expected slug {expected_id_slug}, got {slugify(record_id)}")

	for name in abstract_files:
		path = abstracts_dir / name
		if not read_text(path).strip():
			issues.append(f"empty abstract content: {name}")


def validate_web(root, issues):
	web_dir = root / "web"
	web_files = sorted(path for path in web_dir.iterdir() if path.is_file()) if web_dir.exists() else []
	for path in web_files:
		content = read_text(path)
		if not content.strip():
			issues.append(f"empty web file: {path.name}")
		if path.suffix == ".html" and "<html" not in content.lower():
			issues.append(f"html file does not look like html: {path.name}")


def validate_readme_index(root, issues):
	readme = root / "README.md"
	if not readme.is_file():
		issues.append(f"missing README: {readme}")
		return

	content = read_text(readme)
	actual_searches = collect_files(root / "searches", "*.json")
	actual_metadata = collect_files(root / "metadata", "*.json")
	actual_abstracts = collect_files(root / "abstracts", "*.txt")
	actual_web = collect_files(root / "web", "*.html")

	readme_searches = sorted(re.findall(r"\| searches/(s\d+-[^|`]+\.json) \|", content))
	readme_pairs = sorted(re.findall(r"`([^`]+)\.\{json,txt\}`", content))
	readme_web = sorted(re.findall(r"\| web/([^|` ]+\.html) \|", content))

	expected_metadata = sorted(f"{stem}.json" for stem in readme_pairs)
	expected_abstracts = sorted(f"{stem}.txt" for stem in readme_pairs)

	for label, expected, actual in (
		("search index", readme_searches, actual_searches),
		("metadata index", expected_metadata, actual_metadata),
		("abstract index", expected_abstracts, actual_abstracts),
		("web index", readme_web, actual_web),
	):
		missing = sorted(set(expected) - set(actual))
		extra = sorted(set(actual) - set(expected))
		for item in missing:
			issues.append(f"{label} references missing file: {item}")
		for item in extra:
			issues.append(f"{label} is missing existing file: {item}")


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
	validate_metadata_and_abstracts(root, issues)
	validate_web(root, issues)
	validate_readme_index(root, issues)

	if issues:
		for issue in issues:
			print(f"ERROR: {issue}")
		return 1

	print("med-db validation OK")
	print(f"searches: {len(collect_files(root / 'searches', '*.json'))}")
	print(f"metadata: {len(collect_files(root / 'metadata', '*.json'))}")
	print(f"abstracts: {len(collect_files(root / 'abstracts', '*.txt'))}")
	print(f"web: {len([path for path in (root / 'web').iterdir() if path.is_file()])}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
