#!/usr/bin/python3
import argparse
import datetime
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path


EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EUROPE_PMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
GOOGLE_SCHOLAR_BASE = "https://scholar.google.com/scholar"
USER_AGENT = (
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
	"(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)
DEFAULT_SEARCH_PURPOSE = "Archived via med-db.py; review and refine purpose."
DEFAULT_PAPER_PURPOSE = "Archived via med-db.py; review and refine purpose."
DEFAULT_WEB_PURPOSE = "Archived web source; review and refine purpose."


def slugify(text, fallback="record", max_words=10, max_length=80):
	text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
	text = text.lower()
	text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
	if not text:
		return fallback
	words = [word for word in text.split("-") if word]
	text = "-".join(words[:max_words])
	return text[:max_length].rstrip("-") or fallback


def next_search_filename(search_dir, slug):
	max_index = 0
	for path in search_dir.glob("s*-*.json"):
		match = re.match(r"s(\d+)-", path.name)
		if match:
			max_index = max(max_index, int(match.group(1)))
	return f"s{max_index + 1:02d}-{slug}.json"


def escape_markdown_cell(text):
	return str(text).replace("|", "\\|").strip()


def fetch_text(endpoint, params, timeout=60):
	url = f"{EUTILS_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
	request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
	with urllib.request.urlopen(request, timeout=timeout) as response:
		return response.read().decode("utf-8")


def fetch_europe_pmc_text(module, params, timeout=60):
	url = f"{EUROPE_PMC_BASE}/{module}?{urllib.parse.urlencode(params)}"
	request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
	with urllib.request.urlopen(request, timeout=timeout) as response:
		return response.read().decode("utf-8")


def save_text(path, content):
	path.write_text(content, encoding="utf-8")


def ensure_med_db_structure(med_db):
	for name in ("searches", "metadata", "abstracts", "web"):
		(med_db / name).mkdir(parents=True, exist_ok=True)


def build_common_params(args):
	params = {"db": "pubmed"}
	if args.email:
		params["email"] = args.email
	params["tool"] = "med-db"
	return params


def source_label(source_name):
	labels = {
		"pubmed": "PubMed",
		"europe-pmc": "Europe PMC",
		"google-scholar": "Google Scholar",
	}
	return labels.get(source_name, source_name)


def europe_pmc_article_url(source_name, record_id):
	return f"https://europepmc.org/article/{source_name}/{record_id}"


def build_google_scholar_url(query):
	return f"{GOOGLE_SCHOLAR_BASE}?{urllib.parse.urlencode({'q': query, 'hl': 'en'})}"


def load_existing_readme_entries(readme_path):
	search_entries = {}
	paper_entries = {}
	web_entries = {}

	if not readme_path.is_file():
		return search_entries, paper_entries, web_entries

	for line in readme_path.read_text(encoding="utf-8").splitlines():
		search_match = re.match(
			r"^\| searches/(s\d{2}-[^|`]+\.json) \| ([^|]+) \| `([^`]+)` \| (.+) \|$",
			line,
		)
		if search_match:
			search_entries[search_match.group(1)] = {
				"source": search_match.group(2).strip(),
				"query": search_match.group(3),
				"purpose": search_match.group(4),
			}
			continue

		search_match = re.match(
			r"^\| searches/(s\d{2}-[^|`]+\.json) \| `([^`]+)` \| (.+) \|$",
			line,
		)
		if search_match:
			search_entries[search_match.group(1)] = {
				"source": "PubMed",
				"query": search_match.group(2),
				"purpose": search_match.group(3),
			}
			continue

		paper_match = re.match(
			r"^\| `([^`]+)\.\{json,txt\}` \| ([^|]+) \| ([^|]+) \| (.+) \|$",
			line,
		)
		if paper_match:
			paper_entries[paper_match.group(1)] = {
				"identifier": paper_match.group(2).strip(),
				"url": paper_match.group(3).strip(),
				"purpose": paper_match.group(4),
			}
			continue

		web_match = re.match(
			r"^\| web/([^|` ]+\.html) \| ([^|]+) \| (.+) \|$",
			line,
		)
		if web_match:
			web_entries[web_match.group(1)] = {
				"url": web_match.group(2).strip(),
				"purpose": web_match.group(3),
			}

	return search_entries, paper_entries, web_entries


def query_from_search_json(path):
	data = json.loads(path.read_text(encoding="utf-8"))
	result = data.get("esearchresult", {})
	if result:
		return result.get("querytranslation") or "Query unavailable; review and refine."
	request = data.get("request", {})
	return request.get("queryString") or request.get("query") or "Query unavailable; review and refine."


def source_from_search_json(path):
	data = json.loads(path.read_text(encoding="utf-8"))
	if data.get("esearchresult"):
		return "PubMed"
	if data.get("request") and data.get("resultList") is not None:
		return "Europe PMC"
	return "Unknown"


def default_paper_entry(path):
	data = json.loads(path.read_text(encoding="utf-8"))
	pubmed_result = data.get("result", {})
	if isinstance(pubmed_result, dict) and "uids" in pubmed_result:
		uids = pubmed_result.get("uids", [])
		if len(uids) == 1:
			pmid = str(uids[0])
			return f"PMID:{pmid}", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

	europe_pmc_results = data.get("resultList", {}).get("result", [])
	if europe_pmc_results:
		record = europe_pmc_results[0]
		source_name = str(record.get("source") or "EPMC")
		record_id = str(record.get("id") or record.get("pmid") or "unknown")
		return f"{source_name}:{record_id}", europe_pmc_article_url(source_name, record_id)

	return "unknown", "URL unavailable; review and refine."


def sync_readme(med_db, search_updates, paper_updates, web_updates=None):
	readme_path = med_db / "README.md"
	existing_searches, existing_papers, existing_web = load_existing_readme_entries(readme_path)
	existing_searches.update(search_updates)
	existing_papers.update(paper_updates)
	if web_updates:
		existing_web.update(web_updates)

	search_lines = []
	for path in sorted((med_db / "searches").glob("*.json")):
		entry = existing_searches.get(path.name, {})
		query = entry.get("query") or query_from_search_json(path)
		source_name = entry.get("source") or source_from_search_json(path)
		purpose = entry.get("purpose") or DEFAULT_SEARCH_PURPOSE
		search_lines.append(
			f"| searches/{path.name} | {escape_markdown_cell(source_name)} | `{escape_markdown_cell(query)}` | {escape_markdown_cell(purpose)} |"
		)

	paper_lines = []
	for path in sorted((med_db / "metadata").glob("*.json")):
		stem = path.stem
		entry = existing_papers.get(stem, {})
		identifier, default_url = default_paper_entry(path)
		identifier = entry.get("identifier") or identifier
		url = entry.get("url") or default_url
		purpose = entry.get("purpose") or DEFAULT_PAPER_PURPOSE
		paper_lines.append(
			f"| `{stem}.{{json,txt}}` | {escape_markdown_cell(identifier)} | {escape_markdown_cell(url)} | {escape_markdown_cell(purpose)} |"
		)

	web_lines = []
	for path in sorted((med_db / "web").glob("*.html")):
		entry = existing_web.get(path.name, {})
		url = entry.get("url") or "URL unavailable; review and refine."
		purpose = entry.get("purpose") or DEFAULT_WEB_PURPOSE
		web_lines.append(
			f"| web/{path.name} | {escape_markdown_cell(url)} | {escape_markdown_cell(purpose)} |"
		)

	today = datetime.date.today().isoformat()
	content = [
		"# med-db - Scientific Reference Archive",
		"",
		f"Collected search results, metadata, abstracts, and archived web sources. Saved on {today}.",
		"",
		"Sources: PubMed via NCBI E-utilities, Europe PMC via the REST API, and archived web sources such as Google Scholar search definitions.",
		"",
		"Note: this archive prefers machine-readable search results and greppable abstract text over brittle HTML scraping.",
		"",
		"## Structure",
		"",
		"- `searches/`: raw search responses from supported literature APIs as JSON",
		"- `metadata/`: raw record metadata as JSON",
		"- `abstracts/`: abstract text per archived record as text files",
		"- `web/`: archived web pages or reproducible search definition pages used in review",
		"",
		"---",
		"",
		"## Search Archives (`searches/*.json`)",
		"",
		"| File | Source | Query | Purpose |",
		"|------|--------|-------|---------|",
	]
	content.extend(search_lines)
	content.extend([
		"",
		"---",
		"",
		"## Literature Records (`metadata/*.json` + `abstracts/*.txt`)",
		"",
		"| Files | Record | URL | Purpose |",
		"|-------|--------|-----|---------|",
	])
	content.extend(paper_lines)
	content.extend([
		"",
		"---",
		"",
		"## Web Sources (`web/*`)",
		"",
		"| File | URL | Purpose |",
		"|------|-----|---------|",
	])
	content.extend(web_lines)
	content.extend([
		"",
		"---",
		"",
		"## Usage Notes For Future Runs",
		"",
		"- Check `searches/` before creating new machine-readable searches.",
		"- For cited records, read both `metadata/` and `abstracts/` before summarizing.",
		"- Distinguish study types when evidence conflicts: risk, therapy, biomarker, and animal model are not interchangeable.",
		"- When new structured records are archived, keep both `metadata/*.json` and `abstracts/*.txt` in sync.",
		"- Use Google Scholar as a discovery surface in this workflow; archive reproducible query pages or downstream accessible sources in `web/` rather than relying on fragile structured scraping.",
	])
	readme_path.write_text("\n".join(content) + "\n", encoding="utf-8")


def archive_search(args, med_db):
	if args.source == "europe-pmc":
		params = {
			"query": args.query,
			"format": "json",
			"pageSize": str(args.retmax),
		}
		raw_search = fetch_europe_pmc_text("search", params)
		parsed_search = json.loads(raw_search)
		search_slug = args.search_slug or slugify(args.query, fallback="europe-pmc-search")
		search_dir = med_db / "searches"
		search_dir.mkdir(parents=True, exist_ok=True)
		search_file = search_dir / next_search_filename(search_dir, search_slug)
		save_text(search_file, raw_search)
		records = []
		for item in parsed_search.get("resultList", {}).get("result", []):
			source_name = item.get("source")
			record_id = item.get("id")
			if source_name and record_id:
				records.append(f"{source_name}:{record_id}")
		return search_file, records

	params = build_common_params(args)
	params.update({
		"retmode": "json",
		"term": args.query,
		"retmax": str(args.retmax),
	})
	raw_search = fetch_text("esearch.fcgi", params)
	parsed_search = json.loads(raw_search)
	search_slug = args.search_slug or slugify(args.query, fallback="pubmed-search")
	search_dir = med_db / "searches"
	search_dir.mkdir(parents=True, exist_ok=True)
	search_file = search_dir / next_search_filename(search_dir, search_slug)
	save_text(search_file, raw_search)
	return search_file, parsed_search.get("esearchresult", {}).get("idlist", [])


def archive_pmid(args, med_db, pmid):
	params = build_common_params(args)
	params.update({"retmode": "json", "id": str(pmid)})
	raw_summary = fetch_text("esummary.fcgi", params)
	parsed_summary = json.loads(raw_summary)
	record = parsed_summary.get("result", {}).get(str(pmid), {})
	title = record.get("title") or f"pmid-{pmid}"
	paper_slug = slugify(title, fallback=f"pmid-{pmid}")

	metadata_dir = med_db / "metadata"
	abstracts_dir = med_db / "abstracts"
	metadata_dir.mkdir(parents=True, exist_ok=True)
	abstracts_dir.mkdir(parents=True, exist_ok=True)

	metadata_file = metadata_dir / f"pmid-{pmid}-{paper_slug}.json"
	abstract_file = abstracts_dir / f"pmid-{pmid}-{paper_slug}.txt"
	save_text(metadata_file, raw_summary)

	params = build_common_params(args)
	params.update({
		"id": str(pmid),
		"rettype": "abstract",
		"retmode": "text",
	})
	raw_abstract = fetch_text("efetch.fcgi", params)
	save_text(abstract_file, raw_abstract)

	return metadata_file, abstract_file, title, f"PMID:{pmid}", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"


def parse_europe_pmc_record(record_spec):
	source_name, separator, record_id = record_spec.partition(":")
	if not separator or not source_name or not record_id:
		raise ValueError(f"invalid Europe PMC record spec: {record_spec}; expected SOURCE:ID")
	return source_name.upper(), record_id


def archive_europe_pmc_record(med_db, record_spec):
	source_name, record_id = parse_europe_pmc_record(record_spec)
	params = {
		"query": f"EXT_ID:{record_id} AND SRC:{source_name}",
		"resultType": "core",
		"format": "json",
		"pageSize": "1",
	}
	raw_record = fetch_europe_pmc_text("search", params)
	parsed_record = json.loads(raw_record)
	results = parsed_record.get("resultList", {}).get("result", [])
	if not results:
		raise RuntimeError(f"Europe PMC record not found: {record_spec}")

	record = results[0]
	title = record.get("title") or f"{source_name}:{record_id}"
	paper_slug = slugify(title, fallback=f"{source_name.lower()}-{record_id.lower()}")
	record_slug = slugify(record_id, fallback="record")

	metadata_dir = med_db / "metadata"
	abstracts_dir = med_db / "abstracts"
	metadata_dir.mkdir(parents=True, exist_ok=True)
	abstracts_dir.mkdir(parents=True, exist_ok=True)

	metadata_file = metadata_dir / f"epmc-{source_name.lower()}-{record_slug}-{paper_slug}.json"
	abstract_file = abstracts_dir / f"epmc-{source_name.lower()}-{record_slug}-{paper_slug}.txt"
	save_text(metadata_file, raw_record)

	abstract_text = record.get("abstractText") or f"Abstract unavailable from Europe PMC for {source_name}:{record_id}."
	save_text(abstract_file, abstract_text.rstrip() + "\n")

	return metadata_file, abstract_file, title, f"{source_name}:{record_id}", europe_pmc_article_url(source_name, record_id)


def archive_google_scholar_query(args, med_db):
	query_url = build_google_scholar_url(args.query)
	web_dir = med_db / "web"
	web_dir.mkdir(parents=True, exist_ok=True)
	search_slug = args.search_slug or slugify(args.query, fallback="google-scholar-search")
	web_file = web_dir / f"google-scholar-{search_slug}.html"
	today = datetime.date.today().isoformat()
	html = "\n".join([
		"<!doctype html>",
		"<html lang=\"en\">",
		"<head>",
		"  <meta charset=\"utf-8\">",
		f"  <title>Google Scholar query archive: {args.query}</title>",
		"</head>",
		"<body>",
		"  <h1>Google Scholar Query Archive</h1>",
		f"  <p><strong>Query:</strong> {args.query}</p>",
		f"  <p><strong>Access date:</strong> {today}</p>",
		"  <p>This file archives a reproducible Google Scholar search URL for discovery use in the med-db workflow.</p>",
		f"  <p><a href=\"{query_url}\">Open this Google Scholar query</a></p>",
		"</body>",
		"</html>",
	])
	save_text(web_file, html + "\n")
	return web_file, query_url


def dedupe(values):
	seen = set()
	ordered = []
	for value in values:
		if value in seen:
			continue
		seen.add(value)
		ordered.append(value)
	return ordered


def run_validator(med_db):
	validator = Path(__file__).with_name("med-db-validate.py")
	if not validator.is_file():
		print(f"validator script not found: {validator}", file=sys.stderr)
		return 1

	result = subprocess.run(
		[sys.executable, str(validator), "--med-db", str(med_db)],
		check=False,
	)
	return result.returncode


def parse_args():
	parser = argparse.ArgumentParser(
		description="Archive PubMed or Europe PMC searches, structured literature records, and Google Scholar query definitions into the local med-db schema.",
	)
	parser.add_argument(
		"--source",
		choices=("pubmed", "europe-pmc", "google-scholar"),
		default="pubmed",
		help="Primary source for the current run. Defaults to pubmed.",
	)
	parser.add_argument("--query", help="Search query to archive for the selected source.")
	parser.add_argument("--search-slug", help="Optional slug for the saved search file.")
	parser.add_argument(
		"--pmid",
		action="append",
		default=[],
		help="PMID to archive. May be passed multiple times.",
	)
	parser.add_argument(
		"--epmc-record",
		action="append",
		default=[],
		help="Europe PMC record to archive as SOURCE:ID. May be passed multiple times.",
	)
	parser.add_argument(
		"--archive-first",
		type=int,
		default=0,
		help="Also archive the first N PMIDs returned by --query.",
	)
	parser.add_argument(
		"--retmax",
		type=int,
		default=20,
		help="How many PubMed hits to request for the archived search JSON.",
	)
	parser.add_argument(
		"--med-db",
		default="med-db",
		help="Target med-db directory. Defaults to ./med-db.",
	)
	parser.add_argument(
		"--email",
		help="Optional contact email passed to NCBI E-utilities.",
	)
	parser.add_argument(
		"--delay",
		type=float,
		default=0.34,
		help="Delay between PMID fetches in seconds. Defaults to 0.34.",
	)
	parser.add_argument(
		"--validate",
		action="store_true",
		help="Run med-db-validate.py after the archival step and return its exit status on failure.",
	)
	args = parser.parse_args()
	if not args.query and not args.pmid and not args.epmc_record:
		parser.error("provide --query and/or at least one record identifier")
	if args.source != "pubmed" and args.pmid:
		parser.error("--pmid is only supported with --source pubmed")
	if args.source != "europe-pmc" and args.epmc_record:
		parser.error("--epmc-record is only supported with --source europe-pmc")
	if args.archive_first < 0:
		parser.error("--archive-first must be >= 0")
	if args.archive_first and not args.query:
		parser.error("--archive-first requires --query")
	if args.source == "google-scholar" and args.archive_first:
		parser.error("--archive-first is not supported with --source google-scholar")
	if args.retmax < 1:
		parser.error("--retmax must be >= 1")
	return args


def main():
	args = parse_args()
	med_db = Path(args.med_db)
	med_db.mkdir(parents=True, exist_ok=True)
	ensure_med_db_structure(med_db)

	search_file = None
	search_updates = {}
	paper_updates = {}
	web_updates = {}
	pmids = list(args.pmid)
	epmc_records = list(args.epmc_record)
	if args.query:
		if args.source == "google-scholar":
			web_file, query_url = archive_google_scholar_query(args, med_db)
			web_updates[web_file.name] = {
				"url": query_url,
				"purpose": DEFAULT_WEB_PURPOSE,
			}
		else:
			search_file, search_hits = archive_search(args, med_db)
			search_updates[search_file.name] = {
				"source": source_label(args.source),
				"query": args.query,
				"purpose": DEFAULT_SEARCH_PURPOSE,
			}
			if args.source == "pubmed":
				pmids.extend(search_hits[:args.archive_first])
			else:
				epmc_records.extend(search_hits[:args.archive_first])

	pmids = dedupe([str(pmid) for pmid in pmids])
	epmc_records = dedupe(epmc_records)
	archived = []
	for index, pmid in enumerate(pmids):
		metadata_file, abstract_file, title, identifier, url = archive_pmid(args, med_db, pmid)
		archived.append((identifier, metadata_file, abstract_file, title))
		paper_updates[metadata_file.stem] = {
			"identifier": identifier,
			"url": url,
			"purpose": DEFAULT_PAPER_PURPOSE,
		}
		if index < len(pmids) - 1 and args.delay > 0:
			time.sleep(args.delay)

	for index, record_spec in enumerate(epmc_records):
		metadata_file, abstract_file, title, identifier, url = archive_europe_pmc_record(med_db, record_spec)
		archived.append((identifier, metadata_file, abstract_file, title))
		paper_updates[metadata_file.stem] = {
			"identifier": identifier,
			"url": url,
			"purpose": DEFAULT_PAPER_PURPOSE,
		}
		if index < len(epmc_records) - 1 and args.delay > 0:
			time.sleep(args.delay)

	sync_readme(med_db, search_updates, paper_updates, web_updates)

	if search_file:
		print(f"saved search: {search_file}")
	elif web_updates:
		print("saved search: none")
		print("archived web sources:")
		for filename, details in sorted(web_updates.items()):
			print(f"- web/{filename}: {details['url']}")
	else:
		print("saved search: none")

	if not archived:
		print("archived structured records: none")
		if args.validate:
			print("running validator...")
			return run_validator(med_db)
		return 0

	print("archived structured records:")
	for identifier, metadata_file, abstract_file, title in archived:
		print(f"- {identifier}: {title}")
		print(f"  metadata: {metadata_file}")
		print(f"  abstract: {abstract_file}")

	if args.validate:
		print("running validator...")
		return run_validator(med_db)

	return 0


if __name__ == "__main__":
	try:
		raise SystemExit(main())
	except KeyboardInterrupt:
		print("cancelled", file=sys.stderr)
		raise SystemExit(130)
