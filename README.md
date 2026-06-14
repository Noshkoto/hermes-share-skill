# /share — Hermes Agent Skill

A slash command for Hermes Agent that exports the current session to a clean markdown file, or generates a short summary.

## Install

```bash
cp -r share ~/.hermes/skills/productivity/share/
```

Or symlink it:

```bash
ln -s $(pwd)/share ~/.hermes/skills/productivity/share
```

## Usage

| Command | What it does |
|---------|-------------|
| `/share` | Exports the full conversation to `~/.hermes/exports/{session_id}-{date}.md` with timestamps, roles, and full message content |
| `/share --summary` | Generates a 3-5 sentence recap and saves to `~/.hermes/exports/{session_id}-{date}-summary.md` |

## Output

Files land in `~/.hermes/exports/`:

```
~/.hermes/exports/
├── 20260614_084636_6d2eba-2026-06-14.md          # full export
└── 20260614_084636_6d2eba-2026-06-14-summary.md   # summary
```

## How it works

1. Reads `$HERMES_SESSION_ID` from the environment
2. Pulls session data via `session_search(session_id=...)`
3. Formats with Python (`datetime.fromtimestamp` for readable timestamps)
4. Writes the markdown file and prints the path

Handles all message roles: user, agent, tool output (truncated at 2000 chars), and assistant messages with tool calls. Skips session_meta bookmarks. For long sessions (>30 messages) the export includes a truncation note — use scroll pagination for full coverage.

## Requirements

- Hermes Agent (any recent version)
- `session_search` tool available
- `HERMES_SESSION_ID` env var (set automatically by Hermes)
