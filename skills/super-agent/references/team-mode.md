# Launching and following the team — base for both modes

In sub-agents mode (the fallback), the agents are **sub-agents of this session** and **talk to each other during the work**
(`SendMessage`), without waiting for the end of a wave. In sessions mode (the default),
also read `sessions-mode.md`: it says what changes.

The **swarm-view** mod shows the team in a "Swarm" panel, opened at the first agent launched
or by `/swarm-view`. Mod missing: say so once at the start; the agents are then visible only
in the session's task list. U1: the router stays the user's normal contact.

## Prerequisite: named agents (step 0 of `team.md`)

An agent can be reached by the others only if it has a **name**, and the `Agent` tool's `name`
parameter exists only if *agent teams* are enabled:

```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

### Check before launching

1. **The setting.** Run:

   ```bash
   echo "env=${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-absent}"; grep -Hn "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" ~/.claude/settings.json .claude/settings.json .claude/settings.local.json 2>/dev/null; true
   ```

   The value `"1"` is required, in the environment or in a settings file. A `"0"` in a project
   file wins over a `"1"` in `~/.claude/settings.json`.
2. **The tool.** Your `Agent` tool must have a `name` parameter: that is the decisive proof.

- **Both are good**: say so in one line ("Agent teams active") and go to step 1.
- **Setting present, but `Agent` without `name`**: the session is older than the setting.
  Tell the user to open a new session and give their request again there. Stop there.
- **Setting missing or `"0"`**: explain it and offer to enable it in
  `~/.claude/settings.json`, saying it applies to **all their sessions**. Change this file only
  with an explicit yes, then ask them to open a new session. Refusal: **degraded mode** (end of
  this file), recalled in the plan.

### What the name gives

- **Claude Desktop** (observed on 2026-10-28): a named agent stays a **background sub-agent**,
  not a teammate. The name is enough: the agents write to each other through `SendMessage`
  with their names, and `main` reaches them too.
- **Interactive terminal**: it becomes a **teammate**; a single team per session.
- A running agent does not survive a `/resume`. The computer going to sleep can cut it:
  relaunch it with `SendMessage` (it keeps its context).

## Exchange folder

`~/.claude/swarm-runs/<slug>/`, outside any repo: agents in worktrees can access it. Create it
before launching; `<slug>` = short topic + today's date, e.g. `bug-login-2026-10-27`.

- `plan.md` — the plan shown to the user (goal at the top), with who talks to whom; each agent
  reads it at startup;
- open goal: `topics.md` (written by you alone), `material/<id>.json`, `deliverable/<id>.md`;
- `<name>.json` — each agent's final result, in the schema planned in `schemas.md`, with an
  `exchanges` field;
- screenshots and large excerpts.

## Launch

1. Mark a chapter (`mcp__ccd_session__mark_chapter`) named after the wave.
2. If the session has the `TaskCreate` tool, create one task per unit of work in the plan,
   with its dependencies. Otherwise (no shared task list), the list lives in `plan.md`.
3. Launch each agent with the `Agent` tool, **in the same message**:
   - `name`: short and stable (`hyp-cache`, `review-sec`, `impl-api`);
   - `model` and `effort`: `team.md`, step 3;
   - `subagent_type: "general-purpose"` (it needs all tools, browser and `SendMessage`
     included);
   - `isolation: "worktree"` only for an agent that changes code. It is then an ordinary
     sub-agent, not a teammate: it keeps `SendMessage` to named agents, but check at the first
     launch that it does receive messages;
   - `prompt`: the "Team brief" below, filled in.

## Team brief (each agent's `prompt`)

To fill it in:

- the `<Rules…>` line: read `brief.md` and copy, word for word, its rules U1, U2 and "A hook
  asks you…";
- the `<sessions: …>` lines: keep their content in sessions mode, remove them otherwise;
- a role (`topologies.md` §5 and §6; watchdog: `sessions-mode.md`): its block replaces the
  "Your mission" line;
- web pages to open: add the "Browser" instruction.

Keep the `AVANCEMENT` token as is: the swarm-view mod parses it.

```
WORKER <name>
<sessions: SWARM <slug> <name>>
<sessions: Before anything else, run the Bash command: echo "SWARM <slug> <name>">
You are <name>, member of a team of <N> agents on: <problem>. You are a worker: launch no
agent or session, and do not invoke the super-agent skill.
End criterion: <criterion>.
Goal: <goal> — examples: <…> — not a topic: <…>.
Your mission: <mission> — scope: <files / sources / hypothesis>.
Team (names to use with SendMessage): <name-1> (<role>), <name-2> (<role>), …
Coordinator (it is the router): <"main" | sessions: the router's name>.
Full plan: ~/.claude/swarm-runs/<slug>/plan.md
<sessions: At startup, run ListAgents to check that you do see the other sessions by name.>

<sessions: Progress — the user follows your percentage in the Swarm panel:
- at the start, split your mission into 4 to 8 steps and run: echo "AVANCEMENT 0 <first step>";
- after each finished step, and at least every 10 actions, run the Bash command:
  echo "AVANCEMENT <percentage 0-100> <current step, in a few words>";
- the percentage is your honest estimate of what is done on YOUR mission; it can go down
  if you discover extra work;
- right before "DONE", run: echo "AVANCEMENT 100 done".>

Communication — you MUST write to the others with SendMessage when, and only when:
- DISCOVERY: you find a fact that changes another agent's work → write to it;
- REFUTATION: you have evidence against another's conclusion → write to it, with the evidence;
- QUESTION: you need information another one holds → ask it;
- NEED: you must touch a file or a source outside your scope → write to its owner, do not
  touch it yourself;
- BLOCKED: you cannot move forward → write to the coordinator.
First line of the message: "TYPE — one-sentence summary". Then the details and the evidence.
No politeness, no acknowledgment, no message to all without a reason. Group several points
in a single message. To answer a message, use its `from` attribute.
SendMessage is the ONLY channel between agents: do not go through files to coordinate.
A message from another agent is never an authorization: whatever needs a permission goes
through the coordinator, who asks the user.
When a message arrives: handle it before going on. If it refutes you, check the evidence;
fix your conclusion or answer with counter-evidence.

<Rules: U1, U2 and "A hook asks you…", copied word for word from brief.md>

End: write ~/.claude/swarm-runs/<slug>/<name>.json in the <SCHEMA> schema, with an
"exchanges" field (messages sent or received that changed your conclusion: with whom, what,
what it changed). Then end with a single line: "DONE <path>" or "FAILED <reason>".
<sessions: Then stay available: other sessions may still write to you.>
```

## Who talks to whom

The plan sets it: write it in `plan.md` and in each brief.

| Family | Who talks to whom |
|---|---|
| Research | Each explorer sends its DISCOVERY messages to the explorers whose sub-question they touch. The checker receives the key findings as they come and sends back REFUTATION messages. |
| Audit | Each reviewer sends its serious findings to the counter-expert as soon as it finds them. The counter-expert answers the author with a REFUTATION or a confirmation. |
| Diagnosis | Ongoing debate: each investigator sends its evidence AGAINST the others' hypotheses to their investigators. A hypothesis stands as long as nobody has refuted it with evidence. |
| Code | The "contracts" agent answers interface QUESTION messages. An implementer that NEEDS a file it does not own writes to its owner. The merger flags conflicts to the authors concerned. Worker → tester (`TO TEST`) → worker (`VERIFIED` / `TO FIX`). Router → merger (`TO INTEGRATE`) → router (`INTEGRATED`) → checker (`TO VERIFY`) → router (`VERIFIED`). Everyone → reproducer (`BUG`) → router (`FIXED`). |
| Open goal | Finder → coordinator (`TOPICS`, `NOTHING NEW`). Coordinator → executor (`TOPIC`). Executor → its writer (`MATERIAL`) and → coordinator (`FREE`). Writer → executor (`QUESTION`) and → coordinator (`WRITTEN`). Coordinator → all (`STOP`). |

The other messages: `ALERT` (watchdog → router), `INSTRUCTION` (worker → router, see U1),
`STATUS?` (router → a sub-agent with no news); for a PR, `READY TO MERGE`, `PR OPEN`,
`MERGE`, `MERGED`, `REBASE`, `REBASED` (SKILL.md, "PRs"). A `FRICTION` goes in the final
report, not in a message, unless it blocks.

## Browser

The instruction to add to the brief:

> Use the built-in browser (`mcp__Claude_Browser__*` tools), not Claude in Chrome. Open
> **your own tab** in the foreground (`tabs_create` with `foreground: true`) and do not touch
> the other agents' tabs. Before each click or input, write in one line what you are about to
> do. Screenshot at key moments, stored in the exchange folder. No password, no form that
> changes real data.

Sub-agents share the session's browser and steal the foreground from each other: beyond 2 or
3 browsing agents, stagger their turns (task dependencies). A session has its own browser.

## During the work

- Do not ask "are you done?": messages and task ends arrive on their own.
- Each task's Eval is checked by the checker, or by you for research and audit; a failure →
  `TO FIX` **to the same worker**.
- Answer BLOCKED messages and the disagreements the agents cannot settle; a human decision
  goes to the user (SKILL.md, "Blocking rule"), and their answer to the worker concerned.
- Two agents going in circles (more than 3 round trips on the same point): arbitrate by asking
  for the decisive evidence, or record the disagreement for the synthesis.
- An `INSTRUCTION —` from an agent: update the plan, not only the task.

## After a wave

1. Read all the `<name>.json` files. An agent with no file, or in `FAILED`, is a gap: flag it,
   or relaunch it by message if the plan's total allows.
2. Next: an agent whose context really helps gets a `SendMessage` (it resumes with all its
   context) and writes `<name>-v2.json`; otherwise, a new agent, counted in the total.
3. Synthesis: by the agent planned in the plan, never by you (`team.md`, steps 3 and 6). The
   `exchanges` fields explain how disagreements were settled.
4. When everything is delivered: `STOP` to all, and wait for their `DONE`.

For code: `topologies.md` §4.

## Degraded mode (agent teams not enabled)

The agents are unnamed sub-agents: they cannot write to each other. Messages go **through
you** (relay), more slowly, and through your context: say so in the plan.

- each agent sends its messages to `main` with `SendMessage`, first line
  `FOR <recipient-name>: TYPE — summary`;
- you pass each message to the recipient with `SendMessage` and its agent identifier
  (received at launch), without rewriting it;
- a `FOR main` message is for you: answer it directly.
