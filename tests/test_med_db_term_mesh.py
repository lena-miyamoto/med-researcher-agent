"""Tests for med-db-term-mesh.py — MeSH scope note fetch."""

import json
import sys
import urllib.error

import med_db_term_mesh as mesh


# ---------------------------------------------------------------------------
# URL builders / URI helpers
# ---------------------------------------------------------------------------


class TestBuildLookupUrl:
    def test_exact_match(self):
        url = mesh.build_lookup_url("Executive Function", "exact")
        assert url == (
            "https://id.nlm.nih.gov/mesh/lookup/descriptor?"
            "label=Executive+Function&limit=1&match=exact"
        )

    def test_broad_omits_match(self):
        url = mesh.build_lookup_url("Executive Function", None)
        assert "match=" not in url
        assert "label=Executive+Function" in url


class TestBuildResourceUrl:
    def test_https_json(self):
        assert mesh.build_resource_url("D056344") == "https://id.nlm.nih.gov/mesh/D056344.json"


class TestExtractDescriptorId:
    def test_descriptor_and_concept(self):
        assert mesh.extract_descriptor_id("http://id.nlm.nih.gov/mesh/D056344") == "D056344"
        assert mesh.extract_descriptor_id("http://id.nlm.nih.gov/mesh/M0526990") == "M0526990"


class TestJsonLdValue:
    def test_dict(self):
        assert mesh.json_ld_value({"@value": "hello"}) == "hello"

    def test_plain_string(self):
        assert mesh.json_ld_value("hello") == "hello"

    def test_missing(self):
        assert mesh.json_ld_value(None) == ""


# ---------------------------------------------------------------------------
# response parsers
# ---------------------------------------------------------------------------


class TestParseLookupResponse:
    def test_match(self):
        data = [{"resource": "http://id.nlm.nih.gov/mesh/D056344", "label": "Executive Function"}]
        descriptor_id, label = mesh.parse_lookup_response(data, "Executive Function")
        assert descriptor_id == "D056344"
        assert label == "Executive Function"

    def test_empty(self):
        descriptor_id, label = mesh.parse_lookup_response([], "Nope")
        assert descriptor_id is None
        assert label == "Nope"


class TestParseScopeNote:
    def test_present(self):
        data = {"scopeNote": {"@value": "A set of cognitive functions."}}
        assert mesh.parse_scope_note(data) == "A set of cognitive functions."

    def test_absent(self):
        assert mesh.parse_scope_note({}) == ""


# ---------------------------------------------------------------------------
# fetch_mesh_scope_note
# ---------------------------------------------------------------------------


class TestFetchMeshScopeNote:
    def test_full_flow(self):
        def fake_fetch(url, term):
            if "/lookup/descriptor" in url:
                return json.dumps([
                    {"resource": "http://id.nlm.nih.gov/mesh/D056344", "label": "Executive Function"}
                ])
            if url.endswith("D056344.json"):
                return json.dumps({
                    "identifier": "D056344",
                    "label": {"@value": "Executive Function"},
                    "preferredConcept": "http://id.nlm.nih.gov/mesh/M0526990",
                })
            if url.endswith("M0526990.json"):
                return json.dumps({"scopeNote": {"@value": "A set of cognitive functions."}})
            raise AssertionError(f"unexpected url: {url}")

        result = mesh.fetch_mesh_scope_note("Executive Function", fake_fetch)
        assert result["term"] == "Executive Function"
        assert result["descriptor_id"] == "D056344"
        assert result["descriptor_label"] == "Executive Function"
        assert result["scope_note"] == "A set of cognitive functions."
        assert result["url"] == "https://id.nlm.nih.gov/mesh/D056344"

    def test_no_descriptor_returns_none(self):
        def fake_fetch(url, term):
            return json.dumps([])

        assert mesh.fetch_mesh_scope_note("Nope", fake_fetch) is None

    def test_descriptor_without_scope_note(self):
        def fake_fetch(url, term):
            if "/lookup/descriptor" in url:
                return json.dumps([
                    {"resource": "http://id.nlm.nih.gov/mesh/D000000", "label": "Term"}
                ])
            if url.endswith("D000000.json"):
                return json.dumps({"preferredConcept": "http://id.nlm.nih.gov/mesh/M0000000"})
            if url.endswith("M0000000.json"):
                return json.dumps({})
            raise AssertionError(f"unexpected url: {url}")

        result = mesh.fetch_mesh_scope_note("Term", fake_fetch)
        assert result["scope_note"] == ""
        assert result["descriptor_id"] == "D000000"


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


class TestMain:
    def _result(self):
        return {
            "term": "Executive Function",
            "descriptor_id": "D056344",
            "descriptor_label": "Executive Function",
            "scope_note": "A set of cognitive functions.",
            "url": "https://id.nlm.nih.gov/mesh/D056344",
        }

    def test_json_output(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-mesh", "--term", "Executive Function", "--format", "json",
        ])
        monkeypatch.setattr(mesh, "fetch_mesh_scope_note", lambda term, fetch_url_func=None: self._result())
        assert mesh.main() == 0
        data = json.loads(capsys.readouterr().out)
        assert data["descriptor_id"] == "D056344"
        assert data["scope_note"] == "A set of cognitive functions."

    def test_text_output(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-mesh", "--term", "Executive Function", "--format", "text",
        ])
        monkeypatch.setattr(mesh, "fetch_mesh_scope_note", lambda term, fetch_url_func=None: self._result())
        assert mesh.main() == 0
        out = capsys.readouterr().out
        assert "descriptor:      D056344" in out
        assert "A set of cognitive functions." in out

    def test_not_found_returns_one_json(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["med-db-term-mesh", "--term", "Nope"])
        monkeypatch.setattr(mesh, "fetch_mesh_scope_note", lambda term, fetch_url_func=None: None)
        assert mesh.main() == 1
        data = json.loads(capsys.readouterr().out)
        assert data["term"] == "Nope"
        assert "no MeSH descriptor" in data["error"]

    def test_not_found_returns_one_text(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["med-db-term-mesh", "--term", "Nope", "--format", "text"])
        monkeypatch.setattr(mesh, "fetch_mesh_scope_note", lambda term, fetch_url_func=None: None)
        assert mesh.main() == 1
        assert "no MeSH descriptor" in capsys.readouterr().err

    def test_network_error_json(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["med-db-term-mesh", "--term", "Executive Function"])

        def boom(term, fetch_url_func=None):
            raise OSError("network down")

        monkeypatch.setattr(mesh, "fetch_mesh_scope_note", boom)
        assert mesh.main() == 1
        data = json.loads(capsys.readouterr().out)
        assert data["term"] == "Executive Function"
        assert "network down" in data["error"]

    def test_http_error_json(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["med-db-term-mesh", "--term", "Executive Function"])

        def boom(term, fetch_url_func=None):
            raise urllib.error.HTTPError(
                "https://id.nlm.nih.gov/mesh", 500, "Server Error", None, None
            )

        monkeypatch.setattr(mesh, "fetch_mesh_scope_note", boom)
        assert mesh.main() == 1
        data = json.loads(capsys.readouterr().out)
        assert data["term"] == "Executive Function"
        assert "500" in data["error"]
