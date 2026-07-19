"""Tests for med-db-lookup-icd11.py — ICD-11 MMS lookup functions."""

import sys
from pathlib import Path

import pytest

import med_db_lookup_icd11 as icd11


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_tabulation_file(base_dir, release="2026-01", language="en", rows=None):
    """Create a minimal ICD-11 SimpleTabulation TSV at base_dir/<release>/extracted/<lang>/."""
    extracted = base_dir / release / "extracted" / language
    extracted.mkdir(parents=True)
    path = extracted / f"SimpleTabulation-ICD-11-MMS-{language}.txt"

    if rows is None:
        rows = [
            [
                "Foundation URI", "Linearization URI", "Code", "BlockId",
                "Title", "ClassKind", "DepthInKind", "IsResidual",
                "ChapterNo", "BrowserLink", "isLeaf", "Primary tabulation",
                "Grouping1", "Grouping2", "Grouping3", "Grouping4",
                "Grouping5", "CodingNote", "Parent",
            ],
            [
                "http://id.who.int/icd/entity/123",
                "http://id.who.int/icd/entity/123",  # same as foundation_uri so both ancestor/child lookups work
                "6A02", "Block_6A02",
                "Autism spectrum disorder", "category", "4", "False",
                "06",
                "https://icd.who.int/browse/2026-01/mms/en#123",
                "True", "1", "Neurodevelopmental disorders",
                "Mental, behavioural or neurodevelopmental disorders",
                "", "", "", "",
                "http://id.who.int/icd/entity/456",
            ],
            [
                "http://id.who.int/icd/entity/789",
                "http://id.who.int/icd/release/11/2026-01/mms/789",
                "6A02.0", "Block_6A02_0",
                "Autism spectrum disorder without disorder of intellectual development",
                "category", "5", "False",
                "06",
                "https://icd.who.int/browse/2026-01/mms/en#789",
                "True", "1", "Neurodevelopmental disorders",
                "Mental, behavioural or neurodevelopmental disorders",
                "", "", "", "",
                "http://id.who.int/icd/entity/123",  # parent = parent's foundation_uri
            ],
        ]

    with open(path, "w", encoding="utf-8-sig") as fh:
        for row in rows:
            fh.write("\t".join(row) + "\n")

    return base_dir


def _create_mapping_file(base_dir, release="2026-01", rows=None):
    """Create a minimal ICD-10 → ICD-11 mapping TSV at base_dir/<release>/extracted/mapping/."""
    mapping_dir = base_dir / release / "extracted" / "mapping"
    mapping_dir.mkdir(parents=True)
    path = mapping_dir / "10To11MapToOneCategory.txt"

    if rows is None:
        rows = [
            [
                "icd10Code", "icd10Title", "icd10Chapter",
                "icd11Code", "icd11Title", "icd11Chapter",
            ],
            [
                "F84.0", "Autistic disorder", "Mental and behavioural disorders",
                "6A02", "Autism spectrum disorder",
                "Mental, behavioural or neurodevelopmental disorders",
            ],
            [
                "F90.0", "Disturbance of activity and attention",
                "Mental and behavioural disorders",
                "6A05", "Attention deficit hyperactivity disorder",
                "Mental, behavioural or neurodevelopmental disorders",
            ],
        ]

    with open(path, "w", encoding="utf-8-sig") as fh:
        for row in rows:
            fh.write("\t".join(row) + "\n")

    return base_dir


def _load_entries(tmp_path, monkeypatch):
    """Helper: create tabulation, patch ICD11_BASE, load entries."""
    _create_tabulation_file(tmp_path)
    monkeypatch.setattr(icd11, "ICD11_BASE", tmp_path)
    entries, _ = icd11.load_tabulation("2026-01", "en")
    return entries


# ---------------------------------------------------------------------------
# _build_column_map
# ---------------------------------------------------------------------------


class TestBuildColumnMap:
    def test_en_header(self):
        header = [
            "Foundation URI", "Linearization URI", "Code", "BlockId",
            "Title", "ClassKind", "DepthInKind", "IsResidual",
            "ChapterNo", "BrowserLink", "isLeaf", "Primary tabulation",
            "Grouping1", "Grouping2", "Grouping3", "Grouping4",
            "Grouping5", "CodingNote", "Parent",
        ]
        col_map = icd11._build_column_map(header, "en")
        assert col_map["code"] is not None
        assert col_map["title"] is not None
        assert col_map["class_kind"] is not None
        assert col_map["grouping1"] is not None
        assert col_map["grouping5"] is not None
        assert "title_en" not in col_map

    def test_de_header_has_title_en(self):
        header = [
            "Foundation URI", "Linearization URI", "Code", "BlockId",
            "Title", "TitleEN", "ClassKind", "DepthInKind",
        ]
        col_map = icd11._build_column_map(header, "de")
        assert col_map["title"] is not None
        assert "title_en" in col_map


# ---------------------------------------------------------------------------
# _cell
# ---------------------------------------------------------------------------


class TestCell:
    def test_key_present(self):
        row = ["A", "B", "C"]
        col_map = {"item": 1}
        assert icd11._cell(row, col_map, "item") == "B"

    def test_key_absent_default(self):
        row = ["A"]
        col_map = {"missing": 99}
        assert icd11._cell(row, col_map, "missing") == ""


# ---------------------------------------------------------------------------
# load_tabulation
# ---------------------------------------------------------------------------


class TestLoadTabulation:
    def test_loads_from_tsv(self, tmp_path, monkeypatch):
        _create_tabulation_file(tmp_path)
        monkeypatch.setattr(icd11, "ICD11_BASE", tmp_path)
        entries, _ = icd11.load_tabulation("2026-01", "en")
        assert len(entries) == 2
        assert entries[0]["code"] == "6A02"
        assert entries[0]["title"] == "Autism spectrum disorder"
        assert entries[1]["code"] == "6A02.0"

    def test_missing_file_exits(self, tmp_path, monkeypatch):
        monkeypatch.setattr(icd11, "ICD11_BASE", tmp_path)
        with pytest.raises(SystemExit):
            icd11.load_tabulation("2026-01", "en")


# ---------------------------------------------------------------------------
# _is_match
# ---------------------------------------------------------------------------


class TestIsMatch:
    def test_exact_match(self):
        assert icd11._is_match("Autism", "autism") is True

    def test_substring(self):
        assert icd11._is_match("Autism spectrum disorder", "spectrum") is True

    def test_no_match(self):
        assert icd11._is_match("Autism", "ADHD") is False

    def test_quote_normalization(self):
        """Dashes and quotes are normalized before matching."""
        assert icd11._is_match("it's \"fine\"", "its fine") is True


# ---------------------------------------------------------------------------
# search_by_code
# ---------------------------------------------------------------------------


class TestSearchByCode:
    def test_exact_match(self, tmp_path, monkeypatch):
        entries = _load_entries(tmp_path, monkeypatch)
        result = icd11.search_by_code(entries, "6A02")
        assert len(result) == 1
        assert result[0]["code"] == "6A02"

    def test_stem_prefix_match(self, tmp_path, monkeypatch):
        entries = _load_entries(tmp_path, monkeypatch)
        # Remove exact match to force prefix fallback
        entries_no_exact = [e for e in entries if e["code"] != "6A02"]
        result = icd11.search_by_code(entries_no_exact, "6A02")
        assert len(result) >= 1
        assert result[0]["code"] == "6A02.0"

    def test_not_found(self, tmp_path, monkeypatch):
        entries = _load_entries(tmp_path, monkeypatch)
        result = icd11.search_by_code(entries, "ZZ99")
        assert result == []


# ---------------------------------------------------------------------------
# search_by_keyword
# ---------------------------------------------------------------------------


class TestSearchByKeyword:
    def test_match_in_title(self, tmp_path, monkeypatch):
        entries = _load_entries(tmp_path, monkeypatch)
        results = icd11.search_by_keyword(entries, "autism")
        assert len(results) >= 1
        assert any("autism" in r["title"].lower() for r in results)

    def test_no_match(self, tmp_path, monkeypatch):
        entries = _load_entries(tmp_path, monkeypatch)
        results = icd11.search_by_keyword(entries, "zzz_nonexistent")
        assert results == []

    def test_respects_limit(self, tmp_path, monkeypatch):
        entries = _load_entries(tmp_path, monkeypatch)
        results = icd11.search_by_keyword(entries, "disorder", limit=1)
        assert len(results) <= 1


# ---------------------------------------------------------------------------
# get_ancestors / get_children
# ---------------------------------------------------------------------------


class TestGetAncestors:
    def test_follows_parent_chain(self, tmp_path, monkeypatch):
        entries = _load_entries(tmp_path, monkeypatch)
        child = next(e for e in entries if e["code"] == "6A02.0")
        ancestors = icd11.get_ancestors(entries, child)
        assert len(ancestors) >= 1
        assert ancestors[0]["code"] == "6A02"


class TestGetChildren:
    def test_finds_direct_children(self, tmp_path, monkeypatch):
        entries = _load_entries(tmp_path, monkeypatch)
        parent = next(e for e in entries if e["code"] == "6A02")
        children = icd11.get_children(entries, parent)
        assert len(children) >= 1
        assert children[0]["code"] == "6A02.0"


# ---------------------------------------------------------------------------
# load_icd10_to_icd11_mapping
# ---------------------------------------------------------------------------


class TestLoadIcd10ToIcd11Mapping:
    def test_loads_mapping(self, tmp_path, monkeypatch):
        _create_mapping_file(tmp_path)
        monkeypatch.setattr(icd11, "ICD11_BASE", tmp_path)
        mappings = icd11.load_icd10_to_icd11_mapping("2026-01")
        assert len(mappings) == 2
        assert mappings[0]["icd10_code"] == "F84.0"
        assert mappings[0]["icd11_code"] == "6A02"
