# L'équipe (swarm) — étapes 0 à 7

Version 2.0.0 — la même que `SKILL.md`. Sinon, dis-le en une ligne et applique `SKILL.md` seul.

Lis ce fichier seulement quand un critère de « Passer à une équipe » (SKILL.md) est rempli. Les
seuils (feu vert, accord, plafond, watchdog) restent dans SKILL.md, « Seuils » : ce fichier y
renvoie, sans les réécrire. U1, U2, la règle de blocage et le repli valent aussi pour l'équipe.

Principe directeur : **l'organisation est un livrable**. Tu ne laisses pas les agents
s'organiser seuls ; tu conçois la topologie, tu l'écris dans un plan, tu le montres, puis tu
l'exécutes. L'équipe tourne comme sous-agents de cette session (mode sous-agents, par défaut),
comme sessions liées (mode sessions, si l'utilisateur en demande) ou, s'il le demande, avec
l'outil `Workflow` (mode rapide).

Références de l'équipe, dans ce dossier (lis celle dont tu as besoin, au moment où tu en as
besoin) :

- `topologies.md` — les patrons par famille, leurs règles de redondance et de vérification, les
  rôles spécialisés.
- `schemas.md` — les schémas JSON communs (FINDING, VERDICT, CHANGESET…).
- `team-mode.md` — mode sous-agents : les agents tournent dans cette session et se parlent par
  `SendMessage`.
- `sessions-mode.md` — mode sessions : chaque agent est une session native liée.
- `workflow-templates.md` — mode rapide : un squelette Workflow par patron.
- `flux.md` — file de merge, travail en chaîne, pertes de temps. `exemples.md` — exemples.

## Étape 0 — Choisir le mode et vérifier ses prérequis (toujours, en premier)

- **Mode sous-agents** (par défaut) : les agents tournent dans cette session. Il a besoin des
  *agent teams* (agents nommés). Fais les vérifications de `team-mode.md` (« Vérification avant
  de lancer ») et suis leur verdict.
- **Mode sessions** : seulement si l'utilisateur a demandé des sessions avec ses mots (SKILL.md,
  « Le cycle d'une tâche », étape 2, ligne « Quand »). Il faut `mcp__ccd_session__start_session` ;
  charge-le avec `ToolSearch` s'il est différé. Absent ou refusé : applique le repli de SKILL.md
  (« Quand tu ne délègues pas »), donc le mode sous-agents.
- **Mode rapide** (outil `Workflow`) : seulement si l'utilisateur le demande. Pas de prérequis.
  Charge le skill `workflow-authoring` avant d'écrire le moindre script.

Dis le mode retenu en une ligne, puis passe à l'étape 1.

## Étape 1 — Cadrage (toi seul, sans agent)

Reformule en 6 lignes maximum :

1. **Le problème**, avec son périmètre (fichiers, dépôts, sources, période…).
2. **Le critère de fin** : à quoi reconnaît-on que c'est terminé et juste ?
3. **Les contraintes** : ce qu'il ne faut pas toucher, les accès disponibles, les délais.
4. **Le goal** (toujours) : une phrase qui dit à quoi sert le travail, 2 à 3 exemples de sujets
   qui le remplissent (pris dans la demande de l'utilisateur quand il en donne), et ce qui n'en
   est pas un. Le goal filtre tout le reste : il va en tête de `plan.md` et de chaque brief.

Fais un **repérage inline** si le découpage en dépend (lister les fichiers, les sous-systèmes,
lire le diff, chercher les sources principales). On n'a pas besoin de tout savoir avant de
commencer, mais il faut connaître la liste des éléments à répartir avant d'orchestrer.

S'il manque une information qui change le découpage, pose **une** question précise. Sinon, avance.

## Étape 2 — Classification et test de pertinence

Classe le problème dans **une** famille (ou une combinaison séquentielle, ex. diagnostic puis code) :

| Famille | Signal |
|---|---|
| Recherche / analyse | Question large, sources multiples, besoin de synthèse sourcée |
| Audit / revue | Un objet fixe (code, PR, modèle de données) à examiner sous plusieurs angles |
| Diagnostic / debug | Un symptôme, une cause inconnue, plusieurs hypothèses plausibles |
| Implémentation de code | Construire ou modifier du code en plusieurs morceaux |

Puis dis si le goal est **ouvert** ou **fermé** :

- **ouvert** : le livrable est une collection qui peut grandir (doc de questions, FAQ, cas de
  test, points d'audit). Ajoute le patron `topologies.md` §5 : des apporteurs de sujets cherchent
  d'autres sujets du même type que les exemples, pour nourrir le goal ;
- **fermé** : une seule réponse attendue (un bug, une décision). Pas d'apporteurs, sauf si une
  liste de sujets à trouver (hypothèses, angles) aide vraiment.

Puis **teste la pertinence**. Renonce à l’équipe et reste sur des workers par flux si :

- le problème tient en une poignée d'appels d'outils ;
- les sous-tâches ne sont pas séparables (chaque étape dépend de la précédente, ou, pour le
  code, plusieurs morceaux doivent modifier les mêmes fichiers) ;
- le gain attendu ne justifie pas un coût de 5 à 15× une session.

Dis-le franchement en une ligne : des workers par flux suffisent, une équipe serait coûteuse et
inutile.

## Étape 3 — Conception du plan

Ouvre `references/topologies.md` à la section de la famille retenue et construis le plan :

- **Tâches** : unités autonomes, chacune avec un livrable clair. Pour le code, la liste des
  fichiers possédés par chaque tâche (un fichier n'appartient qu'à une seule tâche). Chaque
  tâche s’écrit pour qu’un worker la fasse sans rien demander :
  - **Quoi** : ce qu'elle livre, en 1 ou 2 phrases, et ce qu'elle ne doit pas toucher ;
  - **Eval** : 1 à 5 vérifications concrètes, cas limites compris, et « Fini quand ».
  C'est contre cet Eval que tu acceptes ou renvoies le résultat.
- **Rôles** : les workers, et les rôles spécialisés dont le plan écrit le besoin
  (`topologies.md` §6). Un watchdog : seulement dans le cas de « Seuils » (SKILL.md).
- **Modèle par rôle** : la table `model` / `effort` de SKILL.md (« Le cycle d'une tâche »,
  étape 2). Le modèle le moins cher, en effort `low`, pour un watchdog.
- **Dépendances** : quelles tâches attendent quelles autres. La hiérarchie se fait par vagues
  successives, jamais par des agents qui en créent d'autres (pas d'imbrication).
- **Redondance** : pour chaque tâche, 1 ou K copies. Toute copie supplémentaire a un **angle
  différent** (consigne, objectif, méthode de recherche, modèle). Jamais K copies identiques :
  leurs erreurs seraient corrélées.
- **Vérification** : qui vérifie quoi, et comment (sources, reproduction, tests, réfutation).
- **Apporteurs de sujets** (goal ouvert) : 1 à 2, chacun avec un angle différent, et un
  **budget de sujets** (nombre maximum de sujets acceptés) : le nombre d'agents ne borne pas le
  nombre de sujets. Voir `topologies.md` §5.
- **Rédacteurs** : possibles, pas obligatoires. Si le livrable est un long texte au style
  unique (doc, CR, rapport) et qu'il y a 3 exécutants ou plus : 1 rédacteur pour 2 à 3
  exécutants. Alors les exécutants ne rédigent pas : ils rendent de la matière brute (schéma
  `MATIERE`), les rédacteurs en font le texte. Sinon, chaque exécutant rédige sa part.
- **Synthèse** : un agent dédié (avec des rédacteurs : le rédacteur en chef `redac-1`), et la
  règle de fusion (étape 6). Exception : un livrable de moins d'une page, que tu écris
  toi-même ; le plan dit alors « Synthèse : router ».
- **Livrable** : un seul format, fixé maintenant (rapport markdown, branche + diff, tableau de
  comparaison, réponse dans le chat). Choisis celui qui sert le mieux le critère de fin.
- **Effort par étape** : `effort: 'low'` pour les étapes mécaniques, l'effort de la session pour
  le reste, plus haut seulement pour les juges et vérificateurs difficiles.

Compte les agents : **tous** les agents prévus (sessions, sous-agents ou appels `agent()`) — apporteurs, workers, copies redondantes,
vérificateurs, rédacteurs, watchdog, merger, checker, tester, reproducer, synthèse. Toi, le
router, tu ne comptes pas. Le seuil de « Seuils » compte les agents actifs en même temps.
Quand un nombre dépend des résultats (ex. un vérificateur par constat), donne une fourchette et
prends sa borne haute pour le seuil.

## Étape 4 — Montrer le plan, puis lancer ou attendre

Présente le plan à l'utilisateur dans ce format :

```
Goal : <une phrase> — exemples : <2 à 3 sujets> — pas un sujet : <…>
Famille : <famille> — patron : <patron> (+ §5 goal ouvert, si ouvert)
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
Synthèse : 1 agent | router (livrable de moins d'une page)
Total : <N> agents (borne haute) — coût estimé ≈ <N×1 à N×1,5>× une session normale
Hors périmètre : <ce qui ne sera pas couvert>
```

Lancer ou attendre : applique « Seuils » (SKILL.md), sans le réécrire.

- **L'utilisateur a demandé l'équipe dans ce message, et le total reste sous le seuil
  d'accord** : montre le plan et lance dans le même tour. Sa demande vaut feu vert ; il peut
  dire stop.
- **Tu proposes l'équipe toi-même** : attends son feu vert (« Je lance ? »).
- **Total au-dessus du seuil d'accord** : demande l'autorisation avec `AskUserQuestion`, en
  nommant **le nombre exact d'agents**, ce que les agents en plus apportent, et une **variante
  allégée** sous le seuil. Ne lance pas plus d'agents que le nombre approuvé. S'il en faut
  davantage en route, arrête-toi et redemande.

Si l'utilisateur modifie le plan, recalcule le total et réapplique la règle.

## Étape 5 — Exécution

**Selon le mode retenu à l'étape 0.** Mode sous-agents : suis `team-mode.md`. Mode sessions :
suis `sessions-mode.md`. En mode rapide, les agents ne se parlent pas pendant le travail, et un
goal ouvert devient trois phases fermées (`topologies.md` §5).

Le reste de cette étape décrit le **mode rapide** :

1. Pars du squelette correspondant dans `workflow-templates.md` et adapte-le au plan
   montré. Les sorties de chaque agent passent par les schémas de `schemas.md` :
   c'est le **contrat de communication** entre agents.
2. **Un workflow par vague** quand une vague dépend du contenu de la précédente pour être conçue
   (ex. diagnostic : enquête → tu lis → réfutation croisée). Lis les résultats entre deux
   workflows et ajuste la vague suivante, dans la limite du nombre d'agents approuvé.
   Un seul workflow suffit quand le plan est entièrement déterminé à l'avance.
3. Utilise `pipeline()` par défaut. Une barrière `parallel()` seulement quand une étape a besoin
   de **tous** les résultats précédents (dédoublonnage, synthèse, réfutation croisée).
4. Les gros artefacts (logs, diffs volumineux, extraits) vont dans le dossier de travail du swarm,
   **hors du dépôt** : le répertoire scratchpad de la session (sous-dossier `swarm-<slug>/`).
   Les agents isolés en worktree ne voient pas un dossier créé dans le checkout principal.
   Les scripts ne peuvent pas appeler `Date.now()` : passe l'identifiant du run et les chemins via
   `args`.
5. Si un agent revient `null` (échec ou abandon), n'improvise pas son résultat : signale le trou
   dans la synthèse, ou relance ce seul agent si le budget approuvé le permet.

## Étape 6 — Vérification et réunification

Règle de fusion appliquée par l'agent de synthèse (et que tu contrôles ensuite) :

- **Accord** entre sources ou copies indépendantes : constat retenu, confiance haute.
- **Désaccord** : les deux positions sont exposées avec leurs preuves. Ne tranche jamais en
  silence ; tranche seulement si une preuve (test, reproduction, source primaire) départage.
- **Constat isolé** non vérifié : retenu mais marqué « non confirmé ».
- **Constat réfuté** par la vérification : écarté, mentionné en annexe.
- **Trous** : ce qui n'a pas été couvert (agent échoué, source inaccessible, échantillonnage)
  est listé explicitement. Pas de troncature silencieuse.

Avec des rédacteurs, les sorties brutes sont les fichiers `matiere/<id>.json` : relis quelques
fiches contre leur matière.

Avant de livrer, relis la synthèse toi-même contre les sorties brutes : la synthèse est le maillon
où l'information se perd le plus. Si tu as écrit la synthèse toi-même (livrable de moins d'une
page), la règle de fusion s'applique à toi.

## Étape 7 — Livraison

Livre dans le format fixé à l'étape 3, avec en tête :

- la réponse au critère de fin (oui / non / partiellement, et pourquoi) ;
- les constats principaux avec leur niveau de confiance ;
- les désaccords non résolus et les trous ;
- avec un goal ouvert : le nombre de sujets proposés, acceptés, traités, et la raison de
  l'arrêt (budget, plus rien de nouveau, stop de l'utilisateur) ;
- le coût réel (nombre d'agents lancés) et, pour l'examen a posteriori, le dossier d'échange
  (`~/.claude/swarm-runs/<slug>/`) ou, en mode rapide, le `journal.jsonl` du workflow.

Pour le code : la branche d'intégration (`swarm-<slug>-integration`), le résultat des tests
(commandes et sortie), et la liste des branches de travail restantes. Ne merge pas dans la branche principale et ne pousse rien sans
accord explicite.
