"""Fetch a MeSH descriptor's scope note via the NLM id.nlm.nih.gov API.

Three sequential requests resolve a term to its authoritative English
definition:

  1. descriptor lookup  (label -> descriptor ID, e.g. D056344)
  2. descriptor record  (descriptor -> preferred concept URI)
  3. concept record     (concept -> scopeNote)

Used by the ``define-terms`` skill as a stage-3 authoritative source.
Scope notes are English-only and often terse; definitions derived from
them still require German translation.

Reference: https://id.nlm.nih.gov/mesh
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse

import utils

MESH_BASE = "https://id.nlm.nih.gov/mesh"


def build_lookup_url(term, match=None):
    """Return the descriptor-lookup URL, with an optional ``match`` filter."""
    query = {"label": term, "limit": "1"}
    if match:
        query["match"] = match
    return f"{MESH_BASE}/lookup/descriptor?{urllib.parse.urlencode(query)}"


def build_resource_url(identifier):
    """Return the HTTPS JSON URL for a descriptor or concept identifier."""
    return f"{MESH_BASE}/{identifier}.json"


def extract_descriptor_id(resource_uri):
    """Return the trailing identifier (``D056344``, ``M0526990``) from a MeSH URI."""
    return resource_uri.rstrip("/").split("/")[-1]


def json_ld_value(value, default=""):
    """Return the plain text of a JSON-LD string field (``{"@value": ...}``)."""
    if isinstance(value, dict):
        return value.get("@value", default)
    if isinstance(value, str):
        return value
    return default


def parse_lookup_response(data, term):
    """Return ``(descriptor_id, label)`` from a lookup response, or ``(None, term)``."""
    results = data if isinstance(data, list) else []
    if not results:
        return None, term
    first = results[0]
    resource = first.get("resource", "")
    descriptor_id = extract_descriptor_id(resource) if resource else ""
    label = first.get("label", term)
    return descriptor_id or None, label


def parse_scope_note(data):
    """Return the ``scopeNote`` plain text, or an empty string when absent."""
    return json_ld_value(data.get("scopeNote"))


def _fetch_url_text(url, term):
    """GET *url* and return the decoded body via the shared retrying fetcher.

    A missing record (HTTP 404) is raised as ``LookupError``; other HTTP
    and network errors propagate.
    """
    return utils.fetch_text(
        url, f"MeSH {term}", not_found_message=f"no MeSH record for '{term}'"
    )


def _lookup_descriptor(term, fetch_url):
    """Try an exact then a broad descriptor lookup; return ``(id, label)``."""
    for match in ("exact", None):
        url = build_lookup_url(term, match)
        data = json.loads(fetch_url(url, term))
        descriptor_id, label = parse_lookup_response(data, term)
        if descriptor_id is not None:
            return descriptor_id, label
    return None, term


def fetch_mesh_scope_note(term, fetch_url_func=None):
    """Resolve *term* to its MeSH scope note via three API requests.

    Returns a dict with ``term``, ``descriptor_id``, ``descriptor_label``,
    ``scope_note``, and ``url``; returns ``None`` when no descriptor
    matches.  ``fetch_url_func`` allows injecting a test double; when
    ``None`` the real network fetch is used.
    """
    fetch_url = fetch_url_func or _fetch_url_text

    descriptor_id, label = _lookup_descriptor(term, fetch_url)
    if descriptor_id is None:
        return None

    descriptor_data = json.loads(fetch_url(build_resource_url(descriptor_id), term))
    preferred_concept = descriptor_data.get("preferredConcept", "")
    if not label:
        label = json_ld_value(descriptor_data.get("label"), term)

    scope_note = ""
    if preferred_concept:
        concept_id = extract_descriptor_id(preferred_concept)
        concept_data = json.loads(fetch_url(build_resource_url(concept_id), term))
        scope_note = parse_scope_note(concept_data)

    return {
        "term": term,
        "descriptor_id": descriptor_id,
        "descriptor_label": label,
        "scope_note": scope_note,
        "url": f"{MESH_BASE}/{descriptor_id}",
    }


def _format_text(result):
    lines = [
        f"term:            {result['term']}",
        f"descriptor:      {result['descriptor_id']}",
        f"label:           {result['descriptor_label']}",
        f"url:             {result['url']}",
        "",
        result["scope_note"] or "(no scope note)",
    ]
    return "\n".join(lines).rstrip() + "\n"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch a MeSH descriptor's scope note via the NLM id.nlm.nih.gov API.",
    )
    parser.add_argument(
        "--term",
        required=True,
        help="MeSH term to look up (e.g. 'Executive Function').",
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
        result = fetch_mesh_scope_note(args.term)
    except LookupError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if result is None:
        print(f"error: no MeSH descriptor for '{args.term}'", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(_format_text(result))
    return 0


if __name__ == "__main__":
    utils.run_cli(main)
