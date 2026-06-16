# Before / After

## Example 1: Debugging session

**Without /share:**

```
User: "Remember that proxy binding fix from last week?
      We changed it from localhost to 0.0.0.0."
Agent: "I don't have access to previous sessions.
       Could you describe the issue again?"
```

**With /share:**

```
User: /share
Agent: "Saved: exports/20260615-proxy-debug-2026-06-15.md"

# Monday morning:
User: "What did we decide about the proxy last week?"
Agent: "[Reading /share export from June 15]
       Session: Proxy binding fix
       Decision: Bind to 0.0.0.0, not 127.0.0.1
       Reason: Tailscale mesh needs all-interface binding
       Outcome: Desktop app connects reliably"
```

## Example 2: Architecture discussion

**Without /share:**

Two weeks later you can't remember why you chose Python over Rust. The discussion happened across 40 messages with trade-offs, links, and a final decision. It's gone.

**With /share:**

```
exports/20260615_arch-decision-2026-06-15.md

---
session_id: 20260615_arch-decision
date: June 15, 2026
source: cli
model: deepseek-v4-pro
message_count: 42
---

## [2026-06-15 14:22:00] User

Should we use Python or Rust for the memory layer?

## [2026-06-15 14:22:15] Agent

Python pros: faster Hermes integration, zero deps possible with stdlib,
quicker iteration. Rust pros: better performance, smaller binary.
But the bottleneck here is SQLite, not the language. Python wins.

## [2026-06-15 14:23:00] User

Agreed. Go with Python. Single-file modules.

---
```

## Example 3: Teaching session

**Without /share:**

You walked a junior dev through setting up Tailscale for the first time. Now they're asking again because nobody exported the session.

**With /share --summary:**

```
exports/20260615_tailscale-setup-2026-06-15-summary.md

Session covered Tailscale installation on Ubuntu with kernel TUN mode.
Key steps: curl install, sudo tailscale up with pre-auth key,
bind proxy to 0.0.0.0, verify with ip addr show tailscale0.
Resolved auth timeout by switching from browser OAuth to --auth-key.
Outcome: Remote desktop connection stable at 100.66.252.84:18889.
```
