# Sessions mode — what changes

**The default team mode** (`team.md`, step 0). Each agent in
the plan is a **real session** linked to this one, and they talk through `SendMessage`. All of
`team-mode.md` applies here, except its prerequisites, its launch and its degraded mode. Link each
session in your messages (U1); open no split view unless the user asks.

## What to know before launching

- **Number**: "Thresholds" counts sessions like other agents. Launch a wave's sessions
  together.
- **What comes back to you**: at the end of a turn, only the first 400 characters of a
  session's report. The real result goes through its `<name>.json` file.
- **Messages**: they are delivered without approval as long as all sessions are in the same
  permission mode family: **do not change the mode** of the sessions you launch (no
  `permission_mode`: they inherit yours). Otherwise they stay stuck waiting for an approval
  that Desktop cannot show.
- **A wake-up turn may not open a session** (SKILL.md, "Wake-up turn"). For a next wave, **reuse the existing sessions** by message, or launch a sub-agent.
- **Your own name**: the sessions must be able to reach you. Before launching, call
  `ListAgents`: the line that designates you gives your name. Write it in `plan.md` and in
  each brief ("Coordinator" line). Not found: write in the brief "to reach the coordinator,
  run `ListAgents` and take the session titled "<title of this session>"".

## Launch

1. Mark a chapter (`mcp__ccd_session__mark_chapter`) named after the wave, then, for each
   session, a bold line with its title and one sentence on what it will do.
2. Call `mcp__ccd_session__start_session` for the first session, alone. It starts → the
   others, **in the same message**. It is refused → do not try the others: it is the SKILL.md
   fallback ("When you do not delegate"), the whole wave goes to sub-agents, with the same
   team brief (the router there is "main"). The parameters are a session's in the SKILL.md
   table ("The task cycle", step 2), with:
   - `prompt`: the team brief from `team-mode.md`, `<sessions: …>` lines included;
     `background`: the overall problem, the end criterion, the role of each other session;
   - `name`: `<router prefix>-<role>` (`aud-sec`, `bug-cache`). The others address it by this
     name, and its JSON file carries it;
   - `use_worktree: false` for read-only work (research, audit, diagnosis);
     `use_worktree: true` and `branch_name: "swarm-<slug>-<task>"` for a session that changes
     code;
   - `wake_when_done: true`: the app wakes you when the wave has finished. With an open goal,
     an idle session is often just waiting for its next topic: only the `DONE` after your
     `STOP` and its `<name>.json` say it has finished.
3. Tell the user, in one line, that the team is launched and that you will come back with the
   result, and ask the archiving question (SKILL.md, "Router and workers").

**The `SWARM <slug> <name>` marker** is the 2nd line of the brief, exactly (slug and name in
lowercase, digits, `-`, `_` or `.`), repeated by the `echo` command on the 3rd. The swarm-view
mod reads it: it recognizes you as coordinator, and writes each session's activity to
`~/.claude/swarm-runs/<slug>/view/<name>.json`, which your panel reads. Without this marker,
the panel stays empty.

## Watchdog

Only in the case written in "Thresholds" (SKILL.md), so in sessions mode and in a user turn.
Launch it first, with the cheapest model (`model` parameter) and `effort: "low"`. It sees only
sessions, not sub-agents. Its brief: the team brief (`team-mode.md`), with this block:

```
Your role: watchdog. You watch the other sessions' signs of life, not their work.
You fix nothing, you archive nothing, and you write only to the router (<router name>).
State source: `sessions` by default. At startup, run:
  find ~/.claude/swarm-runs/<slug>/view -name '*.json' 2>/dev/null | head -1
A line comes out (the view/ folder already holds a file) → source `view/`. Nothing → `sessions`.
Then run with run_in_background: true:
- source sessions: sleep 600
- source view/:
  D=~/.claude/swarm-runs/<slug>; while sleep 600; do [ -f "$D/STOP" ] && exit 0; for f in "$D"/view/*.json; do [ -e "$f" ] || continue; n=$(basename "$f" .json); [ "$n" = <your name> ] && continue; [ -f "$D/$n.json" ] && continue; [ -n "$(find "$f" -mmin +15)" ] && echo "SILENT $n"; done | grep . && exit 0; done
When the command stops, you are woken up:
- source sessions: call mcp__ccd_session_mgmt__list_sessions {"linked": true}, then, for
  each worker (not you, not the router), look at its state and its latest events
  (list_events or get_session);
  source view/: for each SILENT session, read the end of its view/<name>.json;
- a running session with no activity for 15 minutes, looping (the same action repeated), or
  waiting for more than 15 minutes (an answer, or another session that is waiting for it too)
  → write to the router: "ALERT — <name>: <what you see>", with the evidence in one or two
  lines. A worker that has handed in its report or is waiting its turn in the merge queue is
  not silent;
- then rerun the same command in the background.
Do not send another alert for the same session until it has moved.
End: the STOP file (source view/) only stops your loop; wait for the router's "STOP".
On "STOP" from the router: rerun nothing, stop the running command (TaskStop), write
<name>.json if there is an exchange folder, then end with a short report (alerts sent).
```

An `ALERT`: look at the session (or ask it where it stands), then unblock it, nudge it with a
message, or tell the user.

## After the wave, and at the end of the run

- Before reading the `<name>.json` files, check with `mcp__ccd_session_mgmt__list_sessions`
  (`linked: true`) that each session is idle.
- End of the run: create the file `~/.claude/swarm-runs/<slug>/STOP` (it stops a watchdog's
  loop), send `STOP` to all, wait for their `DONE`. Then apply the SKILL.md archiving rule
  ("Router and workers"): the work sessions, then the watchdog. It also applies during the
  run, for a session that has nothing left to do.
