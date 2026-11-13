# config-provider-official

A centralized repository of MCP (Model Context Protocol) server configurations and hooks for AI coding agents (Claude Code, Cursor, Codex, Open Code), distributed via [maconfai](https://github.com/vbarrai/maconfai).

## Install

```bash
npx maconfai install vbarrai/config-provider-official
```

## Available Skills

| Skill | Description |
|-------|-------------|
| `maconfai-author` | Author and publish skills, MCP servers, and hooks in a maconfai-compatible distribution repo. Covers file layout, naming rules, hook event mappings (Claude Code ↔ Cursor), MCP env-syntax translation, and registry-style remote skill references. |
| `super-agent` | Default strategy for any "do something" request: the agent becomes a router that splits the work into ordered tasks (What + Eval), hands them to worker sessions, checks each result against its Eval, and only comes back to the user for decisions. Written in French; relies on Claude Code desktop session tools. |
| [`skill-creator`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator) | Create new skills, modify and improve existing skills, and measure skill performance. Remote reference — fetched from `anthropics/claude-plugins-official`. |

## Available MCP Servers

| Service | Type | Description |
|---------|------|-------------|
| Linear  | SSE  | Project management and issue tracking |
| chrome-devtools | stdio | Browser automation, debugging, and performance/accessibility auditing via Chrome DevTools (`npx chrome-devtools-mcp@latest`) |

## Available Hooks

| Hook | Event | Description |
|------|-------|-------------|
| `maconfai-update` | Claude Code: `SessionStart` · Cursor: `sessionStart` | When `ai-lock.json` is present at the project root, runs `npx maconfai update` to keep maconfai-managed skills, MCP servers, and hooks in sync with their upstream sources. Non-blocking: any failure (offline, missing `npx`, etc.) is swallowed so the session is never interrupted. |
| `super-agent-reminder` | Claude Code: `SessionStart` · Cursor: `sessionStart` | At session start, adds a reminder to the agent's context: for the whole session, invoke the `super-agent` skill whenever a message asks it to do something (exceptions: plain questions, worker sessions, "do it here"). Requires `python3`. |

Hooks are only supported on Claude Code and Cursor (Codex and Open Code have no hook system in maconfai).
