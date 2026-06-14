#!/usr/bin/env python3
"""
/share export helper — formatting and I/O utilities for session exports.

This module is designed to be imported inside an `execute_code` block. The caller
is responsible for retrieving session data via the `session_search` tool first.

Example:
    import sys, os
    sys.path.insert(0, r"C:\\Users\\voltu\\AppData\\Local\\hermes\\skills\\share\\scripts")
    from export import build_export, safe_write

    content = build_export(session_id, meta, messages)
    path = safe_write(os.path.join(export_dir, filename), content)
    print(f"Saved: {path}")
"""

import json
import os
from datetime import datetime, timezone


def safe_write(path: str, content: str) -> str:
    """
    Write content to path, creating parent directories if needed.
    Tries hermes_tools.write_file first; falls back to raw Python open() if the
    underlying shell layer is unreliable (common on Windows git-bash).
    """
    try:
        from hermes_tools import write_file
        result = write_file(path=path, content=content)
        if not result.get("error"):
            return path
    except Exception:
        pass

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def clean_content(content: str, role: str) -> str:
    """
    Strip system-injected skill preamble from user messages so exports contain
    the user's actual intent, not the full injected skill markdown.
    """
    if role != "user" or not content:
        return content

    stripped = content.strip()
    if stripped.startswith("[IMPORTANT:") and "---" in stripped:
        parts = stripped.split("---", 2)
        if len(parts) >= 3:
            remainder = parts[2].strip()
            lines = remainder.splitlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("["):
                    return line
            return "(system skill invocation)"
    return content


def _format_timestamp(ts_raw):
    try:
        return datetime.fromtimestamp(ts_raw).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts_raw)


def _format_frontmatter(fields: dict) -> str:
    return "---\n" + json.dumps(fields, indent=2) + "\n---\n\n"


def build_export(session_id: str, meta: dict, messages: list) -> str:
    """Return the full markdown export as a string."""
    frontmatter = {
        "session_id": session_id,
        "date": meta.get("when", ""),
        "source": meta.get("source", ""),
        "model": meta.get("model", ""),
        "message_count": len(messages),
        "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    lines = [_format_frontmatter(frontmatter)]

    lines.append(f"# Session Export: {session_id}")
    lines.append("")
    lines.append(f"**Date:** {meta.get('when', '')}")
    lines.append(f"**Source:** {meta.get('source', '')}")
    lines.append(f"**Model:** {meta.get('model', '')}")
    lines.append(f"**Messages:** {len(messages)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for msg in messages:
        role = msg.get("role", "unknown")
        if role == "session_meta":
            continue

        ts = _format_timestamp(msg.get("timestamp"))

        if role == "user":
            label = "User"
            content = clean_content(msg.get("content", ""), role)
        elif role == "assistant":
            label = "Agent"
            content = msg.get("content", "")
            if not content and msg.get("tool_calls"):
                names = [tc["function"]["name"] for tc in msg["tool_calls"]]
                content = f"(tool calls: {', '.join(names)})"
            if not content:
                content = "(no content)"
        elif role == "tool":
            tool_name = msg.get("tool_name", "unknown")
            label = f"Tool ({tool_name})"
            content = msg.get("content", "")
            if len(content) > 2000:
                content = content[:2000] + f"\n\n[... truncated {len(content) - 2000} more chars ...]"
        else:
            label = role.capitalize()
            content = msg.get("content", "")

        if not content.strip() and not msg.get("tool_calls"):
            continue

        lines.append(f"## [{ts}] {label}")
        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def build_summary(session_id: str, meta: dict, summary_text: str) -> str:
    """Return the summary markdown export as a string."""
    frontmatter = {
        "session_id": session_id,
        "date": meta.get("when", ""),
        "source": meta.get("source", ""),
        "summary": True,
        "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    lines = [
        _format_frontmatter(frontmatter).rstrip(),
        f"# Session Summary: {session_id}",
        "",
        f"**Date:** {meta.get('when', '')}",
        f"**Source:** {meta.get('source', '')}",
        f"**Model:** {meta.get('model', '')}",
        "",
        "---",
        "",
        summary_text,
    ]
    return "\n".join(lines)
