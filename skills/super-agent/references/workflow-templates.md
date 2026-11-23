# Workflow script skeletons

One skeleton per pattern in `topologies.md`: a starting point. Adjust the number of agents to
the plan **shown to the user**, and paste the schemas from `schemas.md` at the top.

API reminders (details in the `workflow-authoring` skill):

- `meta` is a pure literal; its `phases` repeat exactly the `phase()` titles.
- Plain JavaScript; no `Date.now()`, `Math.random()`, `new Date()`: pass what varies via `args`.
- `agent()` returns `null` on failure: filter with `.filter(Boolean)` and **count** the gaps.
- `pipeline()` by default; a `parallel()` barrier only when a step needs **all** the previous
  results (deduplication, synthesis, cross-refutation).
- `log()` everything that is dropped or truncated.
- Each `agent()` prompt starts with `WORKER <id>`, like every worker brief in the skill, and says not
  to invoke the super-agent skill: the skeletons pass their prompts through the
  `worker(id, prompt)` wrapper, to paste at the top of the script:
  ``const worker = (id, p) => `WORKER ${id}\nYou are a worker: launch no agent and do not invoke the super-agent skill.\n${p}`;``

`args` holds the plan shown (tasks, angles, hypotheses…): the script reinvents nothing.

---

## 1. Research / analysis

```js
export const meta = {
  name: 'swarm-research',
  description: 'super-agent: parallel exploration per sub-question, checking of key findings, synthesis',
  phases: [{ title: 'Explore' }, { title: 'Check' }, { title: 'Synthesize' }],
}
// args = { question, criterion, subquestions: [{ id, prompt, angle }], verify_max, deliverable }

const explored = await pipeline(
  args.subquestions,
  sq => agent(
    worker(`explorer:${sq.id}`, `Overall question: ${args.question}\n` +
    `Your sub-question: ${sq.prompt}\nRequired angle: ${sq.angle}\n` +
    `Return sourced findings. Cite the primary source, not a copy. ` +
    `List in not_covered what you could not examine.`),
    { label: `explorer:${sq.id}`, phase: 'Explore', schema: FINDING },
  ),
)
const ok = explored.filter(Boolean)
if (ok.length < args.subquestions.length) log(`${args.subquestions.length - ok.length} exploration(s) failed`)

// Justified barrier: the key findings are chosen among all of them.
const all = ok.flatMap(r => r.findings)
const key = all.filter(f => f.confidence !== 'high' || f.severity === 'critical').slice(0, args.verify_max)
if (all.length > key.length) log(`${all.length - key.length} finding(s) not checked (over budget or high confidence)`)

const verdicts = await parallel(key.map(f => () => agent(
  worker(`verifier:${f.id}`, `Try to REFUTE this finding by rereading its primary sources.\n${JSON.stringify(f)}\n` +
  `refuted=true if the source does not support it or if you cannot confirm it.`),
  { label: `verifier:${f.id}`, phase: 'Check', schema: VERDICT },
)))

phase('Synthesize')
const report = await agent(
  worker('synthesis', `Synthesize to answer: ${args.question} (end criterion: ${args.criterion}).\n` +
  `Format: ${args.deliverable}.\nMerge rule: agreement → kept; disagreement → lay out both ` +
  `positions; isolated unchecked → "unconfirmed"; refuted → appendix; list the gaps.\n` +
  `Findings: ${JSON.stringify(ok)}\nVerdicts: ${JSON.stringify(verdicts.filter(Boolean))}`),
  { label: 'synthesis', phase: 'Synthesize' },
)
return { report, explored: ok, verdicts, failed: args.subquestions.length - ok.length }
```

---

## 2. Audit / review

```js
export const meta = {
  name: 'swarm-audit',
  description: 'super-agent: review by angles, deduplication, counter-expertise of serious findings, synthesis',
  phases: [{ title: 'Review' }, { title: 'Counter-expertise' }, { title: 'Synthesis' }],
}
// args = { target, context, lenses: [{ id, prompt }], counter_lenses: [string], verify_max }

const reviews = await parallel(args.lenses.map(l => () => agent(
  worker(`review:${l.id}`, `Object to audit: ${args.target}\nContext: ${args.context}\n` +
  `Your angle, and only that one: ${l.prompt}\n` +
  `Each finding has a precise location and evidence.`),
  { label: `review:${l.id}`, phase: 'Review', schema: FINDING },
)))
// Justified barrier: deduplication over the whole set.
const seen = new Map()
for (const f of reviews.filter(Boolean).flatMap(r => r.findings)) {
  const k = `${f.location}|${f.claim.slice(0, 60)}`
  if (!seen.has(k)) seen.set(k, f)
}
const unique = [...seen.values()]
const grave = unique.filter(f => f.severity === 'critical' || f.severity === 'major').slice(0, args.verify_max)
log(`${unique.length} unique findings, ${grave.length} in counter-expertise`)

const verified = await pipeline(grave, (f, _, i) => agent(
  worker(`counter:${f.id}`, `Try to REFUTE this finding from the angle: ${args.counter_lenses[i % args.counter_lenses.length]}.\n` +
  `${JSON.stringify(f)}\nrefuted=true by default if uncertain.`),
  { label: `counter:${f.id}`, phase: 'Counter-expertise', schema: VERDICT },
).then(v => ({ ...f, verdict: v })))

phase('Synthesis')
const report = await agent(
  worker('synthesis', `Audit report of ${args.target}, ranked by severity. Refuted findings in an appendix, ` +
  `minor findings marked "unconfirmed".\nChecked findings: ${JSON.stringify(verified.filter(Boolean))}\n` +
  `Other findings: ${JSON.stringify(unique.filter(f => !grave.includes(f)))}`),
  { label: 'synthesis', phase: 'Synthesis' },
)
return { report, verified, unique }
```

---

## 3. Diagnosis / debug (two workflows)

Workflow A, the investigation:

```js
export const meta = {
  name: 'swarm-diagnose-investigate',
  description: 'super-agent: one investigation per hypothesis, evidence for and against',
  phases: [{ title: 'Investigation' }],
}
// args = { symptom, context, hypotheses: [{ id, text }] }
const results = await pipeline(args.hypotheses, h => agent(
  worker(`investigate:${h.id}`, `Symptom: ${args.symptom}\nContext: ${args.context}\nYour hypothesis: ${h.text}\n` +
  `Look for evidence FOR and AGAINST, with the same rigor. READ-ONLY: no action ` +
  `that changes a system. Propose the experiment that would settle it.`),
  { label: `investigate:${h.id}`, phase: 'Investigation', schema: HYPOTHESIS },
))
return results
```

Read the results, drop the hypotheses refuted with evidence, then launch workflow B:

```js
export const meta = {
  name: 'swarm-diagnose-refutation',
  description: 'super-agent: cross-refutation of surviving hypotheses, synthesis',
  phases: [{ title: 'Refutation' }, { title: 'Synthesis' }],
}
// args = { symptom, survivors: [HYPOTHESIS], all_results: [HYPOTHESIS] }
const n = args.survivors.length
// With a single survivor, a fresh refuter attacks it; with zero, nothing to refute.
if (!n) return null
const cross = await parallel(args.survivors.map((h, i) => () => agent(
  // Each refuter targets a hypothesis it did not originally investigate.
  worker(`refute:${(i + 1) % n}`, `Symptom: ${args.symptom}\nAll conclusions: ${JSON.stringify(args.all_results)}\n` +
  `Your target: "${args.survivors[(i + 1) % n].hypothesis}". Try to REFUTE it with direct ` +
  `evidence (log, trace, query, reproduction). Read-only.`),
  { label: `refute:${(i + 1) % n}`, phase: 'Refutation', schema: HYPOTHESIS },
)))
phase('Synthesis')
return await agent(
  worker('synthesis', `Most likely cause, evidence, confirmation experiment and proposed fix. ` +
  `A hypothesis without direct evidence stays "unconfirmed".\n` +
  `Investigations: ${JSON.stringify(args.all_results)}\nRefutations: ${JSON.stringify(cross.filter(Boolean))}`),
  { label: 'synthesis', phase: 'Synthesis' },
)
```

---

## 4. Code implementation (contracts first, then an execution workflow)

Wave 1, outside a workflow or in a one-agent workflow: a read-only `CONTRACT_PLAN` agent.
If `separable === false`, stop the swarm. Otherwise present the split to the user, then:

```js
export const meta = {
  name: 'swarm-code',
  description: 'super-agent: parallel implementation in worktrees, integration, tests, review',
  phases: [{ title: 'Implement' }, { title: 'Integrate' }, { title: 'Review' }],
}
// args = { slug, need, plan: CONTRACT_PLAN, integration_branch }  — integration_branch: `swarm-<slug>-integration`

const changes = await pipeline(args.plan.tasks, t => agent(
  worker(`impl:${t.id}`, `Overall need: ${args.need}\nFixed interfaces (to follow strictly): ${JSON.stringify(args.plan.interfaces)}\n` +
  `Your task ${t.id}: ${t.goal}\nYou change ONLY these files: ${t.files.join(', ')}.\n` +
  `If you need another file, stop and list it in blocked_on without changing it.\n` +
  `Write or adapt the tests of your piece, run: ${t.tests || args.plan.test_command}.\n` +
  `Create a branch swarm-${args.slug}-${t.id}, commit your work on it, and return branch + commit.`),
  { label: `impl:${t.id}`, phase: 'Implement', schema: CHANGESET, isolation: 'worktree' },
))
const done = changes.filter(Boolean)
const empty = done.filter(c => !c.branch)
const blocked = done.filter(c => c.blocked_on.length)
if (empty.length) log(`${empty.length} task(s) with no change: ${empty.map(c => c.task_id).join(', ')}`)
if (blocked.length) log(`${blocked.length} task(s) blocked on out-of-scope files`)
const red = done.filter(c => c.branch && !c.tests_passed)
if (red.length) log(`Red tests before integration: ${red.map(c => `${c.task_id} (${c.tests_run})`).join('; ')}`)

phase('Integrate')
// In a worktree too: integration must never move HEAD or touch the user's checkout.
const integ = await agent(
  worker('integration', `Create the branch ${args.integration_branch} from ${args.plan.base_branch}, ` +
  `then merge one by one: ${done.filter(c => c.branch).map(c => c.branch).join(', ')}.\n` +
  `Resolve only trivial conflicts; list the others. Run ${args.plan.test_command} and the lint. ` +
  `Push nothing, do not merge into ${args.plan.base_branch}.`),
  { label: 'integration', phase: 'Integrate', schema: INTEGRATION, isolation: 'worktree' },
)

phase('Review')
const review = await agent(
  worker('review', `Review of the diff ${args.plan.base_branch}...${integ?.branch} against these interfaces: ` +
  `${JSON.stringify(args.plan.interfaces)}. Look for correctness defects and deviations from the contract.`),
  { label: 'review', phase: 'Review', schema: FINDING },
)
return { changes: done, integration: integ, review, missing: args.plan.tasks.length - done.length }
```

Blocked task or red tests: do not relaunch in a loop. Report, and propose either a fix wave
(within the plan's total and the approval threshold in "Thresholds"), or a takeover by a
single worker that chains the tasks.
