<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo.svg">
    <img src="assets/logo.svg" width="220" alt="/share — session export for Hermes Agent">
  </picture>
</p>

<h1 align="center">/share</h1>

<p align="center">
  <em>One slash command. Your whole session, exported.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/Noshkoto/hermes-share-skill?style=flat-square&color=111111&label=stars" alt="Stars">
  <img src="https://img.shields.io/badge/works%20with-Hermes%20Agent-111111?style=flat-square" alt="Hermes Agent">
  <img src="https://img.shields.io/badge/license-MIT-111111?style=flat-square" alt="MIT">
  <img src="https://img.shields.io/badge/output-markdown-111111?style=flat-square" alt="Markdown">
</p>

---

## The problem

You just finished a two-hour coding session. Decisions were made. Bugs were fixed. Architecture was debated. You want to save the conversation — not for nostalgia, but because next week you'll need to remember *why* you chose one approach over another.

Copy-pasting from the terminal is tedious. The Hermes TUI scrolls. The desktop app's history is ephemeral.

## Before / after

**Without /share:**

```
"You'll need to scroll back through the terminal to find that decision
about the proxy binding. Hope you remember which session it was in."
```

**With /share:**

```
User: /share
Agent: "Saved: ~/.hermes/exports/20260615_094114_363531-2026-06-15.md"

# File contains:
- YAML frontmatter (session_id, date, model, message_count)
- Every message with timestamps and roles
- Tool calls preserved (function names listed)
- Tool output truncated at 2000 chars with a note
- System-injected skill bodies cleaned from user messages
- Compatible with Obsidian, Notion, any markdown editor
```

## How it works

```
1. You type /share              →  Full export mode
   or /share --summary          →  Summary mode (3-5 sentence recap)

2. Agent fetches session data   →  session_search reads the full transcript

3. Long sessions?               →  Auto-paginates past the 30-message limit
                                   with gap-detection and midpoint scrolling

4. Python formatter runs         →  Cleans system injections, formats timestamps,
                                   truncates huge tool output, writes to disk

5. File lands in exports/        →  Machine-readable YAML frontmatter
                                   Human-readable markdown body
```

## Install

Copy the skill folder into your Hermes skills directory:

```bash
cp -r share ~/.hermes/skills/productivity/share/
```

On Windows:

```powershell
Copy-Item -Recurse share $env:HERMES_HOME\skills\share\
```

That's it. Hermes auto-discovers skills on restart. No config, no API keys, no dependencies.

## Usage

| Command | Output |
|---------|--------|
| `/share` | Full session export with every message, timestamp, and tool call |
| `/share --summary` | 3-5 sentence recap — goal, decisions, outcomes |

## Features

- **YAML frontmatter** — session_id, date, source, model, message_count, exported_at. Obsidian-compatible.
- **Auto-pagination** — scrolls past the 30-message truncation limit. Gap detection ensures nothing is skipped.
- **Message cleanup** — system-injected skill bodies replaced with short descriptions. No noise.
- **Tool output truncation** — outputs over 2000 chars get a summary note instead of filling pages.
- **Fallback I/O** — uses Python's raw `open()` when `hermes_tools.write_file` isn't available (Windows git-bash).
- **Timestamp formatting** — Unix epoch converted to readable `YYYY-MM-DD HH:MM:SS` in every message header.
- **Configurable output dir** — set `HERMES_EXPORT_DIR` to change where files go.

## Output

```
~/.hermes/exports/
├── 20260615_094114_363531-2026-06-15.md          # full export
├── 20260615_094114_363531-2026-06-15-summary.md   # --summary mode
├── 20260616_123456_7b7474-2026-06-16.md
```

Each file opens in any markdown editor:

```
---
{
  "session_id": "20260615_094114_363531",
  "date": "June 15, 2026 at 09:41 AM",
  "source": "cli",
  "model": "deepseek-v4-flash",
  "message_count": 137,
  "exported_at": "2026-06-15 14:30:00 UTC"
}
---

# Session Export: 20260615_094114_363531

**Date:** June 15, 2026
**Source:** cli
**Model:** deepseek-v4-flash

---

## [2026-06-15 09:41:11] User

Need to set up a remote gateway to here from my hermes desktop...

---
```

## Requirements

- Hermes Agent (any recent version)
- `session_search` tool available
- `HERMES_SESSION_ID` environment variable (set automatically)

## Files

```
share/
├── SKILL.md          # Skill definition with full workflow
├── scripts/
│   └── export.py     # Python helper — formatting and I/O
└── references/
    └── skill-evolution-notes.md
```

## Edge cases handled

| Scenario | Behavior |
|----------|----------|
| Empty session | Reports "No messages found" with guidance |
| Missing session ID | Reports "HERMES_SESSION_ID not set" |
| Long session (>30 msgs) | Auto-paginates with gap detection |
| Huge tool output | Truncated at 2000 chars + note |
| Assistant with only tool_calls | Lists function names used |
| Windows git-bash write failures | Falls back to raw `open()` |
| System-injected skill bodies | Stripped and replaced with clear description |

---

*"If it mattered enough to spend two hours on, it matters enough to export."*
