"""Tests for med-db-term-wikipedia.py — Wikimedia REST API summary fetch."""

import json
import sys

import med_db_term_wikipedia as wikipedia


# ---------------------------------------------------------------------------
# build_api_url / build_article_url
# ---------------------------------------------------------------------------


class TestBuildApiUrl:
    def test_underscores_and_encoding(self):
        url = wikipedia.build_api_url("en", "Artificial intelligence")
        assert url == "https://en.wikipedia.org/api/rest_v1/page/summary/Artificial_intelligence"

    def test_language_edition(self):
        url = wikipedia.build_api_url("de", "Hypertonie")
        assert url.startswith("https://de.wikipedia.org/api/rest_v1/page/summary/")

    def test_encodes_reserved_characters(self):
        url = wikipedia.build_api_url("en", "A/B test")
        assert "A%2FB_test" in url


class TestBuildArticleUrl:
    def test_prefers_content_urls(self):
        content_urls = {"desktop": {"page": "https://en.wikipedia.org/wiki/Artificial_intelligence"}}
        url = wikipedia.build_article_url("en", "Artificial_intelligence", content_urls)
        assert url == "https://en.wikipedia.org/wiki/Artificial_intelligence"

    def test_falls_back_to_title(self):
        url = wikipedia.build_article_url("en", "Artificial intelligence")
        assert url == "https://en.wikipedia.org/wiki/Artificial_intelligence"


# ---------------------------------------------------------------------------
# parse_summary_response
# ---------------------------------------------------------------------------


class TestParseSummaryResponse:
    def test_full_mapping(self):
        data = {
            "lang": "en",
            "title": "Artificial intelligence",
            "displaytitle": '<span lang="en" dir="ltr"><span class="mw-page-title-main">Artificial intelligence</span></span>',
            "titles": {"canonical": "Artificial_intelligence"},
            "description": "Field of computer science",
            "extract": "Artificial intelligence (AI) is intelligence exhibited by machines.",
            "type": "standard",
            "content_urls": {
                "desktop": {"page": "https://en.wikipedia.org/wiki/Artificial_intelligence"}
            },
        }
        result = wikipedia.parse_summary_response(data)
        assert result["title"] == "Artificial intelligence"
        assert "displaytitle" not in result
        assert result["description"] == "Field of computer science"
        assert result["extract"].startswith("Artificial intelligence")
        assert result["type"] == "standard"
        assert result["lang"] == "en"

    def test_missing_optional_fields(self):
        result = wikipedia.parse_summary_response({"lang": "en", "title": "Stub"})
        assert result["title"] == "Stub"
        assert result["description"] == ""
        assert result["extract"] == ""
        assert result["url"] == "https://en.wikipedia.org/wiki/Stub"


# ---------------------------------------------------------------------------
# fetch_wikipedia_summary
# ---------------------------------------------------------------------------


class TestFetchWikipediaSummary:
    def test_parses_injected_json(self):
        raw = json.dumps({
            "lang": "en",
            "title": "Artificial_intelligence",
            "displaytitle": "Artificial intelligence",
            "description": "Field of computer science",
            "extract": "Artificial intelligence (AI) is intelligence exhibited by machines.",
        })

        def fake_fetch(url, title):
            assert title == "Artificial intelligence"
            return raw

        result = wikipedia.fetch_wikipedia_summary("en", "Artificial intelligence", fake_fetch)
        assert result["extract"].startswith("Artificial intelligence")

    def test_lookup_error_propagates(self):
        def fake_fetch(url, title):
            raise LookupError("no Wikipedia article for 'Nope'")

        try:
            wikipedia.fetch_wikipedia_summary("en", "Nope", fake_fetch)
            assert False, "expected LookupError"
        except LookupError:
            pass


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


class TestMain:
    def test_json_output(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-wikipedia",
            "--title", "Artificial intelligence",
            "--format", "json",
        ])
        monkeypatch.setattr(
            wikipedia,
            "fetch_wikipedia_summary",
            lambda language, title, fetch_url_func=None: {
                "title": "Artificial intelligence",
                "description": "Field of computer science",
                "extract": "Artificial intelligence (AI).",
                "type": "standard",
                "lang": "en",
                "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
            },
        )
        assert wikipedia.main() == 0
        data = json.loads(capsys.readouterr().out)
        assert data["title"] == "Artificial intelligence"
        assert data["extract"] == "Artificial intelligence (AI)."

    def test_text_output(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-wikipedia",
            "--title", "Artificial intelligence",
            "--format", "text",
        ])
        monkeypatch.setattr(
            wikipedia,
            "fetch_wikipedia_summary",
            lambda language, title, fetch_url_func=None: {
                "title": "Artificial intelligence",
                "description": "Field of computer science",
                "extract": "Artificial intelligence (AI).",
                "type": "standard",
                "lang": "en",
                "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
            },
        )
        assert wikipedia.main() == 0
        out = capsys.readouterr().out
        assert "title:       Artificial intelligence" in out
        assert "Artificial intelligence (AI)." in out

    def test_not_found_returns_one(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-wikipedia",
            "--title", "No such article",
        ])

        def not_found(language, title, fetch_url_func=None):
            raise LookupError("no Wikipedia article for 'No such article'")

        monkeypatch.setattr(wikipedia, "fetch_wikipedia_summary", not_found)
        assert wikipedia.main() == 1
        data = json.loads(capsys.readouterr().out)
        assert "no Wikipedia article" in data["error"]

    def test_network_error_json(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-wikipedia",
            "--title", "Some title",
            "--format", "json",
        ])

        def boom(language, title, fetch_url_func=None):
            raise OSError("connection refused")

        monkeypatch.setattr(wikipedia, "fetch_wikipedia_summary", boom)
        assert wikipedia.main() == 1
        data = json.loads(capsys.readouterr().out)
        assert data["title"] == "Some title"
        assert "connection refused" in data["error"]
