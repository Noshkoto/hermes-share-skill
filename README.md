# /share — Hermes Agent Skill

A slash command for Hermes Agent that exports the current session to a clean markdown file, or generates a short summary.

## Install

Copy the `share/` directory to your skills folder:

```bash
cp -r share ~/.hermes/skills/productivity/share/
```

On Windows, copy to:
```
C:\Users\<you>\AppData\Local\hermes\skills\share\
```

## Usage

| Command | What it does |
|---------|-------------|
| `/share` | Exports the full conversation to `~/.hermes/exports/{session_id}-{date}.md` with YAML frontmatter, timestamps, roles, and message content |
| `/share --summary` | Generates a 3-5 sentence recap and saves to `~/.hermes/exports/{session_id}-{date}-summary.md` |

## Output

Files land in `~/.hermes/exports/`:

```
~/.hermes/exports/
├── 20260614_084636_6d2eba-2026-06-14.md          # full export
├── 20260614_084636_6d2eba-2026-06-14-summary.md   # summary
```

Full exports include YAML frontmatter with `session_id`, `date`, `source`, `model`, `message_count`, and `exported_at` — compatible with Obsidian, Notion, and other markdown note apps.

## How it works

1. You type `/share` or `/share --summary`
2. The agent retrieves session data via `session_search(session_id=...)`
3. A Python helper module (`scripts/export.py`) formats the markdown and writes it to disk
4. The file path is printed in your terminal

### Features

- **YAML frontmatter** — machine-readable metadata for Obsidian/Notion
- **Message cleanup** — strips Hermes system-injected skill bodies from user messages
- **Fallback I/O** — works even when `hermes_tools.write_file` has shell issues (common on Windows git-bash)
- **Long-session pagination** — scrolls past the 30-message truncation limit automatically
- **Configurable output dir** — set `HERMES_EXPORT_DIR` to change where files are saved
- **Tool output truncation** — tool output >2000 chars is truncated with a note
- **Timestamp formatting** — Unix timestamps converted to readable `YYYY-MM-DD HH:MM:SS`

## Requirements

- Hermes Agent (any recent version)
- `session_search` tool available
- `HERMES_SESSION_ID` env var (set automatically by Hermes)

## Files

```
share/
├── SKILL.md          # Skill definition and invocation instructions
└── scripts/
    └── export.py     # Python helper module (formatting & I/O)
```
