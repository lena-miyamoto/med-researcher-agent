import argparse
import datetime
import html
import json
import re
import shutil
import sys
import time
import urllib.parse
from pathlib import Path

import utils

# ---------------------------------------------------------------------------
# Web-source URL bases (only used in this module)
# ---------------------------------------------------------------------------

GOOGLE_SCHOLAR_BASE = "https://scholar.google.com/scholar"
DOAJ_ARTICLES_BASE = "https://doaj.org/search/articles"
OPEN_SCIENCE_DIRECTORY_BASE = "https://opensciencedirectory.net/"
FREE_MEDICAL_JOURNALS_BASE = "http://www.freemedicaljournals.com/"
OPENMD_BASE = "https://openmd.com/"
TRIP_DATABASE_BASE = "https://www.tripdatabase.com/Searchresult"

DEFAULT_SEARCH_PURPOSE = "Archived via med-db.py; review and refine purpose."
DEFAULT_PAPER_PURPOSE = "Archived via med-db.py; review and refine purpose."
DEFAULT_WEB_PURPOSE = "Archived web source; review and refine purpose."
DEFAULT_TOPIC = "uncategorized"


# Re-export canonical slugify for convenience (tests reference it via med_db.slugify)
slugify = utils.slugify


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



# ---------------------------------------------------------------------------
# Thin fetch wrappers — delegate to utils, convert RuntimeError → SystemExit
# for CLI use
# ---------------------------------------------------------------------------


def _fetch_text(endpoint, params, timeout=60):
    try:
        return utils.fetch_pubmed(endpoint, params, timeout)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)


def _fetch_europe_pmc_text(module, params, timeout=60):
    try:
        return utils.fetch_europe_pmc(module, params, timeout)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)


# Re-export shared helpers (referenced by other modules and tests)
europe_pmc_article_url = utils.europe_pmc_article_url
default_paper_entry = utils.default_paper_entry


def save_text(path, content):
    utils.atomic_write(path, content)


def ensure_med_db_structure(med_db):
    for name in ("searches", "papers", "fulltext", "guidelines", "web", "dictionary"):
        (med_db / name).mkdir(parents=True, exist_ok=True)


def validate_topic_slug(topic):
    if not topic or topic in {".", ".."} or "/" in topic or "\\" in topic:
        raise ValueError(f"invalid topic slug: {topic!r}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", topic):
        raise ValueError(f"invalid topic slug: {topic!r}; expected kebab-case ASCII")
    return topic


def build_common_params(args):
    params = {"db": "pubmed"}
    if args.email:
        params["email"] = args.email
    params["tool"] = "med-db"
    return params


def source_label(source_name):
    # PubMed / Europe PMC are not web discovery sources; handle them directly.
    if source_name == "pubmed":
        return "PubMed"
    if source_name == "europe-pmc":
        return "Europe PMC"
    spec = WEB_SOURCE_SPECS.get(source_name)
    if spec:
        return spec["label"]
    return source_name


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
    params = {"criteria": query, "search_type": "standard"}
    return f"{TRIP_DATABASE_BASE}?{urllib.parse.urlencode(params)}"


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
# index.json generation
# ---------------------------------------------------------------------------


def load_existing_index_entries(index_path):
    """Parse existing index.json to preserve user-edited purposes and metadata."""
    if not index_path.is_file():
        return {}, {}, {}, {}, {}, {}

    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}, {}, {}, {}, {}, {}

    search_entries = {entry["path"]: {k: v for k, v in entry.items() if k != "path"} for entry in data.get("searches", [])}
    paper_entries = {entry["path"]: {k: v for k, v in entry.items() if k != "path"} for entry in data.get("papers", [])}
    fulltext_entries = {entry["path"]: {k: v for k, v in entry.items() if k != "path"} for entry in data.get("fulltext", [])}
    guideline_entries = {entry["path"]: {k: v for k, v in entry.items() if k != "path"} for entry in data.get("guidelines", [])}
    web_entries = {entry["path"]: {k: v for k, v in entry.items() if k != "path"} for entry in data.get("web", [])}
    dictionary_entries = {entry["path"]: {k: v for k, v in entry.items() if k != "path"} for entry in data.get("dictionary", [])}

    return search_entries, paper_entries, fulltext_entries, guideline_entries, web_entries, dictionary_entries


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


def collect_index_data(med_db):
    """Walk the filesystem and collect entries for index.json."""
    today = datetime.date.today().isoformat()
    searches = []
    papers = []
    fulltexts = []
    guidelines = []
    web_sources = []
    dictionary = []

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

    # Guidelines — scan both source.md and source.LANG.md patterns
    guidelines_dir = med_db / "guidelines"
    if guidelines_dir.is_dir():
        seen_dirs = set()
        for pattern in ("source.md", "source.*.md"):
            for source_path in sorted(guidelines_dir.rglob(pattern)):
                guideline_dir = source_path.parent
                rel_dir = str(guideline_dir.relative_to(med_db))
                if rel_dir in seen_dirs:
                    continue
                seen_dirs.add(rel_dir)
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

    # Dictionary — term definitions archived by the define-terms skill
    dictionary_dir = med_db / "dictionary"
    if dictionary_dir.is_dir():
        for meta_path in sorted(dictionary_dir.rglob("metadata.json")):
            term_dir = meta_path.parent
            rel_dir = str(term_dir.relative_to(med_db))
            entry = _dictionary_entry(meta_path)
            dictionary.append({
                "path": rel_dir,
                "term": entry.get("term") or "Term unavailable; review and refine.",
                "english": entry.get("english") or "",
                "source_type": entry.get("source_type") or "other",
                "source_ref": entry.get("source_ref") or "",
                "accessed": today,
            })

    return searches, papers, fulltexts, guidelines, web_sources, dictionary


def _dictionary_entry(meta_path):
    """Read a dictionary ``metadata.json`` and return its contents, or empty on failure."""
    try:
        data = json.loads(Path(meta_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def sync_index(med_db, search_updates=None, paper_updates=None, fulltext_updates=None, guideline_updates=None, web_updates=None, dictionary_updates=None):
    """Generate index.json from filesystem, merging in user-provided metadata."""
    index_path = med_db / "index.json"
    existing_searches, existing_papers, existing_fulltexts, existing_guidelines, existing_web, existing_dictionary = load_existing_index_entries(index_path)

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
    if dictionary_updates:
        existing_dictionary.update(dictionary_updates)

    fs_searches, fs_papers, fs_fulltexts, fs_guidelines, fs_web, fs_dictionary = collect_index_data(med_db)

    def _merge(fs_list, existing_dict):
        """Merge filesystem-derived items with existing index entries.

        Filesystem data provides the canonical base (path, identifier,
        url, source, query, accessed).  All existing entry fields are
        overlaid so user edits (purpose, notes, etc.) are preserved.
        """
        result = []
        for item in fs_list:
            entry = existing_dict.get(item["path"], {})
            merged = dict(item)
            merged.update(entry)
            result.append(merged)
        return result

    index_data = {
        "searches": _merge(fs_searches, existing_searches),
        "papers": _merge(fs_papers, existing_papers),
        "fulltext": _merge(fs_fulltexts, existing_fulltexts),
        "guidelines": _merge(fs_guidelines, existing_guidelines),
        "web": _merge(fs_web, existing_web),
        "dictionary": _merge(fs_dictionary, existing_dictionary),
    }
    index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
        raw_search = _fetch_europe_pmc_text("search", params)
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
    raw_search = _fetch_text("esearch.fcgi", params)
    parsed_search = json.loads(raw_search)
    search_slug = args.search_slug or slugify(args.query, fallback="pubmed-search")
    filename = unique_filename(topic_dir, f"pubmed-{search_slug}", ".json")
    search_file = topic_dir / filename
    save_text(search_file, raw_search)
    return search_file, parsed_search.get("esearchresult", {}).get("idlist", [])


def archive_pmid(args, med_db, pmid, topic):
    params = build_common_params(args)
    params.update({"retmode": "json", "id": str(pmid)})
    raw_summary = _fetch_text("esummary.fcgi", params)
    parsed_summary = json.loads(raw_summary)
    record = parsed_summary.get("result", {}).get(str(pmid), {})
    if "error" in record:
        raise RuntimeError(f"PubMed API error for PMID {pmid}: {record['error']}")
    title = record.get("title") or f"pmid-{pmid}"
    paper_slug = slugify(title, fallback=f"pmid-{pmid}")
    folder_name = f"pmid-{pmid}-{paper_slug}"

    paper_dir = med_db / "papers" / topic / folder_name
    if not args.force and paper_dir.exists():
        print(f"skipping already archived: {folder_name}", file=sys.stderr)
        return None
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
    try:
        raw_abstract = utils.fetch_pubmed("efetch.fcgi", params)
    except RuntimeError as exc:
        print(f"warning: could not fetch abstract for PMID {pmid}: {exc}", file=sys.stderr)
        raw_abstract = f"Abstract unavailable from PubMed for PMID {pmid}.\n"
    save_text(abstract_file, raw_abstract)

    return metadata_file, abstract_file, title, f"PMID:{pmid}", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"


def parse_europe_pmc_record(record_spec):
    source_name, separator, record_id = record_spec.partition(":")
    if not separator or not source_name or not record_id:
        raise ValueError(f"invalid Europe PMC record spec: {record_spec}; expected SOURCE:ID")
    return source_name.upper(), record_id


def archive_europe_pmc_record(med_db, record_spec, topic, force=False):
    source_name, record_id = parse_europe_pmc_record(record_spec)
    params = {
        "query": f"EXT_ID:{record_id} AND SRC:{source_name}",
        "resultType": "core",
        "format": "json",
        "pageSize": "1",
    }
    raw_record = _fetch_europe_pmc_text("search", params)
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
    if not force and paper_dir.exists():
        print(f"skipping already archived: {folder_name}", file=sys.stderr)
        return None
    paper_dir.mkdir(parents=True, exist_ok=True)

    metadata_file = paper_dir / "metadata.json"
    abstract_file = paper_dir / "abstract.txt"
    save_text(metadata_file, raw_record)

    abstract_text = record.get("abstractText") or f"Abstract unavailable from Europe PMC for {source_name}:{record_id}."
    save_text(abstract_file, abstract_text.rstrip() + "\n")

    return metadata_file, abstract_file, title, f"{source_name}:{record_id}", europe_pmc_article_url(source_name, record_id)


def _crossref_title(message):
    """Return the first non-empty title from a Crossref work *message*."""
    for title in message.get("title") or []:
        if title and str(title).strip():
            return str(title).strip()
    return None


def _crossref_abstract(message):
    """Return plain-text abstract from a Crossref work *message*, or None."""
    abstract = message.get("abstract")
    if not abstract:
        return None
    return utils._strip_html(str(abstract))


def archive_crossref_doi(med_db, doi, topic, force=False):
    """Archive a paper directly from Crossref metadata for a DOI.

    Used when the DOI is not indexed in PubMed or Europe PMC (e.g. APA
    journals).  Returns the same result tuple shape as ``archive_pmid`` and
    ``archive_europe_pmc_record``, or ``None`` when already archived (unless
    *force* is true).  Raises ``RuntimeError`` when Crossref has no record for
    the DOI.
    """
    raw_work = utils.fetch_crossref_work(doi)
    message = json.loads(raw_work).get("message", {})
    if not message:
        raise RuntimeError(f"Crossref record not found for DOI {doi}")

    title = _crossref_title(message) or doi
    paper_slug = slugify(title, fallback="crossref-record")
    doi_slug = slugify(doi, fallback="doi")
    folder_name = f"crossref-{doi_slug}-{paper_slug}"

    paper_dir = med_db / "papers" / topic / folder_name
    if not force and paper_dir.exists():
        print(f"skipping already archived: {folder_name}", file=sys.stderr)
        return None
    paper_dir.mkdir(parents=True, exist_ok=True)

    metadata_file = paper_dir / "metadata.json"
    abstract_file = paper_dir / "abstract.txt"
    save_text(metadata_file, raw_work)

    abstract_text = _crossref_abstract(message) or f"Abstract unavailable from Crossref for DOI {doi}."
    save_text(abstract_file, abstract_text.rstrip() + "\n")

    url = message.get("URL") or f"https://doi.org/{doi}"
    identifier = f"DOI:{doi}"
    return metadata_file, abstract_file, title, identifier, url


def archive_doi(args, med_db, doi, topic):
    """Resolve a DOI and archive the paper.

    Tries PubMed first, then Europe PMC, then Crossref.
    Returns the archive result tuple from archive_pmid, archive_europe_pmc_record,
    or archive_crossref_doi, or raises RuntimeError if the DOI cannot be resolved.
    """
    source, identifier = utils.resolve_doi_to_id(doi, email=args.email)
    if source == "pubmed":
        return archive_pmid(args, med_db, identifier, topic)
    elif source == "europe-pmc":
        return archive_europe_pmc_record(med_db, identifier, topic, force=args.force)
    elif source == "crossref":
        return archive_crossref_doi(med_db, identifier, topic, force=args.force)

    raise RuntimeError(f"DOI not found in PubMed, Europe PMC, or Crossref: {doi}")


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



def copy2_verified(source, destination):
    shutil.copy2(source, destination)
    if source.stat().st_size != destination.stat().st_size:
        raise OSError(f"copy size mismatch: {source} -> {destination}")


def remove_paper_folders(med_db, folder_prefix):
    """Delete paper folders under papers/ whose name starts with *folder_prefix*.

    Returns a list of removed folder paths relative to *med_db*.
    """
    papers_dir = med_db / "papers"
    removed = []
    for meta_path in sorted(papers_dir.rglob("metadata.json")):
        paper_dir = meta_path.parent
        if paper_dir.name.startswith(folder_prefix):
            shutil.rmtree(paper_dir)
            removed.append(str(paper_dir.relative_to(med_db)))
    return removed


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
                copy2_verified(meta_path, topic_dir / "metadata.json")
                if abstract_path.is_file():
                    copy2_verified(abstract_path, topic_dir / "abstract.txt")
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
                copy2_verified(search_path, dest_file)
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
                copy2_verified(web_path, dest_file)
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
        help="Medical topic for grouping output (e.g. endometriosis, weight-loss, adhd). Defaults to 'uncategorized'.",
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
        "--doi",
        action="append",
        default=[],
        help="DOI to resolve and archive. May be passed multiple times. Tries PubMed, then Europe PMC, then Crossref.",
    )
    parser.add_argument(
        "--remove-pmid",
        action="append",
        default=[],
        help="Remove archived papers by PMID. May be passed multiple times.",
    )
    parser.add_argument(
        "--remove-epmc-record",
        action="append",
        default=[],
        help="Remove archived papers by Europe PMC record (SOURCE:ID). May be passed multiple times.",
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
        "--force",
        action="store_true",
        help="Re-fetch and overwrite papers that are already archived (useful after transient fetch failures).",
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
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format. Defaults to text.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Output only created folder paths, one per line.",
    )
    args = parser.parse_args()

    if args.migrate or args.migrate_dry_run:
        return args

    if args.remove_pmid or args.remove_epmc_record:
        if args.query or args.pmid or args.epmc_record or args.doi:
            parser.error("--remove-pmid/--remove-epmc-record cannot be combined with archival options")
        return args

    if not args.query and not args.pmid and not args.epmc_record and not args.doi:
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


def _format_result_text(result):
    """Format the archival result as human-readable text (existing behavior)."""
    lines = []
    if result["search_file"]:
        lines.append(f"saved search: {result['search_file']}")
    elif result["web_sources"]:
        lines.append("saved search: none")
        lines.append("archived web sources:")
        for source in result["web_sources"]:
            lines.append(f"- {source['path']}: {source['url']}")
    else:
        lines.append("saved search: none")

    if not result["archived_records"]:
        lines.append("archived structured records: none")
    else:
        lines.append("archived structured records:")
        for record in result["archived_records"]:
            lines.append(f"- {record['identifier']}: {record['title']}")
            lines.append(f"  folder: {record['folder']}")
    return "\n".join(lines)


def _format_result_json(result):
    """Format the archival result as JSON."""
    return json.dumps(result, indent=2, default=str, ensure_ascii=False)


def _format_result_quiet(result):
    """Format the archival result as newline-separated folder paths."""
    paths = []
    if result["search_file"]:
        paths.append(result["search_file"])
    for source in result["web_sources"]:
        paths.append(source["path"])
    for record in result["archived_records"]:
        paths.append(record["folder"])
    return "\n".join(paths)


def main():
    args = parse_args()
    med_db = Path(args.med_db)

    if args.migrate or args.migrate_dry_run:
        med_db.mkdir(parents=True, exist_ok=True)
        ensure_med_db_structure(med_db)
        result = migrate_flat_to_topic(med_db, dry_run=args.migrate_dry_run)
        if result != 0:
            return result
        if not args.migrate_dry_run:
            sync_index(med_db)
            if utils.verify_and_report_integrity(med_db) != 0:
                return 1
        return 0

    med_db.mkdir(parents=True, exist_ok=True)
    ensure_med_db_structure(med_db)

    if args.remove_pmid or args.remove_epmc_record:
        removed = []
        for pmid in args.remove_pmid:
            removed.extend(remove_paper_folders(med_db, f"pmid-{pmid}-"))
        for record_spec in args.remove_epmc_record:
            try:
                source_name, record_id = parse_europe_pmc_record(record_spec)
            except ValueError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 1
            prefix = f"epmc-{source_name.lower()}-{slugify(record_id)}-"
            removed.extend(remove_paper_folders(med_db, prefix))
        sync_index(med_db)
        if removed:
            for rel in sorted(removed):
                print(f"removed: {rel}")
        else:
            print("no matching papers found", file=sys.stderr)
        if utils.verify_and_report_integrity(med_db) != 0:
            return 1
        return 0

    topic = validate_topic_slug(args.topic_slug or slugify(args.topic, fallback=DEFAULT_TOPIC))

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
        result = archive_pmid(args, med_db, pmid, topic)
        if result is None:
            continue
        metadata_file, abstract_file, title, identifier, url = result
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
        result = archive_europe_pmc_record(med_db, record_spec, topic, force=args.force)
        if result is None:
            continue
        metadata_file, abstract_file, title, identifier, url = result
        archived.append((identifier, metadata_file, abstract_file, title))
        paper_updates[str(metadata_file.parent.relative_to(med_db))] = {
            "identifier": identifier,
            "url": url,
            "purpose": DEFAULT_PAPER_PURPOSE,
            "accessed": datetime.date.today().isoformat(),
        }
        if index < len(epmc_records) - 1 and args.delay > 0:
            time.sleep(args.delay)

    dois = dedupe([d.strip() for d in args.doi if d.strip()])
    for index, doi in enumerate(dois):
        try:
            result = archive_doi(args, med_db, doi, topic)
        except RuntimeError as exc:
            print(f"error resolving DOI {doi}: {exc}", file=sys.stderr)
            continue
        if result is None:
            continue
        metadata_file, abstract_file, title, identifier, url = result
        archived.append((identifier, metadata_file, abstract_file, title))
        paper_updates[str(metadata_file.parent.relative_to(med_db))] = {
            "identifier": identifier,
            "url": url,
            "purpose": DEFAULT_PAPER_PURPOSE,
            "accessed": datetime.date.today().isoformat(),
        }
        if index < len(dois) - 1 and args.delay > 0:
            time.sleep(args.delay)

    sync_index(med_db, search_updates=search_updates, paper_updates=paper_updates, web_updates=web_updates)

    result = {
        "search_file": str(search_file) if search_file else None,
        "search_source": None,
        "web_sources": [
            {"path": path, "url": details["url"]}
            for path, details in sorted(web_updates.items())
        ],
        "archived_records": [
            {
                "identifier": identifier,
                "title": title,
                "folder": str(metadata_file.parent),
            }
            for identifier, metadata_file, abstract_file, title in archived
        ],
    }
    if search_file:
        result["search_source"] = source_label(args.source) if hasattr(args, "source") else None

    if args.quiet:
        print(_format_result_quiet(result))
        return 0

    if args.format == "json":
        print(_format_result_json(result))
    else:
        print(_format_result_text(result))

    if utils.verify_and_report_integrity(med_db) != 0:
        return 1

    return 0


if __name__ == "__main__":
    utils.run_cli(main)
