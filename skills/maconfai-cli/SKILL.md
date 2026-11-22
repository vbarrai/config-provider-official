---
name: maconfai-cli
description: Run the `maconfai` CLI on the user's behalf to manage what a project gets from a distribution repo — install skills, MCP servers and hooks from a GitHub repo or a local folder, show what is installed (`status`), add or remove one item without prompts, check for and apply updates, trust or untrust a config, uninstall, and diagnose refusals. Use whenever the user says "install this skill / MCP / hook", "add X from owner/repo", "remove that MCP", "what did maconfai install here?", "why doesn't update pick up this skill?", "trust this config", or mentions `maconfai`, `npx maconfai` or `ai-lock.json`. To write or publish a skill, MCP server or hook, use `maconfai-author` instead.
---

# maconfai CLI

`maconfai` copies skills, MCP servers and hooks from a **source** (a GitHub repo or a local folder) into the **project in the current directory**, for one or more agents (`claude-code`, `cursor`, `codex`, `open-code`), and records what it wrote in `ai-lock.json`. This skill is about *running* the CLI for the user. Writing the assets a source provides is the job of the `maconfai-author` skill. Reference: https://github.com/vbarrai/maconfai

## 0. First: which maconfai is this?

```bash
npx maconfai --version
npx maconfai --help
```

Commands below are written `maconfai …`; run them as `npx maconfai …` when the binary is not on the PATH.

- **`--help` lists `maconfai status`** → everything below applies.
- **It does not** (true of 0.6.0, the version on npm when this skill was written) → `status`, `add skill|mcp|hook`, `remove`, `trust`, `untrust` and `--force` do not exist: go to [Older maconfai](#older-maconfai).

Decide from the `--help` text, never from an exit code: an unknown command prints `Unknown command: …` and still exits 0.

## 1. Rules

1. **Work in the project, never in the home directory.** `cd` into the project root first. maconfai only writes project files: `ai-lock.json`, `.agents/skills/` and `.agents/hooks/`, the agents' skill folders (`.claude/skills/`, `.cursor/skills/`…), their MCP config (`.mcp.json`, `.cursor/mcp.json`, `.codex/config.toml`, `opencode.json`) and their hook config (`.claude/settings.json`, `.cursor/hooks.json`, `.codex/hooks.json`).
2. **You cannot answer prompts.** `maconfai install <source>` without `-y`, `maconfai install` with no source, and `maconfai check` when it finds updates all ask questions. Run without a terminal they print the question, change nothing and exit 0 (close stdin with `</dev/null` if your shell may be a terminal, so a prompt cannot hang). Use the prompt-free commands of the table; when only the interactive form fits, give the user the exact command to run in their own terminal.
3. **Exit code 0 is not proof.** After every command that writes, run `maconfai status` and read it.
4. **Ask the user before anything that removes or replaces**: any `remove`, any uninstall, `--force`, and `--include-untrusted`. Say what will go or be overwritten, then wait for a yes.
5. **Trust is the user's call.** A trusted config is re-fetched blindly by every `update`, and hooks and MCP servers run commands. Never add `--trusted` or run `trust` on your own initiative.
6. **`-y` is for scripts and CI**, not a shortcut around a question. With no list it installs *everything* the source provides. To add a named item, use `add`.

## 2. Pick the command

| The user wants… | Command | On disk |
| :-- | :-- | :-- |
| See what is installed, and whether the files are there | `maconfai status` | Read-only |
| Add only these skills | `maconfai add skill <source> <name...>` | Adds; removes nothing |
| Add only these MCP servers | `maconfai add mcp <source> <name...>` | Adds; removes nothing |
| Add only these hooks | `maconfai add hook <source> <name...>` | Adds; removes nothing |
| Browse a source and choose | `maconfai install <source>` — interactive: the user runs it | Adds; unchecking an installed item removes it |
| Remove named items | `maconfai remove skill <name...>`, `maconfai remove mcp <name...>`, `maconfai remove hook <name...>` | **Removes** — ask first |
| Uninstall by picking from a list | `maconfai install` (no source) — interactive: the user runs it | **Removes** |
| See which updates exist | `maconfai check` | Lists them, then asks before installing |
| Install the updates | `maconfai update` | Updates trusted configs only |
| Update the non-trusted ones too, once | `maconfai update --include-untrusted` | Updates everything — ask first |
| Let `update` keep a config current | `maconfai trust <name...>` or `maconfai trust --all` | Only `trusted` in `ai-lock.json` |
| Stop `update` from touching a config | `maconfai untrust <name...>` or `maconfai untrust --all` | Only `trusted` in `ai-lock.json` |
| Install a whole source from a script | `maconfai install <source> -y --agents=claude-code` | Adds everything in the source |

**Sources**: `owner/repo`, `owner/repo#branch`, `https://github.com/owner/repo`, `https://github.com/owner/repo/tree/branch`, or a local path. A local path must start with `./`, `../` or `/` — a bare `folder` is read as a GitHub repo. `--branch=<name>` picks a branch.

## 3. What each command really does

- **`status`** — one block per skill, MCP server and hook: source, `trusted`, and per agent `present`, `missing`, `different` or `unknown`. Exits 0 even when files are missing; exits 1 only when `ai-lock.json` is unreadable.
- **`add skill|mcp|hook`** — no prompt; installs the named items and nothing else. Agents default to the ones already in `ai-lock.json`; on a project with no lock yet, pass `--agents=` (for example `--agents=claude-code,cursor`). New items are **not trusted** unless the user asked for `--trusted`. A name the source does not have, or an item that could not be written, is an `Error:` line and exit 1.
- **`remove skill|mcp|hook`** — removes only what `ai-lock.json` records, from every agent it was installed for, and takes no option. A wrong name fails before anything is touched and lists the installed names.
- **`install <source> -y`** — with no list: every skill, MCP server and hook of the source. With `--skills=`, `--mcps=` or `--hooks=`: only what the lists name; a category given no list is left as it is. No option removes anything — only unchecking an item in the interactive list does. Without `--agents=`, a first install targets the agents it detects on the machine, and all four when it detects none: always pass `--agents=` in a script. A name the source does not have is skipped silently (`Nothing to do.`, exit 0), where `add` fails with exit 1: one more reason "add one thing" is `add`, not `install -y`.
- **`check` / `update`** — both skip configs that are not trusted and say so. `check` lists the updates and asks before installing (`check -y` and `--yes` install without asking); `update` installs them directly. `update` also restores a trusted skill whose folder is gone; it repairs nothing else.
- **`trust` / `untrust`** — change only the `trusted` field; nothing is installed or removed. Use a bare name, or `skill:<name>`, `mcp:<name>`, `hook:<name>` when two kinds share a name (the `check` and `update` output prints the exact argument).

## 4. Diagnose

| What you see | What it means | What to do |
| :-- | :-- | :-- |
| `Refusing to overwrite skill files that ai-lock.json does not record` (exit 1) | A skill of that name was written by hand, or by another tool, at the listed path. | Show the user the path. They rename or move it, or agree to lose it: then rerun with `--force`. |
| `You are in your home directory…` (exit 1) | In the home directory, "project files" are the user's own agent configs, so `-y`, `add` and a terminal-less `check` / `update` are refused. | `cd` into the project. If the user really wants it at user level, they run `maconfai install <source>` in their terminal and confirm. |
| `N item(s) blocked (not trusted)` after `check` / `update` (exit 0); `status` shows `trusted: no (blocked from update)` | The config is not trusted, so updates — and the repair of a missing skill folder — skip it. | Ask the user: `maconfai trust <name>` then `maconfai update`, or `maconfai update --include-untrusted` for this one time. |
| `N item(s) could not be checked for updates` … `cannot read owner/repo from GitHub: HTTP 401` / `403` / `404` (exit 1) | GitHub refused the read: bad or expired token, rate limit, or a private repo. It does **not** mean "up to date". The other configs were still updated. | The user fixes `GITHUB_TOKEN` / `GH_TOKEN` or runs `gh auth login`; then rerun. |
| `MCP server "x" is also defined in your <agent> user config (…)` (warning, exit 0) | The server was installed in the project, and a server of the same name exists at user level. Each agent resolves the pair its own way. | Tell the user which file holds the other one; they keep one. Do not edit their user config yourself. |
| `MCP server(s) already in an agent config of this project, not installed by maconfai` (exit 1) | A same-named server was written by hand in the project's MCP config. maconfai never replaces it. | The user removes their entry, or keeps it and drops the install. |
| `No agent recorded in ai-lock.json yet: pass --agents=…` | First `add` in this project. | Rerun with `--agents=` and the agents the user works with. |
| `Not found in the source: x` / `Not in ai-lock.json: x (installed …)` | Wrong name. | Take the name from the source, or from `maconfai status`. |
| `status` says `missing` or `different` | Files or config entries were deleted or changed after the install. | A skill whose folder is gone: `maconfai update` restores it if the skill is trusted (blocked otherwise, see above). Anything else — an MCP server or a hook taken out of the agent's config, a skill folder shown as `different` — is left alone by `update`: run the matching `add` again, with the source `status` shows. For a `different` skill that overwrites the changed folder, so ask first. |
| `Unknown command: …` (exit 0) | This maconfai is older than the command. | See below. |

## Older maconfai

When `--help` has no `status` line (what follows was checked on 0.6.0), prefer a newer version: once it is released, `npx maconfai@latest …`. If that is not possible:

- **No `status`** — read `ai-lock.json` (`skills`, `mcpServers`, `hooks`, each entry with its `source` and `trusted`) and look at the files yourself.
- **No `add` / `remove`** — there is no prompt-free way to touch a single item. `maconfai install <source> -y` makes the project match its lists for that source: `--skills=a` alone also installs *every* MCP server and hook of the source and removes the source's other installed skills. So either the user runs the interactive `maconfai install <source>` (installed items are pre-checked; unchecking removes), or, with their agreement, you pass the complete lists of what must remain: `maconfai install <source> -y --agents=<agents> --skills=<all to keep> --mcps=<all to keep> --hooks=<all to keep>`. An empty list (`--hooks=`) removes that category.
- **No `trust` / `untrust`** — trust is set at install time only: rerun the install with `--trusted`. `maconfai update --include-untrusted` exists.
- **No guards** — a same-named hand-written skill is overwritten without warning, and nothing stops a run in the home directory. Check both yourself before you run anything.
