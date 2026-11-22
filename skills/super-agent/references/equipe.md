# L'équipe (swarm) — étapes 0 à 7

Version 2.0.0.

À lire quand un critère de « Passer à une équipe » (SKILL.md) est rempli. Seuils, U1, U2, règle
de blocage et repli : SKILL.md ; ils valent aussi pour l'équipe.

**L'organisation est un livrable** : tu conçois la topologie, tu l'écris dans un plan, tu le
montres, puis tu l'exécutes.

## Étape 0 — Choisir le mode et vérifier ses prérequis (toujours, en premier)

- **Mode sous-agents** (par défaut) : il lui faut les *agent teams* (agents nommés) : fais la
  « Vérification avant de lancer » de `team-mode.md`.
- **Mode sessions** : seulement si l'utilisateur a demandé des sessions avec ses mots (SKILL.md,
  « Le cycle d'une tâche », étape 2, ligne « Quand »). `mcp__ccd_session__start_session` absent
  (après `ToolSearch`) ou refusé : le mode sous-agents (repli de SKILL.md).
- **Mode rapide** (outil `Workflow`) : seulement si l'utilisateur le demande. Charge le skill
  `workflow-authoring` avant d'écrire le moindre script.

Dis le mode retenu en une ligne.

## Étape 1 — Cadrage (toi seul, sans agent)

En 6 lignes au plus :

1. **Le problème**, avec son périmètre (fichiers, dépôts, sources, période…).
2. **Le critère de fin** : à quoi reconnaît-on que c'est terminé et juste ?
3. **Les contraintes** : ce qu'il ne faut pas toucher, les accès disponibles, les délais.
4. **Le goal** (toujours) : une phrase qui dit à quoi sert le travail, 2 à 3 exemples de sujets
   qui le remplissent (ceux de l'utilisateur quand il en donne), et ce qui n'en est pas un. Il
   filtre tout le reste : il va en tête de `plan.md` et de chaque brief.

Fais un **repérage inline** si le découpage en dépend (lister les fichiers, lire le diff,
chercher les sources principales) : il faut connaître les éléments à répartir. Sans le
plafond des 3 lectures, mais une recherche de fond part chez un sous-agent.

Une information manque et change le découpage : **une** question précise. Sinon, avance.

## Étape 2 — Classification et test de pertinence

Classe le problème dans **une** famille (ou une suite, ex. diagnostic puis code) :

| Famille | Signal |
|---|---|
| Recherche / analyse | Question large, sources multiples, besoin de synthèse sourcée |
| Audit / revue | Un objet fixe (code, PR, modèle de données) à examiner sous plusieurs angles |
| Diagnostic / debug | Un symptôme, une cause inconnue, plusieurs hypothèses plausibles |
| Implémentation de code | Construire ou modifier du code en plusieurs morceaux |

Le goal est-il **ouvert** ou **fermé** ?

- **ouvert** : le livrable est une collection qui peut grandir (doc de questions, FAQ, cas de
  test, points d'audit). Ajoute le patron `topologies.md` §5 (apporteurs de sujets) ;
- **fermé** : une seule réponse attendue (un bug, une décision). Pas d'apporteurs, sauf si une
  liste de sujets à trouver (hypothèses, angles) aide vraiment.

**Test de pertinence.** Renonce à l'équipe, et dis en une ligne que des workers par flux
suffisent, si :

- le problème tient en une poignée d'appels d'outils ;
- les sous-tâches ne sont pas séparables (chaque étape dépend de la précédente, ou plusieurs
  morceaux de code modifient les mêmes fichiers) ;
- le gain attendu ne justifie pas un coût de 5 à 15× une session.

## Étape 3 — Conception du plan

Ouvre `topologies.md` à la section de la famille et construis le plan :

- **Tâches** : unités autonomes, écrites en **Quoi** et **Eval** (SKILL.md, « Le cycle d'une
  tâche », étape 1) : c'est contre cet Eval que tu acceptes ou renvoies le résultat. Pour le
  code, les fichiers de chaque tâche (un fichier n'appartient qu'à une seule tâche).
- **Rôles** : les workers, et les rôles spécialisés dont le plan écrit le besoin
  (`topologies.md` §6). Un watchdog : seulement dans le cas de « Seuils ».
- **Modèle et effort par rôle** : la table `model` / `effort` de SKILL.md (étape 2 du cycle) :
  `effort: 'low'` pour les étapes mécaniques, plus haut que la session seulement pour les
  juges et vérificateurs difficiles.
- **Dépendances** : quelles tâches attendent quelles autres. La hiérarchie se fait par vagues,
  jamais par des agents qui en créent d'autres.
- **Redondance** : pour chaque tâche, 1 ou K copies, chacune avec un **angle différent**
  (consigne, objectif, méthode de recherche, modèle) : K copies identiques ont des erreurs
  corrélées.
- **Vérification** : qui vérifie quoi, et comment (sources, reproduction, tests, réfutation).
- **Apporteurs de sujets** (goal ouvert) : 1 à 2, et un **budget de sujets** (nombre maximum
  de sujets acceptés) : le nombre d'agents ne le borne pas.
- **Rédacteurs** : possibles, pas obligatoires. Le livrable est un long texte au style unique
  (doc, CR, rapport) et il y a 3 exécutants ou plus : 1 rédacteur pour 2 à 3 exécutants, qui
  rendent alors de la matière brute (schéma `MATIERE`) et ne rédigent pas. Sinon, chaque
  exécutant rédige sa part.
- **Synthèse** : toujours un agent, jamais toi (avec des rédacteurs : le rédacteur en chef
  `redac-1`), selon la règle de fusion (étape 6). Livrable court : un sous-agent suffit.
- **Livrable** : un seul format, fixé maintenant (rapport markdown, branche + diff, tableau de
  comparaison, réponse dans le chat), celui qui sert le mieux le critère de fin.

**Compte les agents** : tous (sessions, sous-agents ou appels `agent()`), toutes vagues
cumulées, rôles, copies redondantes, watchdog et synthèse compris ; toi, tu ne comptes pas.
C'est ce total que compare le seuil d'accord de « Seuils ». Un nombre dépend des résultats
(ex. un vérificateur par constat) : donne une fourchette et prends sa borne haute.

## Étape 4 — Montrer le plan, puis lancer ou attendre

Présente le plan dans ce format :

```
Goal : <une phrase> — exemples : <2 à 3 sujets> — pas un sujet : <…>
Famille : <famille> — patron : <patron> (+ goal ouvert, si ouvert)
Mode : sous-agents (dans cette session) | sessions (sessions natives liées) | rapide (Workflow)
Communication : <qui écrit à qui, et pour quoi>
Rôles : router (moi) — <n> workers — <merger, checker, tester, reproducer, watchdog : ceux retenus, avec le besoin de chacun> | aucun rôle spécialisé
Livrable : <format>
Vagues :
  1. <nom> — <n> agents — <ce qu'ils font> (redondance : <règle>)
  2. ...
Vérification : <n> agents — <méthode>
Apporteurs de sujets : <n> agents — <angle de chacun> | aucun — <raison>
Budget de sujets : <N> sujets au plus (arrêt aussi si 2 fois « rien de nouveau », ou sur ton stop)
Rédacteurs : <n> agents — <format d'une fiche / du CR> | aucun — <raison>
Synthèse : 1 agent
Total : <N> agents (borne haute) — coût estimé ≈ <N×1 à N×1,5>× une session normale
Hors périmètre : <ce qui ne sera pas couvert>
```

Lancer ou attendre : applique « Seuils » (SKILL.md).

- **Tu proposes l'équipe toi-même** : « Je lance ? ».
- **Le Total dépasse le seuil d'accord** : demande-le avec `AskUserQuestion`, en nommant **le
  nombre exact d'agents**, ce que les agents en plus apportent, et une **variante allégée**
  sous ce seuil.
- Ne lance jamais plus d'agents que le nombre approuvé ; s'il en faut davantage en route,
  arrête-toi et redemande. Le plan change : recalcule le total et réapplique la règle.

## Étape 5 — Exécution

Mode sous-agents : `team-mode.md`. Mode sessions : `team-mode.md`, puis `sessions-mode.md`.
Mode rapide, ci-dessous : les agents ne se parlent pas pendant le travail (goal ouvert :
`topologies.md` §5).

1. Pars du squelette de `workflow-templates.md` (rappels de l'API en tête) et adapte-le au
   plan montré. Les sorties passent par les schémas de `schemas.md` : c'est le **contrat de
   communication** entre agents.
2. **Un workflow par vague** quand une vague dépend du contenu de la précédente (ex.
   diagnostic : enquête → tu lis → réfutation croisée) : lis les résultats et ajuste la vague
   suivante, dans le total du plan. Plan déterminé à l'avance : un seul workflow.
3. Les gros artefacts (logs, diffs volumineux, extraits) vont **hors du dépôt**, dans le
   scratchpad de la session (sous-dossier `swarm-<slug>/`) : un agent en worktree ne voit pas
   un dossier créé dans le checkout principal. Passe l'identifiant du run et les chemins via
   `args`.
4. Un agent revient `null` (échec ou abandon) : n'improvise pas son résultat. Signale le trou
   dans la synthèse, ou relance ce seul agent si le total du plan le permet.

## Étape 6 — Vérification et réunification

Règle de fusion, appliquée par l'agent de synthèse et contrôlée par toi :

- **Accord** entre sources ou copies indépendantes : constat retenu, confiance haute.
- **Désaccord** : les deux positions sont exposées avec leurs preuves. On ne tranche jamais en
  silence, et seulement si une preuve (test, reproduction, source primaire) départage.
- **Constat isolé** non vérifié : retenu, marqué « non confirmé ».
- **Constat réfuté** par la vérification : écarté, mentionné en annexe.
- **Trous** : ce qui n'a pas été couvert (agent échoué, source inaccessible, échantillonnage)
  est listé. Pas de troncature silencieuse.

Avant de livrer, relis la synthèse contre les sorties brutes (avec des rédacteurs : quelques
fiches contre leur `matiere/<id>.json`) : c'est là que l'information se perd le plus.

## Étape 7 — Livraison

Dans le format fixé à l'étape 3, avec en tête :

- la réponse au critère de fin (oui / non / partiellement, et pourquoi) ;
- les constats principaux, avec leur niveau de confiance ;
- les désaccords non résolus et les trous ;
- goal ouvert : le nombre de sujets proposés, acceptés, traités, et la raison de l'arrêt
  (budget, plus rien de nouveau, stop de l'utilisateur) ;
- le coût réel (nombre d'agents lancés) et le dossier d'échange
  (`~/.claude/swarm-runs/<slug>/`) ou, en mode rapide, le `journal.jsonl` du workflow.

Pour le code : la branche d'intégration (`swarm-<slug>-integration`), le résultat des tests
(commandes et sortie), et les branches de travail restantes. Ne merge pas dans la branche
principale et ne pousse rien sans accord explicite.
