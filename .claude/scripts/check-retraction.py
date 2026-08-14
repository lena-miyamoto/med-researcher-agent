"""Retraction-status checker — Crossref + PubMed.

Determines whether a paper is retracted or has an outstanding expression of
concern. Crossref ``update-to`` is the primary signal; PubMed ``pubtype`` is
the cross-check for biomedical papers. Read-only: makes no archive writes.

Core functions accept injectable ``fetch_func`` parameters so they can be
tested without network calls, mirroring ``med-db-lookup.py``.
"""

import argparse
import json

import utils


# Re-export for tests that reference them via the module
fetch_pubmed = utils.fetch_pubmed
fetch_europe_pmc = utils.fetch_europe_pmc

CROSSREF_WORKS_BASE = "https://api.crossref.org/works/"

RETRACTION_PUBTYPE_MARKERS = ("retracted", "retraction")


def _looks_like_doi(identifier):
    """Return True when *identifier* is DOI-shaped (starts with ``10.``)."""
    return str(identifier).startswith("10.") and "/" in str(identifier)


def _fetch_crossref_message(doi, fetch_func=None):
    """Fetch the Crossref direct DOI record and return its ``message`` dict."""
    if fetch_func is None:
        fetch_func = utils._fetch_url
    raw = fetch_func(f"{CROSSREF_WORKS_BASE}{doi}", f"Crossref works {doi}")
    return json.loads(raw).get("message", {})


def _parse_update_events(message):
    """Extract update events (retraction/correction) from a Crossref message."""
    events = []
    for entry in message.get("update-to") or []:
        updated = entry.get("updated") or {}
        date_parts = updated.get("date-parts") or []
        date = None
        if date_parts and date_parts[0]:
            date = "-".join(str(part) for part in date_parts[0])
        events.append({
            "type": entry.get("type"),
            "source": entry.get("source"),
            "label": entry.get("label"),
            "doi": entry.get("DOI"),
            "date": date,
        })
    return events


def check_crossref(doi, fetch_func=None):
    """Return the Crossref retraction signal for a DOI.

    Returns a dict with ``retracted`` (bool), ``expression_of_concern`` (bool),
    and ``update_to`` (list of update events).
    """
    message = _fetch_crossref_message(doi, fetch_func=fetch_func)
    events = _parse_update_events(message)
    retraction_events = [event for event in events if event.get("type") == "retraction"]
    concern_events = [
        event
        for event in events
        if event.get("type") != "retraction"
        and "concern" in str(event.get("label") or "").lower()
    ]
    return {
        "doi": doi,
        "update_to": events,
        "retracted": bool(retraction_events),
        "expression_of_concern": bool(concern_events),
    }


def _pubtypes_show_retraction(pubtypes):
    """Return True when any PubMed pubtype marks a retraction."""
    for pubtype in pubtypes or []:
        lowered = str(pubtype).lower()
        if any(marker in lowered for marker in RETRACTION_PUBTYPE_MARKERS):
            return True
    return False


def check_pubmed(pmid, fetch_func=None, email=None):
    """Return the PubMed pubtype signal for a PMID.

    Returns a dict with ``found`` (bool), ``doi`` (or None), ``pubtypes``,
    and ``retracted`` (bool). A missing PMID is a ``found`` result, not an
    error — no PubMed record is expected for non-biomedical journals.
    """
    if fetch_func is None:
        fetch_func = fetch_pubmed
    params = {"db": "pubmed", "retmode": "json", "id": str(pmid), "tool": "check-retraction"}
    if email:
        params["email"] = email
    raw = fetch_func("esummary.fcgi", params)
    summary = json.loads(raw)
    records = summary.get("result", {})
    record = records.get(str(pmid))
    if not record or "error" in record:
        return {"pmid": str(pmid), "found": False, "doi": None, "pubtypes": [], "retracted": False}

    doi = None
    for article_id in record.get("articleids", []):
        if article_id.get("idtype") == "doi":
            doi = article_id.get("value")
            break
    pubtypes = record.get("pubtype", [])
    return {
        "pmid": str(pmid),
        "found": True,
        "doi": doi,
        "pubtypes": pubtypes,
        "retracted": _pubtypes_show_retraction(pubtypes),
    }


def check_retraction(identifier, crossref_fetch=None, pubmed_fetch=None, epmc_fetch=None, email=None):
    """Check retraction status for a DOI or PMID across Crossref and PubMed.

    Returns a verdict dict with ``status`` (retracted / expression-of-concern /
    not-retracted / unknown), ``sources_checked``, ``crossref``, ``pubmed``,
    and ``errors``.
    """
    if crossref_fetch is None:
        crossref_fetch = utils._fetch_url
    if pubmed_fetch is None:
        pubmed_fetch = fetch_pubmed
    if epmc_fetch is None:
        epmc_fetch = fetch_europe_pmc

    is_doi = _looks_like_doi(identifier)
    doi = identifier if is_doi else None
    pmid = None if is_doi else str(identifier)

    result = {
        "identifier": identifier,
        "sources_checked": [],
        "status": "unknown",
        "crossref": None,
        "pubmed": None,
        "errors": {},
    }

    # PubMed cross-check — resolve DOI→PMID, or use the given PMID
    if pmid is None and doi:
        source, resolved = utils.resolve_doi_to_id(
            doi, email=email, pubmed_fetch_func=pubmed_fetch, epmc_fetch_func=epmc_fetch
        )
        if source == "pubmed":
            pmid = resolved
    if pmid:
        try:
            result["pubmed"] = check_pubmed(pmid, fetch_func=pubmed_fetch, email=email)
            result["sources_checked"].append("pubmed")
            if doi is None and result["pubmed"].get("doi"):
                doi = result["pubmed"]["doi"]
        except (RuntimeError, json.JSONDecodeError) as exc:
            result["errors"]["pubmed"] = str(exc)

    # Crossref — primary source
    if doi:
        try:
            result["crossref"] = check_crossref(doi, fetch_func=crossref_fetch)
            result["sources_checked"].append("crossref")
        except (RuntimeError, json.JSONDecodeError) as exc:
            result["errors"]["crossref"] = str(exc)

    result["status"] = _compute_status(result)
    return result


def _compute_status(result):
    """Derive the verdict status from Crossref and PubMed signals."""
    crossref = result.get("crossref")
    pubmed = result.get("pubmed")

    retracted = False
    concern = False
    has_crossref_signal = crossref is not None
    has_pubmed_signal = pubmed is not None and pubmed.get("found")

    if crossref:
        retracted = retracted or crossref.get("retracted", False)
        concern = concern or crossref.get("expression_of_concern", False)
    if pubmed and pubmed.get("found"):
        retracted = retracted or pubmed.get("retracted", False)

    if retracted:
        return "retracted"
    if concern:
        return "expression-of-concern"
    if not has_crossref_signal and not has_pubmed_signal:
        return "unknown"
    return "not-retracted"


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _format_json(results):
    return json.dumps({"results": results}, indent=2, default=str, ensure_ascii=False)


def _format_text(results):
    lines = []
    for index, result in enumerate(results, 1):
        lines.append(f"--- Result {index} ---")
        lines.append(f"Identifier: {result['identifier']}")
        lines.append(f"Status:     {result['status']}")

        crossref = result.get("crossref")
        if crossref is not None:
            if crossref.get("retracted"):
                retraction_events = [
                    event for event in crossref.get("update_to", [])
                    if event.get("type") == "retraction"
                ]
                lines.append(f"Crossref:   retracted ({len(retraction_events)} event(s))")
                for event in retraction_events:
                    lines.append(
                        f"  - {event.get('source', 'unknown')}: {event.get('label', 'Retraction')} "
                        f"({event.get('date', 'date unknown')})"
                    )
            elif crossref.get("expression_of_concern"):
                lines.append("Crossref:   expression of concern")
            else:
                lines.append("Crossref:   no retraction")
        elif "crossref" in result.get("errors", {}):
            lines.append(f"Crossref:   error — {result['errors']['crossref']}")

        pubmed = result.get("pubmed")
        if pubmed is not None:
            if not pubmed.get("found"):
                lines.append("PubMed:     no record (expected for non-biomedical journals)")
            elif pubmed.get("retracted"):
                lines.append(f"PubMed:     retracted pubtype ({', '.join(pubmed['pubtypes'])})")
            else:
                lines.append("PubMed:     not retracted")
        elif "pubmed" in result.get("errors", {}):
            lines.append(f"PubMed:     error — {result['errors']['pubmed']}")

        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check retraction status via Crossref and PubMed. Read-only.",
    )
    parser.add_argument(
        "--doi",
        action="append",
        default=[],
        help="DOI to check. May be passed multiple times.",
    )
    parser.add_argument(
        "--pmid",
        action="append",
        default=[],
        help="PMID to check. May be passed multiple times.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format. Defaults to json.",
    )
    parser.add_argument(
        "--email",
        help="Optional contact email passed to NCBI E-utilities.",
    )

    args = parser.parse_args()
    if not args.doi and not args.pmid:
        parser.error("provide at least one of --doi or --pmid")
    return args


def main():
    args = parse_args()
    identifiers = args.doi + args.pmid
    results = [check_retraction(identifier, email=args.email) for identifier in identifiers]

    if args.format == "text":
        print(_format_text(results))
    else:
        print(_format_json(results))

    # Non-zero only when a check could not be determined (status "unknown").
    return 1 if any(result["status"] == "unknown" for result in results) else 0


if __name__ == "__main__":
    utils.run_cli(main)
