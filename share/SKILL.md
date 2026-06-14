---
name: share
description: Generate a shareable read-only markdown export of the current session, or a short summary. Triggered when the user types /share, /export, 'share session', 'export conversation', or 'save this session'. Use also when the user says 'share' with --summary flag for a condensed recap.
---

# /share — Session Export & Summary

When the user triggers this command (by typing `/share`, `/export`, "share this session", "export conversation", "save this session", etc.), generate a markdown export.

## Detect Mode

Check the user's message for `--summary`:
- `--summary` present → summary mode (short recap)
- No `--summary` → full export mode

## Environment

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `HERMES_SESSION_ID` | Yes | — | Current session identifier |
| `HERMES_HOME` | No | `~/.hermes` (Linux/macOS) or `~/AppData/Local/hermes` (Windows) | Hermes Agent data directory |
| `HERMES_EXPORT_DIR` | No | `$HERMES_HOME/exports` | Where to save the `.md` file |

## Recommended Workflow

The helper module at `scripts/export.py` handles formatting, path normalization, shell-less I/O fallback, and system-injected message cleanup. Retrieve session data with `session_search`, then import the module in `execute_code` to write the file.

See also: `references/skill-evolution-notes.md` for implementation notes from the last major refactor (Windows git-bash issues, `hermes_tools` limitations, helper-module pattern).

### 1. Get session info and messages

Call the `session_search` tool:

```
session_search(session_id="<session_id>")
```

Then extract from the result:

```python
import os

session_id = os.environ.get("HERMES_SESSION_ID", "").strip()
if not session_id:
    raise RuntimeError("HERMES_SESSION_ID is not set. Cannot export session.")

# Paste these from the session_search output:
meta = {"when": "...", "source": "...", "model": "..."}
messages = [...]
```

### 2. Paginate long sessions

```python
if result.get("truncated"):
    ids = sorted(m["id"] for m in messages)
    fetched = set(ids)
    min_id, max_id = ids[0], ids[-1]
    midpoint = (min_id + max_id) // 2
    attempts = 0
    while len(fetched) < result.get("message_count", len(messages)) and attempts < 10:
        chunk = session_search(session_id=session_id, around_message_id=midpoint, window=20)
        for m in chunk.get("messages", []):
            if m["id"] not in fetched:
                messages.append(m)
                fetched.add(m["id"])
        sorted_ids = sorted(fetched)
        gaps = [(sorted_ids[i+1] - sorted_ids[i], sorted_ids[i]) for i in range(len(sorted_ids)-1)]
        if not gaps or max(g[0] for g in gaps) <= 1:
            break
        biggest_gap, gap_start = max(gaps)
        midpoint = gap_start + biggest_gap // 2
        attempts += 1
    messages.sort(key=lambda m: m["id"])
```

### 3. Full export

```python
from datetime import datetime
import os, sys

# --- paste session_id, meta, messages from steps 1-2 ---

hermes_home = os.environ.get("HERMES_HOME", "")
if not hermes_home:
    raise RuntimeError("HERMES_HOME is not set. Cannot find skill scripts.")
export_dir = os.environ.get("HERMES_EXPORT_DIR", "")
if not export_dir:
    export_dir = os.path.join(hermes_home, "exports")
os.makedirs(export_dir, exist_ok=True)

skill_dir = os.path.join(hermes_home, "skills", "share")
sys.path.insert(0, os.path.join(skill_dir, "scripts"))
from export import build_export, safe_write

filename = f"{session_id}-{datetime.now().strftime('%Y-%m-%d')}.md"
content = build_export(session_id, meta, messages)
filepath = safe_write(os.path.join(export_dir, filename), content)
print(f"Saved: {filepath}")
```

### 4. Summary export

```python
from datetime import datetime
import os, sys

# --- paste session_id, meta from steps 1-2 ---

summary = """Your 3-5 sentence summary here: goal, what was built/decided, key outcomes."""

hermes_home = os.environ.get("HERMES_HOME", "")
if not hermes_home:
    raise RuntimeError("HERMES_HOME is not set. Cannot find skill scripts.")
export_dir = os.environ.get("HERMES_EXPORT_DIR", "")
if not export_dir:
    export_dir = os.path.join(hermes_home, "exports")
os.makedirs(export_dir, exist_ok=True)

skill_dir = os.path.join(hermes_home, "skills", "share")
sys.path.insert(0, os.path.join(skill_dir, "scripts"))
from export import build_summary, safe_write

filename = f"{session_id}-{datetime.now().strftime('%Y-%m-%d')}-summary.md"
content = build_summary(session_id, meta, summary)
filepath = safe_write(os.path.join(export_dir, filename), content)
print(f"Saved: {filepath}")
```

## If the helper module is unavailable

Use this self-contained template in `execute_code`:

```python
from hermes_tools import write_file
from datetime import datetime, timezone
import json, os

# 1) Call session_search(session_id=session_id) to get 'result'.
# 2) Paste the result into the variable below:
result = {"session_meta": {...}, "messages": [...], "truncated": False, "message_count": 0}  # from session_search

session_id = os.environ.get("HERMES_SESSION_ID", "").strip()
if not session_id:
    raise RuntimeError("HERMES_SESSION_ID is not set. Cannot export session.")

meta = result.get("session_meta", {})
messages = result.get("messages", [])

if result.get("truncated"):
    ids = sorted(m["id"] for m in messages)
    fetched = set(ids)
    midpoint = (ids[0] + ids[-1]) // 2
    while len(fetched) < result.get("message_count", len(messages)):
        chunk = session_search(session_id=session_id, around_message_id=midpoint, window=20)
        for m in chunk.get("messages", []):
            if m["id"] not in fetched:
                messages.append(m); fetched.add(m["id"])
        messages.sort(key=lambda m: m["id"])
        break  # simplistic; expand if needed

def clean_content(content, role):
    if role != "user" or not content:
        return content
    s = content.strip()
    if s.startswith("[IMPORTANT:") and "---" in s:
        parts = s.split("---", 2)
        if len(parts) >= 3:
            for line in parts[2].splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("["):
                    return line
            return "(system skill invocation)"
    return content

frontmatter = {
    "session_id": session_id,
    "date": meta.get("when", ""),
    "source": meta.get("source", ""),
    "model": meta.get("model", ""),
    "message_count": len(messages),
    "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
}
lines = ["---", json.dumps(frontmatter, indent=2), "---", ""]
lines.append(f"# Session Export: {session_id}"); lines.append("")
lines.append(f"**Date:** {meta.get('when', '')}")
lines.append(f"**Source:** {meta.get('source', '')}")
lines.append(f"**Model:** {meta.get('model', '')}")
lines.append(f"**Messages:** {len(messages)}"); lines.append(""); lines.append("---"); lines.append("")

for msg in messages:
    role = msg.get("role", "unknown")
    if role == "session_meta":
        continue
    ts = datetime.fromtimestamp(msg["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    if role == "user":
        label, content = "User", clean_content(msg.get("content", ""), role)
    elif role == "assistant":
        label = "Agent"
        content = msg.get("content", "")
        if not content and msg.get("tool_calls"):
            content = f"(tool calls: {', '.join(tc['function']['name'] for tc in msg['tool_calls'])})"
        if not content:
            content = "(no content)"
    elif role == "tool":
        label = f"Tool ({msg.get('tool_name', 'unknown')})"
        content = msg.get("content", "")
        if len(content) > 2000:
            content = content[:2000] + f"\n\n[... truncated {len(content) - 2000} more chars ...]"
    else:
        label, content = role.capitalize(), msg.get("content", "")
    if not content.strip() and not msg.get("tool_calls"):
        continue
    lines.extend([f"## [{ts}] {label}", "", content, "", "---", ""])

export_dir = os.environ.get("HERMES_EXPORT_DIR", "") or os.path.join(os.environ.get("HERMES_HOME", os.path.join(os.path.expanduser("~"), ".hermes")), "exports")
os.makedirs(export_dir, exist_ok=True)
filepath = os.path.join(export_dir, f"{session_id}-{datetime.now().strftime('%Y-%m-%d')}.md")

# hermes_tools.write_file with fallback to raw open()
try:
    r = write_file(path=filepath, content="\n".join(lines))
    if r.get("error"):
        raise RuntimeError(r["error"])
except Exception:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
print(f"Saved: {filepath}")
```

## Message Cleanup

When Hermes injects a skill body into a user message (starts with `[IMPORTANT: ...]` and contains `---` frontmatter), the raw content is noise. Replace it with a short description, e.g.:

```
User typed /share to export the session.
```

## Summary Mode

1. Fetch session data the same way as full export.
2. Review user and assistant messages; use tool output only for context.
3. Write 3-5 sentences covering the goal, what was built/fixed/decided, and key deliverables. For very short sessions, 1-2 sentences is fine.
4. Save as `{session_id}-{today}-summary.md` and print the path.

## Edge Cases

- **Empty session** — report: `No messages found for session {id}. The session may not have been persisted yet — try again after a few messages.`
- **Missing session ID** — report: `HERMES_SESSION_ID is not set. Cannot export session.`
- **Long session** — use scroll pagination (see section 2). Add a warning at the top if any gap could not be filled.
- **Huge tool output** — truncate at 2000 chars and mark it.
- **Assistant with only tool_calls** — list the function names.
- **Windows/git-bash shell failures** — avoid shell commands; use Python builtins and raw `open()` for file I/O.
- **hermes_tools.write_file fails** — fall back to raw Python `open()`.
