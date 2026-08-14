"""Tests for check-retraction.py — retraction status without network calls."""

import json
import sys

import pytest

import check_retraction as cr


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

CROSSREF_RETRACTED = json.dumps({
    "message": {
        "DOI": "10.1177/17588359231172420",
        "update-to": [
            {
                "updated": {"date-parts": [[2023, 4, 22]]},
                "DOI": "10.1177/1758835920922055",
                "type": "retraction",
                "source": "publisher",
                "label": "Retraction",
            },
        ],
    },
})

CROSSREF_CLEAN = json.dumps({
    "message": {"DOI": "10.1234/clean", "update-to": None},
})

CROSSREF_CONCERN = json.dumps({
    "message": {
        "DOI": "10.1234/concern",
        "update-to": [
            {
                "updated": {"date-parts": [[2022, 1, 5]]},
                "DOI": "10.1234/concern-notice",
                "type": "correction",
                "label": "Expression of Concern",
            },
        ],
    },
})

PUBMED_ESEARCH_FOUND = json.dumps({"esearchresult": {"idlist": ["12345"], "count": "1"}})
PUBMED_ESEARCH_EMPTY = json.dumps({"esearchresult": {"idlist": [], "count": "0"}})

PUBMED_ESUMMARY_RETRACTED = json.dumps({
    "result": {
        "uids": ["12345"],
        "12345": {
            "pubtype": ["Journal Article", "Retracted Publication"],
            "articleids": [{"idtype": "doi", "value": "10.1234/retracted"}],
        },
    },
})

PUBMED_ESUMMARY_CLEAN = json.dumps({
    "result": {
        "uids": ["12345"],
        "12345": {
            "pubtype": ["Journal Article"],
            "articleids": [{"idtype": "doi", "value": "10.1234/clean"}],
        },
    },
})

EPMC_EMPTY = json.dumps({"resultList": {"result": []}})


def fake_pubmed_fetch(endpoint, params):
    if endpoint == "esearch.fcgi":
        return PUBMED_ESEARCH_FOUND
    if endpoint == "esummary.fcgi":
        return PUBMED_ESUMMARY_RETRACTED
    raise AssertionError(f"unexpected PubMed endpoint: {endpoint}")


def fake_epmc_fetch(module, params):
    return EPMC_EMPTY


# ---------------------------------------------------------------------------
# check_crossref
# ---------------------------------------------------------------------------

class TestCheckCrossref:
    def test_retracted(self):
        def fake_fetch(url, label):
            return CROSSREF_RETRACTED

        result = cr.check_crossref("10.1177/17588359231172420", fetch_func=fake_fetch)
        assert result["retracted"] is True
        assert result["expression_of_concern"] is False
        assert len(result["update_to"]) == 1
        assert result["update_to"][0]["type"] == "retraction"
        assert result["update_to"][0]["date"] == "2023-4-22"

    def test_clean(self):
        def fake_fetch(url, label):
            return CROSSREF_CLEAN

        result = cr.check_crossref("10.1234/clean", fetch_func=fake_fetch)
        assert result["retracted"] is False
        assert result["update_to"] == []

    def test_expression_of_concern(self):
        def fake_fetch(url, label):
            return CROSSREF_CONCERN

        result = cr.check_crossref("10.1234/concern", fetch_func=fake_fetch)
        assert result["retracted"] is False
        assert result["expression_of_concern"] is True

    def test_request_url(self):
        seen = {}

        def fake_fetch(url, label):
            seen["url"] = url
            return CROSSREF_CLEAN

        cr.check_crossref("10.1234/clean", fetch_func=fake_fetch)
        assert seen["url"] == "https://api.crossref.org/works/10.1234/clean"


# ---------------------------------------------------------------------------
# check_pubmed
# ---------------------------------------------------------------------------

class TestCheckPubmed:
    def test_retracted_pubtype(self):
        def fake_fetch(endpoint, params):
            assert endpoint == "esummary.fcgi"
            return PUBMED_ESUMMARY_RETRACTED

        result = cr.check_pubmed("12345", fetch_func=fake_fetch)
        assert result["found"] is True
        assert result["retracted"] is True
        assert result["doi"] == "10.1234/retracted"

    def test_clean_pubtype(self):
        def fake_fetch(endpoint, params):
            return PUBMED_ESUMMARY_CLEAN

        result = cr.check_pubmed("12345", fetch_func=fake_fetch)
        assert result["found"] is True
        assert result["retracted"] is False

    def test_missing_pmid_not_an_error(self):
        missing = json.dumps({"result": {"uids": ["99999"]}})

        def fake_fetch(endpoint, params):
            return missing

        result = cr.check_pubmed("99999", fetch_func=fake_fetch)
        assert result["found"] is False
        assert result["retracted"] is False
        assert result["doi"] is None

    def test_email_passed(self):
        calls = []

        def fake_fetch(endpoint, params):
            calls.append(params)
            return PUBMED_ESUMMARY_CLEAN

        cr.check_pubmed("12345", fetch_func=fake_fetch, email="test@example.com")
        assert calls[0]["email"] == "test@example.com"


# ---------------------------------------------------------------------------
# check_retraction (orchestration)
# ---------------------------------------------------------------------------

class TestCheckRetraction:
    def test_doi_retracted_via_crossref(self):
        def fake_crossref(url, label):
            return CROSSREF_RETRACTED

        def fake_pubmed(endpoint, params):
            if endpoint == "esearch.fcgi":
                return PUBMED_ESEARCH_EMPTY
            raise AssertionError("esummary should not be reached when no PMID resolves")

        result = cr.check_retraction(
            "10.1177/17588359231172420",
            crossref_fetch=fake_crossref,
            pubmed_fetch=fake_pubmed,
            epmc_fetch=fake_epmc_fetch,
        )
        assert result["status"] == "retracted"
        assert "crossref" in result["sources_checked"]

    def test_doi_clean_with_pubmed_crosscheck(self):
        def fake_crossref(url, label):
            return CROSSREF_CLEAN

        def fake_pubmed(endpoint, params):
            if endpoint == "esearch.fcgi":
                return PUBMED_ESEARCH_FOUND
            if endpoint == "esummary.fcgi":
                return PUBMED_ESUMMARY_CLEAN
            raise AssertionError

        result = cr.check_retraction(
            "10.1234/clean",
            crossref_fetch=fake_crossref,
            pubmed_fetch=fake_pubmed,
            epmc_fetch=fake_epmc_fetch,
        )
        assert result["status"] == "not-retracted"
        assert set(result["sources_checked"]) == {"crossref", "pubmed"}

    def test_doi_not_in_pubmed_still_clean(self):
        def fake_crossref(url, label):
            return CROSSREF_CLEAN

        def fake_pubmed(endpoint, params):
            if endpoint == "esearch.fcgi":
                return PUBMED_ESEARCH_EMPTY
            raise AssertionError

        result = cr.check_retraction(
            "10.1234/clean",
            crossref_fetch=fake_crossref,
            pubmed_fetch=fake_pubmed,
            epmc_fetch=fake_epmc_fetch,
        )
        assert result["status"] == "not-retracted"
        assert result["sources_checked"] == ["crossref"]

    def test_pmid_retracted_via_pubtype(self):
        def fake_crossref(url, label):
            return CROSSREF_CLEAN

        def fake_pubmed(endpoint, params):
            if endpoint == "esummary.fcgi":
                return PUBMED_ESUMMARY_RETRACTED
            raise AssertionError(f"unexpected endpoint: {endpoint}")

        result = cr.check_retraction(
            "12345",
            crossref_fetch=fake_crossref,
            pubmed_fetch=fake_pubmed,
            epmc_fetch=fake_epmc_fetch,
        )
        assert result["status"] == "retracted"
        # PMID path resolves the DOI from esummary and also checks Crossref
        assert set(result["sources_checked"]) == {"pubmed", "crossref"}

    def test_unknown_when_all_sources_fail(self):
        def fail(url, label):
            raise RuntimeError("network down")

        def fail_pubmed(endpoint, params):
            raise RuntimeError("network down")

        result = cr.check_retraction(
            "10.1234/clean",
            crossref_fetch=fail,
            pubmed_fetch=fail_pubmed,
            epmc_fetch=fail_pubmed,
        )
        assert result["status"] == "unknown"
        assert "crossref" in result["errors"]


# ---------------------------------------------------------------------------
# _compute_status
# ---------------------------------------------------------------------------

class TestComputeStatus:
    def test_retracted_wins_over_concern(self):
        result = {
            "crossref": {"retracted": True, "expression_of_concern": True},
            "pubmed": None,
        }
        assert cr._compute_status(result) == "retracted"

    def test_not_retracted_requires_a_signal(self):
        assert cr._compute_status({"crossref": None, "pubmed": None}) == "unknown"
        assert cr._compute_status({"crossref": {"retracted": False}, "pubmed": None}) == "not-retracted"


# ---------------------------------------------------------------------------
# CLI / main
# ---------------------------------------------------------------------------

class TestMain:
    def test_requires_identifier(self, capsys):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(sys, "argv", ["check-retraction"])
            with pytest.raises(SystemExit):
                cr.main()

    def test_doi_text_output(self, capsys):
        def fake_crossref(url, label):
            return CROSSREF_RETRACTED

        def fake_pubmed(endpoint, params):
            if endpoint == "esearch.fcgi":
                return PUBMED_ESEARCH_EMPTY
            raise AssertionError

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(sys, "argv", ["check-retraction", "--doi", "10.1177/17588359231172420", "--format", "text"])
            mp.setattr(cr.utils, "_fetch_url", fake_crossref)
            mp.setattr(cr, "fetch_pubmed", fake_pubmed)
            mp.setattr(cr, "fetch_europe_pmc", fake_epmc_fetch)
            exit_code = cr.main()

        out = capsys.readouterr().out
        assert exit_code == 0
        assert "Status:     retracted" in out

    def test_unknown_returns_nonzero(self, capsys):
        def fail(url, label):
            raise RuntimeError("network down")

        def fail_pubmed(endpoint, params):
            raise RuntimeError("network down")

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(sys, "argv", ["check-retraction", "--doi", "10.1234/clean"])
            mp.setattr(cr.utils, "_fetch_url", fail)
            mp.setattr(cr, "fetch_pubmed", fail_pubmed)
            mp.setattr(cr, "fetch_europe_pmc", fail_pubmed)
            exit_code = cr.main()

        assert exit_code == 1
