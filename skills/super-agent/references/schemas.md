# Shared schemas — the communication contract

Each agent returns an object validated through the `schema` option of `agent()`. These schemas
are the only channel between agents: a wave receives the previous one's outputs in its prompt
(JSON) or via `args`. Workflow script: plain JavaScript, no TypeScript.

Tool constraints: root `{type: 'object', properties: {...}}`, `required` included in
`properties`.

```js
const FINDING = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'short, stable identifier, e.g. "sec-03"' },
          claim: { type: 'string', description: 'the finding, in one sentence' },
          location: { type: 'string', description: 'file:line, URL, table… or "" if not applicable' },
          evidence: { type: 'array', items: { type: 'string' }, description: 'quotes, excerpts, command outputs' },
          sources: { type: 'array', items: { type: 'string' }, description: 'URLs or paths consulted' },
          severity: { type: 'string', enum: ['critical', 'major', 'minor', 'info'] },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['id', 'claim', 'evidence', 'sources', 'confidence'],
      },
    },
    open_questions: { type: 'array', items: { type: 'string' } },
    not_covered: { type: 'array', items: { type: 'string' }, description: 'what this agent could not examine, and why' },
  },
  required: ['findings', 'not_covered'],
}

const VERDICT = {
  type: 'object',
  properties: {
    finding_id: { type: 'string' },
    refuted: { type: 'boolean', description: 'true if the finding is wrong or not shown; true by default if uncertain' },
    reason: { type: 'string' },
    evidence: { type: 'array', items: { type: 'string' } },
  },
  required: ['finding_id', 'refuted', 'reason'],
}

const HYPOTHESIS = {
  type: 'object',
  properties: {
    hypothesis: { type: 'string' },
    status: { type: 'string', enum: ['confirmed', 'plausible', 'weakened', 'refuted'] },
    evidence_for: { type: 'array', items: { type: 'string' } },
    evidence_against: { type: 'array', items: { type: 'string' } },
    deciding_experiment: { type: 'string', description: 'experiment or query that would settle it' },
  },
  required: ['hypothesis', 'status', 'evidence_for', 'evidence_against'],
}

const CONTRACT_PLAN = {
  type: 'object',
  properties: {
    separable: { type: 'boolean', description: 'false if shared files or tight coupling prevent parallel work' },
    reason: { type: 'string' },
    base_branch: { type: 'string' },
    interfaces: { type: 'array', items: { type: 'string' }, description: 'signatures, types and formats fixed between tasks' },
    tasks: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          goal: { type: 'string' },
          files: { type: 'array', items: { type: 'string' }, description: 'owned files, disjoint between tasks' },
          tests: { type: 'string', description: 'targeted test command for this piece' },
        },
        required: ['id', 'goal', 'files'],
      },
    },
    test_command: { type: 'string', description: 'full suite command' },
  },
  required: ['separable', 'reason', 'tasks'],
}

const CHANGESET = {
  type: 'object',
  properties: {
    task_id: { type: 'string' },
    branch: { type: 'string', description: 'worktree branch holding the commit, "" if no change' },
    commit: { type: 'string' },
    files_changed: { type: 'array', items: { type: 'string' } },
    tests_run: { type: 'string', description: 'command run and output excerpt' },
    tests_passed: { type: 'boolean' },
    blocked_on: { type: 'array', items: { type: 'string' }, description: 'out-of-scope files the task would have needed' },
  },
  required: ['task_id', 'branch', 'files_changed', 'tests_passed', 'blocked_on'],
}

const INTEGRATION = {
  type: 'object',
  properties: {
    branch: { type: 'string' },
    merged: { type: 'array', items: { type: 'string' } },
    conflicts: { type: 'array', items: { type: 'string' }, description: 'unresolved conflicts' },
    test_output: { type: 'string', description: 'full suite command and output excerpt' },
    tests_passed: { type: 'boolean' },
  },
  required: ['branch', 'merged', 'conflicts', 'tests_passed'],
}
```

## Open goal (`topologies.md` §5)

These two objects go by message or by file in the exchange folder (sessions and sub-agents
modes), or by `schema` (fast mode).

```js
const TOPIC = {
  type: 'object',
  properties: {
    topics: {
      type: 'array',
      description: 'a batch of 5 topics at most',
      items: {
        type: 'object',
        properties: {
          topic: { type: 'string', description: 'the topic, in the form of the goal examples (e.g. a question)' },
          why: { type: 'string', description: 'in one sentence: why it fulfills the goal' },
          seen_in: { type: 'array', items: { type: 'string' }, description: 'file:line, ticket, message, URL where it appears' },
          close_to: { type: 'string', description: 'id of an accepted topic that resembles it, or ""' },
        },
        required: ['topic', 'why', 'seen_in'],
      },
    },
  },
  required: ['topics'],
}

// An executor's raw material for a writer: facts, not prose.
const MATERIAL = {
  type: 'object',
  properties: {
    id: { type: 'string', description: 'topic id, e.g. "s-04"' },
    topic: { type: 'string' },
    facts: { type: 'array', items: { type: 'string' }, description: 'one line per fact, in the order they happen' },
    evidence: { type: 'array', items: { type: 'string' }, description: 'file:line, excerpts, command outputs, screenshots' },
    commands: { type: 'array', items: { type: 'string' }, description: 'commands or steps to reproduce' },
    open_points: { type: 'array', items: { type: 'string' }, description: 'what remains uncertain or unchecked' },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['id', 'topic', 'facts', 'evidence', 'open_points', 'confidence'],
}
```

The synthesis takes no schema when the deliverable is a text (report, answer): it returns
markdown. Give it a schema when the deliverable is structured (comparison table).
