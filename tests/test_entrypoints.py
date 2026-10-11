"""Tests for entrypoints.py — uv run script dispatch, linting, and pytest runner."""

from pathlib import Path
from unittest import mock

import entrypoints as ep
import pytest


class TestLoadScript:
    def test_loads_script_module(self):
        module = ep._load_script("test_entrypoints_load", "utils.py")
        assert module.slugify("Hello World") == "hello-world"

    def test_missing_script_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="missing script entrypoint target"):
            ep._load_script("test_entrypoints_missing", "does-not-exist.py")

    def test_caches_loaded_module(self):
        first = ep._load_script("test_entrypoints_cache", "utils.py")
        second = ep._load_script("test_entrypoints_cache", "utils.py")
        assert first is second

    def test_unsupported_extension_raises_runtime_error(self, tmp_path, monkeypatch):
        (tmp_path / "bad.unknownext").write_text("content")
        monkeypatch.setattr(ep, "SCRIPTS_DIR", tmp_path)
        with pytest.raises(RuntimeError, match="could not load script spec"):
            ep._load_script("test_entrypoints_bad", "bad.unknownext")


ENTRY_POINT_SCRIPTS = [
    ("med_db", "med_db", "med-db.py"),
    ("med_db_lookup", "med_db_lookup", "med-db-lookup.py"),
    ("med_db_query", "med_db_query", "med-db-query.py"),
    ("med_db_lookup_icd11", "med_db_lookup_icd11", "med-db-lookup-icd11.py"),
    ("med_db_download_icd11", "med_db_download_icd11", "med-db-download-icd11.py"),
    ("med_db_download_paper", "med_db_download_paper", "med-db-download-paper.py"),
    ("med_db_integrity_check", "med_db_integrity_check", "med-db-integrity-check.py"),
    ("med_db_term", "med_db_term", "med-db-term.py"),
    ("med_db_term_lookup", "med_db_term_lookup", "med-db-term-lookup.py"),
    ("med_db_term_wikipedia", "med_db_term_wikipedia", "med-db-term-wikipedia.py"),
    ("med_db_term_mesh", "med_db_term_mesh", "med-db-term-mesh.py"),
    ("check_retraction", "check_retraction", "check-retraction.py"),
    ("csv_util", "csv_util", "csv-util.py"),
    ("session_protocol", "session_protocol", "session-protocol.py"),
    ("fetch_archive", "fetch_archive", "fetch-archive.py"),
]


class TestEntryPoints:
    @pytest.mark.parametrize("function_name, module_name, filename", ENTRY_POINT_SCRIPTS)
    def test_entry_point_dispatches_to_main(
        self, function_name, module_name, filename, monkeypatch
    ):
        calls = []

        class FakeModule:
            @staticmethod
            def main():
                calls.append("main")
                return 42

        def fake_load_script(loaded_module_name, loaded_filename):
            calls.append((loaded_module_name, loaded_filename))
            return FakeModule()

        monkeypatch.setattr(ep, "_load_script", fake_load_script)

        result = getattr(ep, function_name)()

        assert result == 42
        assert calls == [(module_name, filename), "main"]


class TestLintMd:
    def _mock_rumdl(self, monkeypatch, returncode=0):
        run_mock = mock.Mock(return_value=mock.Mock(returncode=returncode))
        monkeypatch.setattr(ep.subprocess, "run", run_mock)
        return run_mock

    def _patch_argv(self, monkeypatch, args):
        monkeypatch.setattr(ep.sys, "argv", ["entrypoints.py", *args])

    def test_explicit_path_single_check(self, monkeypatch):
        run_mock = self._mock_rumdl(monkeypatch)
        result = ep.lint_md(["README.md"])
        assert result == 0
        run_mock.assert_called_once_with(["rumdl", "check", "README.md"], check=False)

    def test_default_targets(self, monkeypatch):
        run_mock = self._mock_rumdl(monkeypatch)
        repo_root = Path(ep.SCRIPTS_DIR).resolve().parent.parent
        result = ep.lint_md([])
        assert result == 0
        run_mock.assert_called_once_with(
            [
                "rumdl",
                "check",
                str(repo_root / "AGENTS.md"),
                str(repo_root / "README.md"),
                str(repo_root / "CLAUDE.md"),
                str(repo_root / ".github"),
                str(repo_root / ".claude"),
            ],
            check=False,
        )

    def test_fix_formats_then_checks(self, monkeypatch):
        run_mock = self._mock_rumdl(monkeypatch)
        result = ep.lint_md(["--fix", "README.md"])
        assert result == 0
        assert run_mock.call_args_list == [
            mock.call(["rumdl", "fmt", "README.md"], check=False),
            mock.call(["rumdl", "check", "README.md"], check=False),
        ]

    def test_reads_sys_argv_by_default(self, monkeypatch):
        run_mock = self._mock_rumdl(monkeypatch)
        self._patch_argv(monkeypatch, ["AGENTS.md"])
        result = ep.lint_md()
        assert result == 0
        run_mock.assert_called_once_with(["rumdl", "check", "AGENTS.md"], check=False)

    def test_returns_rumdl_exit_code(self, monkeypatch):
        self._mock_rumdl(monkeypatch, returncode=1)
        assert ep.lint_md(["README.md"]) == 1

    def test_check_source_md_delegates_to_utils(self, tmp_path, monkeypatch, capsys):
        source_file = tmp_path / "source.md"
        source_file.write_text("x" * 130 + "\n", encoding="utf-8")
        run_mock = self._mock_rumdl(monkeypatch)
        result = ep.lint_md(["--check-source-md", str(source_file)])
        assert result == 1
        assert "line length 130 > 120" in capsys.readouterr().out
        run_mock.assert_not_called()

    def test_fix_source_md_delegates_to_utils(self, tmp_path, monkeypatch):
        source_file = tmp_path / "source.md"
        source_file.write_text("word " * 40, encoding="utf-8")
        run_mock = self._mock_rumdl(monkeypatch)
        result = ep.lint_md(["--fix-source-md", str(source_file)])
        assert result == 0
        run_mock.assert_not_called()
        for line in source_file.read_text(encoding="utf-8").splitlines():
            assert len(line) <= 120


class TestRunTests:
    def test_test_function_runs_pytest_with_args(self):
        with mock.patch("pytest.main", return_value=0) as pytest_main:
            result = ep.test(["tests/", "-q"])
        assert result == 0
        pytest_main.assert_called_once_with(["tests/", "-q"])

    def test_test_function_defaults(self, monkeypatch):
        monkeypatch.setattr(ep.sys, "argv", ["entrypoints.py"])
        with mock.patch("pytest.main", return_value=0) as pytest_main:
            ep.test()
        pytest_main.assert_called_once_with(["tests/", "-v"])


class TestLintAndFormat:
    def _mock_run(self, monkeypatch, returncode=0):
        run_mock = mock.Mock(return_value=mock.Mock(returncode=returncode))
        monkeypatch.setattr(ep.subprocess, "run", run_mock)
        return run_mock

    def _patch_argv(self, monkeypatch, args):
        monkeypatch.setattr(ep.sys, "argv", ["entrypoints.py", *args])

    def _calls(self, run_mock):
        return [call.args[0] for call in run_mock.call_args_list]

    def test_lint_defaults(self, monkeypatch):
        run_mock = self._mock_run(monkeypatch)
        self._patch_argv(monkeypatch, [])
        result = ep.lint()
        assert result == 0
        assert self._calls(run_mock) == [
            ["ruff", "check", ".claude/scripts", "tests"],
            ["ruff", "format", "--check", ".claude/scripts", "tests"],
        ]

    def test_lint_fix_runs_fix_then_check_then_format_check(self, monkeypatch):
        run_mock = self._mock_run(monkeypatch)
        self._patch_argv(monkeypatch, ["--fix"])
        ep.lint()
        assert self._calls(run_mock) == [
            ["ruff", "check", "--fix", ".claude/scripts", "tests"],
            ["ruff", "check", ".claude/scripts", "tests"],
            ["ruff", "format", "--check", ".claude/scripts", "tests"],
        ]

    def test_lint_explicit_target(self, monkeypatch):
        run_mock = self._mock_run(monkeypatch)
        self._patch_argv(monkeypatch, ["some_script.py"])
        ep.lint()
        assert self._calls(run_mock) == [
            ["ruff", "check", "some_script.py"],
            ["ruff", "format", "--check", "some_script.py"],
        ]

    def test_lint_combines_return_codes(self, monkeypatch):
        self._mock_run(monkeypatch, returncode=1)
        self._patch_argv(monkeypatch, [])
        assert ep.lint() == 1

    def test_format_defaults(self, monkeypatch):
        run_mock = self._mock_run(monkeypatch)
        self._patch_argv(monkeypatch, [])
        result = ep.format()
        assert result == 0
        assert self._calls(run_mock) == [["ruff", "format", ".claude/scripts", "tests"]]

    def test_format_keeps_flags(self, monkeypatch):
        run_mock = self._mock_run(monkeypatch)
        self._patch_argv(monkeypatch, ["--check"])
        ep.format()
        assert self._calls(run_mock) == [["ruff", "format", "--check", ".claude/scripts", "tests"]]

    def test_format_explicit_path(self, monkeypatch):
        run_mock = self._mock_run(monkeypatch)
        self._patch_argv(monkeypatch, ["custom.py"])
        ep.format()
        assert self._calls(run_mock) == [["ruff", "format", "custom.py"]]
