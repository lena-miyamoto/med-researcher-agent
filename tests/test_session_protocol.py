"""Tests for session-protocol.py — the therapy-session transcript extractor."""

import json
import os
import sys

import pytest

import session_protocol as sp
import utils

SESSION_ENDED = "SESSION_ENDED"


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def text_block(text):
    return {"type": "text", "text": text}


def thinking_block(text):
    return {"type": "thinking", "thinking": text}


def tool_use_block(name, tool_input):
    return {"type": "tool_use", "name": name, "id": "tool-1", "input": tool_input}


def user_entry(*blocks):
    return {"type": "user", "message": {"role": "user", "content": list(blocks)}}


def assistant_entry(*blocks):
    return {"type": "assistant", "message": {"role": "assistant", "content": list(blocks)}}


def handoff_entry():
    return assistant_entry(
        tool_use_block("Agent", {"subagent_type": "psychotherapist", "description": "handoff"})
    )


def session_end_entry(closing="Closing words."):
    return assistant_entry(text_block(f"{closing}\n\n{SESSION_ENDED}"))


def end_skill_entry():
    return assistant_entry(tool_use_block("Skill", {"skill": "end-therapy-session", "args": "lena"}))


def write_jsonl(path, entries):
    path.write_text("\n".join(json.dumps(entry) for entry in entries) + "\n", encoding="utf-8")
    return path


def write_history(path, client="Lena", language="de"):
    lines = [
        "---",
        f"client: {client}",
        "slug: lena",
        f"language: {language}",
        "first_session: 2026-07-17",
        "sessions: 22",
        "---",
        "",
        "# Lena — Session History",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def set_mtime(path, timestamp):
    os.utime(path, (timestamp, timestamp))
    return path


def make_transcript(directory, name, closing="Bye.", mtime=None, with_skill_call=True):
    entries = [
        handoff_entry(),
        assistant_entry(text_block("Hi.")),
        user_entry(text_block("Hello.")),
        session_end_entry(closing),
    ]
    if with_skill_call:
        entries.append(end_skill_entry())
    path = directory / name
    write_jsonl(path, entries)
    if mtime is not None:
        set_mtime(path, mtime)
    return path


def run_main(argv):
    saved = sys.argv
    sys.argv = ["session-protocol"] + argv
    try:
        return sp.main()
    finally:
        sys.argv = saved


# ---------------------------------------------------------------------------
# Path encoding
# ---------------------------------------------------------------------------


class TestEncodeProjectDirectory:
    def test_single_segment(self):
        assert sp.encode_project_directory("/repo") == "-repo"

    def test_multi_segment(self):
        assert sp.encode_project_directory("/media/data/repo") == "-media-data-repo"


# ---------------------------------------------------------------------------
# Content extraction
# ---------------------------------------------------------------------------


class TestTextBlocks:
    def test_string_content_wraps_to_text_block(self):
        entry = {"type": "user", "message": {"role": "user", "content": "hello"}}
        assert sp.text_blocks(entry) == ["hello"]

    def test_missing_content_is_empty(self):
        entry = {"type": "user", "message": {"role": "user"}}
        assert sp.text_blocks(entry) == []

    def test_filters_non_text_blocks(self):
        entry = assistant_entry(
            text_block("hi"), thinking_block("think"), tool_use_block("Skill", {"skill": "x"})
        )
        assert sp.text_blocks(entry) == ["hi"]


# ---------------------------------------------------------------------------
# Entry classification
# ---------------------------------------------------------------------------


class TestIsSessionEndEntry:
    def test_marker_as_whole_line(self):
        assert sp.is_session_end_entry(session_end_entry("Bye.")) is True

    def test_marker_inside_prose(self):
        assert sp.is_session_end_entry(assistant_entry(text_block("I wrote SESSION_ENDED here"))) is False

    def test_user_entry_with_marker(self):
        assert sp.is_session_end_entry(user_entry(text_block(SESSION_ENDED))) is False

    def test_thinking_only_is_false(self):
        assert sp.is_session_end_entry(assistant_entry(thinking_block("output SESSION_ENDED"))) is False


class TestHasEndSkillCall:
    def test_end_skill(self):
        assert sp.has_end_skill_call(end_skill_entry()) is True

    def test_other_skill(self):
        assert sp.has_end_skill_call(assistant_entry(tool_use_block("Skill", {"skill": "med-db"}))) is False

    def test_agent_tool_use(self):
        assert sp.has_end_skill_call(handoff_entry()) is False


class TestIsHandoffEntry:
    def test_psychotherapist(self):
        assert sp.is_handoff_entry(handoff_entry()) is True

    def test_med_researcher(self):
        entry = assistant_entry(tool_use_block("Agent", {"subagent_type": "med-researcher"}))
        assert sp.is_handoff_entry(entry) is False

    def test_user_entry(self):
        assert sp.is_handoff_entry(user_entry(text_block("hello"))) is False


class TestIsNoiseUserEntry:
    def test_command_message(self):
        assert sp.is_noise_user_entry(user_entry(text_block("<command-message>start</command-message>"))) is True

    def test_local_command(self):
        assert sp.is_noise_user_entry(user_entry(text_block("<local-command-caveat>Caveat: ..."))) is True

    def test_system_reminder(self):
        assert sp.is_noise_user_entry(user_entry(text_block("<system-reminder>...</system-reminder>"))) is True

    def test_compaction_prefix(self):
        entry = user_entry(text_block("This session is being continued from a previous conversation..."))
        assert sp.is_noise_user_entry(entry) is True

    def test_empty_text(self):
        assert sp.is_noise_user_entry(user_entry()) is True

    def test_client_speech(self):
        assert sp.is_noise_user_entry(user_entry(text_block("Gestern gab es eine Diskussion."))) is False


# ---------------------------------------------------------------------------
# Marker stripping
# ---------------------------------------------------------------------------


class TestStripMarker:
    def test_closing_text_kept(self):
        assert sp.strip_marker(["Closing words.\n\nSESSION_ENDED"]) == ["Closing words."]

    def test_multiple_blocks_marker_in_second(self):
        texts = ["First paragraph.", "Second paragraph.\n\nSESSION_ENDED"]
        assert sp.strip_marker(texts) == ["First paragraph.", "Second paragraph."]

    def test_no_marker_unchanged(self):
        assert sp.strip_marker(["Plain text."]) == ["Plain text."]


# ---------------------------------------------------------------------------
# Turn extraction
# ---------------------------------------------------------------------------


class TestExtractTurns:
    def test_happy_path(self):
        entries = [
            handoff_entry(),
            assistant_entry(text_block("Welcome.")),
            user_entry(text_block("Hello, I feel bad.")),
            assistant_entry(text_block("Tell me more.")),
            user_entry(text_block("Okay.")),
            session_end_entry("Goodbye."),
        ]
        assert sp.extract_turns(entries, "test.jsonl") == [
            ("therapist", "Welcome."),
            ("client", "Hello, I feel bad."),
            ("therapist", "Tell me more."),
            ("client", "Okay."),
            ("therapist", "Goodbye."),
        ]

    def test_multi_block_join(self):
        entries = [
            handoff_entry(),
            assistant_entry(text_block("Part one."), text_block("Part two.")),
            session_end_entry("Bye."),
        ]
        assert sp.extract_turns(entries, "test.jsonl")[0] == ("therapist", "Part one.\n\nPart two.")

    def test_noise_skipped(self):
        entries = [
            handoff_entry(),
            assistant_entry(text_block("Hi.")),
            user_entry(text_block("<system-reminder>...</system-reminder>")),
            user_entry(text_block("This session is being continued from a previous conversation...")),
            user_entry(text_block("Real client words.")),
            assistant_entry(thinking_block("thinking only")),
            session_end_entry("Bye."),
        ]
        assert sp.extract_turns(entries, "test.jsonl") == [
            ("therapist", "Hi."),
            ("client", "Real client words."),
            ("therapist", "Bye."),
        ]

    def test_pre_handoff_excluded(self):
        entries = [
            assistant_entry(text_block("intake instructions")),
            handoff_entry(),
            session_end_entry("Bye."),
        ]
        assert sp.extract_turns(entries, "test.jsonl") == [("therapist", "Bye.")]

    def test_no_handoff(self):
        entries = [assistant_entry(text_block("hi")), session_end_entry("bye")]
        with pytest.raises(ValueError):
            sp.extract_turns(entries, "test.jsonl")

    def test_no_end(self):
        entries = [handoff_entry(), assistant_entry(text_block("hi"))]
        with pytest.raises(ValueError):
            sp.extract_turns(entries, "test.jsonl")

    def test_end_before_handoff(self):
        entries = [session_end_entry("bye"), handoff_entry()]
        with pytest.raises(ValueError):
            sp.extract_turns(entries, "test.jsonl")

    def test_empty_dialogue(self):
        entries = [
            handoff_entry(),
            user_entry(text_block("<system-reminder>...</system-reminder>")),
            assistant_entry(text_block(SESSION_ENDED)),
        ]
        with pytest.raises(ValueError):
            sp.extract_turns(entries, "test.jsonl")


# ---------------------------------------------------------------------------
# JSONL parsing
# ---------------------------------------------------------------------------


class TestParseJsonlLines:
    def test_blank_lines_skipped(self, tmp_path):
        entries = [handoff_entry(), session_end_entry("bye")]
        path = tmp_path / "s.jsonl"
        path.write_text(
            "\n" + json.dumps(entries[0]) + "\n\n" + json.dumps(entries[1]) + "\n", encoding="utf-8"
        )
        assert sp.parse_jsonl_lines(path) == entries

    def test_corrupt_last_line_skipped(self, tmp_path):
        path = tmp_path / "s.jsonl"
        path.write_text(
            json.dumps(handoff_entry()) + "\n" + json.dumps(session_end_entry("bye")) + "\n{partial",
            encoding="utf-8",
        )
        assert len(sp.parse_jsonl_lines(path)) == 2

    def test_corrupt_middle_line_raises(self, tmp_path):
        path = tmp_path / "s.jsonl"
        path.write_text(
            json.dumps(handoff_entry()) + "\n{corrupt\n" + json.dumps(session_end_entry("bye")) + "\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError):
            sp.parse_jsonl_lines(path)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


class TestRenderProtocol:
    def test_de_exact(self):
        turns = [("therapist", "Hallo."), ("client", "Guten Tag.")]
        expected = (
            "# S22: 2026-08-29 — Lena\n"
            "\n"
            "**Session language:** de\n"
            "\n"
            "**Therapeutin:**\n"
            "\n"
            "Hallo.\n"
            "\n"
            "**Client:**\n"
            "\n"
            "Guten Tag.\n"
        )
        assert sp.render_protocol(turns, "Lena", "de", 22, "2026-08-29") == expected

    def test_en_therapist_label(self):
        turns = [("therapist", "Hello.")]
        result = sp.render_protocol(turns, "Lena", "en", 1, "2026-01-01")
        assert "**Therapist:**" in result
        assert "**Therapeutin:**" not in result

    def test_language_case_insensitive(self):
        turns = [("therapist", "Hallo.")]
        result = sp.render_protocol(turns, "Lena", "DE", 1, "2026-01-01")
        assert "**Therapeutin:**" in result


# ---------------------------------------------------------------------------
# File selection
# ---------------------------------------------------------------------------


class TestSelectSessionFile:
    def _primary_directory(self, projects):
        return projects / sp.encode_project_directory(utils.REPO_ROOT)

    def test_override_wins(self, tmp_path):
        projects = tmp_path / "projects"
        primary = self._primary_directory(projects)
        primary.mkdir(parents=True)
        make_transcript(primary, "a.jsonl", mtime=100)
        override = tmp_path / "override.jsonl"
        write_jsonl(override, [handoff_entry(), session_end_entry("x"), end_skill_entry()])
        assert sp.select_session_file(projects, str(override)) == override

    def test_override_must_exist(self, tmp_path):
        with pytest.raises(ValueError):
            sp.select_session_file(tmp_path, str(tmp_path / "missing.jsonl"))

    def test_primary_beats_fallback(self, tmp_path):
        projects = tmp_path / "projects"
        primary = self._primary_directory(projects)
        primary.mkdir(parents=True)
        other = projects / "other"
        other.mkdir(parents=True)
        primary_file = make_transcript(primary, "primary.jsonl", mtime=10)
        make_transcript(other, "fallback.jsonl", mtime=100)
        assert sp.select_session_file(projects, None) == primary_file

    def test_newest_within_primary(self, tmp_path):
        projects = tmp_path / "projects"
        primary = self._primary_directory(projects)
        primary.mkdir(parents=True)
        make_transcript(primary, "old.jsonl", mtime=10)
        newest = make_transcript(primary, "new.jsonl", mtime=100)
        assert sp.select_session_file(projects, None) == newest

    def test_fallback_used_when_primary_empty(self, tmp_path):
        projects = tmp_path / "projects"
        self._primary_directory(projects).mkdir(parents=True)
        other = projects / "other"
        other.mkdir(parents=True)
        fallback_file = make_transcript(other, "fallback.jsonl", mtime=100)
        assert sp.select_session_file(projects, None) == fallback_file

    def test_marker_without_skill_not_selected(self, tmp_path):
        projects = tmp_path / "projects"
        primary = self._primary_directory(projects)
        primary.mkdir(parents=True)
        make_transcript(primary, "quote.jsonl", with_skill_call=False)
        with pytest.raises(ValueError):
            sp.select_session_file(projects, None)

    def test_no_match_raises(self, tmp_path):
        projects = tmp_path / "projects"
        self._primary_directory(projects).mkdir(parents=True)
        with pytest.raises(ValueError):
            sp.select_session_file(projects, None)


# ---------------------------------------------------------------------------
# CLI end-to-end
# ---------------------------------------------------------------------------


class TestCLI:
    def _setup(self, tmp_path, client="Lena", language="de"):
        projects = tmp_path / "projects"
        sessions = tmp_path / "sessions"
        sessions.mkdir(parents=True)
        write_history(sessions / "lena.md", client=client, language=language)
        primary = projects / sp.encode_project_directory(utils.REPO_ROOT)
        primary.mkdir(parents=True)
        make_transcript(primary, "session.jsonl", mtime=100)
        return projects, sessions

    def _args(self, projects, sessions, **extra):
        args = [
            "--slug", "lena",
            "--session-number", "22",
            "--date", "2026-08-29",
            "--projects-directory", str(projects),
            "--sessions-directory", str(sessions),
        ]
        for key, value in extra.items():
            args += [key, value]
        return args

    def test_exit_zero_and_output(self, tmp_path, capsys):
        projects, sessions = self._setup(tmp_path)
        assert run_main(self._args(projects, sessions)) == 0
        out = capsys.readouterr().out
        assert "protocol:" in out
        output = sessions / "protocols" / "2026-08-29_S22_lena.md"
        assert output.is_file()
        assert output.read_text(encoding="utf-8").startswith("# S22: 2026-08-29 — Lena\n")

    def test_protocols_dir_autocreated(self, tmp_path):
        projects, sessions = self._setup(tmp_path)
        assert run_main(self._args(projects, sessions)) == 0
        assert (sessions / "protocols").is_dir()

    def test_output_override(self, tmp_path, capsys):
        projects, sessions = self._setup(tmp_path)
        out = tmp_path / "custom.md"
        assert run_main(self._args(projects, sessions, **{"--output": str(out)})) == 0
        assert out.is_file()
        assert f"protocol: {out}" in capsys.readouterr().out

    def test_en_labels(self, tmp_path):
        projects, sessions = self._setup(tmp_path, language="en")
        assert run_main(self._args(projects, sessions, **{"--date": "2026-01-01", "--session-number": "1"})) == 0
        content = (sessions / "protocols" / "2026-01-01_S1_lena.md").read_text(encoding="utf-8")
        assert "**Therapist:**" in content

    def test_session_file_flag(self, tmp_path, capsys):
        projects, sessions = self._setup(tmp_path)
        explicit = tmp_path / "explicit.jsonl"
        write_jsonl(
            explicit,
            [
                handoff_entry(),
                assistant_entry(text_block("Hi.")),
                user_entry(text_block("Yo.")),
                session_end_entry("Bye."),
                end_skill_entry(),
            ],
        )
        assert run_main(self._args(projects, sessions, **{"--session-file": str(explicit)})) == 0
        assert f"source: {explicit}" in capsys.readouterr().out

    def test_error_missing_history(self, tmp_path, capsys):
        projects = tmp_path / "projects"
        sessions = tmp_path / "sessions"
        (projects / sp.encode_project_directory(utils.REPO_ROOT)).mkdir(parents=True)
        assert run_main(self._args(projects, sessions)) == 1
        assert "error:" in capsys.readouterr().err

    def test_error_missing_frontmatter_field(self, tmp_path, capsys):
        projects = tmp_path / "projects"
        sessions = tmp_path / "sessions"
        sessions.mkdir(parents=True)
        (sessions / "lena.md").write_text("---\nclient: Lena\nslug: lena\n---\n", encoding="utf-8")
        (projects / sp.encode_project_directory(utils.REPO_ROOT)).mkdir(parents=True)
        assert run_main(self._args(projects, sessions)) == 1
        assert "error:" in capsys.readouterr().err

    def test_error_bad_date(self, tmp_path, capsys):
        assert run_main(self._args(tmp_path / "p", tmp_path / "s", **{"--date": "2026/08/29"})) == 1
        assert "error:" in capsys.readouterr().err

    def test_error_bad_slug(self, tmp_path, capsys):
        assert run_main(self._args(tmp_path / "p", tmp_path / "s", **{"--slug": "../lena"})) == 1
        assert "error:" in capsys.readouterr().err

    def test_error_no_combo_found(self, tmp_path, capsys):
        projects = tmp_path / "projects"
        sessions = tmp_path / "sessions"
        sessions.mkdir(parents=True)
        write_history(sessions / "lena.md")
        (projects / sp.encode_project_directory(utils.REPO_ROOT)).mkdir(parents=True)
        assert run_main(self._args(projects, sessions)) == 1
        assert "error:" in capsys.readouterr().err
