"""Tests for med-db-validate.py — structure and index validator."""

import json
import sys
from pathlib import Path
from unittest import mock

import pytest

import med_db_validate


# ---------------------------------------------------------------------------
# slugify (validator variant)
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_basic(self):
        assert med_db_validate.slugify("Hello World") == "hello-world"

    def test_special_chars(self):
        assert med_db_validate.slugify("Vitamin D & Calcium") == "vitamin-d-calcium"

    def test_empty_string(self):
        assert med_db_validate.slugify("") == "record"

    def test_only_special(self):
        assert med_db_validate.slugify("!!!") == "record"

    def test_number(self):
        assert med_db_validate.slugify(35350465) == "35350465"

    def test_nfkd_normalization_non_ascii(self):
        """REGRESSION: the validator's old slugify lacked NFKD normalisation,
        so Umlauts/accents were replaced with hyphens instead of being
        transliterated to ASCII.  The canonical utils.slugify now handles
        this correctly."""
        # ü → u, ß → ss, é → e (NFKD transliteration)
        assert med_db_validate.slugify("Käse-Törtchen") == "kase-tortchen"
        # The old variant would have produced "k-se-t-rtchen"

    def test_validator_slugify_matches_canonical(self):
        """The validator must use the same slugify as the archiver to avoid
        false 'id mismatch' errors when validating folder names."""
        import utils
        test_cases = [
            ("Hello World", "record", 10, 80),
            ("Café Étude", "record", 10, 80),
            ("Übergewicht Ernährung", "record", 10, 80),
            ("!!!", "custom-fallback", 10, 80),
            (35350465, "record", 10, 80),
        ]
        for text, fallback, max_words, max_length in test_cases:
            assert med_db_validate.slugify(text, fallback, max_words, max_length) == \
                   utils.slugify(text, fallback, max_words, max_length)


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------

class TestParseArgs:
    def test_default_med_db(self):
        with mock.patch.object(sys, "argv", ["med-db-validate.py"]):
            args = med_db_validate.parse_args()
        assert args.med_db == "med-db"

    def test_custom_med_db(self):
        with mock.patch.object(sys, "argv", ["med-db-validate.py", "--med-db", "/tmp/test-db"]):
            args = med_db_validate.parse_args()
        assert args.med_db == "/tmp/test-db"


# ---------------------------------------------------------------------------
# validate_required_dirs
# ---------------------------------------------------------------------------

class TestValidateRequiredDirs:
    def test_all_present(self, tmp_path):
        for name in ("searches", "papers", "fulltext", "guidelines", "web"):
            (tmp_path / name).mkdir()
        issues = []
        med_db_validate.validate_required_dirs(tmp_path, issues)
        assert issues == []

    def test_missing_dirs(self, tmp_path):
        issues = []
        med_db_validate.validate_required_dirs(tmp_path, issues)
        assert len(issues) == 5
        for name in ("searches", "papers", "fulltext", "guidelines", "web"):
            assert any(name in issue for issue in issues)

    def test_partial_missing(self, tmp_path):
        (tmp_path / "searches").mkdir()
        (tmp_path / "papers").mkdir()
        issues = []
        med_db_validate.validate_required_dirs(tmp_path, issues)
        assert len(issues) == 3
        for name in ("fulltext", "guidelines", "web"):
            assert any(name in issue for issue in issues)


# ---------------------------------------------------------------------------
# validate_non_empty_files
# ---------------------------------------------------------------------------

class TestValidateNonEmptyFiles:
    def test_empty_file_detected(self, tmp_path):
        (tmp_path / "empty.txt").write_text("")
        issues = []
        med_db_validate.validate_non_empty_files(tmp_path, issues)
        assert len(issues) == 1
        assert "empty" in issues[0]

    def test_non_empty_ok(self, tmp_path):
        (tmp_path / "not-empty.txt").write_text("content")
        issues = []
        med_db_validate.validate_non_empty_files(tmp_path, issues)
        assert issues == []

    def test_mixed(self, tmp_path):
        (tmp_path / "empty.json").write_text("")
        (tmp_path / "has-content.json").write_text('{"key":"val"}')
        issues = []
        med_db_validate.validate_non_empty_files(tmp_path, issues)
        assert len(issues) == 1

    def test_nested_directories(self, tmp_path):
        subdir = tmp_path / "sub" / "deep"
        subdir.mkdir(parents=True)
        (subdir / "empty.txt").write_text("")
        issues = []
        med_db_validate.validate_non_empty_files(tmp_path, issues)
        assert len(issues) == 1
        assert "empty.txt" in issues[0]


# ---------------------------------------------------------------------------
# validate_search_json
# ---------------------------------------------------------------------------

class TestValidateSearchJson:
    def test_valid_pubmed_search(self, tmp_path):
        searches = tmp_path / "searches"
        searches.mkdir()
        data = {
            "header": {"type": "esearch"},
            "esearchresult": {
                "idlist": ["123", "456"],
                "querytranslation": "endometriosis[MeSH]",
            },
        }
        (searches / "pubmed-endo.json").write_text(json.dumps(data))
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        assert issues == []

    def test_pubmed_missing_idlist(self, tmp_path):
        searches = tmp_path / "searches"
        searches.mkdir()
        data = {
            "header": {"type": "esearch"},
            "esearchresult": {"querytranslation": "test"},
            # no idlist
        }
        (searches / "pubmed-missing.json").write_text(json.dumps(data))
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        assert any("idlist" in issue for issue in issues)

    def test_pubmed_missing_querytranslation(self, tmp_path):
        searches = tmp_path / "searches"
        searches.mkdir()
        data = {
            "header": {"type": "esearch"},
            "esearchresult": {"idlist": ["1"]},
            # no querytranslation
        }
        (searches / "pubmed-no-query.json").write_text(json.dumps(data))
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        assert any("querytranslation" in issue for issue in issues)

    def test_valid_europe_pmc_search(self, tmp_path):
        searches = tmp_path / "searches"
        searches.mkdir()
        data = {
            "request": {"queryString": "endometriosis AND diet"},
            "resultList": {"result": []},
        }
        (searches / "epmc-search.json").write_text(json.dumps(data))
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        assert issues == []

    def test_europe_pmc_missing_query_string(self, tmp_path):
        searches = tmp_path / "searches"
        searches.mkdir()
        # request dict must be truthy for the Europe PMC detection to trigger,
        # but lack the queryString key.
        data = {
            "request": {"otherKey": "value"},
            "resultList": {"result": []},
        }
        (searches / "epmc-no-query.json").write_text(json.dumps(data))
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        assert any("queryString" in issue for issue in issues)

    def test_europe_pmc_missing_result(self, tmp_path):
        searches = tmp_path / "searches"
        searches.mkdir()
        data = {
            "request": {"queryString": "test"},
            "resultList": {},
        }
        (searches / "epmc-no-result.json").write_text(json.dumps(data))
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        # resultList exists but has no "result" key
        assert any("result list" in issue.lower() for issue in issues)

    def test_europe_pmc_missing_resultlist_key(self, tmp_path):
        searches = tmp_path / "searches"
        searches.mkdir()
        data = {
            "request": {"queryString": "test"},
        }
        (searches / "epmc-no-resultlist.json").write_text(json.dumps(data))
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        # europe_pmc_request set, but no resultList key → dict.get returns None
        # Condition: request AND resultList is not None → True since None IS None
        # Wait — the code checks `europe_pmc_results is not None`.
        # data.get("resultList", {}) → {} if key missing. {} is not None → True.
        # Then checks "result" not in {}, which IS true → issue added.
        assert any("result list" in issue.lower() or "result" in issue.lower() for issue in issues)

    def test_unrecognized_search_format(self, tmp_path):
        searches = tmp_path / "searches"
        searches.mkdir()
        data = {"something": "unexpected"}
        (searches / "unknown.json").write_text(json.dumps(data))
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        assert any("unrecognized" in issue for issue in issues)

    def test_invalid_json(self, tmp_path):
        searches = tmp_path / "searches"
        searches.mkdir()
        (searches / "bad.json").write_text("not valid json {{{")
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        assert any("invalid search json" in issue for issue in issues)

    def test_missing_searches_dir_no_issues(self, tmp_path):
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        assert issues == []

    def test_skips_non_json_files(self, tmp_path):
        searches = tmp_path / "searches"
        searches.mkdir()
        (searches / "readme.txt").write_text("not json")
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        assert issues == []

    def test_multiple_mixed_searches(self, tmp_path):
        searches = tmp_path / "searches"
        searches.mkdir()
        (searches / "valid.json").write_text(json.dumps({
            "header": {"type": "esearch"},
            "esearchresult": {"idlist": ["1"], "querytranslation": "test"},
        }))
        (searches / "bad.json").write_text("invalid")
        (searches / "unknown.json").write_text(json.dumps({"x": "y"}))
        issues = []
        med_db_validate.validate_search_json(tmp_path, issues)
        assert len(issues) == 2  # bad.json + unknown.json


# ---------------------------------------------------------------------------
# validate_papers
# ---------------------------------------------------------------------------

class TestValidatePapers:
    def test_valid_pmid_paper(self, tmp_path):
        papers = tmp_path / "papers" / "endometriosis" / "pmid-12345-diet-study"
        papers.mkdir(parents=True)
        (papers / "metadata.json").write_text(json.dumps({
            "result": {"uids": ["12345"]},
        }))
        (papers / "abstract.txt").write_text("This is the abstract.")
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert issues == []

    def test_missing_abstract_txt(self, tmp_path):
        papers = tmp_path / "papers" / "endometriosis" / "pmid-12345-diet-study"
        papers.mkdir(parents=True)
        (papers / "metadata.json").write_text(json.dumps({
            "result": {"uids": ["12345"]},
        }))
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert any("missing abstract.txt" in issue for issue in issues)

    def test_pmid_mismatch(self, tmp_path):
        papers = tmp_path / "papers" / "endometriosis" / "pmid-12345-diet-study"
        papers.mkdir(parents=True)
        (papers / "metadata.json").write_text(json.dumps({
            "result": {"uids": ["99999"]},  # doesn't match folder pmid-12345
        }))
        (papers / "abstract.txt").write_text("abstract")
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert any("pmid mismatch" in issue for issue in issues)

    def test_pmid_unexpected_uid_count(self, tmp_path):
        papers = tmp_path / "papers" / "endometriosis" / "pmid-12345-diet-study"
        papers.mkdir(parents=True)
        (papers / "metadata.json").write_text(json.dumps({
            "result": {"uids": []},  # zero uids
        }))
        (papers / "abstract.txt").write_text("abstract")
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert any("unexpected uid count" in issue for issue in issues)

    def test_valid_europe_pmc_paper(self, tmp_path):
        papers = tmp_path / "papers" / "endometriosis" / "epmc-med-35350465-some-title"
        papers.mkdir(parents=True)
        (papers / "metadata.json").write_text(json.dumps({
            "resultList": {
                "result": [{"source": "MED", "id": "35350465"}],
            },
        }))
        (papers / "abstract.txt").write_text("abstract text")
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert issues == []

    def test_europe_pmc_source_mismatch(self, tmp_path):
        papers = tmp_path / "papers" / "endometriosis" / "epmc-med-35350465-some-title"
        papers.mkdir(parents=True)
        (papers / "metadata.json").write_text(json.dumps({
            "resultList": {
                "result": [{"source": "PPR", "id": "35350465"}],
            },
        }))
        (papers / "abstract.txt").write_text("abstract")
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert any("Europe PMC source mismatch" in issue for issue in issues)

    def test_europe_pmc_id_slug_mismatch(self, tmp_path):
        papers = tmp_path / "papers" / "endometriosis" / "epmc-med-35350465-some-title"
        papers.mkdir(parents=True)
        (papers / "metadata.json").write_text(json.dumps({
            "resultList": {
                "result": [{"source": "MED", "id": "99999999"}],
            },
        }))
        (papers / "abstract.txt").write_text("abstract")
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert any("Europe PMC id mismatch" in issue for issue in issues)

    def test_europe_pmc_unexpected_result_count(self, tmp_path):
        papers = tmp_path / "papers" / "endometriosis" / "epmc-med-35350465-some-title"
        papers.mkdir(parents=True)
        (papers / "metadata.json").write_text(json.dumps({
            "resultList": {
                "result": [],  # empty results
            },
        }))
        (papers / "abstract.txt").write_text("abstract")
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert any("unexpected Europe PMC result count" in issue for issue in issues)

    def test_unrecognized_folder_name(self, tmp_path):
        papers = tmp_path / "papers" / "endometriosis" / "weird-folder-name"
        papers.mkdir(parents=True)
        (papers / "metadata.json").write_text(json.dumps({"something": "else"}))
        (papers / "abstract.txt").write_text("abstract")
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert any("unrecognized paper folder name" in issue for issue in issues)

    def test_invalid_metadata_json(self, tmp_path):
        papers = tmp_path / "papers" / "endometriosis" / "pmid-12345-study"
        papers.mkdir(parents=True)
        (papers / "metadata.json").write_text("not valid {{{ json")
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert any("invalid metadata json" in issue for issue in issues)

    def test_empty_abstract_content(self, tmp_path):
        papers = tmp_path / "papers" / "endometriosis" / "pmid-12345-study"
        papers.mkdir(parents=True)
        (papers / "metadata.json").write_text(json.dumps({
            "result": {"uids": ["12345"]},
        }))
        (papers / "abstract.txt").write_text("   \n  ")
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        # The empty abstract check runs separately on all abstract.txt files
        assert any("empty abstract content" in issue for issue in issues)

    def test_missing_papers_dir_no_issues(self, tmp_path):
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert issues == []

    def test_skips_non_paper_directories(self, tmp_path):
        """Directories without metadata.json should be skipped."""
        papers = tmp_path / "papers" / "endometriosis" / "some-readme"
        papers.mkdir(parents=True)
        (papers / "readme.txt").write_text("not a paper")
        issues = []
        med_db_validate.validate_papers(tmp_path, issues)
        assert issues == []


# ---------------------------------------------------------------------------
# validate_web
# ---------------------------------------------------------------------------

class TestValidateWeb:
    def test_valid_html(self, tmp_path):
        web_dir = tmp_path / "web" / "endometriosis"
        web_dir.mkdir(parents=True)
        (web_dir / "search.html").write_text(
            "<!doctype html>\n<html lang=\"en\">\n<head></head>\n<body>test</body>\n</html>\n"
        )
        issues = []
        med_db_validate.validate_web(tmp_path, issues)
        assert issues == []

    def test_empty_web_file(self, tmp_path):
        web_dir = tmp_path / "web" / "endometriosis"
        web_dir.mkdir(parents=True)
        (web_dir / "empty.html").write_text("")
        issues = []
        med_db_validate.validate_web(tmp_path, issues)
        assert any("empty web file" in issue for issue in issues)

    def test_html_file_without_html_tag(self, tmp_path):
        web_dir = tmp_path / "web" / "endometriosis"
        web_dir.mkdir(parents=True)
        (web_dir / "not-html.html").write_text("just some text, no html tags")
        issues = []
        med_db_validate.validate_web(tmp_path, issues)
        assert any("does not look like html" in issue for issue in issues)

    def test_non_html_file_not_checked_for_html(self, tmp_path):
        """Only .html files are checked for HTML-ness."""
        web_dir = tmp_path / "web" / "endometriosis"
        web_dir.mkdir(parents=True)
        (web_dir / "readme.txt").write_text("not html, but also not checked")
        issues = []
        med_db_validate.validate_web(tmp_path, issues)
        assert issues == []

    def test_missing_web_dir_no_issues(self, tmp_path):
        issues = []
        med_db_validate.validate_web(tmp_path, issues)
        assert issues == []

    def test_html_case_insensitive_check(self, tmp_path):
        web_dir = tmp_path / "web" / "endometriosis"
        web_dir.mkdir(parents=True)
        (web_dir / "test.html").write_text(
            "<!DOCTYPE HTML>\n<HTML>\n<BODY>test</BODY>\n</HTML>\n"
        )
        issues = []
        med_db_validate.validate_web(tmp_path, issues)
        assert issues == []

    def test_whitespace_only_web_file(self, tmp_path):
        web_dir = tmp_path / "web" / "endometriosis"
        web_dir.mkdir(parents=True)
        (web_dir / "blank.html").write_text("   \n   \n  ")
        issues = []
        med_db_validate.validate_web(tmp_path, issues)
        assert any("empty web file" in issue for issue in issues)


# ---------------------------------------------------------------------------
# validate_index
# ---------------------------------------------------------------------------

class TestValidateIndex:
    def test_missing_index(self, tmp_path):
        issues = []
        med_db_validate.validate_index(tmp_path, issues)
        assert any("missing INDEX.md" in issue for issue in issues)

    def test_index_matches_filesystem(self, tmp_path):
        # Create filesystem entries
        for name in ("searches", "papers", "fulltext", "guidelines", "web"):
            (tmp_path / name).mkdir()

        searches_dir = tmp_path / "searches" / "endometriosis"
        searches_dir.mkdir(parents=True)
        (searches_dir / "pubmed-test.json").write_text("{}")

        papers_dir = tmp_path / "papers" / "endometriosis" / "pmid-12345-test"
        papers_dir.mkdir(parents=True)
        (papers_dir / "metadata.json").write_text("{}")

        ft_dir = tmp_path / "fulltext" / "endometriosis" / "pmid-12345-test"
        ft_dir.mkdir(parents=True)
        (ft_dir / "metadata.json").write_text("{}")

        gl_dir = tmp_path / "guidelines" / "endometriosis" / "eshre-guideline"
        gl_dir.mkdir(parents=True)
        (gl_dir / "source.en.md").write_text("content")

        web_dir = tmp_path / "web" / "endometriosis"
        web_dir.mkdir(parents=True)
        (web_dir / "google-scholar-test.html").write_text("<html></html>")

        # Build a matching index
        index = tmp_path / "INDEX.md"
        index.write_text("""# med-db Index

## Searches

| File | Source | Query | Purpose | Accessed |
|------|--------|-------|---------|----------|
| `searches/endometriosis/pubmed-test.json` | PubMed | test | test | 2026-01-01 |

## Papers

| Folder | Record | URL | Purpose | Accessed |
|--------|--------|-----|---------|----------|
| `papers/endometriosis/pmid-12345-test/` | PMID:12345 | url | purpose | 2026-01-01 |

## Fulltext

| Folder | Record | URL | Purpose | Accessed |
|--------|--------|-----|---------|----------|
| `fulltext/endometriosis/pmid-12345-test/` | PMID:12345 | url | purpose | 2026-01-01 |

## Guidelines

| Folder | Source | URL | Purpose | Accessed |
|--------|--------|-----|---------|----------|
| `guidelines/endometriosis/eshre-guideline/` | ESHRE | url | purpose | 2026-01-01 |

## Web Sources

| File | URL | Purpose | Accessed |
|------|-----|---------|----------|
| `web/endometriosis/google-scholar-test.html` | url | purpose | 2026-01-01 |
""")
        issues = []
        med_db_validate.validate_index(tmp_path, issues)
        assert issues == []

    def test_index_paths_tolerate_missing_backticks(self, tmp_path):
        for name in ("searches", "papers", "fulltext", "guidelines", "web"):
            (tmp_path / name).mkdir()
        searches_dir = tmp_path / "searches" / "endometriosis"
        searches_dir.mkdir(parents=True)
        (searches_dir / "pubmed-test.json").write_text("{}")
        index = tmp_path / "INDEX.md"
        index.write_text("""# med-db Index

## Searches

| File | Source | Query | Purpose | Accessed |
|------|--------|-------|---------|----------|
| searches/endometriosis/pubmed-test.json | PubMed | test | test | 2026-01-01 |

## Papers

## Fulltext

## Guidelines

## Web Sources
""")
        issues = []
        med_db_validate.validate_index(tmp_path, issues)
        assert not any("search index" in issue for issue in issues)

    def test_index_references_missing_file(self, tmp_path):
        for name in ("searches", "papers", "fulltext", "guidelines", "web"):
            (tmp_path / name).mkdir()
        index = tmp_path / "INDEX.md"
        index.write_text("""# med-db Index

## Searches

| File | Source | Query | Purpose | Accessed |
|------|--------|-------|---------|----------|
| `searches/endometriosis/nonexistent.json` | PubMed | test | test | 2026-01-01 |
""")
        issues = []
        med_db_validate.validate_index(tmp_path, issues)
        assert any("references missing file" in issue for issue in issues)

    def test_index_missing_existing_entry(self, tmp_path):
        for name in ("searches", "papers", "fulltext", "guidelines", "web"):
            (tmp_path / name).mkdir()
        searches_dir = tmp_path / "searches" / "endometriosis"
        searches_dir.mkdir(parents=True)
        (searches_dir / "pubmed-test.json").write_text("{}")
        index = tmp_path / "INDEX.md"
        index.write_text("# med-db Index\n\n## Searches\n\n"
                          "| File | Source | Query | Purpose | Accessed |\n"
                          "|------|--------|-------|---------|----------|\n")
        issues = []
        med_db_validate.validate_index(tmp_path, issues)
        assert any("is missing existing entry" in issue for issue in issues)

    def test_empty_index_sections(self, tmp_path):
        for name in ("searches", "papers", "fulltext", "guidelines", "web"):
            (tmp_path / name).mkdir()
        index = tmp_path / "INDEX.md"
        index.write_text("# med-db Index\n")
        issues = []
        med_db_validate.validate_index(tmp_path, issues)
        # No tables → nothing parsed. All actual filesystem entries are "extra".
        # Since we have no actual files in the empty dirs, issues should be empty.
        assert issues == []

    def test_checks_all_sections(self, tmp_path):
        for name in ("searches", "papers", "fulltext", "guidelines", "web"):
            (tmp_path / name).mkdir()
        # Make actual filesystem entries
        searches_dir = tmp_path / "searches" / "test"
        searches_dir.mkdir(parents=True)
        (searches_dir / "s.json").write_text("{}")
        papers_dir = tmp_path / "papers" / "test" / "pmid-1-x"
        papers_dir.mkdir(parents=True)
        (papers_dir / "metadata.json").write_text("{}")
        ft_dir = tmp_path / "fulltext" / "test" / "pmid-1-x"
        ft_dir.mkdir(parents=True)
        (ft_dir / "metadata.json").write_text("{}")
        gl_dir = tmp_path / "guidelines" / "test" / "g"
        gl_dir.mkdir(parents=True)
        (gl_dir / "source.en.md").write_text("x")
        web_dir = tmp_path / "web" / "test"
        web_dir.mkdir(parents=True)
        (web_dir / "w.html").write_text("<html></html>")

        # Empty index
        index = tmp_path / "INDEX.md"
        index.write_text("# med-db Index\n\n## Searches\n\n## Papers\n\n## Fulltext\n\n## Guidelines\n\n## Web Sources\n\n")
        issues = []
        med_db_validate.validate_index(tmp_path, issues)
        # All 5 sections should report missing existing entries
        assert len(issues) == 5
        assert all("is missing existing entry" in i for i in issues)


# ---------------------------------------------------------------------------
# validate_legacy_dirs
# ---------------------------------------------------------------------------

class TestValidateLegacyDirs:
    def test_no_legacy_dirs(self, tmp_path):
        warnings = []
        med_db_validate.validate_legacy_dirs(tmp_path, warnings)
        assert warnings == []

    def test_legacy_metadata_dir(self, tmp_path):
        (tmp_path / "metadata").mkdir()
        warnings = []
        med_db_validate.validate_legacy_dirs(tmp_path, warnings)
        assert len(warnings) == 1
        assert "metadata" in warnings[0]

    def test_legacy_abstracts_dir(self, tmp_path):
        (tmp_path / "abstracts").mkdir()
        warnings = []
        med_db_validate.validate_legacy_dirs(tmp_path, warnings)
        assert len(warnings) == 1
        assert "abstracts" in warnings[0]

    def test_both_legacy_dirs(self, tmp_path):
        (tmp_path / "metadata").mkdir()
        (tmp_path / "abstracts").mkdir()
        warnings = []
        med_db_validate.validate_legacy_dirs(tmp_path, warnings)
        assert len(warnings) == 2


# ---------------------------------------------------------------------------
# main (integration)
# ---------------------------------------------------------------------------

class TestMain:
    def test_missing_root(self, capsys):
        with mock.patch.object(sys, "argv", ["med-db-validate.py", "--med-db", "/nonexistent/path/12345"]):
            exit_code = med_db_validate.main()
        assert exit_code == 1

    def test_missing_required_dirs(self, tmp_path, capsys):
        # Empty tmp_path — no required dirs
        with mock.patch.object(sys, "argv", ["med-db-validate.py", "--med-db", str(tmp_path)]):
            exit_code = med_db_validate.main()
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "missing required directory" in captured.out

    def test_valid_minimal_structure(self, tmp_path, capsys):
        for name in ("searches", "papers", "fulltext", "guidelines", "web"):
            (tmp_path / name).mkdir()
        # Create an INDEX.md
        (tmp_path / "INDEX.md").write_text("# med-db Index\n\n## Searches\n\n## Papers\n\n## Fulltext\n\n## Guidelines\n\n## Web Sources\n")
        with mock.patch.object(sys, "argv", ["med-db-validate.py", "--med-db", str(tmp_path)]):
            exit_code = med_db_validate.main()
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "med-db validation OK" in captured.out

    def test_prints_counts(self, tmp_path, capsys):
        for name in ("searches", "papers", "fulltext", "guidelines", "web"):
            (tmp_path / name).mkdir()
        # Add some content
        searches_dir = tmp_path / "searches" / "test"
        searches_dir.mkdir(parents=True)
        (searches_dir / "s.json").write_text(json.dumps({
            "header": {"type": "esearch"},
            "esearchresult": {"idlist": ["1"], "querytranslation": "test"},
        }))
        papers_dir = tmp_path / "papers" / "test" / "pmid-1-x"
        papers_dir.mkdir(parents=True)
        (papers_dir / "metadata.json").write_text(json.dumps({"result": {"uids": ["1"]}}))
        (papers_dir / "abstract.txt").write_text("abstract")
        # INDEX.md
        index = tmp_path / "INDEX.md"
        index.write_text("""# med-db Index

## Searches

| File | Source | Query | Purpose | Accessed |
|------|--------|-------|---------|----------|
| `searches/test/s.json` | PubMed | test | test | 2026-01-01 |

## Papers

| Folder | Record | URL | Purpose | Accessed |
|--------|--------|-----|---------|----------|
| `papers/test/pmid-1-x/` | PMID:1 | url | purpose | 2026-01-01 |
""")
        with mock.patch.object(sys, "argv", ["med-db-validate.py", "--med-db", str(tmp_path)]):
            exit_code = med_db_validate.main()
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "searches: 1" in captured.out
        assert "papers: 1" in captured.out

    def test_warns_about_legacy_dirs(self, tmp_path, capsys):
        for name in ("searches", "papers", "fulltext", "guidelines", "web"):
            (tmp_path / name).mkdir()
        (tmp_path / "metadata").mkdir()
        (tmp_path / "INDEX.md").write_text("# med-db Index\n\n## Searches\n\n## Papers\n\n## Fulltext\n\n## Guidelines\n\n## Web Sources\n")
        with mock.patch.object(sys, "argv", ["med-db-validate.py", "--med-db", str(tmp_path)]):
            exit_code = med_db_validate.main()
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "legacy flat directory" in captured.out

    def test_validation_errors_abort_early(self, tmp_path, capsys):
        """When required dirs are missing, the validator should exit with code 1 without checking further."""
        with mock.patch.object(sys, "argv", ["med-db-validate.py", "--med-db", str(tmp_path)]):
            exit_code = med_db_validate.main()
        assert exit_code == 1
        captured = capsys.readouterr()
        # Only the required-dir errors should appear; no further validation
        assert "missing required directory" in captured.out
        # Should NOT see index validation errors (stops early)
        assert "missing INDEX.md" not in captured.out
