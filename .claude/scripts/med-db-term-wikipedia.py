"""Fetch a Wikipedia article's lead summary via the Wikimedia REST API.

Calls ``/api/rest_v1/page/summary/{title}`` and returns the lead-section
``extract`` (plain text), the short Wikidata ``description``, and the
canonical article URL.  Used by the ``define-terms`` skill as the fallback
web source for term definitions.

Reference: https://en.wikipedia.org/api/rest_v1/
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

import utils


def build_api_url(language, title):
    """Return the REST summary URL for a Wikipedia article *title*."""
    title_slug = title.strip().replace(" ", "_")
    encoded_title = urllib.parse.quote(title_slug, safe="")
    return f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"


def build_article_url(language, title, content_urls=None):
    """Return the canonical article URL, preferring the API's ``content_urls``."""
    if content_urls and content_urls.get("desktop", {}).get("page"):
        return content_urls["desktop"]["page"]
    title_slug = title.strip().replace(" ", "_")
    encoded_title = urllib.parse.quote(title_slug, safe="")
    return f"https://{language}.wikipedia.org/wiki/{encoded_title}"


def parse_summary_response(data):
    """Map the REST summary JSON to a flat result dict.

    ``title`` is the API's space-separated page title (plain text); the
    ``displaytitle`` and ``titles.display`` fields are HTML markup, so they
    are not surfaced.  The canonical underscore form is only needed to
    build the article URL, which prefers ``content_urls``.
    """
    language = data.get("lang", "")
    title = data.get("title", "")
    return {
        "title": title,
        "description": data.get("description", ""),
        "extract": data.get("extract", ""),
        "type": data.get("type", ""),
        "lang": language,
        "url": build_article_url(language, title, data.get("content_urls")),
    }


def _fetch_url_text(url, title):
    """GET *url* and return the decoded body, with one retry on server errors.

    A missing article (HTTP 404) is raised as ``LookupError``; other HTTP
    and network errors propagate.
    """
    request = urllib.request.Request(url, headers={"User-Agent": utils.USER_AGENT})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                charset = response.headers.get_content_charset("utf-8")
                return raw.decode(charset)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise LookupError(f"no Wikipedia article for '{title}'") from exc
            if exc.code < 500 or attempt == 1:
                raise
        except (urllib.error.URLError, OSError):
            if attempt == 1:
                raise


def fetch_wikipedia_summary(language, title, fetch_url_func=None):
    """Fetch and parse the Wikipedia lead summary for *title*.

    Raises ``LookupError`` when the article does not exist and
    ``urllib.error.URLError``/``OSError`` on network failures.
    ``fetch_url_func`` allows injecting a test double; when ``None`` the
    real network fetch is used.
    """
    fetch_url = fetch_url_func or _fetch_url_text
    url = build_api_url(language, title)
    raw = fetch_url(url, title)
    data = json.loads(raw)
    return parse_summary_response(data)


def _format_text(result):
    lines = [
        f"title:       {result['title']}",
        f"description: {result['description'] or '(none)'}",
        f"lang:        {result['lang']}",
        f"url:         {result['url']}",
        "",
        result["extract"],
    ]
    return "\n".join(lines).rstrip() + "\n"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch a Wikipedia article's lead summary via the Wikimedia REST API.",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Wikipedia article title, spaces or underscores (e.g. 'Artificial intelligence').",
    )
    parser.add_argument(
        "--lang",
        default="en",
        help="Wikipedia language edition. Default: en.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format. Default: json.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        result = fetch_wikipedia_summary(args.lang, args.title)
    except LookupError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(_format_text(result))
    return 0


if __name__ == "__main__":
    utils.run_cli(main)
