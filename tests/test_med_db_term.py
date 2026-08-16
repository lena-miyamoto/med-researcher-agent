"""Tests for med-db-term.py and med-db-term-lookup.py — dictionary category."""

import json
import sys

import med_db_term as term
import med_db_term_lookup as lookup


# ---------------------------------------------------------------------------
# source_type_label / resolve_source_url
# ---------------------------------------------------------------------------


class TestSourceTypeLabel:
    def test_known_label(self):
        assert term.source_type_label("icd11") == "ICD-11"

    def test_unknown_falls_back(self):
        assert term.source_type_label("bogus") == "bogus"


class TestResolveSourceUrl:
    def test_prefers_explicit_url(self):
        assert term.resolve_source_url("https://ref.example", "https://url.example") == "https://url.example"

    def test_falls_back_to_url_ref(self):
        assert term.resolve_source_url("https://ref.example", "") == "https://ref.example"

    def test_falls_back_to_doi(self):
        assert term.resolve_source_url("doi:10.1000/xyz", "") == "doi:10.1000/xyz"

    def test_non_url_ref_returns_empty(self):
        assert term.resolve_source_url("F90.2", "") == ""


# ---------------------------------------------------------------------------
# build_source_md / build_metadata
# ---------------------------------------------------------------------------


class TestBuildSourceMd:
    def test_frontmatter_and_body(self):
        md = term.build_source_md(
            "Hypertonie", "hypertension", "Chronisch erhöhter Blutdruck.",
            "who", "https://example.org/x", "https://example.org/x", "2026-08-16",
            "non-authoritative community usage",
        )
        assert md.startswith("---\n")
        assert "title: Hypertonie" in md
        assert "english: hypertension" in md
        assert "source_type: who" in md
        assert "language: de" in md
        assert "extraction_notes: non-authoritative community usage" in md
        assert "Chronisch erhöhter Blutdruck." in md


class TestBuildMetadata:
    def test_fields(self):
        meta = term.build_metadata(
            "Hypertonie", "hypertension", "Definition", "who", "https://example.org/x",
            "https://example.org/x", "2026-08-16", "non-authoritative community usage",
        )
        assert meta["term"] == "Hypertonie"
        assert meta["english"] == "hypertension"
        assert meta["definition"] == "Definition"
        assert meta["source_type"] == "who"
        assert meta["extraction_notes"] == "non-authoritative community usage"
        assert "path" not in meta


# ---------------------------------------------------------------------------
# archive_term
# ---------------------------------------------------------------------------


class TestArchiveTerm:
    def test_writes_files_and_slugifies(self, tmp_path):
        med_db = tmp_path / "med-db"
        term_dir = term.archive_term(
            med_db, "Hypertonie", "hypertension", "Chronisch erhöhter Blutdruck.",
            "who", "https://example.org/x", "https://example.org/x", "2026-08-16", "",
        )
        assert term_dir == med_db / "dictionary" / "hypertonie"
        source = term_dir / "source.md"
        meta = term_dir / "metadata.json"
        assert source.is_file()
        assert meta.is_file()

        source_text = source.read_text(encoding="utf-8")
        assert source_text.startswith("---\n")
        assert "title: Hypertonie" in source_text
        assert "Chronisch erhöhter Blutdruck." in source_text

        data = json.loads(meta.read_text(encoding="utf-8"))
        assert data["term"] == "Hypertonie"
        assert data["english"] == "hypertension"
        assert data["definition"] == "Chronisch erhöhter Blutdruck."

    def test_idempotent_rearchive(self, tmp_path):
        med_db = tmp_path / "med-db"
        args = ("Hypertonie", "hypertension", "Definition", "who", "", "", "2026-08-16", "")
        first = term.archive_term(med_db, *args)
        second = term.archive_term(med_db, *args)
        assert first == second
        assert (second / "source.md").is_file()
        assert (second / "metadata.json").is_file()

    def test_writes_extraction_notes(self, tmp_path):
        med_db = tmp_path / "med-db"
        term_dir = term.archive_term(
            med_db, "Mental Load", "mental load", "Definition.",
            "web", "https://example.org/x", "https://example.org/x", "2026-08-16",
            "non-authoritative community usage",
        )
        source_text = (term_dir / "source.md").read_text(encoding="utf-8")
        assert "extraction_notes: non-authoritative community usage" in source_text


# ---------------------------------------------------------------------------
# load_entries / search_by_term / search_by_keyword
# ---------------------------------------------------------------------------


def _archive(tmp_path, term_name="Hypertonie", english="hypertension",
             definition="Chronisch erhöhter Blutdruck.", source_ref="https://example.org/x"):
    med_db = tmp_path / "med-db"
    term.archive_term(
        med_db, term_name, english, definition, "who", source_ref,
        source_ref, "2026-08-16", "",
    )
    return med_db


class TestLoadEntries:
    def test_empty_when_no_dir(self, tmp_path):
        assert lookup.load_entries(tmp_path / "med-db") == []

    def test_loads_archived_entries(self, tmp_path):
        med_db = _archive(tmp_path)
        entries = lookup.load_entries(med_db)
        assert len(entries) == 1
        assert entries[0]["term"] == "Hypertonie"
        assert entries[0]["path"] == "dictionary/hypertonie"


class TestSearchByTerm:
    def test_exact_match(self, tmp_path):
        entries = lookup.load_entries(_archive(tmp_path))
        result = lookup.search_by_term(entries, "Hypertonie")
        assert len(result) == 1
        assert result[0]["english"] == "hypertension"

    def test_case_insensitive(self, tmp_path):
        entries = lookup.load_entries(_archive(tmp_path))
        assert len(lookup.search_by_term(entries, "hypertonie")) == 1

    def test_not_found(self, tmp_path):
        entries = lookup.load_entries(_archive(tmp_path))
        assert lookup.search_by_term(entries, "Diabetes") == []


class TestSearchByKeyword:
    def test_match_in_definition(self, tmp_path):
        entries = lookup.load_entries(_archive(tmp_path))
        results = lookup.search_by_keyword(entries, "Blutdruck")
        assert len(results) == 1

    def test_match_in_source_ref(self, tmp_path):
        entries = lookup.load_entries(_archive(tmp_path))
        results = lookup.search_by_keyword(entries, "example.org")
        assert len(results) == 1

    def test_no_match(self, tmp_path):
        entries = lookup.load_entries(_archive(tmp_path))
        assert lookup.search_by_keyword(entries, "zzz") == []


# ---------------------------------------------------------------------------
# main() — archive (end-to-end via sys.argv)
# ---------------------------------------------------------------------------


class TestMainArchive:
    def test_archives_and_passes_integrity(self, tmp_path, monkeypatch, capsys):
        med_db = tmp_path / "med-db"
        monkeypatch.setattr(sys, "argv", [
            "med-db-term",
            "--term", "Hypertonie",
            "--english", "hypertension",
            "--definition", "Chronisch erhöhter Blutdruck.",
            "--source-type", "who",
            "--source-ref", "https://example.org/hypertonie",
            "--med-db", str(med_db),
            "--format", "json",
        ])
        code = term.main()
        assert code == 0
        assert (med_db / "dictionary" / "hypertonie" / "metadata.json").is_file()
        index = json.loads((med_db / "index.json").read_text(encoding="utf-8"))
        assert len(index["dictionary"]) == 1

    def test_rearchive_is_idempotent(self, tmp_path, monkeypatch):
        med_db = tmp_path / "med-db"
        argv = [
            "med-db-term",
            "--term", "Hypertonie",
            "--definition", "Definition",
            "--source-type", "other",
            "--med-db", str(med_db),
        ]
        monkeypatch.setattr(sys, "argv", argv)
        assert term.main() == 0
        monkeypatch.setattr(sys, "argv", argv)
        assert term.main() == 0
        index = json.loads((med_db / "index.json").read_text(encoding="utf-8"))
        assert len(index["dictionary"]) == 1

    def test_extraction_notes_flag(self, tmp_path, monkeypatch):
        med_db = tmp_path / "med-db"
        monkeypatch.setattr(sys, "argv", [
            "med-db-term",
            "--term", "Mental Load",
            "--definition", "Definition.",
            "--source-type", "web",
            "--extraction-notes", "non-authoritative community usage",
            "--med-db", str(med_db),
        ])
        assert term.main() == 0
        source_text = (med_db / "dictionary" / "mental-load" / "source.md").read_text(encoding="utf-8")
        assert "extraction_notes: non-authoritative community usage" in source_text


# ---------------------------------------------------------------------------
# main() — lookup (end-to-end via sys.argv)
# ---------------------------------------------------------------------------


class TestMainLookup:
    def test_term_json(self, tmp_path, monkeypatch, capsys):
        med_db = _archive(tmp_path)
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-lookup", "--term", "Hypertonie",
            "--med-db", str(med_db), "--format", "json",
        ])
        assert lookup.main() == 0
        data = json.loads(capsys.readouterr().out)
        assert data["term"] == "Hypertonie"
        assert data["english"] == "hypertension"

    def test_definition_only(self, tmp_path, monkeypatch, capsys):
        med_db = _archive(tmp_path)
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-lookup", "--term", "Hypertonie",
            "--definition-only", "--med-db", str(med_db),
        ])
        assert lookup.main() == 0
        assert capsys.readouterr().out.strip() == "Chronisch erhöhter Blutdruck."

    def test_english_only(self, tmp_path, monkeypatch, capsys):
        med_db = _archive(tmp_path)
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-lookup", "--term", "Hypertonie",
            "--english-only", "--med-db", str(med_db),
        ])
        assert lookup.main() == 0
        assert capsys.readouterr().out.strip() == "hypertension"

    def test_term_not_found_returns_one(self, tmp_path, monkeypatch, capsys):
        med_db = _archive(tmp_path)
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-lookup", "--term", "Diabetes",
            "--med-db", str(med_db),
        ])
        assert lookup.main() == 1
        assert "not found" in capsys.readouterr().out

    def test_keyword(self, tmp_path, monkeypatch, capsys):
        med_db = _archive(tmp_path)
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-lookup", "--keyword", "Blutdruck",
            "--med-db", str(med_db), "--format", "json",
        ])
        assert lookup.main() == 0
        data = json.loads(capsys.readouterr().out)
        assert data["count"] == 1
        assert data["results"][0]["term"] == "Hypertonie"

    def test_list(self, tmp_path, monkeypatch, capsys):
        med_db = _archive(tmp_path)
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-lookup", "--list",
            "--med-db", str(med_db), "--format", "json",
        ])
        assert lookup.main() == 0
        data = json.loads(capsys.readouterr().out)
        assert data["count"] == 1

    def test_term_json_includes_extraction_notes(self, tmp_path, monkeypatch, capsys):
        med_db = tmp_path / "med-db"
        term.archive_term(
            med_db, "Mental Load", "mental load", "Definition.",
            "web", "https://example.org/x", "https://example.org/x", "2026-08-16",
            "non-authoritative community usage",
        )
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-lookup", "--term", "Mental Load",
            "--med-db", str(med_db), "--format", "json",
        ])
        assert lookup.main() == 0
        data = json.loads(capsys.readouterr().out)
        assert data["extraction_notes"] == "non-authoritative community usage"

    def test_term_text_includes_extraction_notes(self, tmp_path, monkeypatch, capsys):
        med_db = tmp_path / "med-db"
        term.archive_term(
            med_db, "Mental Load", "mental load", "Definition.",
            "web", "https://example.org/x", "https://example.org/x", "2026-08-16",
            "non-authoritative community usage",
        )
        monkeypatch.setattr(sys, "argv", [
            "med-db-term-lookup", "--term", "Mental Load",
            "--med-db", str(med_db), "--format", "text",
        ])
        assert lookup.main() == 0
        assert "Notes:       non-authoritative community usage" in capsys.readouterr().out
