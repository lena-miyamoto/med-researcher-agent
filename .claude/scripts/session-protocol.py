"""Extract a therapy-session protocol from a Claude Code JSONL transcript.

Reads the client name and language from ``sessions/<slug>.md`` frontmatter,
locates the session transcript (newest ``*.jsonl`` under the project directory
containing both the ``SESSION_ENDED`` marker and the ``end-therapy-session``
Skill call), and writes a clean speaker-labelled protocol.

Run as ``uv run session-protocol --slug <slug> --session-number <N> --date <YYYY-MM-DD>``
from the repo root.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import utils

SESSION_ENDED_MARKER = "SESSION_ENDED"
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

NOISE_PREFIXES = (
    "<command-name",
    "<command-message",
    "<local-command",
    "<system-reminder",
    "This session is being continued from a previous conversation",
)


# ---------------------------------------------------------------------------
# Content extraction
# ---------------------------------------------------------------------------


def _content_blocks(entry):
    """Return the message content as a list of blocks.

    A string content wraps to a single text block; missing or non-list content
    returns an empty list.
    """
    message = entry.get("message") or {}
    content = message.get("content", [])
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if not isinstance(content, list):
        return []
    return content


def text_blocks(entry):
    """Return the list of text strings in *entry*'s content."""
    return [
        block["text"]
        for block in _content_blocks(entry)
        if isinstance(block, dict) and block.get("type") == "text" and "text" in block
    ]


def tool_use_blocks(entry):
    """Return the list of tool_use blocks in *entry*'s content."""
    return [
        block
        for block in _content_blocks(entry)
        if isinstance(block, dict) and block.get("type") == "tool_use"
    ]


# ---------------------------------------------------------------------------
# Entry classification
# ---------------------------------------------------------------------------


def _tool_input(block, key):
    """Return ``block["input"][key]`` when the input is a dict, else None."""
    value = block.get("input")
    if not isinstance(value, dict):
        return None
    return value.get(key)


def is_handoff_entry(entry):
    """Return True when *entry* dispatches the psychotherapist subagent."""
    if entry.get("type") != "assistant":
        return False
    for block in tool_use_blocks(entry):
        if block.get("name") == "Agent" and _tool_input(block, "subagent_type") == "psychotherapist":
            return True
    return False


def is_session_end_entry(entry):
    """Return True when *entry* is an assistant entry whose text has a whole
    line equal to the ``SESSION_ENDED`` marker."""
    if entry.get("type") != "assistant":
        return False
    for text in text_blocks(entry):
        for line in text.split("\n"):
            if line.strip() == SESSION_ENDED_MARKER:
                return True
    return False


def has_end_skill_call(entry):
    """Return True when *entry* invokes the ``end-therapy-session`` skill."""
    for block in tool_use_blocks(entry):
        if block.get("name") == "Skill" and _tool_input(block, "skill") == "end-therapy-session":
            return True
    return False


def is_noise_user_entry(entry):
    """Return True when a user entry carries no client speech.

    Empty text, or text starting with a command tag or the compaction prefix,
    is orchestrator noise rather than dialogue.
    """
    combined = "\n".join(text_blocks(entry)).lstrip()
    if not combined:
        return True
    return combined.startswith(NOISE_PREFIXES)


# ---------------------------------------------------------------------------
# JSONL reading
# ---------------------------------------------------------------------------


def has_session_end_entry(path):
    """Return True when *path* contains a session end marker and a skill call.

    Unparseable lines are skipped — this is a lenient search, not a parse.
    """
    found_marker = False
    found_skill = False
    for line in Path(path).read_text(encoding="utf-8").split("\n"):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if is_session_end_entry(entry):
            found_marker = True
        if has_end_skill_call(entry):
            found_skill = True
        if found_marker and found_skill:
            return True
    return False


def parse_jsonl_lines(path):
    """Parse every non-blank line of *path* into entry dicts.

    Blank lines are skipped. A ``JSONDecodeError`` on the final non-blank line
    (Claude Code's partially-flushed append tail) is skipped; a corrupt line
    elsewhere raises ``ValueError`` with the line number.
    """
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    non_blank = [index for index, line in enumerate(lines) if line.strip()]
    if not non_blank:
        return []
    last_index = non_blank[-1]

    entries = []
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as exc:
            if index == last_index:
                continue
            raise ValueError(f"corrupt JSON at line {index + 1} in {path}: {exc}") from exc
    return entries


# ---------------------------------------------------------------------------
# Anchor finding
# ---------------------------------------------------------------------------


def find_handoff_index(entries):
    """Return the index of the first psychotherapist handoff, or None."""
    for index, entry in enumerate(entries):
        if is_handoff_entry(entry):
            return index
    return None


def find_session_end_index(entries):
    """Return the index of the first session-end marker entry, or None."""
    for index, entry in enumerate(entries):
        if is_session_end_entry(entry):
            return index
    return None


# ---------------------------------------------------------------------------
# Marker stripping
# ---------------------------------------------------------------------------


def strip_marker(texts):
    """Strip the ``SESSION_ENDED`` marker (and everything after it) from *texts*.

    Keeps text before the marker line, dropping the blank line that precedes it.
    Blocks after the marker are discarded. Without a marker the list is returned
    unchanged.
    """
    stripped = []
    for text in texts:
        lines = text.split("\n")
        marker_line = None
        for index, line in enumerate(lines):
            if line.strip() == SESSION_ENDED_MARKER:
                marker_line = index
                break
        if marker_line is None:
            stripped.append(text)
            continue
        prefix_lines = lines[:marker_line]
        while prefix_lines and prefix_lines[-1] == "":
            prefix_lines.pop()
        if prefix_lines:
            stripped.append("\n".join(prefix_lines))
        break
    return stripped


# ---------------------------------------------------------------------------
# Turn extraction
# ---------------------------------------------------------------------------


def extract_turns(entries, session_file):
    """Return the dialogue between handoff and session end as ``(speaker, text)``.

    Client turns come from non-noise user text entries; therapist turns from
    assistant text entries. Every other entry type and non-text block is ignored.
    Raises ``ValueError`` when the anchors are missing, out of order, or enclose
    no dialogue.
    """
    handoff_index = find_handoff_index(entries)
    if handoff_index is None:
        raise ValueError(f"no therapist handoff found in {session_file}")

    end_index = find_session_end_index(entries)
    if end_index is None:
        raise ValueError(f"no session end marker found in {session_file}")
    if end_index <= handoff_index:
        raise ValueError(f"session end precedes handoff in {session_file}")

    turns = []
    for index in range(handoff_index + 1, end_index + 1):
        entry = entries[index]
        entry_type = entry.get("type")
        if entry_type == "user":
            if is_noise_user_entry(entry):
                continue
            text = "\n\n".join(text_blocks(entry))
            if text:
                turns.append(("client", text))
        elif entry_type == "assistant":
            texts = text_blocks(entry)
            if index == end_index:
                texts = strip_marker(texts)
            text = "\n\n".join(texts)
            if text:
                turns.append(("therapist", text))

    if not turns:
        raise ValueError(f"no dialogue found between handoff and session end in {session_file}")
    return turns


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_protocol(turns, client_name, language, session_number, date_string):
    """Render *turns* as a protocol document, byte-exact against existing files."""
    parts = [
        f"# S{session_number}: {date_string} — {client_name}",
        "",
        f"**Session language:** {language}",
        "",
    ]
    for speaker, text in turns:
        if speaker == "client":
            label = "Client"
        else:
            label = "Therapeutin" if language.lower() == "de" else "Therapist"
        parts.append(f"**{label}:**")
        parts.append("")
        parts.append(text)
        parts.append("")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# File selection
# ---------------------------------------------------------------------------


def encode_project_directory(root):
    """Encode a repository root as its Claude Code project-directory name."""
    return str(root).replace("/", "-")


def _newest_matching_file(directory):
    """Return the newest ``*.jsonl`` with a session end in *directory*, or None."""
    if not directory.is_dir():
        return None
    files = sorted(directory.glob("*.jsonl"), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in files:
        if has_session_end_entry(path):
            return path
    return None


def select_session_file(projects_directory, session_file_override):
    """Select the session transcript JSONL.

    An explicit override wins (must exist). Otherwise the primary project
    directory (encoded from the repo root) is scanned first; the newest matching
    file there beats any fallback directory. If the primary directory has no
    match, all other project directories are scanned and the newest overall wins.
    """
    if session_file_override is not None:
        path = Path(session_file_override)
        if not path.is_file():
            raise ValueError(f"session file not found: {path}")
        return path

    projects_directory = Path(projects_directory)
    primary_directory = projects_directory / encode_project_directory(utils.REPO_ROOT)

    primary_match = _newest_matching_file(primary_directory)
    if primary_match is not None:
        return primary_match

    fallback_matches = []
    for directory in projects_directory.iterdir():
        if not directory.is_dir() or directory == primary_directory:
            continue
        match = _newest_matching_file(directory)
        if match is not None:
            fallback_matches.append(match)
    if fallback_matches:
        return max(fallback_matches, key=lambda path: path.stat().st_mtime)

    raise ValueError(
        "no session transcript found; pass --session-file explicitly"
    )


# ---------------------------------------------------------------------------
# History context
# ---------------------------------------------------------------------------


def load_history_context(history_path):
    """Return ``{"client", "language"}`` from a history file's frontmatter."""
    path = Path(history_path)
    if not path.is_file():
        raise FileNotFoundError(f"history file not found: {path}")
    frontmatter = utils.parse_frontmatter(path.read_text(encoding="utf-8"))
    if frontmatter is None:
        raise ValueError(f"no frontmatter found in {path}")
    client = str(frontmatter.get("client") or "").strip()
    language = str(frontmatter.get("language") or "").strip()
    if not client or not language:
        raise ValueError(f"frontmatter in {path} is missing 'client' or 'language'")
    return {"client": client, "language": language}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def validate_args(args):
    """Validate slug, session number, and date, raising ``ValueError``."""
    if args.session_number < 1:
        raise ValueError(f"session number must be >= 1, got {args.session_number}")
    if not SLUG_PATTERN.match(args.slug):
        raise ValueError(f"invalid slug {args.slug!r}; expected [a-z0-9][a-z0-9-]*")
    if not DATE_PATTERN.match(args.date):
        raise ValueError(f"invalid date {args.date!r}; expected YYYY-MM-DD")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="session-protocol",
        description="Extract a therapy-session protocol from a Claude Code JSONL transcript.",
    )
    parser.add_argument("--slug", required=True, help="Client slug, e.g. 'lena'.")
    parser.add_argument("--session-number", type=int, required=True, help="Session number (>= 1).")
    parser.add_argument("--date", required=True, help="Session date, YYYY-MM-DD.")
    parser.add_argument("--session-file", default=None, help="Explicit transcript JSONL path.")
    parser.add_argument(
        "--projects-directory",
        default=str(Path.home() / ".claude" / "projects"),
        help="Root of Claude Code project directories.",
    )
    parser.add_argument(
        "--sessions-directory",
        default=str(utils.REPO_ROOT / "sessions"),
        help="Directory holding history files and protocols.",
    )
    parser.add_argument("--output", default=None, help="Output protocol path override.")
    return parser


def parse_args():
    return build_parser().parse_args()


def _run(args):
    validate_args(args)

    sessions_directory = Path(args.sessions_directory)
    projects_directory = Path(args.projects_directory)

    context = load_history_context(sessions_directory / f"{args.slug}.md")
    session_file = select_session_file(projects_directory, args.session_file)
    entries = parse_jsonl_lines(session_file)
    turns = extract_turns(entries, str(session_file))

    if args.output:
        output = Path(args.output)
    else:
        output = (
            sessions_directory
            / "protocols"
            / f"{args.date}_S{args.session_number}_{args.slug}.md"
        )

    rendered = render_protocol(
        turns, context["client"], context["language"], args.session_number, args.date
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    utils.atomic_write(output, rendered)

    therapist_count = sum(1 for speaker, _ in turns if speaker == "therapist")
    client_count = sum(1 for speaker, _ in turns if speaker == "client")
    print(
        f"protocol: {output} ({len(turns)} turns: {therapist_count} therapist, "
        f"{client_count} client; source: {session_file})"
    )
    return 0


def main():
    args = parse_args()
    try:
        return _run(args)
    except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    utils.run_cli(main)
