# Schémas communs — le contrat de communication

Chaque agent rend un objet validé via l'option `schema` de `agent()`. Ces schémas sont le seul
canal entre agents : une vague reçoit les sorties de la précédente dans son prompt (JSON) ou via
`args`. Copie les constantes utiles en tête du script Workflow (JavaScript pur, pas de TypeScript).

Contraintes de l'outil : racine `{type: 'object', properties: {...}}`, `required` inclus dans
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
          id: { type: 'string', description: 'identifiant court et stable, ex. "sec-03"' },
          claim: { type: 'string', description: 'le constat, en une phrase' },
          location: { type: 'string', description: 'fichier:ligne, URL, table… ou "" si sans objet' },
          evidence: { type: 'array', items: { type: 'string' }, description: 'citations, extraits, sorties de commande' },
          sources: { type: 'array', items: { type: 'string' }, description: 'URL ou chemins consultés' },
          severity: { type: 'string', enum: ['critique', 'majeur', 'mineur', 'info'] },
          confidence: { type: 'string', enum: ['haute', 'moyenne', 'basse'] },
        },
        required: ['id', 'claim', 'evidence', 'sources', 'confidence'],
      },
    },
    open_questions: { type: 'array', items: { type: 'string' } },
    not_covered: { type: 'array', items: { type: 'string' }, description: 'ce que cet agent n\'a pas pu examiner, et pourquoi' },
  },
  required: ['findings', 'not_covered'],
}

const VERDICT = {
  type: 'object',
  properties: {
    finding_id: { type: 'string' },
    refuted: { type: 'boolean', description: 'true si le constat est faux ou non démontré ; true par défaut si incertain' },
    reason: { type: 'string' },
    evidence: { type: 'array', items: { type: 'string' } },
  },
  required: ['finding_id', 'refuted', 'reason'],
}

const HYPOTHESIS = {
  type: 'object',
  properties: {
    hypothesis: { type: 'string' },
    status: { type: 'string', enum: ['confirmée', 'plausible', 'affaiblie', 'réfutée'] },
    evidence_for: { type: 'array', items: { type: 'string' } },
    evidence_against: { type: 'array', items: { type: 'string' } },
    deciding_experiment: { type: 'string', description: 'expérience ou requête qui départagerait' },
  },
  required: ['hypothesis', 'status', 'evidence_for', 'evidence_against'],
}

const CONTRACT_PLAN = {
  type: 'object',
  properties: {
    separable: { type: 'boolean', description: 'false si des fichiers partagés ou un couplage fort empêchent le parallèle' },
    reason: { type: 'string' },
    base_branch: { type: 'string' },
    interfaces: { type: 'array', items: { type: 'string' }, description: 'signatures, types et formats fixés entre tâches' },
    tasks: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          goal: { type: 'string' },
          files: { type: 'array', items: { type: 'string' }, description: 'fichiers possédés, disjoints entre tâches' },
          tests: { type: 'string', description: 'commande de test ciblée pour ce morceau' },
        },
        required: ['id', 'goal', 'files'],
      },
    },
    test_command: { type: 'string', description: 'commande de la suite complète' },
  },
  required: ['separable', 'reason', 'tasks'],
}

const CHANGESET = {
  type: 'object',
  properties: {
    task_id: { type: 'string' },
    branch: { type: 'string', description: 'branche du worktree contenant le commit, "" si aucun changement' },
    commit: { type: 'string' },
    files_changed: { type: 'array', items: { type: 'string' } },
    tests_run: { type: 'string', description: 'commande lancée et extrait de sortie' },
    tests_passed: { type: 'boolean' },
    blocked_on: { type: 'array', items: { type: 'string' }, description: 'fichiers hors périmètre dont la tâche aurait eu besoin' },
  },
  required: ['task_id', 'branch', 'files_changed', 'tests_passed', 'blocked_on'],
}

const INTEGRATION = {
  type: 'object',
  properties: {
    branch: { type: 'string' },
    merged: { type: 'array', items: { type: 'string' } },
    conflicts: { type: 'array', items: { type: 'string' }, description: 'conflits non résolus' },
    test_output: { type: 'string', description: 'commande et extrait de sortie de la suite complète' },
    tests_passed: { type: 'boolean' },
  },
  required: ['branch', 'merged', 'conflicts', 'tests_passed'],
}
```

## Goal ouvert (`topologies.md` §5)

Ces deux objets passent par message ou par fichier dans le dossier d'échange (modes sessions et
sous-agents), ou par `schema` (mode rapide).

```js
const SUJET = {
  type: 'object',
  properties: {
    sujets: {
      type: 'array',
      description: 'un lot de 5 sujets au plus',
      items: {
        type: 'object',
        properties: {
          sujet: { type: 'string', description: 'le sujet, dans la forme des exemples du goal (ex. une question)' },
          pourquoi: { type: 'string', description: 'en une phrase : pourquoi il remplit le goal' },
          vu_ou: { type: 'array', items: { type: 'string' }, description: 'fichier:ligne, ticket, message, URL où il apparaît' },
          proche_de: { type: 'string', description: 'id d\'un sujet accepté qui y ressemble, ou ""' },
        },
        required: ['sujet', 'pourquoi', 'vu_ou'],
      },
    },
  },
  required: ['sujets'],
}

// Matière brute d'un exécutant pour un rédacteur : des faits, pas de prose.
const MATIERE = {
  type: 'object',
  properties: {
    id: { type: 'string', description: 'id du sujet, ex. "s-04"' },
    sujet: { type: 'string' },
    faits: { type: 'array', items: { type: 'string' }, description: 'une ligne par fait, dans l\'ordre où ils se produisent' },
    preuves: { type: 'array', items: { type: 'string' }, description: 'fichier:ligne, extraits, sorties de commande, captures' },
    commandes: { type: 'array', items: { type: 'string' }, description: 'commandes ou étapes pour reproduire' },
    points_ouverts: { type: 'array', items: { type: 'string' }, description: 'ce qui reste incertain ou non vérifié' },
    confiance: { type: 'string', enum: ['haute', 'moyenne', 'basse'] },
  },
  required: ['id', 'sujet', 'faits', 'preuves', 'points_ouverts', 'confiance'],
}
```

La synthèse ne prend pas de schéma quand le livrable est un texte (rapport, réponse) : elle rend
du markdown. Donne-lui un schéma quand le livrable est structuré (tableau de comparaison).
