# Topology catalog

Combine the patterns in sequence if the problem requires it (e.g. diagnosis → code): the agents
of all sequences count in the total. Agent numbers are for an average problem.

## 1. Research / analysis — "map then merge"

1. **Exploration** (3 to 6 agents): one sub-question per agent; disjoint, together they cover
   the question. Each agent returns sourced `FINDING` objects.
2. **Checking** (1 to 3 agents): on the findings that carry the conclusion, a checker rereads
   the primary source and returns a `VERDICT`.
3. **Synthesis** (1 agent): merge rule in `team.md`, step 6.

**Redundancy**: through diversity of method, not duplication. Critical sub-question: two
agents with different angles (e.g. academic sources vs field feedback). "Completeness critic"
option: a final agent looks for what is missing (unread source, unexplored angle); what it
finds becomes one more wave if the plan's total allows.

**Checking**: a claim is confirmed if its primary source really supports it. Drop those whose
only source is a copy of another.

**Default deliverable**: sourced markdown report, or comparison table.

**Pitfall**: overlapping sub-questions give duplicates that look like independent
confirmation. Deduplicate before counting agreements.

## 2. Audit / review — "multiple angles then counter-expertise"

1. **Review by angle** (3 to 5 agents): one angle per agent (e.g. correctness, security,
   performance, consistency with existing code, test coverage). Large object: cross angle ×
   partition, watching the total. Each agent returns `FINDING` objects with a precise location
   (`file:line`).
2. **Deduplication** (code, no agent): same location + same defect = a single finding.
3. **Counter-expertise** (1 agent per serious finding, plan the upper bound): a checker tasked
   with **refuting**, with an angle distinct from the finder's (e.g. "does the calling context
   prevent it?"). Finding kept if it is not refuted. Minor findings pass without
   counter-expertise, marked "unconfirmed".
4. **Synthesis** (1 agent): ranking by severity.

**Default deliverable**: report of ranked findings, with location and failure scenario.

**Pitfall**: a checker prompted to confirm confirms. Always prompt to refute, with "refuted by
default if uncertain".

## 3. Diagnosis / debug — "competing hypotheses"

0. **Look-around** (you, read-only: `team.md`, step 1): the symptom, the logs, the timeline,
   the scope. List 3 to 5 truly distinct hypotheses.
1. **Investigation** (1 agent per hypothesis): it looks for evidence **for and against** its
   hypothesis, and an experiment that would settle it. Returns a `HYPOTHESIS`.
2. **Cross-refutation** (1 agent per hypothesis still standing): each receives all the wave 1
   conclusions and tries to refute a hypothesis **other than its original one**. It is a
   barrier: in fast mode, a second workflow, after reading the wave 1 results.
3. **Synthesis** (1 agent): surviving hypothesis, evidence, proposed confirmation experiment.

**Redundancy**: organized disagreement. Hypotheses that look alike make the pattern useless:
rephrase them before launching.

**Checking**: reproduction or direct evidence (log, trace, query), never a vote. A hypothesis
confirmed by 3 agents without evidence stays "unconfirmed".

**Default deliverable**: answer in the chat or a short report: cause, evidence, proposed fix.
If the fix is code: it fits in one worker → a sub-agent, no second plan; otherwise, chain into
pattern 4 (new plan, shown to the user: `team.md`, step 4).

**Pitfall**: in production, no agent acts (restart, write, purge). Read-only.

## 4. Code implementation — "contracts, parallel, integration"

For code that can be split into pieces with disjoint files.

1. **Contracts** (1 agent, no isolation, read-only): it sets the interfaces between pieces
   (signatures, types, exchange formats), splits into tasks and gives each a **disjoint** list
   of files. Returns a `CONTRACT_PLAN`. Unavoidable shared file or tight coupling →
   `separable: false` and **the swarm stops**: `STOP` to the roles already launched, and
   propose a single worker (sub-agent) that chains the tasks. Otherwise, show this split to
   the user and go on without waiting, unless the launch is still waiting for their go-ahead
   (`team.md`, step 4).
2. **Implementation** (1 worker per task, `isolation: 'worktree'`): it changes only its files,
   writes or adapts its tests, runs them, **commits** on its branch `swarm-<slug>-<task>` and
   returns a `CHANGESET` (branch, commit, files touched, tests run and result). Needs a file
   outside its list: it stops and reports it in `blocked_on`, without changing it. A
   **tester** (§6) can test for it in the browser.
3. **Integration**: the **merger** (§6), in a worktree too, so as never to move HEAD or touch
   the user's checkout. Returns an `INTEGRATION`.
4. **Checking**: the **checker** (§6) tests the merged result against each task's Eval; if the
   diff is large, 1 reviewer rereads it against the contracts (reduced pattern 2).
5. **Report**: no text to synthesize; you report the state (branch, tests, review, leftovers).

**One PR per worker** (with the user's approval) → merge queue (`flow.md` §1), no merger.
"PRs" in SKILL.md applies; add to the brief the "PR" rule from `brief.md` (sub-agent or
session): the `READY TO MERGE — <URL>` line comes before `DONE`.

**Redundancy**: rare. For a small and critical piece (tricky algorithm): two implementations
with different approaches, settled by the tests and a review.

**Checking**: the tests pass on the integration branch. An agent review never replaces a
failing test.

**Default deliverable**: integration branch + diff + test output. No merge into the main
branch or the user's checkout, no push, no PR without explicit approval.

**Pitfalls**

- A worktree with no change is deleted: an agent that committed nothing leaves nothing to
  integrate; its `CHANGESET` must say so.
- Isolated agents do not see the main checkout's uncommitted files: commit, or pass what they
  need in the prompt.
- A dependency between tasks (B uses A's module) is handled by the contract (interface fixed
  in wave 1), not by making B wait. If B really needs A's code: two waves, or a single task.

## 5. Open goal — "finders, executors, writers"

For an open goal (`team.md`, steps 1 and 2), e.g. a doc "what happens when I do X?". This
pattern **adds to** the chosen family, whose redundancy and checking apply to the
**material**, before the writing. Closed goal: the plan does without it, and says so:
`Topic finders: none — <reason>`.

Each role has its block for the team brief (`team-mode.md`, "Team brief"), whose ending
replaces the "End" part:

```
End: you do NOT finish after a topic. After each topic, wait for the next one.
You finish only when the coordinator sends you "STOP": then write
~/.claude/swarm-runs/<slug>/<name>.json (topics handled, paths, open points, "exchanges"),
then end with a single line: "DONE <path>" or "FAILED <reason>".
```

**Topic finders** (1 to 2, one angle each: e.g. one reads the code, the other the tickets,
Slack and the existing doc).

```
Your role: topic finder. Angle: <code | tickets and Slack | existing doc | …>.
You look for other topics of the same kind as the goal examples. You handle no topic.
Send the coordinator batches of 5 topics at most, message "TOPICS — <n> topics", in the
TOPIC schema (topic, why it fulfills the goal, where you saw it). Before each batch, filter
with the goal and remove the duplicates of ~/.claude/swarm-runs/<slug>/topics.md (which you
read, without writing it). Wait for the coordinator's answer before the next batch. If you
find nothing more: "NOTHING NEW". Progress: accepted topics / budget (<N>).
```

**Executors** (the bulk of the team).

```
Your role: executor. The coordinator sends you one topic at a time (message "TOPIC — <id>").
For each topic: <the family's method: trace in the code, reproduce, source…>.
You do not write: no minutes, no prose. Write the raw material to
~/.claude/swarm-runs/<slug>/material/<id>.json in the MATERIAL schema (facts, evidence,
commands, open points, confidence). Then send "MATERIAL — <id> <path>" to <writer>, and
"FREE — <id>" to the coordinator. Answer the writer's QUESTION messages.
Progress: topics finished / topics received.
```

**Writers** (possible, not required: `team.md`, step 3).

```
Your role: writer, for <executor-1>, <executor-2>. Format of a sheet: <set format>.
For each "MATERIAL — <id>" received: read the material and write the sheet to
~/.claude/swarm-runs/<slug>/deliverable/<id>.md. Invent nothing: a gap or a doubt → QUESTION
to the executor that provided the material. Then "WRITTEN — <id>" to the coordinator.
[writer-1 only] You are the lead writer: at the start, write the common style to
deliverable/STYLE.md; after the STOP, assemble the final deliverable in deliverable/INDEX.md.
Progress: sheets written / material received.
```

**You, the coordinator**: you are the **only one** writing `topics.md` (stable id `s-01`,
`s-02`…, used to deduplicate, not the text; status: proposed, accepted, refused + reason, in
progress <name>, material ready, written). At each `TOPICS`, accept or refuse each topic
according to the goal (outside the goal, even if interesting: refused, with the reason), give
it an id, answer the finder, and give each accepted topic to a free executor (`TOPIC`). You
keep the topic budget.

- All roles start **in wave 1**. Topics travel by message to the agents already running;
  never "one agent per topic".
- Stop when the **topic budget** is reached, or after two `NOTHING NEW`, or on the user's
  stop: `STOP` to each. Finders and executors write their `<name>.json` and finish; writers
  finish their sheets in progress, `writer-1` assembles the deliverable, then they finish.
  `DONE` comes only after a `STOP`.
- Fast mode (`Workflow`) has no open loop: three closed phases (finders up to the budget, then
  executors, then writers).

## 6. Specialized roles — merger, checker, tester, reproducer, watchdog

**A role is taken on a need written in the plan**, not on an automatic threshold, and counts in
the agent total. You do none of these jobs.

| Role | The need that justifies it | Returns |
|---|---|---|
| **Merger** (the "integrator" of §4) | The branches must be tested together before any PR. | `INTEGRATION` |
| **Checker** (in §1 and §2: the "checker" or "counter-expert") | A result to accept that you cannot check yourself by replaying 1 to 3 commands. | `VERDICT` per task |
| **Tester** (as work goes, before the merge) | An interface or flows to click through that the workers cannot test themselves. | `VERDICT` |
| **Reproducer** | A bug to reproduce, or a long run on an app that can be launched locally. Launch it when the need appears (sub-agent), not in advance. | `HYPOTHESIS` (cause and evidence) and, if it fixes, `CHANGESET` |
| **Watchdog** | The only case written in "Thresholds" (SKILL.md). Brief: `sessions-mode.md`, "Watchdog". | `ALERT` messages |

The workers return the family's schema (`FINDING`, `HYPOTHESIS`, `CHANGESET`, `MATERIAL`).

Launch these roles in the same wave as the workers: they wait for their first message.
Exception: the reproducer, launched when a bug arrives. Checker and tester look for what does
not work, not to confirm: a check not replayed is "unchecked", never "OK". Their blocks, for
the team brief:

**Merger**

```
Your role: merger. You work in your own worktree. When the router writes to you
"TO INTEGRATE — <branches>", create (or resume) the branch swarm-<slug>-integration from <starting
branch>, merge each branch by its full name refs/heads/…, one by one. Trivial conflict:
resolve it. Substantive conflict: invent nothing, write to the worker concerned and to the router.
Then run the tests and the lint: <commands>. Push nothing, do not merge into the main
branch. Write the result in the INTEGRATION schema, then "INTEGRATED — <summary>" to the router.
You do not finish after a merge: wait for the next one, until the STOP.
```

**Checker**

```
Your role: checker. When the router writes to you "TO VERIFY — <tasks>", take the integration
branch, launch the app (<command>), and replay each check of each task's Eval
(in ~/.claude/swarm-runs/<slug>/plan.md), for real, in the browser if needed.
Your goal is to find what does not work. A check you could not replay is
"unchecked", never OK. Screenshot for each check, in the exchange folder.
Return a VERDICT per task, then "VERIFIED — <n> OK, <n> KO, <n> unchecked" to the router.
Wait for the next check, until the STOP.
```

**Tester**

```
Your role: tester, for <worker-1>, <worker-2>, <worker-3>. When a worker writes to you
"TO TEST — <task> <branch>", launch the app on its branch (in your worktree), test the
flows and edge cases of its task's Eval in the browser. Answer the worker:
"VERIFIED — <task> OK" or "TO FIX — <task>: <what breaks, how to replay it>".
You do not fix the code yourself.
```

**Reproducer**

```
Your role: reproducer. When someone writes to you "BUG — <symptom>", replay the steps until
you see the bug (browser, commands, tests). Find the cause, with evidence.
- Small and safe fix: do it on your branch swarm-fix-<bug>, add a test that failed
  before, commit, then "FIXED — <bug> <branch>" to the router (the merger will integrate it).
- Otherwise: "BUG — <bug>: cause, evidence, proposed fix" to the router.
Never touch the workers' branches. Bug impossible to reproduce: say so.
Wait for the next bug, until the STOP.
```

**Order at task end (code, with a merger)**: worker "everything is committed" → merger →
checker. A checker failure goes back **to the task's worker** (`TO FIX — <task>`), with the
failing check, then goes through the merger and the checker again. The reproducer's fix is a
branch of its own, which the merger integrates like the others (or a PR of its own).
