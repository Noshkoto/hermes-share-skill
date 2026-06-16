# /share — AI agent instructions

You are working on the /share skill for Hermes Agent. It exports conversation sessions to clean markdown files.

## What /share does

Users type `/share` or `/share --summary` and get a markdown file with their entire session — every message, timestamp, role, and tool call. Summary mode gives a 3-5 sentence recap.

## Architecture

```
session_search()  →  messages array  →  Python formatter  →  write_file()  →  exports/*.md
```

The SKILL.md contains the full prompt that Hermes uses. The scripts/export.py module handles formatting and I/O. The fallback path uses raw Python `open()` when `hermes_tools.write_file` is unavailable.

## How to work on this

- **SKILL.md** — this is the prompt. Keep it precise and executable. The agent follows it literally.
- **scripts/export.py** — formatting logic. Tests live in the docstrings.
- **Don't break Windows** — git-bash has `hermes_tools.write_file` issues. The fallback path must always work.
- **Test with a real Hermes session** — ` /share` in your terminal. Verify the file opens in Obsidian.

## Edge cases that must work

1. Empty session → friendly error message, not a crash
2. Long session (>30 messages) → auto-paginate, gap detection
3. Huge tool output → truncated with a note, not a 50KB markdown file
4. Missing HERMES_SESSION_ID → clear error
5. write_file unavailable → fallback to raw open()
6. System-injected skill bodies → stripped from user messages
