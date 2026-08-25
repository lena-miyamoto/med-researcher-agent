"""Download a paper's full text into the med-db fulltext archive.

Resolves a reference (DOI, PMID, arXiv ID, Europe PMC SOURCE:ID, title, or
URL) to metadata, then downloads the full text.  Open-access papers are
fetched from legal open-access sources (Europe PMC, OpenAlex, Unpaywall,
publisher open access, arXiv).  Paywalled papers skip those and go straight
to Sci-Hub; the legal alternatives are only tried if Sci-Hub fails.  Sci-Hub
is disabled entirely via ``--no-sci-hub``.

Writes ``paper.pdf`` + ``source.md`` (YAML frontmatter + extracted text) +
``metadata.json`` (raw record + provenance) into
``med-db/fulltext/<topic-slug>/<identifier>-<title-slug>/``, syncs
``index.json``, and runs the integrity check.  Idempotent — skips papers
that are already archived unless ``--force`` is given.

Usage:
    uv run med-db-download-paper --reference 10.1038/s41586-020-2649-2 --topic test
    uv run med-db-download-paper --reference 35350465 --topic test
    uv run med-db-download-paper --reference 2203.15556 --topic test
    uv run med-db-download-paper --reference MED:35350465 --topic test
    uv run med-db-download-paper --title "Attention deficit hyperactivity disorder adults" --year 2015 --topic test
    uv run med-db-download-paper --url https://example.org/paper.pdf --topic test
    uv run med-db-download-paper --reference 10.1038/x --topic test --no-sci-hub
"""

import argparse
import datetime
import html
import importlib.util
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import utils
from pypdf import PdfReader
from pypdf.errors import PdfReadError

# ---------------------------------------------------------------------------
# API / network constants
# ---------------------------------------------------------------------------

PMC_IDCONV_URL = "https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"
UNPAYWALL_API = "https://api.unpaywall.org/v2/"
OPENALEX_API = "https://api.openalex.org/works/"
ARXIV_EXPORT_API = "https://export.arxiv.org/api/query"
ARXIV_PDF_BASE = "https://arxiv.org/pdf/"
ARXIV_ABS_BASE = "https://arxiv.org/abs/"
CROSSREF_API = "https://api.crossref.org/"
DOI_RESOLVER = "https://doi.org/"

SCIHUB_MIRRORS = ["https://sci-hub.se", "https://sci-hub.st", "https://sci-hub.ru"]

DEFAULT_FULLTEXT_PURPOSE = "Downloaded via med-db-download-paper; review and refine purpose."

# ---------------------------------------------------------------------------
# Reference detection
# ---------------------------------------------------------------------------

DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[^\s\"'<>]+")
ARXIV_ID_PATTERN = re.compile(r"^(?:arxiv:)?(\d{4}\.\d{4,5})(v\d+)?$", re.IGNORECASE)
EPMC_RECORD_PATTERN = re.compile(r"^([A-Z]{2,10}):(\S+)$")


def detect_reference_type(reference):
    """Return ``(kind, value)`` for a raw reference string.

    Detection order: URL host → DOI → PMID (all digits) → arXiv ID →
    Europe PMC ``SOURCE:ID`` → title fallback.
    """
    reference = reference.strip()
    if not reference:
        raise ValueError("empty reference")
    if reference.startswith(("http://", "https://", "www.")):
        return classify_url(reference)
    doi_match = DOI_PATTERN.search(reference)
    if doi_match:
        return ("doi", doi_match.group(0))
    if reference.isdigit():
        return ("pmid", reference)
    arxiv_match = ARXIV_ID_PATTERN.match(reference)
    if arxiv_match:
        return ("arxiv", arxiv_match.group(1) + (arxiv_match.group(2) or ""))
    epmc_match = EPMC_RECORD_PATTERN.match(reference)
    if epmc_match:
        return ("epmc-record", reference)
    return ("title", reference)


def classify_url(url):
    """Return ``(kind, value)`` for a URL, classified by host and path."""
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path

    if host in ("doi.org", "dx.doi.org", "www.doi.org"):
        stripped = path.strip("/")
        if stripped:
            return ("doi", stripped)
    if host == "arxiv.org":
        if path.startswith("/abs/"):
            return ("arxiv", path.split("/abs/", 1)[1].strip("/").split("/")[0])
        if path.startswith("/pdf/"):
            return ("arxiv", path.split("/pdf/", 1)[1].strip("/").split("/")[0])
    if host == "europepmc.org":
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[0] == "article":
            return ("epmc-record", f"{parts[1].upper()}:{parts[2]}")
    if host in ("pubmed.ncbi.nlm.nih.gov", "www.ncbi.nlm.nih.gov"):
        match = re.search(r"/(\d+)/?$", path)
        if match:
            return ("pmid", match.group(1))
    if "pmc.ncbi.nlm.nih.gov" in host:
        match = re.search(r"PMC(\d+)", path, re.IGNORECASE)
        if match:
            return ("pmcid", f"PMC{match.group(1)}")
    if path.lower().endswith(".pdf"):
        return ("pdf-url", url)
    return ("url", url)


# ---------------------------------------------------------------------------
# med-db module loading (reuse archival helpers without duplicating them)
# ---------------------------------------------------------------------------


def load_med_db_module():
    """Load ``med-db.py`` as the ``med_db`` module.

    Tests pre-load it into ``sys.modules`` via conftest; in production the
    file is loaded from the scripts directory.
    """
    existing = sys.modules.get("med_db")
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(
        "med_db", Path(__file__).resolve().parent / "med-db.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load med-db.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["med_db"] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Metadata resolution
# ---------------------------------------------------------------------------


def _authors_from_pubmed(summary):
    names = [author.get("name") for author in summary.get("authors", [])]
    return ", ".join(name for name in names if name)


def _doi_from_pubmed(summary):
    for article_id in summary.get("articleids", []):
        if article_id.get("idtype") == "doi":
            return article_id.get("value")
    return None


def split_epmc_record(record_spec):
    source_name, separator, record_id = record_spec.partition(":")
    if not separator or not source_name or not record_id:
        raise ValueError(f"invalid Europe PMC record spec: {record_spec}; expected SOURCE:ID")
    return source_name.upper(), record_id


def metadata_from_pubmed(pmid, email, pubmed_fetch_func):
    params = {"db": "pubmed", "retmode": "json", "id": str(pmid), "tool": "med-db-download-paper"}
    if email:
        params["email"] = email
    raw = pubmed_fetch_func("esummary.fcgi", params)
    record = json.loads(raw)
    summary = record.get("result", {}).get(str(pmid), {})
    if "error" in summary:
        raise RuntimeError(f"PubMed API error for PMID {pmid}: {summary['error']}")
    return {
        "kind": "pmid",
        "identifier": f"PMID:{pmid}",
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        "title": summary.get("title") or f"PMID {pmid}",
        "authors": _authors_from_pubmed(summary),
        "source_name": "PubMed",
        "record": record,
        "pmid": str(pmid),
        "doi": _doi_from_pubmed(summary),
    }


def metadata_from_europe_pmc(source_name, record_id, epmc_fetch_func):
    params = {
        "query": f"EXT_ID:{record_id} AND SRC:{source_name}",
        "resultType": "core",
        "format": "json",
        "pageSize": "1",
    }
    raw = epmc_fetch_func("search", params)
    record = json.loads(raw)
    results = record.get("resultList", {}).get("result", [])
    if not results:
        raise RuntimeError(f"Europe PMC record not found: {source_name}:{record_id}")
    item = results[0]
    epmc_record = f"{source_name}:{record_id}"
    return {
        "kind": "epmc-record",
        "identifier": epmc_record,
        "url": utils.europe_pmc_article_url(source_name, record_id),
        "title": item.get("title") or epmc_record,
        "authors": item.get("authorString") or "",
        "source_name": "Europe PMC",
        "record": record,
        "epmc_record": epmc_record,
        "pmid": item.get("pmid"),
        "doi": item.get("doi"),
    }


def metadata_from_crossref(doi, fetch_url_func):
    raw = fetch_url_func(f"{CROSSREF_API}works/{urllib.parse.quote(doi)}", "Crossref")
    message = json.loads(raw).get("message", {})
    titles = message.get("title") or []
    title = titles[0] if titles else doi
    author_names = []
    for author in message.get("author", []):
        name = f"{author.get('given', '')} {author.get('family', '')}".strip()
        if name:
            author_names.append(name)
    return {
        "kind": "doi",
        "identifier": f"DOI:{doi}",
        "url": f"{DOI_RESOLVER}{doi}",
        "title": title,
        "authors": ", ".join(author_names),
        "source_name": "Crossref",
        "record": {"resultList": {"result": []}},
        "doi": doi,
    }


def metadata_from_doi(doi, email, pubmed_fetch_func, epmc_fetch_func, fetch_url_func):
    source, identifier = utils.resolve_doi_to_id(
        doi, email=email,
        pubmed_fetch_func=pubmed_fetch_func,
        epmc_fetch_func=epmc_fetch_func,
        # Crossref metadata is fetched by metadata_from_crossref below; skip the
        # resolver's Crossref lookup to avoid a duplicate, injected-fetcher-
        # bypassing call.
        crossref_fetch_func=lambda _doi: "{}",
    )
    if source == "pubmed":
        return metadata_from_pubmed(identifier, email, pubmed_fetch_func)
    if source == "europe-pmc":
        source_name, record_id = split_epmc_record(identifier)
        return metadata_from_europe_pmc(source_name, record_id, epmc_fetch_func)
    try:
        return metadata_from_crossref(doi, fetch_url_func)
    except (RuntimeError, json.JSONDecodeError, KeyError, IndexError):
        return {
            "kind": "doi",
            "identifier": f"DOI:{doi}",
            "url": f"{DOI_RESOLVER}{doi}",
            "title": doi,
            "authors": "",
            "source_name": "Crossref",
            "record": {"resultList": {"result": []}},
            "doi": doi,
        }


def metadata_from_pmcid(pmcid, email, pubmed_fetch_func, epmc_fetch_func, fetch_url_func):
    params = {"ids": pmcid, "format": "json", "tool": "med-db-download-paper"}
    if email:
        params["email"] = email
    raw = fetch_url_func(
        f"{PMC_IDCONV_URL}?{urllib.parse.urlencode(params)}", "PMC ID converter"
    )
    records = json.loads(raw).get("records", [])
    if not records or records[0].get("status") == "error":
        raise RuntimeError(f"PMC ID converter could not resolve {pmcid}")
    item = records[0]
    if item.get("pmid"):
        return metadata_from_pubmed(item["pmid"], email, pubmed_fetch_func)
    if item.get("doi"):
        return metadata_from_doi(item["doi"], email, pubmed_fetch_func, epmc_fetch_func, fetch_url_func)
    raise RuntimeError(f"PMC ID converter returned no PMID or DOI for {pmcid}")


def _parse_arxiv_atom(raw, fallback_title):
    entry_match = re.search(r"<entry>(.*?)</entry>", raw, re.DOTALL)
    if not entry_match:
        raise RuntimeError(f"arXiv API found no record for {fallback_title}")
    entry = entry_match.group(1)
    title_match = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
    title = " ".join(title_match.group(1).split()) if title_match else fallback_title
    authors = ", ".join(
        match.group(1) for match in re.finditer(r"<name>(.*?)</name>", entry, re.DOTALL)
    )
    return title, authors


def _parse_arxiv_id_from_atom(raw):
    entry_match = re.search(r"<entry>(.*?)</entry>", raw, re.DOTALL)
    if not entry_match:
        return None
    id_match = re.search(r"<id>https?://arxiv\.org/abs/([^<]+)</id>", entry_match.group(1))
    return id_match.group(1) if id_match else None


def metadata_from_arxiv(arxiv_id, fetch_url_func):
    raw = fetch_url_func(
        f"{ARXIV_EXPORT_API}?id_list={urllib.parse.quote(arxiv_id)}&max_results=1", "arXiv API"
    )
    title, authors = _parse_arxiv_atom(raw, arxiv_id)
    return {
        "kind": "arxiv",
        "identifier": f"arXiv:{arxiv_id}",
        "url": f"{ARXIV_ABS_BASE}{arxiv_id}",
        "title": title,
        "authors": authors,
        "source_name": "arXiv",
        "record": {"resultList": {"result": []}},
        "arxiv_id": arxiv_id,
    }


def metadata_from_title(title, year, email, pubmed_fetch_func, epmc_fetch_func, fetch_url_func):
    # 1. PubMed esearch by title (+year)
    try:
        term = f"{title}[ti]"
        if year:
            term += f" AND {year}[dp]"
        params = {
            "db": "pubmed",
            "retmode": "json",
            "term": term,
            "retmax": "1",
            "tool": "med-db-download-paper",
        }
        if email:
            params["email"] = email
        raw = pubmed_fetch_func("esearch.fcgi", params)
        idlist = json.loads(raw).get("esearchresult", {}).get("idlist", [])
        if idlist:
            return metadata_from_pubmed(idlist[0], email, pubmed_fetch_func)
    except (RuntimeError, json.JSONDecodeError):
        pass

    # 2. Europe PMC search
    try:
        query = f'title:"{title}"'
        if year:
            query += f" AND PUB_YEAR:{year}"
        params = {"query": query, "resultType": "core", "format": "json", "pageSize": "1"}
        raw = epmc_fetch_func("search", params)
        results = json.loads(raw).get("resultList", {}).get("result", [])
        if results:
            item = results[0]
            source_name = str(item.get("source") or "MED")
            record_id = str(item.get("id") or item.get("pmid") or "")
            if record_id:
                return metadata_from_europe_pmc(source_name, record_id, epmc_fetch_func)
    except (RuntimeError, json.JSONDecodeError):
        pass

    # 3. Crossref bibliographic search
    try:
        params = {"query.bibliographic": title, "rows": "1"}
        if email:
            params["mailto"] = email
        raw = fetch_url_func(f"{CROSSREF_API}works?{urllib.parse.urlencode(params)}", "Crossref")
        items = json.loads(raw).get("message", {}).get("items", [])
        if items and items[0].get("DOI"):
            return metadata_from_doi(items[0]["DOI"], email, pubmed_fetch_func, epmc_fetch_func, fetch_url_func)
    except (RuntimeError, json.JSONDecodeError):
        pass

    # 4. arXiv API search
    try:
        query = f'all:"{title}"'
        raw = fetch_url_func(
            f"{ARXIV_EXPORT_API}?search_query={urllib.parse.quote(query)}&max_results=1", "arXiv API"
        )
        arxiv_id = _parse_arxiv_id_from_atom(raw)
        if arxiv_id:
            return metadata_from_arxiv(arxiv_id, fetch_url_func)
    except RuntimeError:
        pass

    raise RuntimeError(f"could not resolve title to a record: {title}")


def metadata_from_url(url):
    parsed = urllib.parse.urlparse(url)
    title = utils.slugify(Path(parsed.path).stem, fallback="paper").replace("-", " ")
    return {
        "kind": "url",
        "identifier": f"URL:{url}",
        "url": url,
        "title": title,
        "authors": "",
        "source_name": "URL",
        "record": {"resultList": {"result": []}},
        "direct_pdf_url": url,
    }


def resolve_metadata(reference_kind, reference_value, year=None, email=None,
                     pubmed_fetch_func=None, epmc_fetch_func=None, fetch_url_func=None):
    """Resolve a reference to a metadata dict. Raises RuntimeError/ValueError."""
    pubmed_fetch = pubmed_fetch_func or utils.fetch_pubmed
    epmc_fetch = epmc_fetch_func or utils.fetch_europe_pmc
    fetch_url = fetch_url_func or utils._fetch_url

    if reference_kind == "pmid":
        return metadata_from_pubmed(reference_value, email, pubmed_fetch)
    if reference_kind == "epmc-record":
        source_name, record_id = split_epmc_record(reference_value)
        return metadata_from_europe_pmc(source_name, record_id, epmc_fetch)
    if reference_kind == "doi":
        return metadata_from_doi(reference_value, email, pubmed_fetch, epmc_fetch, fetch_url)
    if reference_kind == "pmcid":
        return metadata_from_pmcid(reference_value, email, pubmed_fetch, epmc_fetch, fetch_url)
    if reference_kind == "arxiv":
        return metadata_from_arxiv(reference_value, fetch_url)
    if reference_kind == "title":
        return metadata_from_title(reference_value, year, email, pubmed_fetch, epmc_fetch, fetch_url)
    if reference_kind in ("pdf-url", "url"):
        return metadata_from_url(reference_value)
    raise ValueError(f"unsupported reference kind: {reference_kind}")


# ---------------------------------------------------------------------------
# Full-text sources
# ---------------------------------------------------------------------------


def fetch_fulltext_xml(epmc_record, fetch_func=None):
    """Fetch the Europe PMC fullTextXML for an open-access record.

    Returns the JATS XML string; raises RuntimeError when the record has no
    open-access full text (HTTP 404) and ValueError on a malformed response.
    """
    fetch = fetch_func or utils.fetch_europe_pmc
    raw = fetch(f"{epmc_record}/fullTextXML", {})
    if "<article" not in raw.lower():
        raise ValueError(f"Europe PMC fullTextXML response is not an article for {epmc_record}")
    return raw


def fulltext_xml_to_text(xml_string):
    """Convert JATS full-text XML to plain text, preserving paragraph breaks."""
    text = re.sub(r"<(ref-list)[^>]*>.*?</\1>", " ", xml_string, flags=re.DOTALL)
    text = re.sub(r"</?(?:p|sec|title|abstract|body|article)[^>]*>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line)


def fetch_unpaywall_pdf_url(doi, email=None, fetch_url_func=None):
    """Return the best open-access PDF URL from Unpaywall, or None."""
    fetch_url = fetch_url_func or utils._fetch_url
    url = f"{UNPAYWALL_API}{urllib.parse.quote(doi)}"
    if email:
        url += f"?email={urllib.parse.quote(email)}"
    raw = fetch_url(url, "Unpaywall")
    location = json.loads(raw).get("best_oa_location") or {}
    return location.get("url_for_pdf") or location.get("url")


def fetch_openalex_oa(doi, fetch_url_func=None):
    """Return ``(is_oa, pdf_url)`` for a DOI from OpenAlex.

    ``is_oa`` is True or False when OpenAlex reports open-access status and
    None when the lookup failed or the record has no status. ``pdf_url`` is
    the best open-access PDF location, or None.
    """
    fetch_url = fetch_url_func or utils._fetch_url
    try:
        raw = fetch_url(
            f"{OPENALEX_API}{urllib.parse.quote(f'https://doi.org/{doi}')}", "OpenAlex"
        )
        data = json.loads(raw)
    except (RuntimeError, json.JSONDecodeError, ValueError):
        return None, None
    is_oa = data.get("is_oa")
    if not isinstance(is_oa, bool):
        is_oa = None
    location = data.get("best_oa_location") or {}
    pdf_url = location.get("pdf_url") or location.get("landing_page_url")
    return is_oa, pdf_url


def build_arxiv_pdf_url(arxiv_id):
    return f"{ARXIV_PDF_BASE}{arxiv_id}"


def fetch_publisher_pdf(doi, timeout=60):
    """Download the PDF via DOI content negotiation. Returns bytes or raises."""
    request = urllib.request.Request(
        f"{DOI_RESOLVER}{doi}",
        headers={"Accept": "application/pdf", "User-Agent": utils.USER_AGENT},
    )
    try:
        response = utils._request_with_retry(
            request, f"publisher PDF {doi}", timeout, retries=2, retry_delay=0.25
        )
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
        raise RuntimeError(f"error fetching publisher PDF for {doi}: {exc}") from exc
    try:
        with response:
            content_type = response.headers.get_content_type()
            content = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
        raise RuntimeError(f"error reading publisher PDF for {doi}: {exc}") from exc
    if content_type != "application/pdf":
        raise RuntimeError(f"publisher did not return PDF for {doi}: {content_type}")
    if not content.startswith(b"%PDF"):
        raise RuntimeError(f"publisher response is not a PDF for {doi}")
    return content


def fetch_scihub_pdf_url(reference_value, mirror, fetch_url_func=None):
    """Return the PDF URL from a Sci-Hub mirror page, or None.

    A captcha page (or any page without a PDF link) returns None so the
    caller can move on to the next mirror.
    """
    fetch_url = fetch_url_func or utils._fetch_url
    page_url = f"{mirror.rstrip('/')}/{urllib.parse.quote(reference_value, safe='')}"
    raw = fetch_url(page_url, "Sci-Hub", timeout=30)
    if "captcha" in raw.lower():
        return None
    match = re.search(
        r"(?:src|href)\s*=\s*[\"']((?:https?:)?//[^\"']+?\.pdf[^\"']*)[\"']",
        raw,
        re.IGNORECASE,
    )
    if not match:
        return None
    pdf_url = urllib.parse.urljoin(page_url, match.group(1))
    if pdf_url.startswith("http://"):
        pdf_url = "https://" + pdf_url[len("http://"):]
    return pdf_url


# ---------------------------------------------------------------------------
# Binary downloads and PDF text extraction
# ---------------------------------------------------------------------------


def download_binary(url, destination, timeout=60):
    """Download *url* to *destination*. Returns True on success.

    Verifies the PDF magic bytes, retries transient (429/5xx) and network
    errors, and removes partial files on failure.
    """
    request = urllib.request.Request(url, headers={"User-Agent": utils.USER_AGENT})
    destination = Path(destination)
    tmp = destination.with_suffix(destination.suffix + ".tmp")
    try:
        response = utils._request_with_retry(
            request, url, timeout, retries=2, retry_delay=0.25
        )
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        return False
    try:
        with response:
            first_chunk = response.read(4096)
            if not first_chunk.startswith(b"%PDF"):
                return False
            with tmp.open("wb") as output:
                output.write(first_chunk)
                while True:
                    chunk = response.read(65536)
                    if not chunk:
                        break
                    output.write(chunk)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        tmp.unlink(missing_ok=True)
        return False
    tmp.replace(destination)
    return True


def write_binary(path, content):
    """Write *content* bytes atomically via a temporary file + rename."""
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(content)
    tmp.replace(path)


def extract_pdf_text(pdf_path):
    """Extract plain text from a PDF. Raises ValueError when empty."""
    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(pages).strip()
    if not text:
        raise ValueError(f"text extraction from PDF produced no text: {pdf_path}")
    return text


# ---------------------------------------------------------------------------
# Archive writing
# ---------------------------------------------------------------------------


def build_fulltext_folder(resolved):
    """Build the fulltext folder name from resolved metadata."""
    title_slug = utils.slugify(resolved["title"], fallback="paper")
    if resolved.get("pmid"):
        return f"pmid-{resolved['pmid']}-{title_slug}"
    if resolved.get("epmc_record"):
        source_name, record_id = split_epmc_record(resolved["epmc_record"])
        record_slug = utils.slugify(record_id, fallback="record")
        return f"epmc-{source_name.lower()}-{record_slug}-{title_slug}"
    if resolved.get("arxiv_id"):
        return f"arxiv-{utils.slugify(resolved['arxiv_id'], fallback='arxiv')}-{title_slug}"
    if resolved.get("doi"):
        return f"doi-{utils.slugify(resolved['doi'], fallback='doi')}-{title_slug}"
    return f"title-{title_slug}"


def write_source_markdown(path, frontmatter, body_text):
    """Write source.md with YAML frontmatter (JSON-encoded scalar values)."""
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.extend(["---", "", body_text.rstrip()])
    utils.atomic_write(path, "\n".join(lines) + "\n")


def write_metadata_json(path, record, provenance):
    payload = dict(record)
    payload["provenance"] = provenance
    utils.atomic_write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Download orchestration
# ---------------------------------------------------------------------------


def attempt_pdf_download(url, label, pdf_destination, source_chain, download_binary_func=None):
    """Try downloading a PDF; record the outcome. Returns True on success."""
    downloader = download_binary_func if download_binary_func is not None else download_binary
    if not url:
        source_chain.append({"source": label, "outcome": "failed", "detail": "no URL available"})
        return False
    if downloader(url, pdf_destination):
        source_chain.append({"source": label, "outcome": "ok", "detail": url})
        return True
    source_chain.append({"source": label, "outcome": "failed", "detail": f"download failed: {url}"})
    return False


def legal_pdf_candidates(resolved, email, source_chain, oa_pdf_url=None, fetch_url_func=None):
    """Yield ``(label, url)`` PDF candidates from legal open-access sources.

    ``oa_pdf_url`` is the OpenAlex best-OA location already fetched during OA
    detection; when given, the OpenAlex lookup is not repeated. Unpaywall is
    only queried when an email is available — without one it always returns
    HTTP 422.
    """
    doi = resolved.get("doi")
    if not doi:
        return
    if oa_pdf_url:
        yield "openalex", oa_pdf_url
    else:
        source_chain.append({
            "source": "openalex",
            "outcome": "failed",
            "detail": "no open-access PDF location recorded",
        })
    if email:
        try:
            url = fetch_unpaywall_pdf_url(doi, email, fetch_url_func=fetch_url_func or utils._fetch_url)
            if url:
                yield "unpaywall", url
            else:
                source_chain.append({
                    "source": "unpaywall",
                    "outcome": "failed",
                    "detail": "no open-access location recorded",
                })
        except RuntimeError as exc:
            source_chain.append({"source": "unpaywall", "outcome": "failed", "detail": str(exc)})
    else:
        source_chain.append({
            "source": "unpaywall",
            "outcome": "skipped",
            "detail": "no email provided (Unpaywall requires one)",
        })


def _try_sci_hub(reference_value, resolved, mirrors, pdf_destination, source_chain,
                 provenance, download_binary_func, fetch_url_func):
    """Try Sci-Hub mirrors in order; return True when a PDF is fetched."""
    lookup_value = resolved.get("doi") or resolved.get("pmid") or reference_value
    for mirror in mirrors:
        try:
            url = fetch_scihub_pdf_url(
                lookup_value, mirror, fetch_url_func=fetch_url_func or utils._fetch_url
            )
        except RuntimeError as exc:
            source_chain.append({
                "source": "sci-hub",
                "outcome": "failed",
                "detail": f"{mirror}: {exc}",
            })
            continue
        if not url:
            source_chain.append({
                "source": "sci-hub",
                "outcome": "failed",
                "detail": f"{mirror}: captcha or no PDF link",
            })
            continue
        if attempt_pdf_download(url, "sci-hub", pdf_destination, source_chain, download_binary_func):
            provenance["pdf_source"] = "sci-hub"
            provenance["pdf_url"] = url
            provenance["sci_hub_used"] = True
            return True
    return False


def _download_legal_pdf(resolved, email, source_chain, pdf_destination, provenance,
                        oa_pdf_url, download_binary_func, fetch_url_func):
    """Try legal PDF sources; return True when a PDF was fetched.

    Order: OpenAlex OA location, Unpaywall (only with email), publisher open
    access (DOI content negotiation), then arXiv for arXiv records.
    """
    fetched_pdf = False
    for label, url in legal_pdf_candidates(
        resolved, email, source_chain, oa_pdf_url=oa_pdf_url, fetch_url_func=fetch_url_func
    ):
        if attempt_pdf_download(url, label, pdf_destination, source_chain, download_binary_func):
            fetched_pdf = True
            provenance["pdf_source"] = label
            provenance["pdf_url"] = url
            break

    if not fetched_pdf and resolved.get("doi"):
        try:
            content = fetch_publisher_pdf(resolved["doi"])
            write_binary(pdf_destination, content)
            fetched_pdf = True
            provenance["pdf_source"] = "publisher-open-access"
            provenance["pdf_url"] = f"{DOI_RESOLVER}{resolved['doi']}"
            source_chain.append({
                "source": "publisher-open-access",
                "outcome": "ok",
                "detail": provenance["pdf_url"],
            })
        except RuntimeError as exc:
            source_chain.append({
                "source": "publisher-open-access",
                "outcome": "failed",
                "detail": str(exc),
            })

    if not fetched_pdf and resolved.get("arxiv_id"):
        url = build_arxiv_pdf_url(resolved["arxiv_id"])
        if attempt_pdf_download(url, "arxiv", pdf_destination, source_chain, download_binary_func):
            fetched_pdf = True
            provenance["pdf_source"] = "arxiv"
            provenance["pdf_url"] = url

    return fetched_pdf


def _remove_temporary_files(target):
    for path in target.glob("*.tmp"):
        path.unlink(missing_ok=True)


def download_paper(reference_kind, reference_value, year=None, topic="uncategorized",
                   med_db=None, email=None, force=False, allow_sci_hub=True,
                   sci_hub_mirrors=None, pubmed_fetch_func=None, epmc_fetch_func=None,
                   fetch_url_func=None, download_binary_func=None,
                   extract_pdf_text_func=None):
    """Download one paper's full text into the med-db fulltext archive.

    Returns a result dict; raises RuntimeError when no source could provide
    the full text.
    """
    if med_db is None:
        med_db = utils.MED_DB
    med_db = Path(med_db)

    resolved = resolve_metadata(
        reference_kind, reference_value, year=year, email=email,
        pubmed_fetch_func=pubmed_fetch_func, epmc_fetch_func=epmc_fetch_func,
        fetch_url_func=fetch_url_func,
    )
    folder_name = build_fulltext_folder(resolved)
    target = med_db / "fulltext" / topic / folder_name

    if (target / "paper.pdf").is_file() or (target / "source.md").is_file():
        if not force:
            return {
                "status": "skipped",
                "folder": str(target),
                "identifier": resolved["identifier"],
                "url": resolved["url"],
                "title": resolved["title"],
            }

    created = not target.exists()
    target.mkdir(parents=True, exist_ok=True)
    pdf_destination = target / "paper.pdf"
    source_chain = []
    provenance = {
        "source_chain": source_chain,
        "pdf_source": None,
        "pdf_url": None,
        "sci_hub_used": False,
        "access_date": datetime.date.today().isoformat(),
        "extraction_method": None,
    }
    fetched_pdf = False

    # 1. Direct PDF URL (--url input)
    if resolved.get("direct_pdf_url"):
        if attempt_pdf_download(
            resolved["direct_pdf_url"], "direct-url", pdf_destination, source_chain,
            download_binary_func,
        ):
            fetched_pdf = True
            provenance["pdf_source"] = "direct-url"
            provenance["pdf_url"] = resolved["direct_pdf_url"]

    # 2. Europe PMC fullTextXML (open-access text). PMID-resolved records use
    #    the MED:<pmid> alias so PubMed-only records get an open-access attempt.
    text = None
    epmc_record = resolved.get("epmc_record") or (
        f"MED:{resolved['pmid']}" if resolved.get("pmid") else None
    )
    if not fetched_pdf and epmc_record:
        try:
            xml_string = fetch_fulltext_xml(
                epmc_record,
                fetch_func=epmc_fetch_func or utils.fetch_europe_pmc,
            )
            text = fulltext_xml_to_text(xml_string)
            provenance["extraction_method"] = "europe-pmc-fulltext-xml"
            source_chain.append({
                "source": "europe-pmc-fulltext",
                "outcome": "ok",
                "detail": f"https://www.ebi.ac.uk/europepmc/webservices/rest/{epmc_record}/fullTextXML",
            })
        except (RuntimeError, ValueError) as exc:
            source_chain.append({"source": "europe-pmc-fulltext", "outcome": "failed", "detail": str(exc)})

    # 3. OpenAlex OA status drives the branch: open-access papers use legal
    #    sources first; paywalled papers go straight to Sci-Hub.
    is_oa = None
    oa_pdf_url = None
    if not fetched_pdf and not text and resolved.get("doi"):
        try:
            is_oa, oa_pdf_url = fetch_openalex_oa(resolved["doi"], fetch_url_func)
        except RuntimeError as exc:
            source_chain.append({"source": "openalex", "outcome": "failed", "detail": str(exc)})

    mirrors = sci_hub_mirrors or SCIHUB_MIRRORS
    paywalled = resolved.get("doi") and is_oa is False

    if not fetched_pdf and not text and paywalled:
        # Paywalled: Sci-Hub first, legal alternatives only after it fails.
        if allow_sci_hub:
            fetched_pdf = _try_sci_hub(
                reference_value, resolved, mirrors, pdf_destination, source_chain,
                provenance, download_binary_func, fetch_url_func,
            )
        if not fetched_pdf:
            fetched_pdf = _download_legal_pdf(
                resolved, email, source_chain, pdf_destination, provenance,
                oa_pdf_url, download_binary_func, fetch_url_func,
            )
    elif not fetched_pdf and not text:
        # Open access (or unknown status): legal sources first, Sci-Hub last.
        fetched_pdf = _download_legal_pdf(
            resolved, email, source_chain, pdf_destination, provenance,
            oa_pdf_url, download_binary_func, fetch_url_func,
        )
        if not fetched_pdf and allow_sci_hub:
            fetched_pdf = _try_sci_hub(
                reference_value, resolved, mirrors, pdf_destination, source_chain,
                provenance, download_binary_func, fetch_url_func,
            )

    if not fetched_pdf and not text:
        _remove_temporary_files(target)
        if created:
            target.rmdir()
        chain_report = ", ".join(
            f"{step['source']} {step['outcome']}" for step in source_chain
        ) or "no sources attempted"
        raise RuntimeError(
            f"could not obtain full text for {resolved['identifier'] or reference_value}; chain: {chain_report}"
        )

    # 5. Write source.md
    body = text
    if body is None and fetched_pdf:
        try:
            extract = extract_pdf_text_func if extract_pdf_text_func is not None else extract_pdf_text
            body = extract(pdf_destination)
            provenance["extraction_method"] = "pypdf"
        except (ValueError, PdfReadError) as exc:
            chain = ", ".join(f"{step['source']} {step['outcome']}" for step in source_chain)
            print(f"warning: {exc} (chain: {chain})", file=sys.stderr)
            body = "Text extraction from PDF failed; see paper.pdf."
            provenance["extraction_method"] = "none"

    if text:
        extraction_notes = "Full text from Europe PMC fullTextXML"
        if fetched_pdf:
            extraction_notes += f"; PDF from {provenance['pdf_source']}"
        else:
            extraction_notes += "; no PDF available"
    else:
        extraction_notes = f"PDF from {provenance['pdf_source']}; text extracted with pypdf"
    if provenance["sci_hub_used"]:
        extraction_notes += "; Sci-Hub fallback used"

    write_source_markdown(
        target / "source.md",
        {
            "title": resolved["title"],
            "authors": resolved["authors"],
            "source": resolved["source_name"],
            "source_url": resolved["url"],
            "access_date": provenance["access_date"],
            "language": "und",
            "extraction_notes": extraction_notes,
        },
        body,
    )

    # 6. Write metadata.json
    write_metadata_json(target / "metadata.json", resolved["record"], provenance)

    return {
        "status": "downloaded",
        "folder": str(target),
        "identifier": resolved["identifier"],
        "url": resolved["url"],
        "title": resolved["title"],
        "pdf": fetched_pdf,
        "pdf_source": provenance["pdf_source"],
        "source_chain": source_chain,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download a paper's full text (PDF plus extracted source text) into the local med-db fulltext archive.",
    )
    parser.add_argument(
        "--reference",
        action="append",
        default=[],
        help="Raw reference (DOI, PMID, arXiv ID, Europe PMC SOURCE:ID, URL, or title); auto-detected. May be passed multiple times.",
    )
    parser.add_argument(
        "--title",
        help="Explicit title search (use when a string could misparse as an identifier).",
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Publication year filter for --title.",
    )
    parser.add_argument(
        "--url",
        help="Explicit URL of the paper (alternative to passing it in --reference).",
    )
    parser.add_argument(
        "--topic",
        help="Medical topic for grouping output (e.g. endometriosis, adhd). Required.",
    )
    parser.add_argument(
        "--topic-slug",
        help="Explicit kebab-case slug for the topic folder. Overrides --topic if both are given.",
    )
    parser.add_argument(
        "--med-db",
        default="med-db",
        help="Target med-db directory. Defaults to ./med-db.",
    )
    parser.add_argument(
        "--email",
        help="Optional contact email passed to NCBI E-utilities, Unpaywall, and Crossref.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.34,
        help="Delay between downloads in seconds. Defaults to 0.34.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if the paper is already archived.",
    )
    parser.add_argument(
        "--no-sci-hub",
        action="store_true",
        help="Disable Sci-Hub entirely (paywalled papers fall back to legal sources only).",
    )
    parser.add_argument(
        "--sci-hub-mirror",
        help="Explicit Sci-Hub mirror URL to try first (mirrors change frequently).",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format. Defaults to text.",
    )
    args = parser.parse_args()

    if not args.reference and not args.title and not args.url:
        parser.error("provide at least one of --reference, --title, or --url")
    if not args.topic:
        parser.error("--topic is required")
    if args.year is not None and not args.title:
        parser.error("--year requires --title")
    if args.year is not None and args.year < 1:
        parser.error("--year must be a positive integer")
    if args.delay < 0:
        parser.error("--delay must be >= 0")
    return args


def _format_results_text(results, failures):
    lines = []
    for result in results:
        if result["status"] == "skipped":
            lines.append(f"skipped (already archived): {result['folder']}")
            continue
        lines.append(f"{result['identifier']}: {result['title']}")
        lines.append(f"  folder: {result['folder']}")
        if result["pdf"]:
            lines.append(f"  pdf: {result['pdf_source']}")
        else:
            lines.append("  pdf: none (text-only archive)")
        lines.append(
            "  chain: " + ", ".join(f"{step['source']} {step['outcome']}" for step in result["source_chain"])
        )
    if failures:
        lines.append(f"{failures} reference(s) failed; see stderr for details")
    return "\n".join(lines)


def main():
    args = parse_args()
    med_db = Path(args.med_db)
    med_db.mkdir(parents=True, exist_ok=True)
    med_db_module = load_med_db_module()
    med_db_module.ensure_med_db_structure(med_db)

    topic = med_db_module.validate_topic_slug(
        args.topic_slug or utils.slugify(args.topic, fallback=med_db_module.DEFAULT_TOPIC)
    )

    sci_hub_mirrors = None
    if args.sci_hub_mirror:
        sci_hub_mirrors = [args.sci_hub_mirror] + SCIHUB_MIRRORS

    references = [detect_reference_type(reference) for reference in args.reference]
    if args.url:
        references.append(classify_url(args.url))
    if args.title:
        references.append(("title", args.title))

    results = []
    failures = 0
    fulltext_updates = {}
    today = datetime.date.today().isoformat()
    for index, (kind, value) in enumerate(references):
        try:
            result = download_paper(
                reference_kind=kind,
                reference_value=value,
                year=args.year,
                topic=topic,
                med_db=med_db,
                email=args.email,
                force=args.force,
                allow_sci_hub=not args.no_sci_hub,
                sci_hub_mirrors=sci_hub_mirrors,
            )
        except (RuntimeError, ValueError) as exc:
            print(f"error downloading {value}: {exc}", file=sys.stderr)
            failures += 1
            continue
        results.append(result)
        if result["status"] == "downloaded":
            fulltext_updates[str(Path(result["folder"]).relative_to(med_db))] = {
                "identifier": result["identifier"],
                "url": result["url"],
                "purpose": DEFAULT_FULLTEXT_PURPOSE,
                "accessed": today,
            }
        if index < len(references) - 1 and args.delay > 0:
            time.sleep(args.delay)

    med_db_module.sync_index(med_db, fulltext_updates=fulltext_updates)

    if args.format == "json":
        print(json.dumps({"downloaded": results, "failures": failures}, indent=2, ensure_ascii=False))
    else:
        print(_format_results_text(results, failures))

    integrity_ok = utils.verify_and_report_integrity(med_db) == 0
    if failures > 0 or not integrity_ok:
        return 1
    return 0


if __name__ == "__main__":
    utils.run_cli(main)
