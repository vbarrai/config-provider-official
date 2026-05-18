---
name: maconfai-author
description: Author and publish skills, MCP servers, and hooks in a maconfai-compatible distribution repo (like vbarrai/config-provider-official) so they can be installed with `npx maconfai install owner/repo`. Use when the user wants to add a new skill/MCP/hook to a distribution repo, create a new distribution repo from scratch, or restructure an existing repo to be maconfai-discoverable.
---

# maconfai distribution repo author

A maconfai distribution repo exposes three asset types — **skills**, **MCP servers**, **hooks** — laid out in conventional directories that `maconfai install` auto-discovers. Reference: https://github.com/vbarrai/maconfai

## When to use this skill

- Adding a new skill, MCP, or hook to an existing distribution repo
- Bootstrapping a new distribution repo
- Converting a one-off skill/MCP/hook into a publishable maconfai asset
- Building a **registry repo** that re-exports skills hosted elsewhere

## Repo layout

```
<repo-root>/
├── README.md
├── skills/
│   └── <skill-name>/
│       └── SKILL.md
├── mcps/
│   └── <server-name>/
│       └── mcp.json
└── hooks/
    └── <hook-name>/
        ├── hooks.json
        └── <companion-files>   # optional scripts referenced by hooks.json
```

All three directories are optional — install only what the repo provides. The single-skill shortcut (`SKILL.md` at the repo root) also works, but multi-asset repos must use the `skills/` directory layout.

## 1. Skills

A skill is a Markdown file with YAML frontmatter that gets loaded into an agent's skill set.

**Path:** `skills/<skill-name>/SKILL.md`

**Required frontmatter:**

```markdown
---
name: <skill-name>
description: <one-sentence trigger description — when should the agent invoke this skill?>
---

<skill body: instructions, examples, constraints>
```

**Authoring rules:**
- `name` MUST match the directory name (kebab-case).
- `description` is the trigger — write it so an agent can decide whether the skill applies to the user's request. Lead with the use case, not the implementation.
- Keep the body focused: one skill = one capability. Split unrelated capabilities into separate skills.
- Companion files (scripts, templates, examples) can live alongside `SKILL.md` in the same directory and be referenced by relative path.

## 2. MCP servers

An MCP server config is a single JSON file declaring how to launch or connect to an MCP endpoint.

**Path:** `mcps/<server-name>/mcp.json`

**Local command server:**

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "npx",
      "args": ["-y", "some-mcp-package"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

**Remote SSE / HTTP server:**

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://example.com/mcp"]
    }
  }
}
```

**Authoring rules:**
- The key under `mcpServers` SHOULD match `<server-name>` (the directory name).
- Use `${VAR}` for env interpolation — maconfai translates syntax per agent automatically (Cursor uses `${env:VAR}`).
- Always author in the canonical `mcpServers` / `env` format. maconfai converts to Codex (`config.toml`) and Open Code (`mcp` + `environment`) on install.

## 3. Hooks

A hook declares an event handler — a command or script invoked on agent lifecycle events (session start, pre/post tool, file edit, etc.).

**Path:** `hooks/<hook-name>/hooks.json` (+ optional companion files in the same directory)

**Structure:**

```json
{
  "hooks": {
    "<hook-name>": {
      "description": "<what this hook does and when it fires>",
      "claude-code": {
        "<EventName>": [
          {
            "matcher": "<optional matcher, e.g. tool name>",
            "hooks": [
              { "type": "command", "command": ".agents/hooks/<hook-name>/<script>" }
            ]
          }
        ]
      },
      "cursor": {
        "<eventName>": [
          {
            "hooks": [
              { "type": "command", "command": ".agents/hooks/<hook-name>/<script>" }
            ]
          }
        ]
      }
    }
  }
}
```

**Companion files** (shell scripts, executables) are copied to `.agents/hooks/<hook-name>/` on install — reference them by that path in `command`.

**Common events:**

| Intent                     | Claude Code      | Cursor                |
| :------------------------- | :--------------- | :-------------------- |
| Session start              | `SessionStart`   | `sessionStart`        |
| Before any tool call       | `PreToolUse`     | `preToolUse`          |
| After tool call            | `PostToolUse`    | `postToolUse`         |
| Before file write/edit     | `PreToolUse` (matcher `Edit\|Write`) | `afterFileEdit` (post-only) |
| Before shell execution     | `PreToolUse` (matcher `Bash`) | `beforeShellExecution` |

Full Cursor event list: https://cursor.com/docs/hooks. Claude Code: https://docs.anthropic.com/en/docs/claude-code/hooks

**Authoring rules:**
- Hooks are **agent-specific** — declare each agent's event explicitly. Codex and Open Code do not support hooks (maconfai silently skips them).
- Use relative paths starting from project root: `.agents/hooks/<hook-name>/<file>`.
- Companion scripts MUST be executable (`chmod +x`) before commit. Use POSIX `sh` for portability unless you have a reason to target bash.
- Make hooks **non-blocking by default**: swallow errors with `|| true` and `exit 0` when the failure shouldn't break the agent session. Only fail loudly when the hook's purpose is to gate an action (e.g. block dangerous commands).
- Detect project root via `$CLAUDE_PROJECT_DIR` first, then `$PWD`, then walk up from `$0`.

## 4. Remote skill references (registry repos)

A distribution repo can act as a **registry** that points to skills hosted elsewhere, without copying them.

**Path:** `skills/<name>` (extensionless file, not a directory)

**Plain string form:**

```
anthropics/claude-plugins-official/plugins/skill-creator
```

**YAML form:**

```yaml
source: anthropics/claude-plugins-official/plugins/skill-creator
include: [skills, mcps, hooks]
prefix: official
```

`prefix` rewrites the installed skill name (`skill-creator` → `official-skill-creator`), MCP keys, and hook group names. `ai-lock.json` tracks the **remote** source, so `maconfai check` detects updates from the origin repo, not the registry.

## Authoring workflow

1. **Decide the asset type** — skill (prompt logic), MCP (external tool), or hook (event handler).
2. **Pick a kebab-case name** — used as the directory name AND inside the file (`name:` frontmatter, `mcpServers` key, hook group key).
3. **Create the file at the canonical path** (see layouts above).
4. **For hooks with companion files**: `chmod +x` and verify the path `.agents/hooks/<name>/<file>` is what the JSON references.
5. **Update the README** — list the new asset in the appropriate table so consumers can discover it.
6. **Test locally** before publishing:
   ```bash
   cd /tmp/test-project
   npx maconfai install /path/to/your/repo -y
   cat ai-lock.json   # verify the asset was picked up
   ```
7. **Commit and push.** Consumers pull updates via `npx maconfai update`.

## Common pitfalls

- **Name mismatch** — directory name, frontmatter `name`, and the JSON key (for MCPs/hooks) must all agree.
- **Hook script not executable** — commit with `chmod +x`; otherwise it silently fails on install.
- **Wrong MCP env syntax** — always author with bare `${VAR}`. Don't hand-write `${env:VAR}`; maconfai produces that for Cursor.
- **Targeting unsupported agents for hooks** — Codex and Open Code have no hook system; only `claude-code` and `cursor` keys are honored.
- **Blocking hooks at session start** — `npx`-based hooks can be slow on first run; default to non-blocking (`|| true`).
