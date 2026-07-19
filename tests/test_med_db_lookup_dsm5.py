"""Tests for med-db-lookup-dsm5.py — DSM-5-TR classification lookup."""

import json
from pathlib import Path

import pytest

import med_db_lookup_dsm5 as dsm5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_classification(tmp_path):
    """Create a minimal DSM-5-TR classification.json fixture."""
    data = {
        "categories": [
            {
                "name": "Neurodevelopmental Disorders",
                "icd10cm_range": "F70-F98",
                "disorders": [
                    {
                        "code": "F84.0",
                        "name": "Autism Spectrum Disorder",
                        "specifiers": [
                            "Level 1: Requiring support",
                            "Level 2: Requiring substantial support",
                            "Level 3: Requiring very substantial support",
                        ],
                    },
                    {
                        "code": "F90.2",
                        "name": "Attention-Deficit/Hyperactivity Disorder",
                        "specifiers": [
                            "Combined presentation",
                            "Predominantly inattentive presentation",
                        ],
                    },
                ],
            },
            {
                "name": "Depressive Disorders",
                "icd10cm_range": "F32-F39",
                "disorders": [
                    {
                        "code": "F32.0",
                        "name": "Major Depressive Disorder, Single episode, Mild",
                    },
                    {
                        "code": "F32.1",
                        "name": "Major Depressive Disorder, Single episode, Moderate",
                    },
                ],
                "dsm5tr_note": "Includes specifiers for severity and course.",
            },
        ],
    }
    path = tmp_path / "classification.json"
    path.write_text(json.dumps(data))
    return path


# ---------------------------------------------------------------------------
# _flatten_disorders
# ---------------------------------------------------------------------------


class TestFlattenDisorders:
    def test_yields_all_disorders(self, tmp_path):
        path = _make_classification(tmp_path)
        data = json.loads(path.read_text())
        results = list(dsm5._flatten_disorders(data))
        assert len(results) == 4  # 2 + 2
        categories = {cat for cat, d in results}
        assert "Neurodevelopmental Disorders" in categories
        assert "Depressive Disorders" in categories

    def test_empty_categories(self):
        data = {"categories": []}
        results = list(dsm5._flatten_disorders(data))
        assert results == []


# ---------------------------------------------------------------------------
# _is_match
# ---------------------------------------------------------------------------


class TestIsMatch:
    def test_case_insensitive_match(self):
        assert dsm5._is_match("Autism Spectrum Disorder", "autism") is True

    def test_no_match(self):
        assert dsm5._is_match("Depression", "autism") is False


# ---------------------------------------------------------------------------
# search_by_code
# ---------------------------------------------------------------------------


class TestSearchByCode:
    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path):
        path = _make_classification(tmp_path)
        self.data = json.loads(path.read_text())

    def test_exact_match(self):
        result = dsm5.search_by_code(self.data, "F84.0")
        assert isinstance(result, list)
        assert len(result) == 1
        cat, disorder = result[0]
        assert cat == "Neurodevelopmental Disorders"
        assert disorder["code"] == "F84.0"

    def test_partial_match_single(self):
        """A code that matches exactly one disorder returns a single-element list."""
        result = dsm5.search_by_code(self.data, "F32.0")
        assert isinstance(result, list)
        assert len(result) == 1
        cat, disorder = result[0]
        assert disorder["code"] == "F32.0"

    def test_partial_match_multiple(self):
        """A prefix that matches multiple disorders returns a multi-element list."""
        result = dsm5.search_by_code(self.data, "F32")
        assert isinstance(result, list)
        assert len(result) == 2
        codes = {d["code"] for c, d in result}
        assert "F32.0" in codes
        assert "F32.1" in codes

    def test_not_found(self):
        result = dsm5.search_by_code(self.data, "ZZ99")
        assert result == []


# ---------------------------------------------------------------------------
# search_by_keyword
# ---------------------------------------------------------------------------


class TestSearchByKeyword:
    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path):
        path = _make_classification(tmp_path)
        self.data = json.loads(path.read_text())

    def test_match_found(self):
        results = dsm5.search_by_keyword(self.data, "attention")
        assert len(results) == 1
        cat, disorder = results[0]
        assert "Hyperactivity" in disorder["name"]

    def test_no_match(self):
        results = dsm5.search_by_keyword(self.data, "zzz_nonexistent")
        assert results == []

    def test_respects_limit(self):
        results = dsm5.search_by_keyword(self.data, "disorder", limit=1)
        assert len(results) <= 1


# ---------------------------------------------------------------------------
# search_category
# ---------------------------------------------------------------------------


class TestSearchCategory:
    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path):
        path = _make_classification(tmp_path)
        self.data = json.loads(path.read_text())

    def test_match_found(self):
        results = dsm5.search_category(self.data, "depressive")
        assert len(results) == 1
        assert results[0]["name"] == "Depressive Disorders"

    def test_no_match(self):
        results = dsm5.search_category(self.data, "zzz_nonexistent")
        assert results == []
