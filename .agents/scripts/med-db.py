#!/usr/bin/python3
import argparse
import datetime
import html
import json
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EUROPE_PMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
GOOGLE_SCHOLAR_BASE = "https://scholar.google.com/scholar"
DOAJ_ARTICLES_BASE = "https://doaj.org/search/articles"
OPEN_SCIENCE_DIRECTORY_BASE = "https://opensciencedirectory.net/"
FREE_MEDICAL_JOURNALS_BASE = "http://www.freemedicaljournals.com/"
OPENMD_BASE = "https://openmd.com/"
TRIP_DATABASE_BASE = "https://www.tripdatabase.com/Searchresult"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)
DEFAULT_SEARCH_PURPOSE = "Archived via med-db.py; review and refine purpose."
DEFAULT_PAPER_PURPOSE = "Archived via med-db.py; review and refine purpose."
DEFAULT_WEB_PURPOSE = "Archived web source; review and refine purpose."
DEFAULT_TOPIC = "_uncategorized"


def slugify(text, fallback="record", max_words=10, max_length=80):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if not text:
        return fallback
    words = [word for word in text.split("-") if word]
    text = "-".join(words[:max_words])
    return text[:max_length].rstrip("-") or fallback


def unique_filename(directory, stem, suffix):
    """Return stem.suffix, or stem-N.suffix if stem.suffix already exists."""
    candidate = f"{stem}{suffix}"
    path = directory / candidate
    if not path.exists():
        return candidate
    n = 2
    while True:
        candidate = f"{stem}-{n}{suffix}"
        if not (directory / candidate).exists():
            return candidate
        n += 1


def escape_markdown_cell(text):
    return str(text).replace("|", "\\|").strip()


def fetch_text(endpoint, params, timeout=60):
    url = f"{EUTILS_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except (urllib.error.URLError, OSError) as exc:
        print(f"error fetching {url}: {exc}", file=sys.stderr)
        raise SystemExit(1)


def fetch_europe_pmc_text(module, params, timeout=60):
    url = f"{EUROPE_PMC_BASE}/{module}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except (urllib.error.URLError, OSError) as exc:
        print(f"error fetching {url}: {exc}", file=sys.stderr)
        raise SystemExit(1)


def save_text(path, content):
    path.write_text(content, encoding="utf-8")


def ensure_med_db_structure(med_db):
    for name in ("searches", "papers", "fulltext", "guidelines", "web"):
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
        "doaj": "Directory of Open Access Journals",
        "open-science-directory": "Open Science Directory",
        "free-medical-journals": "Free Medical Journals",
        "openmd": "OpenMD",
        "trip-database": "Trip Database",
    }
    return labels.get(source_name, source_name)


def europe_pmc_article_url(source_name, record_id):
    return f"https://europepmc.org/article/{source_name}/{record_id}"


def build_google_scholar_url(query):
    return f"{GOOGLE_SCHOLAR_BASE}?{urllib.parse.urlencode({'q': query, 'hl': 'en'})}"


def build_doaj_url(query):
    payload = {
        "query": {
            "multi_match": {
                "query": query,
                "operator": "and",
            }
        },
        "size": 10,
        "track_total_hits": True,
    }
    params = {
        "ref": "homepage",
        "source": json.dumps(payload, separators=(",", ":")),
    }
    return f"{DOAJ_ARTICLES_BASE}?{urllib.parse.urlencode(params)}"


def build_trip_database_url(query):
    return f"{TRIP_DATABASE_BASE}?{urllib.parse.urlencode({'criteria': query, 'search_type': 'standard'})}"


WEB_SOURCE_SPECS = {
    "google-scholar": {
        "label": "Google Scholar",
        "filename_prefix": "google-scholar",
        "landing_url": GOOGLE_SCHOLAR_BASE,
        "query_url_builder": build_google_scholar_url,
    },
    "doaj": {
        "label": "Directory of Open Access Journals",
        "filename_prefix": "doaj",
        "landing_url": DOAJ_ARTICLES_BASE,
        "query_url_builder": build_doaj_url,
    },
    "open-science-directory": {
        "label": "Open Science Directory",
        "filename_prefix": "open-science-directory",
        "landing_url": OPEN_SCIENCE_DIRECTORY_BASE,
    },
    "free-medical-journals": {
        "label": "Free Medical Journals",
        "filename_prefix": "free-medical-journals",
        "landing_url": FREE_MEDICAL_JOURNALS_BASE,
    },
    "openmd": {
        "label": "OpenMD",
        "filename_prefix": "openmd",
        "landing_url": OPENMD_BASE,
    },
    "trip-database": {
        "label": "Trip Database",
        "filename_prefix": "trip-database",
        "landing_url": TRIP_DATABASE_BASE,
        "query_url_builder": build_trip_database_url,
    },
}


# ---------------------------------------------------------------------------
# INDEX.md generation
# ---------------------------------------------------------------------------

def load_existing_index_entries(index_path):
    """Parse existing INDEX.md to preserve user-edited purposes and metadata."""
    search_entries = {}
    paper_entries = {}
    fulltext_entries = {}
    guideline_entries = {}
    web_entries = {}

    if not index_path.is_file():
        return search_entries, paper_entries, fulltext_entries, guideline_entries, web_entries

    current_section = None
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Searches"):
            current_section = "searches"
            continue
        elif line.startswith("## Papers"):
            current_section = "papers"
            continue
        elif line.startswith("## Fulltext"):
            current_section = "fulltext"
            continue
        elif line.startswith("## Guidelines"):
            current_section = "guidelines"
            continue
        elif line.startswith("## Web"):
            current_section = "web"
            continue
        elif line.startswith("## "):
            current_section = None
            continue

        if current_section == "searches":
            match = re.match(
                r"^\| `searches/([^`]+\.json)` \| ([^|]+) \| `([^`]+)` \| ([^|]+) \| (.+) \|$",
                line,
            )
            if match:
                search_entries[match.group(1)] = {
                    "source": match.group(2).strip(),
                    "query": match.group(3),
                    "purpose": match.group(4).strip(),
                    "accessed": match.group(5).strip(),
                }
        elif current_section == "papers":
            match = re.match(
                r"^\| `papers/([^`]+)/` \| ([^|]+) \| ([^|]+) \| ([^|]+) \| (.+) \|$",
                line,
            )
            if match:
                paper_entries[match.group(1)] = {
                    "identifier": match.group(2).strip(),
                    "url": match.group(3).strip(),
                    "purpose": match.group(4).strip(),
                    "accessed": match.group(5).strip(),
                }
        elif current_section == "fulltext":
            match = re.match(
                r"^\| `fulltext/([^`]+)/` \| ([^|]+) \| ([^|]+) \| ([^|]+) \| (.+) \|$",
                line,
            )
            if match:
                fulltext_entries[match.group(1)] = {
                    "identifier": match.group(2).strip(),
                    "url": match.group(3).strip(),
                    "purpose": match.group(4).strip(),
                    "accessed": match.group(5).strip(),
                }
        elif current_section == "guidelines":
            match = re.match(
                r"^\| `guidelines/([^`]+)/` \| ([^|]+) \| ([^|]+) \| ([^|]+) \| (.+) \|$",
                line,
            )
            if match:
                guideline_entries[match.group(1)] = {
                    "source": match.group(2).strip(),
                    "url": match.group(3).strip(),
                    "purpose": match.group(4).strip(),
                    "accessed": match.group(5).strip(),
                }
        elif current_section == "web":
            match = re.match(
                r"^\| `web/([^`]+\.html)` \| ([^|]+) \| ([^|]+) \| (.+) \|$",
                line,
            )
            if match:
                web_entries[match.group(1)] = {
                    "url": match.group(2).strip(),
                    "purpose": match.group(3).strip(),
                    "accessed": match.group(4).strip(),
                }

    return search_entries, paper_entries, fulltext_entries, guideline_entries, web_entries


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


def collect_index_data(med_db):
    """Walk the filesystem and collect entries for INDEX.md."""
    today = datetime.date.today().isoformat()
    searches = []
    papers = []
    fulltexts = []
    guidelines = []
    web_sources = []

    # Searches
    searches_dir = med_db / "searches"
    if searches_dir.is_dir():
        for path in sorted(searches_dir.rglob("*.json")):
            rel = str(path.relative_to(med_db))
            query = query_from_search_json(path)
            source_name = source_from_search_json(path)
            searches.append({
                "path": rel,
                "source": source_name,
                "query": query,
                "purpose": DEFAULT_SEARCH_PURPOSE,
                "accessed": today,
            })

    # Papers
    papers_dir = med_db / "papers"
    if papers_dir.is_dir():
        for meta_path in sorted(papers_dir.rglob("metadata.json")):
            paper_dir = meta_path.parent
            rel_dir = str(paper_dir.relative_to(med_db))
            identifier, url = default_paper_entry(meta_path)
            papers.append({
                "path": rel_dir,
                "identifier": identifier,
                "url": url,
                "purpose": DEFAULT_PAPER_PURPOSE,
                "accessed": today,
            })

    # Fulltext
    fulltext_dir = med_db / "fulltext"
    if fulltext_dir.is_dir():
        for meta_path in sorted(fulltext_dir.rglob("metadata.json")):
            ft_dir = meta_path.parent
            rel_dir = str(ft_dir.relative_to(med_db))
            identifier, url = default_paper_entry(meta_path)
            fulltexts.append({
                "path": rel_dir,
                "identifier": identifier,
                "url": url,
                "purpose": DEFAULT_PAPER_PURPOSE,
                "accessed": today,
            })

    # Guidelines
    guidelines_dir = med_db / "guidelines"
    if guidelines_dir.is_dir():
        for source_path in sorted(guidelines_dir.rglob("source.*.md")):
            guideline_dir = source_path.parent
            rel_dir = str(guideline_dir.relative_to(med_db))
            guidelines.append({
                "path": rel_dir,
                "source": "Review and refine source.",
                "url": "URL unavailable; review and refine.",
                "purpose": DEFAULT_PAPER_PURPOSE,
                "accessed": today,
            })

    # Web
    web_dir = med_db / "web"
    if web_dir.is_dir():
        for path in sorted(web_dir.rglob("*.html")):
            rel = str(path.relative_to(med_db))
            web_sources.append({
                "path": rel,
                "url": "URL unavailable; review and refine.",
                "purpose": DEFAULT_WEB_PURPOSE,
                "accessed": today,
            })

    return searches, papers, fulltexts, guidelines, web_sources


def sync_index(med_db, search_updates=None, paper_updates=None, fulltext_updates=None, guideline_updates=None, web_updates=None):
    """Generate INDEX.md from filesystem, merging in user-provided metadata."""
    index_path = med_db / "INDEX.md"
    existing_searches, existing_papers, existing_fulltexts, existing_guidelines, existing_web = load_existing_index_entries(index_path)

    if search_updates:
        existing_searches.update(search_updates)
    if paper_updates:
        existing_papers.update(paper_updates)
    if fulltext_updates:
        existing_fulltexts.update(fulltext_updates)
    if guideline_updates:
        existing_guidelines.update(guideline_updates)
    if web_updates:
        existing_web.update(web_updates)

    fs_searches, fs_papers, fs_fulltexts, fs_guidelines, fs_web = collect_index_data(med_db)

    today = datetime.date.today().isoformat()
    lines = [
        "# med-db Index",
        "",
        "Archive root: `med-db/`",
        "",
        "Every archived search, paper, full-text capture, guideline, and web source must be listed here.",
        "",
    ]

    # Searches table
    lines.extend([
        "## Searches",
        "",
        "| File | Source | Query | Purpose | Accessed |",
        "|------|--------|-------|---------|----------|",
    ])
    for s in fs_searches:
        entry = existing_searches.get(s["path"], {})
        source_name = entry.get("source") or s["source"]
        query = entry.get("query") or s["query"]
        purpose = entry.get("purpose") or s["purpose"]
        accessed = entry.get("accessed") or s["accessed"]
        lines.append(
            f"| `{s['path']}` | {escape_markdown_cell(source_name)} | `{escape_markdown_cell(query)}` | {escape_markdown_cell(purpose)} | {escape_markdown_cell(accessed)} |"
        )

    # Papers table
    lines.extend([
        "",
        "## Papers",
        "",
        "| Folder | Record | URL | Purpose | Accessed |",
        "|--------|--------|-----|---------|----------|",
    ])
    for p in fs_papers:
        entry = existing_papers.get(p["path"], {})
        identifier = entry.get("identifier") or p["identifier"]
        url = entry.get("url") or p["url"]
        purpose = entry.get("purpose") or p["purpose"]
        accessed = entry.get("accessed") or p["accessed"]
        lines.append(
            f"| `{p['path']}/` | {escape_markdown_cell(identifier)} | {escape_markdown_cell(url)} | {escape_markdown_cell(purpose)} | {escape_markdown_cell(accessed)} |"
        )

    # Fulltext table
    lines.extend([
        "",
        "## Fulltext",
        "",
        "| Folder | Record | URL | Purpose | Accessed |",
        "|--------|--------|-----|---------|----------|",
    ])
    for f in fs_fulltexts:
        entry = existing_fulltexts.get(f["path"], {})
        identifier = entry.get("identifier") or f["identifier"]
        url = entry.get("url") or f["url"]
        purpose = entry.get("purpose") or f["purpose"]
        accessed = entry.get("accessed") or f["accessed"]
        lines.append(
            f"| `{f['path']}/` | {escape_markdown_cell(identifier)} | {escape_markdown_cell(url)} | {escape_markdown_cell(purpose)} | {escape_markdown_cell(accessed)} |"
        )

    # Guidelines table
    lines.extend([
        "",
        "## Guidelines",
        "",
        "| Folder | Source | URL | Purpose | Accessed |",
        "|--------|--------|-----|---------|----------|",
    ])
    for g in fs_guidelines:
        entry = existing_guidelines.get(g["path"], {})
        source = entry.get("source") or g["source"]
        url = entry.get("url") or g["url"]
        purpose = entry.get("purpose") or g["purpose"]
        accessed = entry.get("accessed") or g["accessed"]
        lines.append(
            f"| `{g['path']}/` | {escape_markdown_cell(source)} | {escape_markdown_cell(url)} | {escape_markdown_cell(purpose)} | {escape_markdown_cell(accessed)} |"
        )

    # Web table
    lines.extend([
        "",
        "## Web Sources",
        "",
        "| File | URL | Purpose | Accessed |",
        "|------|-----|---------|----------|",
    ])
    for w in fs_web:
        entry = existing_web.get(w["path"], {})
        url = entry.get("url") or w["url"]
        purpose = entry.get("purpose") or w["purpose"]
        accessed = entry.get("accessed") or w["accessed"]
        lines.append(
            f"| `{w['path']}` | {escape_markdown_cell(url)} | {escape_markdown_cell(purpose)} | {escape_markdown_cell(accessed)} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Usage Notes",
        "",
        "- Check `INDEX.md` and `searches/` before creating new searches.",
        "- For cited papers, read both `metadata.json` and `abstract.txt` in the paper folder before summarizing.",
        "- Distinguish study types when evidence conflicts: RCT, systematic review, meta-analysis, cohort, case report, in-vitro, and animal model are not interchangeable.",
        "- When new records are archived, keep `metadata.json` and `abstract.txt` in sync within each paper folder.",
        "- Use Google Scholar and other web discovery sources in this workflow; archive reproducible query pages when available.",
    ])
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Archive operations
# ---------------------------------------------------------------------------

def archive_search(args, med_db, topic):
    topic_dir = med_db / "searches" / topic
    topic_dir.mkdir(parents=True, exist_ok=True)

    if args.source == "europe-pmc":
        params = {
            "query": args.query,
            "format": "json",
            "pageSize": str(args.retmax),
        }
        raw_search = fetch_europe_pmc_text("search", params)
        parsed_search = json.loads(raw_search)
        search_slug = args.search_slug or slugify(args.query, fallback="europe-pmc-search")
        filename = unique_filename(topic_dir, f"europe-pmc-{search_slug}", ".json")
        search_file = topic_dir / filename
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
    filename = unique_filename(topic_dir, f"pubmed-{search_slug}", ".json")
    search_file = topic_dir / filename
    save_text(search_file, raw_search)
    return search_file, parsed_search.get("esearchresult", {}).get("idlist", [])


def archive_pmid(args, med_db, pmid, topic):
    params = build_common_params(args)
    params.update({"retmode": "json", "id": str(pmid)})
    raw_summary = fetch_text("esummary.fcgi", params)
    parsed_summary = json.loads(raw_summary)
    record = parsed_summary.get("result", {}).get(str(pmid), {})
    title = record.get("title") or f"pmid-{pmid}"
    paper_slug = slugify(title, fallback=f"pmid-{pmid}")
    folder_name = f"pmid-{pmid}-{paper_slug}"

    paper_dir = med_db / "papers" / topic / folder_name
    if paper_dir.exists():
        print(f"skipping already archived: {folder_name}", file=sys.stderr)
        return None, None, None, None, None
    paper_dir.mkdir(parents=True, exist_ok=True)

    metadata_file = paper_dir / "metadata.json"
    abstract_file = paper_dir / "abstract.txt"
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


def archive_europe_pmc_record(med_db, record_spec, topic):
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
    folder_name = f"epmc-{source_name.lower()}-{record_slug}-{paper_slug}"

    paper_dir = med_db / "papers" / topic / folder_name
    if paper_dir.exists():
        print(f"skipping already archived: {folder_name}", file=sys.stderr)
        return None, None, None, None, None
    paper_dir.mkdir(parents=True, exist_ok=True)

    metadata_file = paper_dir / "metadata.json"
    abstract_file = paper_dir / "abstract.txt"
    save_text(metadata_file, raw_record)

    abstract_text = record.get("abstractText") or f"Abstract unavailable from Europe PMC for {source_name}:{record_id}."
    save_text(abstract_file, abstract_text.rstrip() + "\n")

    return metadata_file, abstract_file, title, f"{source_name}:{record_id}", europe_pmc_article_url(source_name, record_id)


def archive_web_query(args, med_db, topic):
    spec = WEB_SOURCE_SPECS[args.source]
    query_url_builder = spec.get("query_url_builder")
    target_url = query_url_builder(args.query) if query_url_builder else spec["landing_url"]
    topic_dir = med_db / "web" / topic
    topic_dir.mkdir(parents=True, exist_ok=True)
    web_slug = args.search_slug or slugify(args.query, fallback=f"{spec['filename_prefix']}-search")
    filename = unique_filename(topic_dir, f"{spec['filename_prefix']}-{web_slug}", ".html")
    web_file = topic_dir / filename
    today = datetime.date.today().isoformat()
    if query_url_builder:
        archive_note = (
            f"This file archives a reproducible {spec['label']} search URL for discovery use in the med-db workflow."
        )
        link_label = f"Open this {spec['label']} query"
    else:
        archive_note = (
            "This source does not expose a stable public query URL in this workflow. "
            "This file preserves the query text together with the source landing page used for manual lookup."
        )
        link_label = f"Open the {spec['label']} search entry"
    html_body = "\n".join([
        "<!doctype html>",
        "<html lang=\"en\">",
        "<head>",
        "  <meta charset=\"utf-8\">",
        f"  <title>{spec['label']} query archive: {html.escape(args.query)}</title>",
        "</head>",
        "<body>",
        f"  <h1>{spec['label']} Query Archive</h1>",
        f"  <p><strong>Source:</strong> {spec['label']}</p>",
        f"  <p><strong>Query:</strong> {html.escape(args.query)}</p>",
        f"  <p><strong>Access date:</strong> {today}</p>",
        f"  <p>{archive_note}</p>",
        f"  <p><a href=\"{target_url}\">{link_label}</a></p>",
        "</body>",
        "</html>",
    ])
    save_text(web_file, html_body + "\n")
    return web_file, target_url


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


# ---------------------------------------------------------------------------
# Migration from old flat structure
# ---------------------------------------------------------------------------

def migrate_flat_to_topic(med_db, dry_run=False):
    """Migrate old flat metadata/ + abstracts/ into papers/_migrated/ and
    searches/*.json into searches/_migrated/.  Does not delete originals."""
    migrated = 0
    errors = 0

    old_metadata = med_db / "metadata"
    old_abstracts = med_db / "abstracts"
    old_searches = med_db / "searches"

    # Migrate papers
    if old_metadata.is_dir():
        for meta_path in sorted(old_metadata.glob("*.json")):
            stem = meta_path.stem
            abstract_path = old_abstracts / f"{stem}.txt"
            topic_dir = med_db / "papers" / "_migrated" / stem
            if topic_dir.exists():
                continue  # already migrated
            if dry_run:
                migrated += 1
                print(f"[dry-run] would migrate: {stem}")
                continue
            topic_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(meta_path, topic_dir / "metadata.json")
                if abstract_path.is_file():
                    shutil.copy2(abstract_path, topic_dir / "abstract.txt")
                else:
                    (topic_dir / "abstract.txt").write_text(
                        "Abstract not found in old flat abstracts/ directory.\n", encoding="utf-8"
                    )
                migrated += 1
            except OSError as exc:
                errors += 1
                print(f"error migrating {stem}: {exc}", file=sys.stderr)

    # Migrate searches
    if old_searches.is_dir():
        for search_path in sorted(old_searches.glob("s*.json")):
            dest_dir = med_db / "searches" / "_migrated"
            dest_file = dest_dir / search_path.name
            if dest_file.exists():
                continue
            if dry_run:
                migrated += 1
                print(f"[dry-run] would migrate search: {search_path.name}")
                continue
            dest_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(search_path, dest_file)
                migrated += 1
            except OSError as exc:
                errors += 1
                print(f"error migrating search {search_path.name}: {exc}", file=sys.stderr)

    # Migrate web
    old_web = med_db / "web"
    if old_web.is_dir():
        for web_path in sorted(old_web.glob("*.html")):
            dest_dir = med_db / "web" / "_migrated"
            dest_file = dest_dir / web_path.name
            if dest_file.exists():
                continue
            if dry_run:
                migrated += 1
                print(f"[dry-run] would migrate web: {web_path.name}")
                continue
            dest_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(web_path, dest_file)
                migrated += 1
            except OSError as exc:
                errors += 1
                print(f"error migrating web {web_path.name}: {exc}", file=sys.stderr)

    if dry_run:
        print(f"Would migrate {migrated} items ({errors} errors).")
    else:
        print(f"Migrated {migrated} items ({errors} errors).")
        if migrated > 0:
            print("Original files preserved. Verify the new structure, then remove old flat directories.")
    return 0 if errors == 0 else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Archive PubMed or Europe PMC searches, structured literature records, and source-specific web discovery queries into the local med-db schema.",
    )
    parser.add_argument(
        "--source",
        choices=("pubmed", "europe-pmc") + tuple(WEB_SOURCE_SPECS),
        default="pubmed",
        help="Primary source for the current run. Defaults to pubmed.",
    )
    parser.add_argument("--query", help="Search query to archive for the selected source.")
    parser.add_argument("--search-slug", help="Optional slug for the saved search file.")
    parser.add_argument(
        "--topic",
        help="Medical topic for grouping output (e.g. endometriosis, weight-loss, adhd). Defaults to '_uncategorized'.",
        default=DEFAULT_TOPIC,
    )
    parser.add_argument(
        "--topic-slug",
        help="Explicit kebab-case slug for the topic folder. Overrides --topic if both are given.",
    )
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
        help="How many machine-readable hits to request for the archived search JSON.",
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
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Migrate existing flat med-db/ structure to topic-based per-paper folders. Preserves originals.",
    )
    parser.add_argument(
        "--migrate-dry-run",
        action="store_true",
        help="Preview --migrate without copying files.",
    )
    args = parser.parse_args()

    if args.migrate or args.migrate_dry_run:
        return args

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
    if args.source in WEB_SOURCE_SPECS and args.archive_first:
        parser.error("--archive-first is not supported with web discovery sources")
    if args.retmax < 1:
        parser.error("--retmax must be >= 1")
    return args


def main():
    args = parse_args()
    med_db = Path(args.med_db)

    if args.migrate or args.migrate_dry_run:
        med_db.mkdir(parents=True, exist_ok=True)
        return migrate_flat_to_topic(med_db, dry_run=args.migrate_dry_run)

    med_db.mkdir(parents=True, exist_ok=True)
    ensure_med_db_structure(med_db)

    topic = args.topic_slug or slugify(args.topic, fallback=DEFAULT_TOPIC)

    search_file = None
    search_updates = {}
    paper_updates = {}
    web_updates = {}
    pmids = list(args.pmid)
    epmc_records = list(args.epmc_record)
    if args.query:
        if args.source in WEB_SOURCE_SPECS:
            web_file, query_url = archive_web_query(args, med_db, topic)
            web_updates[str(web_file.relative_to(med_db))] = {
                "url": query_url,
                "purpose": DEFAULT_WEB_PURPOSE,
                "accessed": datetime.date.today().isoformat(),
            }
        else:
            search_file, search_hits = archive_search(args, med_db, topic)
            search_updates[str(search_file.relative_to(med_db))] = {
                "source": source_label(args.source),
                "query": args.query,
                "purpose": DEFAULT_SEARCH_PURPOSE,
                "accessed": datetime.date.today().isoformat(),
            }
            if args.source == "pubmed":
                pmids.extend(search_hits[:args.archive_first])
            else:
                epmc_records.extend(search_hits[:args.archive_first])

    pmids = dedupe([str(pmid) for pmid in pmids])
    epmc_records = dedupe([r.upper() for r in epmc_records])
    archived = []
    for index, pmid in enumerate(pmids):
        metadata_file, abstract_file, title, identifier, url = archive_pmid(args, med_db, pmid, topic)
        if metadata_file is None:
            continue
        archived.append((identifier, metadata_file, abstract_file, title))
        paper_updates[str(metadata_file.parent.relative_to(med_db))] = {
            "identifier": identifier,
            "url": url,
            "purpose": DEFAULT_PAPER_PURPOSE,
            "accessed": datetime.date.today().isoformat(),
        }
        if index < len(pmids) - 1 and args.delay > 0:
            time.sleep(args.delay)

    for index, record_spec in enumerate(epmc_records):
        metadata_file, abstract_file, title, identifier, url = archive_europe_pmc_record(med_db, record_spec, topic)
        if metadata_file is None:
            continue
        archived.append((identifier, metadata_file, abstract_file, title))
        paper_updates[str(metadata_file.parent.relative_to(med_db))] = {
            "identifier": identifier,
            "url": url,
            "purpose": DEFAULT_PAPER_PURPOSE,
            "accessed": datetime.date.today().isoformat(),
        }
        if index < len(epmc_records) - 1 and args.delay > 0:
            time.sleep(args.delay)

    sync_index(med_db, search_updates, paper_updates, web_updates)

    if search_file:
        print(f"saved search: {search_file}")
    elif web_updates:
        print("saved search: none")
        print("archived web sources:")
        for filename, details in sorted(web_updates.items()):
            print(f"- {filename}: {details['url']}")
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
        print(f"  folder: {metadata_file.parent}")

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
