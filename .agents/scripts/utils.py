"""Shared utilities for med-db scripts.

Constants, slugify, API fetch helpers, and the unified default_paper_entry
parser used across med-db.py, med-db-lookup.py, med-db-query.py, and
med-db-validate.py.
"""

import html as _html
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# API / network constants
# ---------------------------------------------------------------------------

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EUROPE_PMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# slugify — canonical version (NFKD → ASCII → kebab-case)
# ---------------------------------------------------------------------------


def slugify(text, fallback="record", max_words=10, max_length=80):
    """Normalise *text* into an ASCII kebab-case slug."""
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if not text:
        return fallback
    words = [word for word in text.split("-") if word]
    text = "-".join(words[:max_words])
    return text[:max_length].rstrip("-") or fallback


# ---------------------------------------------------------------------------
# API fetch helpers (raise RuntimeError on failure — callers decide how to
# handle it)
# ---------------------------------------------------------------------------


def _fetch_url(url, label, timeout=60, retries=2, retry_delay=0.25):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
                charset = response.headers.get_content_charset("utf-8")
                try:
                    return raw.decode(charset)
                except UnicodeDecodeError:
                    return raw.decode(charset, errors="replace")
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code < 500 or attempt == retries:
                break
        except (urllib.error.URLError, OSError) as exc:
            last_error = exc
            if attempt == retries:
                break
        if retry_delay > 0:
            time.sleep(retry_delay * (2 ** attempt))
    raise RuntimeError(f"error fetching {label}: {last_error}")


def fetch_pubmed(endpoint, params, timeout=60):
    """GET *endpoint* from PubMed E-utilities, return decoded UTF-8 body.

    Raises ``RuntimeError`` on network / HTTP errors so library callers can
    catch and recover (e.g. fall back to an "unavailable" message).
    """
    url = f"{EUTILS_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    return _fetch_url(url, f"PubMed {endpoint}", timeout=timeout)


def fetch_europe_pmc(module, params, timeout=60):
    """GET *module* from Europe PMC REST API, return decoded UTF-8 body.

    Raises ``RuntimeError`` on network / HTTP errors.
    """
    url = f"{EUROPE_PMC_BASE}/{module}?{urllib.parse.urlencode(params)}"
    return _fetch_url(url, f"Europe PMC {module}", timeout=timeout)


# ---------------------------------------------------------------------------
# europe_pmc_article_url
# ---------------------------------------------------------------------------


def europe_pmc_article_url(source_name, record_id):
    """Build a human-readable Europe PMC article URL from source + id."""
    return f"https://europepmc.org/article/{source_name}/{record_id}"


# ---------------------------------------------------------------------------
# default_paper_entry — unified parser for metadata.json
# ---------------------------------------------------------------------------


def default_paper_entry(meta_path):
    """Parse a *metadata.json* file and return ``(identifier, url)``.

    Handles both PubMed esummary-format metadata and Europe PMC search-format
    metadata.  Returns ``("unknown", "URL unavailable; review and refine.")``
    when neither format is recognised.
    """
    try:
        data = json.loads(Path(meta_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "unknown", "URL unavailable; review and refine."

    # PubMed esummary format
    pubmed_result = data.get("result", {})
    if isinstance(pubmed_result, dict) and "uids" in pubmed_result:
        uids = pubmed_result.get("uids", [])
        if len(uids) == 1:
            pmid = str(uids[0])
            return f"PMID:{pmid}", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

    # Europe PMC search format
    epmc_results = data.get("resultList", {}).get("result", [])
    if epmc_results:
        record = epmc_results[0]
        source = str(record.get("source") or "EPMC")
        rid = str(record.get("id") or record.get("pmid") or "unknown")
        return f"{source}:{rid}", europe_pmc_article_url(source, rid)

    return "unknown", "URL unavailable; review and refine."


# ---------------------------------------------------------------------------
# _strip_html — lightweight HTML → plain-text
# ---------------------------------------------------------------------------


def _strip_html(text):
    """Strip HTML tags, decode entities, collapse whitespace."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = _html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
