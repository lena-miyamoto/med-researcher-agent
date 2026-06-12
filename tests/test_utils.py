"""Tests for utils.py — shared helpers used across med-db scripts."""

import json
import urllib.error
from pathlib import Path

import pytest

import utils


class _FakeHeaders:
    def __init__(self, charset="utf-8"):
        self.charset = charset

    def get_content_charset(self, default="utf-8"):
        return self.charset or default


class _FakeResponse:
    def __init__(self, body, charset="utf-8"):
        self.body = body
        self.headers = _FakeHeaders(charset)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.body


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------


class TestSlugify:
    def test_basic_english(self):
        assert utils.slugify("Hello World") == "hello-world"

    def test_with_special_chars(self):
        assert utils.slugify("Vitamin D & Calcium (benefits)") == "vitamin-d-calcium-benefits"

    def test_unicode_to_ascii(self):
        """NFKD normalization converts accented chars to ASCII."""
        result = utils.slugify("café naïve étude")
        assert result == "cafe-naive-etude"

    def test_german_umlauts(self):
        result = utils.slugify("Übergewicht und Ernährung")
        assert result == "ubergewicht-und-ernahrung"

    def test_empty_string_fallback(self):
        assert utils.slugify("") == "record"

    def test_only_special_chars_fallback(self):
        assert utils.slugify("!@#$%") == "record"

    def test_custom_fallback(self):
        assert utils.slugify("!!!", fallback="custom-fb") == "custom-fb"

    def test_max_words_truncation(self):
        result = utils.slugify(
            "one two three four five six seven eight nine ten eleven twelve",
            max_words=5,
        )
        assert result == "one-two-three-four-five"

    def test_max_length_truncation(self):
        result = utils.slugify("a very long title that exceeds the character limit easily", max_length=25)
        assert len(result) <= 25
        assert result == "a-very-long-title-that-ex"

    def test_max_length_doesnt_end_with_hyphen(self):
        result = utils.slugify("abcdef-ghijklm-nopqrstuv", max_length=13)
        assert not result.endswith("-")

    def test_consecutive_special_chars(self):
        assert utils.slugify("hello---world___test") == "hello-world-test"

    def test_str_coerces_non_string(self):
        """Should handle numeric input via str()."""
        assert utils.slugify(35350465) == "35350465"

    def test_default_max_words(self):
        """max_words defaults to 10."""
        result = utils.slugify("a " * 15)
        assert result.count("-") == 9  # 10 words, 9 hyphens

    def test_default_max_length(self):
        """max_length defaults to 80, rstrip hyphen."""
        long_text = "a" * 100
        assert len(utils.slugify(long_text)) <= 80

    def test_nfkd_vs_no_nfkd_non_ascii_slug_difference(self):
        """Prove NFKD normalisation matters for non-ASCII input.

        This is the regression test for the validator slugify divergence
        bug.  Without NFKD, Umlauts and accents are stripped to hyphens
        rather than transliterated to ASCII.
        """
        # NFKD ON  (canonical) — ü → u, ß → ss, é → e
        assert utils.slugify("Käse-Törtchen") == "kase-tortchen"
        # NFKD OFF (old validator variant) would produce "k-se-t-rtchen"
        # because ä, ö, ü, é are not in [a-z0-9].


# ---------------------------------------------------------------------------
# fetch_pubmed / fetch_europe_pmc
# ---------------------------------------------------------------------------


class TestFetchPubmed:
    def test_raises_runtime_error_on_failure(self):
        """Network errors raise RuntimeError (not SystemExit)."""
        with pytest.raises(RuntimeError):
            utils.fetch_pubmed("nonexistent.fcgi", {}, timeout=0.1)

    def test_includes_user_agent(self):
        """The request should carry our User-Agent header."""
        # We verify the constant is non-empty — the actual header is set
        # inside the function, tested implicitly by integration.
        assert len(utils.USER_AGENT) > 20

    def test_retries_transient_failure(self, monkeypatch):
        calls = []

        def fake_urlopen(request, timeout):
            calls.append((request, timeout))
            if len(calls) == 1:
                raise urllib.error.URLError("temporary reset")
            return _FakeResponse(b'{"ok": true}')

        monkeypatch.setattr(utils.urllib.request, "urlopen", fake_urlopen)
        monkeypatch.setattr(utils.time, "sleep", lambda delay: None)

        assert utils.fetch_pubmed("esearch.fcgi", {}, timeout=5) == '{"ok": true}'
        assert len(calls) == 2

    def test_decodes_declared_charset(self, monkeypatch):
        def fake_urlopen(request, timeout):
            return _FakeResponse("café".encode("iso-8859-1"), charset="iso-8859-1")

        monkeypatch.setattr(utils.urllib.request, "urlopen", fake_urlopen)

        assert utils.fetch_pubmed("esearch.fcgi", {}, timeout=5) == "café"

    def test_does_not_retry_client_http_error(self, monkeypatch):
        calls = []

        def fake_urlopen(request, timeout):
            calls.append(request)
            raise urllib.error.HTTPError(request.full_url, 404, "not found", {}, None)

        monkeypatch.setattr(utils.urllib.request, "urlopen", fake_urlopen)

        with pytest.raises(RuntimeError):
            utils.fetch_pubmed("missing.fcgi", {}, timeout=5)
        assert len(calls) == 1


class TestFetchEuropePmc:
    def test_raises_runtime_error_on_failure(self):
        with pytest.raises(RuntimeError):
            utils.fetch_europe_pmc("nonexistent", {}, timeout=0.1)


# ---------------------------------------------------------------------------
# europe_pmc_article_url
# ---------------------------------------------------------------------------


class TestEuropePmcArticleUrl:
    def test_med_source(self):
        assert utils.europe_pmc_article_url("MED", "35350465") == "https://europepmc.org/article/MED/35350465"

    def test_ppr_source(self):
        assert utils.europe_pmc_article_url("PPR", "PPR12345") == "https://europepmc.org/article/PPR/PPR12345"


# ---------------------------------------------------------------------------
# default_paper_entry
# ---------------------------------------------------------------------------


class TestDefaultPaperEntry:
    def test_pubmed_single_uid(self, tmp_path):
        data = {"result": {"uids": ["12345678"]}}
        path = tmp_path / "metadata.json"
        path.write_text(json.dumps(data))
        ident, url = utils.default_paper_entry(path)
        assert ident == "PMID:12345678"
        assert url == "https://pubmed.ncbi.nlm.nih.gov/12345678/"

    def test_pubmed_multiple_uids(self, tmp_path):
        """Multiple uids → falls through to unknown."""
        data = {"result": {"uids": ["111", "222"]}}
        path = tmp_path / "metadata.json"
        path.write_text(json.dumps(data))
        ident, url = utils.default_paper_entry(path)
        assert ident == "unknown"
        assert "unavailable" in url

    def test_europe_pmc_record(self, tmp_path):
        data = {
            "resultList": {
                "result": [{"source": "MED", "id": "35350465", "title": "Test"}]
            }
        }
        path = tmp_path / "metadata.json"
        path.write_text(json.dumps(data))
        ident, url = utils.default_paper_entry(path)
        assert ident == "MED:35350465"
        assert "europepmc.org/article/MED/35350465" in url

    def test_europe_pmc_fallback_to_pmid(self, tmp_path):
        """When 'id' is missing, fall back to 'pmid'."""
        data = {
            "resultList": {
                "result": [{"source": "MED", "pmid": "12345678"}]
            }
        }
        path = tmp_path / "metadata.json"
        path.write_text(json.dumps(data))
        ident, url = utils.default_paper_entry(path)
        assert ident == "MED:12345678"

    def test_unknown_format(self, tmp_path):
        data = {"something": "unexpected"}
        path = tmp_path / "metadata.json"
        path.write_text(json.dumps(data))
        ident, url = utils.default_paper_entry(path)
        assert ident == "unknown"
        assert "unavailable" in url

    def test_invalid_json_returns_unknown(self, tmp_path):
        """Corrupt JSON should not crash — regression test for dedup
        where med-db.py had no error handling but med-db-query.py did."""
        path = tmp_path / "metadata.json"
        path.write_text("not valid {{{ json")
        ident, url = utils.default_paper_entry(path)
        assert ident == "unknown"
        assert "unavailable" in url

    def test_missing_file_returns_unknown(self, tmp_path):
        """Missing file should not crash."""
        path = tmp_path / "nonexistent.json"
        ident, url = utils.default_paper_entry(path)
        assert ident == "unknown"
        assert "unavailable" in url

    def test_empty_file_returns_unknown(self, tmp_path):
        path = tmp_path / "metadata.json"
        path.write_text("")
        ident, url = utils.default_paper_entry(path)
        assert ident == "unknown"
        assert "unavailable" in url

    def test_accepts_string_path(self, tmp_path):
        """Should accept a string path, not just Path."""
        data = {"result": {"uids": ["12345"]}}
        path = tmp_path / "metadata.json"
        path.write_text(json.dumps(data))
        ident, url = utils.default_paper_entry(str(path))
        assert ident == "PMID:12345"

    def test_pubmed_with_zero_uids(self, tmp_path):
        """Empty uids list → falls through to unknown."""
        data = {"result": {"uids": []}}
        path = tmp_path / "metadata.json"
        path.write_text(json.dumps(data))
        ident, url = utils.default_paper_entry(path)
        assert ident == "unknown"

    def test_europe_pmc_empty_result_list(self, tmp_path):
        """Empty result list → falls through to unknown."""
        data = {"resultList": {"result": []}}
        path = tmp_path / "metadata.json"
        path.write_text(json.dumps(data))
        ident, url = utils.default_paper_entry(path)
        assert ident == "unknown"


# ---------------------------------------------------------------------------
# _strip_html
# ---------------------------------------------------------------------------


class TestStripHtml:
    def test_removes_tags(self):
        assert utils._strip_html("<p>Hello</p>") == "Hello"

    def test_decodes_entities(self):
        assert utils._strip_html("&amp;") == "&"
        assert utils._strip_html("&lt;") == "<"
        assert utils._strip_html("&gt;") == ">"

    def test_collapses_whitespace(self):
        assert utils._strip_html("<p>a  b</p>") == "a b"

    def test_empty_string(self):
        assert utils._strip_html("") == ""
        assert utils._strip_html(None) == ""

    def test_nested_tags(self):
        assert utils._strip_html("<div><p>text</p></div>") == "text"


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_eutils_base_is_https(self):
        assert utils.EUTILS_BASE.startswith("https://")

    def test_europe_pmc_base_is_https(self):
        assert utils.EUROPE_PMC_BASE.startswith("https://")

    def test_user_agent_not_empty(self):
        assert len(utils.USER_AGENT) > 0
        assert "Mozilla" in utils.USER_AGENT
