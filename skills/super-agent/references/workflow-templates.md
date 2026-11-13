# Squelettes de scripts Workflow

Un squelette par patron de `topologies.md`. Ce sont des points de départ : remplace les `<…>`,
ajuste le nombre d'agents au plan **validé**, et colle les schémas de `schemas.md` en tête.

Rappels de l'API (détail dans le skill `workflow-authoring`) :

- `meta` est un littéral pur ; ses `phases` reprennent exactement les titres de `phase()`.
- JavaScript pur ; pas de `Date.now()`, `Math.random()`, `new Date()` : passe ce qui varie via `args`.
- `agent()` rend `null` en cas d'échec : filtre avec `.filter(Boolean)` et **compte** les trous.
- `pipeline()` par défaut ; `parallel()` seulement quand une étape a besoin de tous les résultats.
- `log()` tout ce qui est écarté ou tronqué.

Le premier argument `args` de chaque template contient le plan validé (tâches, angles,
hypothèses…), pour que le script ne réinvente rien.

---

## 1. Recherche / analyse

```js
export const meta = {
  name: 'swarm-research',
  description: 'super-agent : exploration parallèle par sous-question, vérification des constats clés, synthèse',
  phases: [{ title: 'Explorer' }, { title: 'Vérifier' }, { title: 'Synthétiser' }],
}
// args = { question, criterion, subquestions: [{ id, prompt, angle }], verify_max, deliverable }

const explored = await pipeline(
  args.subquestions,
  sq => agent(
    `Question générale : ${args.question}\n` +
    `Ta sous-question : ${sq.prompt}\nAngle imposé : ${sq.angle}\n` +
    `Rends des constats sourcés. Cite la source primaire, pas une reprise. ` +
    `Liste dans not_covered ce que tu n'as pas pu examiner.`,
    { label: `explorer:${sq.id}`, phase: 'Explorer', schema: FINDING },
  ),
)
const ok = explored.filter(Boolean)
if (ok.length < args.subquestions.length) log(`${args.subquestions.length - ok.length} exploration(s) en échec`)

// Barrière justifiée : on choisit les constats clés parmi tous.
const all = ok.flatMap(r => r.findings)
const key = all.filter(f => f.confidence !== 'haute' || f.severity === 'critique').slice(0, args.verify_max)
if (all.length > key.length) log(`${all.length - key.length} constat(s) non vérifiés (hors budget ou confiance haute)`)

const verdicts = await parallel(key.map(f => () => agent(
  `Essaie de RÉFUTER ce constat en relisant ses sources primaires.\n${JSON.stringify(f)}\n` +
  `refuted=true si la source ne le soutient pas ou si tu ne peux pas le confirmer.`,
  { label: `verifier:${f.id}`, phase: 'Vérifier', schema: VERDICT },
)))

phase('Synthétiser')
const report = await agent(
  `Synthétise pour répondre à : ${args.question} (critère de fin : ${args.criterion}).\n` +
  `Format : ${args.deliverable}.\nRègle de fusion : accord → retenu ; désaccord → exposer les deux ` +
  `positions ; isolé non vérifié → "non confirmé" ; réfuté → annexe ; lister les trous.\n` +
  `Constats : ${JSON.stringify(ok)}\nVerdicts : ${JSON.stringify(verdicts.filter(Boolean))}`,
  { label: 'synthese', phase: 'Synthétiser' },
)
return { report, explored: ok, verdicts, failed: args.subquestions.length - ok.length }
```

---

## 2. Audit / revue

```js
export const meta = {
  name: 'swarm-audit',
  description: 'super-agent : revue par angles, dédoublonnage, contre-expertise des constats graves, synthèse',
  phases: [{ title: 'Revue' }, { title: 'Contre-expertise' }, { title: 'Synthèse' }],
}
// args = { target, context, lenses: [{ id, prompt }], counter_lenses: [string], verify_max }

const reviews = await parallel(args.lenses.map(l => () => agent(
  `Objet à auditer : ${args.target}\nContexte : ${args.context}\n` +
  `Ton angle, et seulement lui : ${l.prompt}\n` +
  `Chaque constat a une localisation précise et une preuve.`,
  { label: `revue:${l.id}`, phase: 'Revue', schema: FINDING },
)))
// Barrière justifiée : dédoublonnage sur l'ensemble.
const seen = new Map()
for (const f of reviews.filter(Boolean).flatMap(r => r.findings)) {
  const k = `${f.location}|${f.claim.slice(0, 60)}`
  if (!seen.has(k)) seen.set(k, f)
}
const unique = [...seen.values()]
const grave = unique.filter(f => f.severity === 'critique' || f.severity === 'majeur').slice(0, args.verify_max)
log(`${unique.length} constats uniques, ${grave.length} en contre-expertise`)

const verified = await pipeline(grave, (f, _, i) => agent(
  `Essaie de RÉFUTER ce constat sous l'angle : ${args.counter_lenses[i % args.counter_lenses.length]}.\n` +
  `${JSON.stringify(f)}\nrefuted=true par défaut si incertain.`,
  { label: `contre:${f.id}`, phase: 'Contre-expertise', schema: VERDICT },
).then(v => ({ ...f, verdict: v })))

phase('Synthèse')
const report = await agent(
  `Rapport d'audit de ${args.target}, classé par gravité. Constats réfutés en annexe, ` +
  `constats mineurs marqués "non confirmé".\nConstats vérifiés : ${JSON.stringify(verified.filter(Boolean))}\n` +
  `Autres constats : ${JSON.stringify(unique.filter(f => !grave.includes(f)))}`,
  { label: 'synthese', phase: 'Synthèse' },
)
return { report, verified, unique }
```

---

## 3. Diagnostic / debug (deux workflows)

Workflow A, l'enquête :

```js
export const meta = {
  name: 'swarm-diagnose-enquete',
  description: 'super-agent : une enquête par hypothèse, preuves pour et contre',
  phases: [{ title: 'Enquête' }],
}
// args = { symptom, context, hypotheses: [{ id, text }] }
const results = await pipeline(args.hypotheses, h => agent(
  `Symptôme : ${args.symptom}\nContexte : ${args.context}\nTon hypothèse : ${h.text}\n` +
  `Cherche des preuves POUR et CONTRE, avec la même rigueur. LECTURE SEULE : aucune action ` +
  `qui modifie un système. Propose l'expérience qui départagerait.`,
  { label: `enquete:${h.id}`, phase: 'Enquête', schema: HYPOTHESIS },
))
return results
```

Lis les résultats, écarte les hypothèses réfutées avec preuve, puis lance le workflow B :

```js
export const meta = {
  name: 'swarm-diagnose-refutation',
  description: 'super-agent : réfutation croisée des hypothèses survivantes, synthèse',
  phases: [{ title: 'Réfutation' }, { title: 'Synthèse' }],
}
// args = { symptom, survivors: [HYPOTHESIS], all_results: [HYPOTHESIS] }
const n = args.survivors.length
// Avec une seule survivante, un réfutateur neuf s'y attaque ; avec zéro, rien à réfuter.
if (!n) return null
const cross = await parallel(args.survivors.map((h, i) => () => agent(
  // Chaque réfutateur vise une hypothèse dont il n'est pas l'enquêteur d'origine.
  `Symptôme : ${args.symptom}\nToutes les conclusions : ${JSON.stringify(args.all_results)}\n` +
  `Ta cible : "${args.survivors[(i + 1) % n].hypothesis}". Essaie de la RÉFUTER par une preuve ` +
  `directe (log, trace, requête, reproduction). Lecture seule.`,
  { label: `refute:${(i + 1) % n}`, phase: 'Réfutation', schema: HYPOTHESIS },
)))
phase('Synthèse')
return await agent(
  `Cause la plus probable, preuves, expérience de confirmation et correctif proposé. ` +
  `Une hypothèse sans preuve directe reste "non confirmée".\n` +
  `Enquêtes : ${JSON.stringify(args.all_results)}\nRéfutations : ${JSON.stringify(cross.filter(Boolean))}`,
  { label: 'synthese', phase: 'Synthèse' },
)
```

---

## 4. Implémentation de code (contrats d'abord, puis un workflow d'exécution)

Vague 1, hors workflow ou en workflow d'un agent : un agent `CONTRACT_PLAN` en lecture seule.
Si `separable === false`, arrête le swarm. Sinon présente le découpage à l'utilisateur, puis :

```js
export const meta = {
  name: 'swarm-code',
  description: 'super-agent : implémentation parallèle en worktrees, intégration, tests, revue',
  phases: [{ title: 'Implémenter' }, { title: 'Intégrer' }, { title: 'Revue' }],
}
// args = { need, plan: CONTRACT_PLAN, integration_branch }

const changes = await pipeline(args.plan.tasks, t => agent(
  `Besoin global : ${args.need}\nInterfaces fixées (à respecter strictement) : ${JSON.stringify(args.plan.interfaces)}\n` +
  `Ta tâche ${t.id} : ${t.goal}\nTu ne modifies QUE ces fichiers : ${t.files.join(', ')}.\n` +
  `S'il te faut un autre fichier, arrête-toi et liste-le dans blocked_on sans le modifier.\n` +
  `Écris ou adapte les tests de ton morceau, lance : ${t.tests || args.plan.test_command}.\n` +
  `Crée une branche swarm/${t.id}, committe ton travail dessus, et rends branche + commit.`,
  { label: `impl:${t.id}`, phase: 'Implémenter', schema: CHANGESET, isolation: 'worktree' },
))
const done = changes.filter(Boolean)
const empty = done.filter(c => !c.branch)
const blocked = done.filter(c => c.blocked_on.length)
if (empty.length) log(`${empty.length} tâche(s) sans changement : ${empty.map(c => c.task_id).join(', ')}`)
if (blocked.length) log(`${blocked.length} tâche(s) bloquée(s) sur des fichiers hors périmètre`)
const red = done.filter(c => c.branch && !c.tests_passed)
if (red.length) log(`Tests rouges avant intégration : ${red.map(c => `${c.task_id} (${c.tests_run})`).join(' ; ')}`)

phase('Intégrer')
// En worktree aussi : l'intégration ne doit jamais déplacer le HEAD ni toucher le checkout de l'utilisateur.
const integ = await agent(
  `Crée la branche ${args.integration_branch} depuis ${args.plan.base_branch}, ` +
  `puis merge une par une : ${done.filter(c => c.branch).map(c => c.branch).join(', ')}.\n` +
  `Résous seulement les conflits triviaux ; liste les autres. Lance ${args.plan.test_command} et le lint. ` +
  `Ne pousse rien, ne merge pas dans ${args.plan.base_branch}.`,
  { label: 'integration', phase: 'Intégrer', schema: INTEGRATION, isolation: 'worktree' },
)

phase('Revue')
const review = await agent(
  `Revue du diff ${args.plan.base_branch}...${integ?.branch} contre ces interfaces : ` +
  `${JSON.stringify(args.plan.interfaces)}. Cherche les défauts de correction et les écarts au contrat.`,
  { label: 'revue', phase: 'Revue', schema: FINDING },
)
return { changes: done, integration: integ, review, missing: args.plan.tasks.length - done.length }
```

Tâche bloquée ou tests rouges : ne relance pas en boucle. Rapporte, et propose soit une vague de
correction (nouvelle validation si le total dépasse le nombre approuvé), soit une reprise en
session unique.
