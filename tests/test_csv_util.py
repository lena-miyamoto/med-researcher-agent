"""Tests for csv-util.py — the CSV/TSV inspection and transform tool."""

import csv
import io
import json
import sys

import pytest

import csv_util as cu


HEADER = ["Deutscher Begriff", "Englischer Begriff", "Definition"]


def write_csv(path, rows, newline="\r\n"):
    """Write *rows* as CRLF/QUOTE_MINIMAL CSV with no trailing newline."""
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL, lineterminator=newline)
    writer.writerows(rows)
    text = buf.getvalue()
    if text.endswith(newline):
        text = text[: -len(newline)]
    path.write_bytes(text.encode("utf-8"))
    return text


def read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


class TestNorm:
    def test_lowercases_and_collapses_whitespace(self):
        assert cu.norm("  Hypertonie  ") == "hypertonie"

    def test_maps_dashes_and_slashes_to_spaces(self):
        assert cu.norm("Aufmerksamkeitsdefizit–Hyperaktivitätsstörung") == "aufmerksamkeitsdefizit hyperaktivitätsstörung"
        assert cu.norm("Myokardinfarkt / Herzinfarkt") == "myokardinfarkt herzinfarkt"

    def test_collapses_periods(self):
        assert cu.norm("a.b") == "a b"


class TestParseDelimiter:
    def test_named(self):
        assert cu.parse_delimiter("comma") == ","
        assert cu.parse_delimiter("TAB") == "\t"

    def test_literal_character(self):
        assert cu.parse_delimiter(";") == ";"

    def test_rejects_multi_char(self):
        with pytest.raises(ValueError):
            cu.parse_delimiter("||")


class TestDetectLineEnding:
    def test_crlf(self, tmp_path):
        p = tmp_path / "a.csv"
        p.write_bytes(b"a,b\r\nc,d\r\n")
        assert cu.detect_line_ending(p) == "\r\n"

    def test_lf(self, tmp_path):
        p = tmp_path / "a.csv"
        p.write_bytes(b"a,b\nc,d\n")
        assert cu.detect_line_ending(p) == "\n"


class TestResolveColumn:
    def test_by_name(self):
        assert cu.resolve_column(HEADER, "Definition") == 2

    def test_by_index(self):
        assert cu.resolve_column(HEADER, "3") == 2

    def test_missing_name(self):
        with pytest.raises(ValueError):
            cu.resolve_column(HEADER, "nope")

    def test_out_of_range_index(self):
        with pytest.raises(ValueError):
            cu.resolve_column(HEADER, "9")


class TestCellHelpers:
    def test_cell_pads_short_rows(self):
        assert cu.cell(["a"], 3) == ""

    def test_is_empty_row(self):
        assert cu.is_empty_row(["", "", ""]) is True
        assert cu.is_empty_row([]) is True
        assert cu.is_empty_row(["", "x"]) is False


class TestSplitColumns:
    def test_flattens_repeatable_and_comma(self):
        assert cu.split_columns(["a,b", "c", " d "]) == ["a", "b", "c", "d"]

    def test_none(self):
        assert cu.split_columns(None) == []


class TestRenderCsv:
    def test_roundtrip_crlf_no_trailing_newline(self):
        rows = [HEADER, ["Hypertonie", "hypertension", "Bluthochdruck"]]
        text = cu.render_csv(rows, ",", "\r\n")
        assert not text.endswith("\r\n")
        assert cu.render_csv(rows, ",", "\r\n") == "\r\n".join(
            ["Deutscher Begriff,Englischer Begriff,Definition", "Hypertonie,hypertension,Bluthochdruck"]
        )

    def test_quotes_embedded_newline(self):
        text = cu.render_csv([["a", "line1\nline2", "c"]], ",", "\r\n")
        assert '"line1\nline2"' in text


class TestDedupeRows:
    def test_full_row_first(self):
        rows = [["a", "1"], ["b", "2"], ["a", "1"]]
        assert cu.dedupe_rows(rows, tuple) == [["a", "1"], ["b", "2"]]

    def test_key_norm_first(self):
        rows = [["Hypertonie", "1"], ["hypertonie", "2"]]
        result = cu.dedupe_rows(rows, lambda r: cu.norm(r[0]))
        assert result == [["Hypertonie", "1"]]

    def test_keep_last(self):
        rows = [["a", "1"], ["b", "2"], ["a", "3"]]
        result = cu.dedupe_rows(rows, lambda r: r[0], keep="last")
        assert result == [["a", "3"], ["b", "2"]]


# ---------------------------------------------------------------------------
# CLI end-to-end
# ---------------------------------------------------------------------------


def run_main(argv):
    """Set sys.argv and run csv_util.main(), returning the exit code."""
    saved = sys.argv
    sys.argv = ["csv-util"] + argv
    try:
        return cu.main()
    finally:
        sys.argv = saved


class TestStatsCLI:
    def test_text_output(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        write_csv(p, [HEADER, ["Hypertonie", "hypertension", "Bluthochdruck"]])
        assert run_main(["stats", str(p)]) == 0
        out = capsys.readouterr().out
        assert "columns: 3" in out
        assert "data rows: 1" in out
        assert "placeholder rows (all fields empty): 0" in out

    def test_json_output(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        write_csv(p, [HEADER, ["Hypertonie", "hypertension", "Bluthochdruck"]])
        assert run_main(["stats", str(p), "--format", "json"]) == 0
        data = json.loads(capsys.readouterr().out)
        assert data["columns"] == 3
        assert data["data_rows"] == 1


class TestCheckCLI:
    def test_clean(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        write_csv(p, [HEADER, ["Hypertonie", "hypertension", "Bluthochdruck"]])
        assert run_main(["check", str(p), "--require", "Definition"]) == 0
        assert "status: clean" in capsys.readouterr().out

    def test_flags_placeholder_and_required(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        write_csv(p, [HEADER, ["", "", ""], ["Hypertonie", "hypertension", ""]])
        assert run_main(["check", str(p), "--require", "Definition"]) == 1
        out = capsys.readouterr().out
        assert "placeholder" in out
        assert "required" in out

    def test_flags_ragged_row(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        write_csv(p, [HEADER, ["only", "two"]])
        assert run_main(["check", str(p)]) == 1
        assert "field-count" in capsys.readouterr().out


class TestCutCLI:
    def test_selects_columns(self, tmp_path):
        p = tmp_path / "g.csv"
        out = tmp_path / "out.csv"
        write_csv(p, [HEADER, ["Hypertonie", "hypertension", "Bluthochdruck"]])
        assert run_main(["cut", str(p), "--columns", "Deutscher Begriff,Definition", "-o", str(out)]) == 0
        rows = read_csv(out)
        assert rows[0] == ["Deutscher Begriff", "Definition"]
        assert rows[1] == ["Hypertonie", "Bluthochdruck"]

    def test_requires_columns(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        write_csv(p, [HEADER, ["Hypertonie", "hypertension", "Bluthochdruck"]])
        assert run_main(["cut", str(p)]) == 1
        assert "cut requires" in capsys.readouterr().err


class TestHeadCLI:
    def test_limits_rows(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        write_csv(p, [HEADER, ["a", "1", "x"], ["b", "2", "x"]])
        assert run_main(["head", str(p), "--rows", "1"]) == 0
        rows = list(csv.reader(io.StringIO(capsys.readouterr().out)))
        assert rows[0] == HEADER
        assert rows[1] == ["a", "1", "x"]


class TestDropEmptyCLI:
    def test_removes_placeholder_rows(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        out = tmp_path / "out.csv"
        write_csv(p, [HEADER, ["", "", ""], ["Hypertonie", "hypertension", "Bluthochdruck"], ["", "", ""]])
        assert run_main(["drop-empty", str(p), "-o", str(out)]) == 0
        assert "dropped 2" in capsys.readouterr().err
        assert read_csv(out) == [HEADER, ["Hypertonie", "hypertension", "Bluthochdruck"]]

    def test_drops_by_columns(self, tmp_path):
        p = tmp_path / "g.csv"
        out = tmp_path / "out.csv"
        write_csv(p, [HEADER, ["Hypertonie", "hypertension", ""], ["Other", "x", "filled"]])
        assert run_main(["drop-empty", str(p), "--columns", "Definition", "-o", str(out)]) == 0
        assert read_csv(out) == [HEADER, ["Other", "x", "filled"]]


class TestDedupeCLI:
    def test_key_norm(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        out = tmp_path / "out.csv"
        write_csv(p, [HEADER, ["Hypertonie", "h", "x"], ["hypertonie", "h2", "x"]])
        assert run_main(["dedupe", str(p), "--key", "Deutscher Begriff", "--norm", "-o", str(out)]) == 0
        assert "removed 1" in capsys.readouterr().err
        assert read_csv(out) == [HEADER, ["Hypertonie", "h", "x"]]

    def test_norm_without_key_warns(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        write_csv(p, [HEADER, ["A", "a", "x"]])
        assert run_main(["dedupe", str(p), "--norm"]) == 0
        assert "no effect without --key" in capsys.readouterr().err


class TestFillCLI:
    def test_fills_from_map(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        out = tmp_path / "out.csv"
        mapping = tmp_path / "map.json"
        write_csv(p, [HEADER, ["Hypertonie", "hypertension", ""]])
        mapping.write_text(json.dumps({"Hypertonie": {"Definition": "Chronisch erhöhter Blutdruck"}}), encoding="utf-8")
        assert run_main(["fill", str(p), "--map", str(mapping), "--key-column", "Deutscher Begriff", "-o", str(out)]) == 0
        assert "filled 1" in capsys.readouterr().err
        rows = read_csv(out)
        assert rows[1][2] == "Chronisch erhöhter Blutdruck"

    def test_fill_pads_short_rows(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        out = tmp_path / "out.csv"
        mapping = tmp_path / "map.json"
        write_csv(p, [HEADER, ["Hypertonie", "hypertension"]])
        mapping.write_text(json.dumps({"Hypertonie": {"Definition": "Chronisch erhöhter Blutdruck"}}), encoding="utf-8")
        assert run_main(["fill", str(p), "--map", str(mapping), "--key-column", "Deutscher Begriff", "-o", str(out)]) == 0
        assert "filled 1" in capsys.readouterr().err
        assert read_csv(out) == [HEADER, ["Hypertonie", "hypertension", "Chronisch erhöhter Blutdruck"]]

    def test_reports_unmatched_keys(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        out = tmp_path / "out.csv"
        mapping = tmp_path / "map.json"
        write_csv(p, [HEADER, ["Hypertonie", "hypertension", ""]])
        mapping.write_text(json.dumps({"NoSuchTerm": {"Definition": "Unbekannt"}}), encoding="utf-8")
        assert run_main(["fill", str(p), "--map", str(mapping), "--key-column", "Deutscher Begriff", "-o", str(out)]) == 0
        assert "unmatched key" in capsys.readouterr().err


class TestInPlace:
    def test_overwrites_input(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        write_csv(p, [HEADER, ["", "", ""], ["Hypertonie", "hypertension", "Bluthochdruck"]])
        assert run_main(["drop-empty", str(p), "--in-place"]) == 0
        assert read_csv(p) == [HEADER, ["Hypertonie", "hypertension", "Bluthochdruck"]]

    def test_in_place_and_output_conflict(self, tmp_path, capsys):
        p = tmp_path / "g.csv"
        write_csv(p, [HEADER, ["Hypertonie", "hypertension", "Bluthochdruck"]])
        assert run_main(["cut", str(p), "--columns", "Definition", "--in-place", "-o", "other.csv"]) == 1
        assert "mutually exclusive" in capsys.readouterr().err
