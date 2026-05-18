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
| [`skill-creator`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator) | Create new skills, modify and improve existing skills, and measure skill performance. Remote reference — fetched from `anthropics/claude-plugins-official`. |

## Available MCP Servers

| Service | Type | Description |
|---------|------|-------------|
| Linear  | SSE  | Project management and issue tracking |

## Available Hooks

| Hook | Event | Description |
|------|-------|-------------|
| `maconfai-update` | Claude Code: `SessionStart` · Cursor: `sessionStart` | When `ai-lock.json` is present at the project root, runs `npx maconfai update` to keep maconfai-managed skills, MCP servers, and hooks in sync with their upstream sources. Non-blocking: any failure (offline, missing `npx`, etc.) is swallowed so the session is never interrupted. |

Hooks are only supported on Claude Code and Cursor (Codex and Open Code have no hook system in maconfai).
