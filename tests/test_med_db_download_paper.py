import json
import sys
from pathlib import Path
from unittest import mock

import pytest

import med_db_download_paper as paper


def fake_pubmed_fetch(endpoint, params, timeout=60):
    if endpoint == "esearch.fcgi":
        return json.dumps({"esearchresult": {"idlist": ["35350465"]}})
    if endpoint == "esummary.fcgi":
        pmid = params["id"]
        return json.dumps({
            "header": {},
            "result": {
                "uids": [str(pmid)],
                str(pmid): {
                    "title": "Test Paper Title",
                    "authors": [{"name": "Author One"}, {"name": "Author Two"}],
                    "articleids": [{"idtype": "doi", "value": "10.1234/test.2020"}],
                },
            },
        })
    raise AssertionError(f"unexpected PubMed endpoint: {endpoint}")


def fake_epmc_fetch(module, params, timeout=60):
    if module.endswith("/fullTextXML"):
        return "<article><body><p>Full text paragraph.</p></body></article>"
    return json.dumps({
        "resultList": {"result": [{
            "source": "MED",
            "id": "35350465",
            "pmid": "35350465",
            "doi": "10.1234/test.2020",
            "title": "Test Paper Title",
            "authorString": "Author One, Author Two",
        }]},
    })


def fake_resolved():
    return {
        "kind": "pmid",
        "identifier": "PMID:35350465",
        "url": "https://pubmed.ncbi.nlm.nih.gov/35350465/",
        "title": "Test Paper Title",
        "authors": "Author One, Author Two",
        "source_name": "PubMed",
        "record": {"result": {"uids": ["35350465"]}},
        "pmid": "35350465",
        "doi": "10.1234/test.2020",
    }


def fake_epmc_resolved():
    return {
        "kind": "epmc-record",
        "identifier": "MED:35350465",
        "url": "https://europepmc.org/article/MED/35350465",
        "title": "Test Paper Title",
        "authors": "Author One",
        "source_name": "Europe PMC",
        "record": {"resultList": {"result": [{"source": "MED", "id": "35350465"}]}},
        "epmc_record": "MED:35350465",
        "doi": "10.1234/test.2020",
    }


def fake_download_binary(url, destination, timeout=60):
    Path(destination).write_bytes(b"%PDF-1.4 fake content")
    return True


def raise_runtime_error(*args, **kwargs):
    raise RuntimeError("not open access")


# ---------------------------------------------------------------------------
# Reference detection
# ---------------------------------------------------------------------------

class TestDetectReferenceType:
    def test_doi(self):
        assert paper.detect_reference_type("10.1038/s41586-020-2649-2") == (
            "doi", "10.1038/s41586-020-2649-2")

    def test_doi_with_prefix(self):
        assert paper.detect_reference_type("doi:10.1038/s41586-020-2649-2") == (
            "doi", "10.1038/s41586-020-2649-2")

    def test_pmid(self):
        assert paper.detect_reference_type("35350465") == ("pmid", "35350465")

    def test_arxiv(self):
        assert paper.detect_reference_type("2203.15556") == ("arxiv", "2203.15556")

    def test_arxiv_prefixed_versioned(self):
        assert paper.detect_reference_type("arXiv:2203.15556v2") == ("arxiv", "2203.15556v2")

    def test_epmc_record(self):
        assert paper.detect_reference_type("MED:35350465") == ("epmc-record", "MED:35350465")

    def test_title_fallback(self):
        assert paper.detect_reference_type("Attention deficit hyperactivity disorder adults") == (
            "title", "Attention deficit hyperactivity disorder adults")

    def test_url_passthrough(self):
        assert paper.detect_reference_type("https://pubmed.ncbi.nlm.nih.gov/35350465/") == (
            "pmid", "35350465")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            paper.detect_reference_type("   ")


class TestClassifyUrl:
    def test_doi_org(self):
        assert paper.classify_url("https://doi.org/10.1038/s41586-020-2649-2") == (
            "doi", "10.1038/s41586-020-2649-2")

    def test_arxiv_abs(self):
        assert paper.classify_url("https://arxiv.org/abs/2203.15556v2") == (
            "arxiv", "2203.15556v2")

    def test_arxiv_pdf(self):
        assert paper.classify_url("https://arxiv.org/pdf/2203.15556") == (
            "arxiv", "2203.15556")

    def test_europepmc(self):
        assert paper.classify_url("https://europepmc.org/article/MED/35350465") == (
            "epmc-record", "MED:35350465")

    def test_pubmed(self):
        assert paper.classify_url("https://pubmed.ncbi.nlm.nih.gov/35350465/") == (
            "pmid", "35350465")

    def test_pmc(self):
        assert paper.classify_url("https://pmc.ncbi.nlm.nih.gov/articles/PMC9000000/") == (
            "pmcid", "PMC9000000")

    def test_pdf_url(self):
        assert paper.classify_url("https://example.org/paper.pdf") == (
            "pdf-url", "https://example.org/paper.pdf")

    def test_generic_url(self):
        assert paper.classify_url("https://example.org/article") == (
            "url", "https://example.org/article")


# ---------------------------------------------------------------------------
# Metadata resolution (injected fetch functions)
# ---------------------------------------------------------------------------

class TestResolveMetadata:
    def test_pmid(self):
        resolved = paper.resolve_metadata("pmid", "35350465", pubmed_fetch_func=fake_pubmed_fetch)
        assert resolved["identifier"] == "PMID:35350465"
        assert resolved["title"] == "Test Paper Title"
        assert resolved["authors"] == "Author One, Author Two"
        assert resolved["doi"] == "10.1234/test.2020"

    def test_epmc_record(self):
        resolved = paper.resolve_metadata("epmc-record", "MED:35350465", epmc_fetch_func=fake_epmc_fetch)
        assert resolved["identifier"] == "MED:35350465"
        assert resolved["epmc_record"] == "MED:35350465"

    def test_doi_resolves_via_pubmed(self):
        resolved = paper.resolve_metadata(
            "doi", "10.1234/test.2020",
            pubmed_fetch_func=fake_pubmed_fetch, epmc_fetch_func=fake_epmc_fetch,
        )
        assert resolved["identifier"] == "PMID:35350465"
        assert resolved["title"] == "Test Paper Title"

    def test_title_resolves_via_pubmed(self):
        resolved = paper.resolve_metadata(
            "title", "Test Paper Title", year=2020,
            pubmed_fetch_func=fake_pubmed_fetch, epmc_fetch_func=fake_epmc_fetch,
        )
        assert resolved["identifier"] == "PMID:35350465"

    def test_unresolvable_title_raises(self):
        def empty_pubmed(endpoint, params, timeout=60):
            return json.dumps({"esearchresult": {"idlist": []}})

        def empty_epmc(module, params, timeout=60):
            return json.dumps({"resultList": {"result": []}})

        def empty_web(url, label, timeout=60, retries=2, retry_delay=0.25):
            if "arxiv" in url:
                return "<feed></feed>"
            return json.dumps({"message": {"items": []}})

        with pytest.raises(RuntimeError, match="could not resolve title"):
            paper.resolve_metadata(
                "title", "No Such Paper Ever",
                pubmed_fetch_func=empty_pubmed, epmc_fetch_func=empty_epmc,
                fetch_url_func=empty_web,
            )

    def test_invalid_epmc_record_raises(self):
        with pytest.raises(ValueError):
            paper.resolve_metadata("epmc-record", "no-colon-here", epmc_fetch_func=fake_epmc_fetch)


# ---------------------------------------------------------------------------
# Full-text XML conversion
# ---------------------------------------------------------------------------

class TestFulltextXmlToText:
    def test_paragraphs_preserved_and_references_dropped(self):
        xml_string = (
            "<article><body><p>First paragraph.</p><p>Second paragraph.</p>"
            "<ref-list><title>References</title></ref-list></body></article>"
        )
        text = paper.fulltext_xml_to_text(xml_string)
        assert "First paragraph." in text
        assert "Second paragraph." in text
        assert "References" not in text
        assert "\n" in text


# ---------------------------------------------------------------------------
# Source lookups (injected fetch functions)
# ---------------------------------------------------------------------------

class TestScihubHtmlParsing:
    def test_protocol_relative_embed_src(self):
        page = '<html><embed type="application/pdf" src="//mirror.example/downloads/1234/paper.pdf"></html>'
        url = paper.fetch_scihub_pdf_url(
            "10.1/x", "https://sci-hub.se", fetch_url_func=lambda url, label, **kw: page)
        assert url == "https://mirror.example/downloads/1234/paper.pdf"

    def test_absolute_link(self):
        page = '<a href="https://download.example/x/paper.pdf">x</a>'
        url = paper.fetch_scihub_pdf_url(
            "10.1/x", "https://sci-hub.se", fetch_url_func=lambda url, label, **kw: page)
        assert url == "https://download.example/x/paper.pdf"

    def test_http_upgraded_to_https(self):
        page = '<embed src="http://mirror.example/x/paper.pdf">'
        url = paper.fetch_scihub_pdf_url(
            "10.1/x", "https://sci-hub.se", fetch_url_func=lambda url, label, **kw: page)
        assert url == "https://mirror.example/x/paper.pdf"

    def test_captcha_returns_none(self):
        page = "<html>Please verify you are not a robot: Captcha</html>"
        assert paper.fetch_scihub_pdf_url(
            "10.1/x", "https://sci-hub.se", fetch_url_func=lambda url, label, **kw: page) is None

    def test_no_pdf_link_returns_none(self):
        page = "<html><body>no links here</body></html>"
        assert paper.fetch_scihub_pdf_url(
            "10.1/x", "https://sci-hub.se", fetch_url_func=lambda url, label, **kw: page) is None


# ---------------------------------------------------------------------------
# Source chain order (download_paper with monkeypatched network)
# ---------------------------------------------------------------------------

class TestSourceChainOrder:
    def _fail_all_legal(self, monkeypatch):
        monkeypatch.setattr(paper, "resolve_metadata", lambda *a, **k: fake_resolved())
        monkeypatch.setattr(paper, "fetch_fulltext_xml", raise_runtime_error)
        monkeypatch.setattr(paper, "fetch_openalex_oa", lambda doi, fetch_url_func=None: (None, None))
        monkeypatch.setattr(paper, "fetch_unpaywall_pdf_url", lambda doi, email=None, fetch_url_func=None: None)
        monkeypatch.setattr(paper, "fetch_publisher_pdf", raise_runtime_error)
        monkeypatch.setattr(paper, "download_binary", lambda url, destination, timeout=60: False)

    def test_oa_paper_uses_legal_source_and_never_touches_sci_hub(self, tmp_path, monkeypatch):
        monkeypatch.setattr(paper, "resolve_metadata", lambda *a, **k: fake_resolved())
        monkeypatch.setattr(paper, "fetch_fulltext_xml", raise_runtime_error)
        monkeypatch.setattr(paper, "fetch_openalex_oa", lambda doi, fetch_url_func=None: (True, "https://example.org/paper.pdf"))
        monkeypatch.setattr(paper, "download_binary", fake_download_binary)
        monkeypatch.setattr(paper, "extract_pdf_text", lambda pdf_path: "Extracted text.")
        sci_hub_calls = []
        monkeypatch.setattr(paper, "fetch_scihub_pdf_url", lambda *a, **k: sci_hub_calls.append(1))

        result = paper.download_paper("pmid", "35350465", topic="test", med_db=tmp_path / "med-db")

        assert result["status"] == "downloaded"
        assert result["pdf_source"] == "openalex"
        assert sci_hub_calls == []
        sources = [step["source"] for step in result["source_chain"]]
        assert "sci-hub" not in sources
        meta = json.loads((tmp_path / "med-db" / "fulltext" / "test" / "pmid-35350465-test-paper-title" / "metadata.json").read_text())
        assert meta["provenance"]["sci_hub_used"] is False

    def test_all_legal_fail_without_sci_hub_raises_and_leaves_nothing(self, tmp_path, monkeypatch):
        self._fail_all_legal(monkeypatch)
        med_db_path = tmp_path / "med-db"
        with pytest.raises(RuntimeError, match="could not obtain full text"):
            paper.download_paper("pmid", "35350465", topic="test", med_db=med_db_path, allow_sci_hub=False)
        assert not (med_db_path / "fulltext" / "test" / "pmid-35350465-test-paper-title").exists()

    def test_all_legal_fail_uses_sci_hub_and_records_it(self, tmp_path, monkeypatch):
        self._fail_all_legal(monkeypatch)
        monkeypatch.setattr(paper, "fetch_scihub_pdf_url", lambda value, mirror, fetch_url_func=None: "https://sci-hub.se/downloads/x/paper.pdf")
        monkeypatch.setattr(paper, "download_binary", fake_download_binary)
        monkeypatch.setattr(paper, "extract_pdf_text", lambda pdf_path: "Extracted text.")

        result = paper.download_paper("pmid", "35350465", topic="test", med_db=tmp_path / "med-db")

        assert result["pdf_source"] == "sci-hub"
        folder = tmp_path / "med-db" / "fulltext" / "test" / "pmid-35350465-test-paper-title"
        meta = json.loads((folder / "metadata.json").read_text())
        assert meta["provenance"]["sci_hub_used"] is True
        assert meta["provenance"]["pdf_source"] == "sci-hub"
        assert "Sci-Hub fallback used" in (folder / "source.md").read_text()

    def test_paywalled_goes_to_sci_hub_before_legal_sources(self, tmp_path, monkeypatch):
        calls = []
        monkeypatch.setattr(paper, "resolve_metadata", lambda *a, **k: fake_resolved())
        monkeypatch.setattr(paper, "fetch_fulltext_xml", raise_runtime_error)
        monkeypatch.setattr(paper, "fetch_openalex_oa", lambda doi, fetch_url_func=None: (False, None))
        monkeypatch.setattr(paper, "fetch_unpaywall_pdf_url", lambda doi, email=None, fetch_url_func=None: calls.append("unpaywall"))

        def record_scihub(value, mirror, fetch_url_func=None):
            calls.append("sci-hub")
            return "https://sci-hub.se/downloads/x/paper.pdf"

        def record_publisher(doi, timeout=60):
            calls.append("publisher")
            raise RuntimeError("paywalled")

        monkeypatch.setattr(paper, "fetch_scihub_pdf_url", record_scihub)
        monkeypatch.setattr(paper, "fetch_publisher_pdf", record_publisher)
        monkeypatch.setattr(paper, "download_binary", fake_download_binary)
        monkeypatch.setattr(paper, "extract_pdf_text", lambda pdf_path: "Extracted text.")

        result = paper.download_paper("pmid", "35350465", topic="test", med_db=tmp_path / "med-db")

        assert result["pdf_source"] == "sci-hub"
        assert calls == ["sci-hub"]
        meta = json.loads((tmp_path / "med-db" / "fulltext" / "test" / "pmid-35350465-test-paper-title" / "metadata.json").read_text())
        assert meta["provenance"]["sci_hub_used"] is True

    def test_paywalled_sci_hub_fail_falls_back_to_publisher(self, tmp_path, monkeypatch):
        calls = []
        monkeypatch.setattr(paper, "resolve_metadata", lambda *a, **k: fake_resolved())
        monkeypatch.setattr(paper, "fetch_fulltext_xml", raise_runtime_error)
        monkeypatch.setattr(paper, "fetch_openalex_oa", lambda doi, fetch_url_func=None: (False, None))

        def record_scihub(value, mirror, fetch_url_func=None):
            calls.append("sci-hub")
            return None

        def record_publisher(doi, timeout=60):
            calls.append("publisher")
            return b"%PDF-1.4 publisher content"

        monkeypatch.setattr(paper, "fetch_scihub_pdf_url", record_scihub)
        monkeypatch.setattr(paper, "fetch_publisher_pdf", record_publisher)
        monkeypatch.setattr(paper, "extract_pdf_text", lambda pdf_path: "Extracted text.")

        result = paper.download_paper(
            "pmid", "35350465", topic="test", med_db=tmp_path / "med-db",
            sci_hub_mirrors=["https://sci-hub.se"],
        )

        assert result["pdf_source"] == "publisher-open-access"
        assert calls == ["sci-hub", "publisher"]

    def test_legal_text_obtained_skips_sci_hub(self, tmp_path, monkeypatch):
        monkeypatch.setattr(paper, "resolve_metadata", lambda *a, **k: fake_epmc_resolved())
        monkeypatch.setattr(paper, "fetch_fulltext_xml", lambda epmc_record, fetch_func=None: "<article><body><p>Text.</p></body></article>")
        monkeypatch.setattr(paper, "fetch_unpaywall_pdf_url", lambda doi, email=None, fetch_url_func=None: None)
        monkeypatch.setattr(paper, "fetch_publisher_pdf", raise_runtime_error)
        sci_hub_calls = []
        monkeypatch.setattr(paper, "fetch_scihub_pdf_url", lambda *a, **k: sci_hub_calls.append(1))

        result = paper.download_paper("epmc-record", "MED:35350465", topic="test", med_db=tmp_path / "med-db")

        assert result["pdf"] is False
        assert result["pdf_source"] is None
        assert sci_hub_calls == []
        folder = tmp_path / "med-db" / "fulltext" / "test" / "epmc-med-35350465-test-paper-title"
        assert (folder / "source.md").is_file()
        assert not (folder / "paper.pdf").exists()
        meta = json.loads((folder / "metadata.json").read_text())
        assert meta["provenance"]["extraction_method"] == "europe-pmc-fulltext-xml"

    def test_pubmed_record_gets_epmc_fulltext_attempt(self, tmp_path, monkeypatch):
        monkeypatch.setattr(paper, "resolve_metadata", lambda *a, **k: fake_resolved())
        epmc_calls = []

        def fake_fulltext_xml(epmc_record, fetch_func=None):
            epmc_calls.append(epmc_record)
            return "<article><body><p>Open access text.</p></body></article>"

        monkeypatch.setattr(paper, "fetch_fulltext_xml", fake_fulltext_xml)
        monkeypatch.setattr(paper, "fetch_unpaywall_pdf_url", lambda doi, email=None, fetch_url_func=None: None)
        monkeypatch.setattr(paper, "fetch_publisher_pdf", raise_runtime_error)
        monkeypatch.setattr(paper, "download_binary", lambda url, destination, timeout=60: False)
        sci_hub_calls = []
        monkeypatch.setattr(paper, "fetch_scihub_pdf_url", lambda *a, **k: sci_hub_calls.append(1))

        result = paper.download_paper("pmid", "35350465", topic="test", med_db=tmp_path / "med-db")

        assert epmc_calls == ["MED:35350465"]
        assert result["pdf"] is False
        assert result["pdf_source"] is None
        assert sci_hub_calls == []
        folder = tmp_path / "med-db" / "fulltext" / "test" / "pmid-35350465-test-paper-title"
        meta = json.loads((folder / "metadata.json").read_text())
        assert meta["provenance"]["extraction_method"] == "europe-pmc-fulltext-xml"


# ---------------------------------------------------------------------------
# End-to-end via main()
# ---------------------------------------------------------------------------

class TestFulltextLayout:
    def _run_main(self, med_db_path, monkeypatch, *arguments):
        monkeypatch.setattr(paper, "resolve_metadata", lambda *a, **k: fake_resolved())
        monkeypatch.setattr(paper, "fetch_fulltext_xml", raise_runtime_error)
        monkeypatch.setattr(paper, "fetch_openalex_oa", lambda doi, fetch_url_func=None: (True, "https://example.org/paper.pdf"))
        monkeypatch.setattr(paper, "download_binary", fake_download_binary)
        monkeypatch.setattr(paper, "extract_pdf_text", lambda pdf_path: "Extracted full text.")
        with mock.patch.object(sys, "argv", ["med-db-download-paper.py", *arguments]):
            return paper.main()

    def test_end_to_end_layout(self, tmp_path, monkeypatch):
        med_db_path = tmp_path / "med-db"
        exit_code = self._run_main(
            med_db_path, monkeypatch,
            "--reference", "35350465", "--topic", "Test Topic", "--med-db", str(med_db_path),
        )
        assert exit_code == 0
        folder = med_db_path / "fulltext" / "test-topic" / "pmid-35350465-test-paper-title"
        assert (folder / "paper.pdf").is_file()
        source_md = (folder / "source.md").read_text()
        for key in ("title:", "authors:", "source:", "source_url:", "access_date:", "language:", "extraction_notes:"):
            assert key in source_md
        assert "Extracted full text." in source_md
        meta = json.loads((folder / "metadata.json").read_text())
        assert meta["provenance"]["pdf_source"] == "openalex"
        index = json.loads((med_db_path / "index.json").read_text())
        fulltext_entries = {entry["path"]: entry for entry in index["fulltext"]}
        assert "fulltext/test-topic/pmid-35350465-test-paper-title" in fulltext_entries
        assert fulltext_entries["fulltext/test-topic/pmid-35350465-test-paper-title"]["identifier"] == "PMID:35350465"

    def test_second_run_skips(self, tmp_path, monkeypatch, capsys):
        med_db_path = tmp_path / "med-db"
        arguments = ["--reference", "35350465", "--topic", "Test Topic", "--med-db", str(med_db_path)]
        assert self._run_main(med_db_path, monkeypatch, *arguments) == 0
        assert "skipped" not in capsys.readouterr().out
        assert self._run_main(med_db_path, monkeypatch, *arguments) == 0
        assert "skipped (already archived)" in capsys.readouterr().out

    def test_pdf_extraction_failure_falls_back(self, tmp_path, monkeypatch):
        monkeypatch.setattr(paper, "resolve_metadata", lambda *a, **k: fake_resolved())
        monkeypatch.setattr(paper, "fetch_fulltext_xml", raise_runtime_error)
        monkeypatch.setattr(paper, "fetch_openalex_oa", lambda doi, fetch_url_func=None: (True, "https://example.org/paper.pdf"))
        monkeypatch.setattr(paper, "download_binary", fake_download_binary)
        monkeypatch.setattr(paper, "extract_pdf_text", lambda pdf_path: (_ for _ in ()).throw(ValueError("no text")))

        result = paper.download_paper("pmid", "35350465", topic="test", med_db=tmp_path / "med-db")

        assert result["status"] == "downloaded"
        source_md = (tmp_path / "med-db" / "fulltext" / "test" / "pmid-35350465-test-paper-title" / "source.md").read_text()
        assert "Text extraction from PDF failed; see paper.pdf." in source_md


# ---------------------------------------------------------------------------
# CLI validation
# ---------------------------------------------------------------------------

class TestCLIValidation:
    def test_no_inputs(self):
        with mock.patch.object(sys, "argv", ["med-db-download-paper.py", "--topic", "test"]):
            with pytest.raises(SystemExit):
                paper.main()

    def test_topic_required(self):
        with mock.patch.object(sys, "argv", ["med-db-download-paper.py", "--reference", "10.1/x"]):
            with pytest.raises(SystemExit):
                paper.main()

    def test_year_requires_title(self):
        with mock.patch.object(sys, "argv", [
            "med-db-download-paper.py", "--reference", "10.1/x", "--year", "2020", "--topic", "test",
        ]):
            with pytest.raises(SystemExit):
                paper.main()


# ---------------------------------------------------------------------------
# Real pypdf extraction
# ---------------------------------------------------------------------------

class TestPdfExtraction:
    def test_blank_pdf_raises(self, tmp_path):
        from pypdf import PdfWriter

        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        pdf_path = tmp_path / "blank.pdf"
        with open(pdf_path, "wb") as handle:
            writer.write(handle)
        with pytest.raises(ValueError, match="no text"):
            paper.extract_pdf_text(pdf_path)


# ---------------------------------------------------------------------------
# Real download_binary streaming
# ---------------------------------------------------------------------------

class FakeUrlopenResponse:
    def __init__(self, chunks):
        self.chunks = list(chunks)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self, size=None):
        if not self.chunks:
            return b""
        return self.chunks.pop(0)


class TestDownloadBinary:
    def test_multi_chunk_pdf_written_completely(self, tmp_path):
        chunks = [
            b"%PDF-1.7\nheader bytes\n",
            b"middle chunk bytes\n",
            b"trailing xref and trailer\n",
        ]
        destination = tmp_path / "paper.pdf"
        with mock.patch("urllib.request.urlopen", return_value=FakeUrlopenResponse(chunks)):
            assert paper.download_binary("https://example.org/paper.pdf", destination) is True
        assert destination.read_bytes() == b"".join(chunks)

    def test_non_pdf_first_chunk_rejected(self, tmp_path):
        destination = tmp_path / "paper.pdf"
        with mock.patch("urllib.request.urlopen", return_value=FakeUrlopenResponse([b"<html>not a pdf</html>"])):
            assert paper.download_binary("https://example.org/paper.pdf", destination) is False
        assert not destination.exists()
