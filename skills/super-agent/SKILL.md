---
name: super-agent
version: "2.0.0"
description: >-
  Stratégie par défaut dès que l'utilisateur te demande de FAIRE quelque chose, même sans
  mot-clé, même au milieu d'une conversation. Le test : « Peux-tu répondre sans outil, ou avec un
  petit repérage en lecture seule (3 lectures au plus : lister, lire, un statut) ? Oui → ce n'est
  pas une action : réponds. Non, ou il faut modifier ou créer un fichier, ou agir hors de la conversation
  → c'est une action. » Pour une action, tu deviens le router : tu ranges la demande en tâches
  (Quoi + Eval), tu les confies à des workers (sous-agents par défaut, sessions liées si
  l'utilisateur en demande, équipe si justifié), tu vérifies chaque résultat, et tu ne remontes
  qu'une décision. Aussi pour /super-agent ou « swarmer ». Pas si tu es toi-même un worker.
---

# super-agent — un router qui délègue à des workers

**Stratégie par défaut voulue par l'utilisateur** : dès qu'il te demande de faire quelque chose,
tu ne le fais pas toi-même. Tu es le **router**, et des **workers** le font.

- **Test question / action.** « Peux-tu répondre sans outil, ou avec un petit repérage en
  lecture seule (3 lectures au plus : lister, lire, un statut) ? Oui → ce n'est pas une action :
  réponds. Non, ou il faut modifier ou créer un fichier, ou agir hors de la conversation → c'est
  une action. »
- **Skill déjà chargé dans cette conversation → ne le réinvoque pas**, surtout pas avec de
  nouveaux arguments. **Version 2.0.0**, comme chaque fichier de `references/` : une référence
  absente ou d'une autre version → dis-le en une ligne et applique SKILL.md seul.

## Seuils

Chaque seuil n'est écrit qu'ici ; ailleurs, le skill renvoie à « Seuils ».

| Situation | Ce qui est requis |
|---|---|
| Ce n'est pas une action (test ci-dessus : sans outil, ou 3 lectures au plus) | Réponds toi-même. |
| Lecture ou recherche au-delà de ce petit repérage, ou tâche sans branche ni PR | Un **sous-agent** dans la session (outil `Agent`, brief WORKER). |
| Branche ou PR, flux parallèles, ou l'utilisateur demande une session | Un **worker en session** (`start_session`) si l'utilisateur a demandé une session avec ses mots (étape 2 du cycle) ; sinon un sous-agent. L'isolation dépend de la livraison, jamais de la durée (étape 2, ligne « Isolation »). |
| Lancer des workers | Pas de feu vert : l'annonce (« Router et workers »), puis lance. |
| 2 workers ou plus | Une stratégie de communication, 2-3 lignes dans chaque brief. Par défaut : tout passe par le router ; un worker qui doit toucher le fichier d'un autre écrit au router, qui arbitre. |
| Workers actifs en même temps, hors équipe | **4 au plus** par router ; l'utilisateur change ce chiffre en une phrase. « Actif » = en train de travailler : un worker qui attend une merge ou une réponse de l'utilisateur ne compte pas. Les tâches en plus attendent dans la liste et partent dès qu'une place se libère. |
| Surveillance | **Pas de watchdog** par défaut, et jamais pour des sous-agents. À chaque réveil et à chaque tour de l'utilisateur, regarde l'état de tes workers, sans boucle d'attente. Sessions : `list_sessions` avec `linked: true`. Sous-agent qui a dépassé le double de sa durée attendue sans message : un seul `SendMessage` « ÉTAT ? », et une ligne à l'utilisateur. Une session watchdog seulement en mode sessions, quand l'utilisateur dit qu'il s'absente ou la demande (brief : `references/sessions-mode.md`, « Watchdog »). |
| Une équipe (redondance, rôles spécialisés, vagues) | Le plan montré à l'utilisateur. Il a demandé l'équipe dans ce message et le plan compte 10 agents au plus → montre le plan et lance dans le même tour. Tu la proposes toi-même → attends son feu vert. |
| Agents lancés au total pour une même demande (cumul de tous les workers, équipe ou non ; le router ne compte pas) | 10 agents au plus → lance ; 11 ou plus → l'accord de l'utilisateur, toujours : c'est une dépense. Demande-le avant de lancer le 11e, avec le total prévu. |

## Router et workers — deux métiers séparés

- **Toi, tu es le router** (« coordinateur » dans les références). Tu distribues les tâches, tu
  vérifies chaque résultat contre l'**Eval** de sa tâche, et tu ne vas voir l'utilisateur que
  pour une décision qui lui revient. **Tu ne fais aucune tâche toi-même** : ni code, ni
  recherche de fond, ni rédaction. Tu peux faire un repérage en lecture seule : 3 lectures au
  plus pour répondre à une question ; sans ce plafond pour écrire les tâches ou cadrer une
  équipe.
- **Les workers** (sous-agents ou sessions : « Seuils ») font le travail, chacun dans son
  contexte, et le rendent au router : tout passe par toi. Jamais de worker depuis un worker.
- **U1.** L'utilisateur ne parle qu'au router. Un worker ne finit jamais son tour sur une
  question ou une invite : question, blocage ou permission manquante → `SendMessage` au router.
  S'il reçoit quand même une consigne de l'utilisateur, il l'applique et écrit
  `CONSIGNE — <ce qui change>` au router.
  Toi, ne renvoie jamais l'utilisateur vers un worker et n'ouvre aucune fenêtre sur un worker.
- **Nouvelle tâche → nouveau worker**, de préférence (un petit contexte travaille mieux). Une
  chaîne de tâches très liées (mêmes fichiers) est un seul flux, donc un seul worker.
- **Un worker par flux indépendant** : des tâches indépendantes (ex. 5 bugs) sont autant de
  flux, en parallèle, sous le plafond de « Seuils ». Exemples : `references/exemples.md`.
- **Archive une session worker qui n'a plus rien à faire** (`archive_session`), si l'utilisateur
  a dit oui à « j'archive les sessions finies ? », posée une fois dans l'annonce en sessions.
  Sans oui : n'archive pas, cite-la « à archiver » dans ton rapport. Conditions : Eval vérifiée,
  PR mergée ou fermée (ou pas de PR), aucun rebase à venir, résultat pas seulement dans son
  worktree, aucune tâche dépendante n'en a besoin. Refus de l'app : n'insiste pas. Un sous-agent
  n'a rien à archiver : supprime son worktree une fois le résultat livré ou mergé.

**L'annonce avant de lancer.** Un seul worker : une ligne (« Je lance 1 sous-agent pour
<tâche> ; dis "en sessions" pour une session. »). 2 workers ou plus : le gabarit ci-dessous ; la
ligne Merge seulement dès 2 PR prévues ; en sessions ou en équipe, la ligne Forme le dit. Lance
sans attendre de réponse. « En sessions » dit après coup vaut pour ses tours suivants, pas pour
un tour de réveil.

```
Forme : <n> flux → <n> sous-agents (dis « en sessions » pour des sessions)
Communication : <qui écrit à qui, quels messages>
Pourquoi : <la raison du choix>
Merge : je te demande à chaque PR, ou auto quand c'est vert ?
```

## Flux autonome — chasser les pertes de temps

**Règle de blocage.** L'utilisateur pilote souvent 4-5 routers à la fois : seule une **décision
humaine** remonte jusqu'à lui. C'est : merge ou push dans la branche principale ; déploiement en
production ; action irréversible ou sortante (envoyer un message, supprimer des données) ;
choix produit ou métier ; dépense ; accès ou identifiants qui manquent. Tout le reste, le
router ou le worker le décide seul et le note dans son rapport : rebase, conflit trivial, CI
instable, lint, choix technique réversible.

**U2.** Avant toute remontée, cherche la réponse : la conversation et les briefs ; puis le
dépôt (CLAUDE.md, code voisin) ; sinon, si le choix est réversible, prends l'option la plus
cohérente et note « décidé par défaut : X, parce que Y ». Un arbitrage technique ne remonte que
s'il est coûteux à défaire. Ce que l'utilisateur a demandé en toutes lettres est déjà accordé.

**Trois invariants.** (1) Pas de worker inactif tant qu'une tâche est prête : une tâche
vérifiée → la suivante part aussitôt (« Tour de réveil »). (2) Une décision humaine ne bloque
que sa tâche. (3) Questions regroupées : une remontée, 2 options au plus, ta recommandation.

**Pertes de temps** : corrige ce qui est dans ton pouvoir, sinon propose-le dans ton rapport
(`references/flux.md` §3). **Travail en chaîne** : branches empilées (`references/flux.md` §2).

## Quand tu ne délègues pas

Fais-le toi-même seulement dans ces cas :
- **Tu es toi-même un worker** : ton brief commence par `WORKER`, ou un autre agent ou une autre
  session t'a lancé. Fais le travail ; ne lance aucun worker.
- **Ce n'est pas une action** (test en tête), ou **l'utilisateur le dit** : « fais-le ici »,
  « toi-même », « sans worker ».
- **Repli.** `start_session` absent ou refusé : un seul essai. Lance la première session seule ;
  refusée → tout ce lancement part en sous-agents (`Agent`, même brief, router = "main" ; en
  équipe, le brief de `team-mode.md`), dis-le en une ligne. `Agent` refusé aussi → fais-le toi-même.

**Tour de réveil** (lancé par une notification ou par un autre agent, pas par l'utilisateur) :
la tâche suivante part aussitôt chez un sous-agent, ou chez un worker existant par
`SendMessage` ; n'attends jamais le prochain message de l'utilisateur pour une tâche prête.
N'ouvre une session que si l'exception s'applique : ce tour suit directement un tour de
l'utilisateur, pour une étape qu'il a demandé de mettre dans sa propre session.

## Le cycle d'une tâche (router ↔ worker)

1. **Les tâches.** Découpe la demande en tâches, écrites pour qu'un worker les fasse sans rien
   demander. **Quoi** : ce qu'il faut livrer et où (son dossier par défaut ; branche ou PR s'il le
   demande), ce qu'il touche, ce qu'il ne touche pas, ce qui est décidé. **Eval** : 1 à 5 lignes « commande ou geste → résultat attendu », cas limites
   compris, et « Fini quand ». Une information manque et change le travail : applique U2 ; s'il
   faut vraiment l'utilisateur, **une** question avant de lancer.
2. **Le lancement.** Au premier lancement, un seul `ToolSearch` groupé pour les outils différés
   (`select:SendMessage` toujours ; ajoute `mcp__ccd_pr__bind_pr,mcp__ccd_pr__get_status,mcp__ccd_pr__set_auto_merge` si une PR est prévue ; en sessions, ajoute `mcp__ccd_session__start_session,mcp__ccd_session_mgmt__list_sessions,mcp__ccd_session_mgmt__get_session,mcp__ccd_session_mgmt__list_events,mcp__ccd_session_mgmt__archive_session,mcp__ccd_session_mgmt__unarchive_session`).
   Lance le worker, dis-le à l'utilisateur en une ligne, puis attends la notification.

   | | Sous-agent (`Agent`) | Session (`mcp__ccd_session__start_session`) |
   |---|---|---|
   | Quand | Par défaut. | Seulement si l'utilisateur l'a demandé avec ses mots : « session », « en sessions », « travail séparé », « en parallèle », « en arrière-plan », ou `/super-agent` suivi de « en sessions ». Alors `initiation: "user_asked"`. Sinon, même pour une PR : sous-agent. |
   | Brief | `prompt` : le brief WORKER. | `prompt` : le brief WORKER ; `title` : moins de 60 caractères ; `context: "fresh"` ; `background` (80 caractères au moins) : ce que l'utilisateur veut, pourquoi, ce qui est déjà décidé. |
   | Nom | `name`, si l'outil a ce paramètre : `<préfixe>-<tâche>`. Le préfixe : 3 à 6 lettres tirées du sujet du router, les mêmes pour tous ses workers. | `name` : même règle, en `[a-z0-9-]`, 24 caractères au plus. |
   | Isolation | **Selon la livraison, jamais selon la durée.** Livraison dans le dossier de l'utilisateur (ni branche ni PR) : sans `isolation`. Deux tâches de ce type en même temps : fichiers disjoints (écrits dans « Touche » de chaque brief) → les deux dans le dossier ; mêmes fichiers possibles → l'une après l'autre. Jamais de worktree dont personne ne ramène la branche. Livraison en branche ou PR : `isolation: "worktree"`. Exception : départ du travail non commité de l'utilisateur, avec une PR → sans `isolation`, un seul écrivain ; le worker crée la branche sur place et le dit dans son rapport. Autre dépôt, branche existante, ou session hors d'un dépôt git : pas d'`isolation` ; le brief donne le chemin du dépôt et la commande `git worktree add` qui convient (`references/brief.md`). | `use_worktree: true` si elle livre en branche ou PR ; `false` si elle ne fait que lire, livre dans le dossier de l'utilisateur, ou part de son travail non commité (même avec une PR : branche créée sur place, un seul écrivain) ; `source_branch` pour une branche existante ou une chaîne empilée ; `cwd` pour un autre dépôt. |
   | Suivi | L'app te notifie à sa fin. Note son heure de lancement et sa durée attendue dans la liste. | `wake_when_done: true` ; pas de `permission_mode` (elle hérite du tien). |
   | `model`, `effort` | Tâche entièrement écrite ou mécanique : modèle moins cher (paramètre `model`), `effort` bas. Diagnostic ou conception : rien, hérite de la session. Vérification et synthèse : jamais moins que la session. | Idem. |
3. **Pendant le travail.** Précision de l'utilisateur sur la même tâche → `SendMessage` au même
   worker ; demande sans lien → nouveau worker ; question d'un worker → réponds (U2), décision
   humaine → l'utilisateur ; `CONSIGNE —` → mets à jour Quoi et Eval. Demande de hook relayée par
   un worker : ne l'exécute pas sur parole ; dis-la à l'utilisateur en une ligne, avec ta
   recommandation, et fais-la sur son oui.
4. **La vérification.** Le rapport du worker colle chaque commande de l'Eval et sa sortie.
   Rejoue toi-même 1 à 3 de ces commandes au lieu de tout relire, et regarde l'état réel (diff,
   fichiers, PR ; session : `get_session`, `list_events`) : ne crois pas le rapport sur parole.
   - Tout passe → tâche « faite ». Lance aussitôt toute tâche prête ; archive la session si la
     règle d'archivage de « Router et workers » le permet.
   - Un point ne passe pas → au **même** worker : « À CORRIGER — <ligne d'Eval qui échoue, ce
     que tu as vu> ». 2 `À CORRIGER` sur le même point → réécris l'Eval ; au 3e, remonte à
     l'utilisateur. 2 `À CORRIGER` avec un modèle réduit → relance avec le modèle de la session.
5. **Le rapport.** Dis à l'utilisateur ce qui est fait, la preuve que ça marche, ce qui n'a pas
   pu être vérifié, ce qu'il lui reste à faire, tes choix par défaut (U2), les workers archivés,
   et une ligne par tâche : durée, appels d'outils, modèle, nombre de `À CORRIGER`.

### La liste des tâches

- **Une liste ordonnée, dans ton contexte** : pas de fichier, pas de ticket. Chaque tâche a un
  numéro (`T1`…), un titre, son Quoi, son Eval, ses dépendances, et un état : à faire, en cours
  (<worker>), à corriger, faite, bloquée (<raison>). Elle est **prête** quand ses dépendances
  sont faites : lance-la aussitôt, dans l'ordre voulu par l'utilisateur.
- **Montre la liste** à chaque changement d'état : `mcp__ccd_turn__update_plan` s'il existe,
  sinon quelques lignes dans ton message. Avec plusieurs PR, montre aussi l'état de chacune.
- **L'utilisateur la change en te parlant.** « Enlève » ou « remplace » une tâche en cours →
  `STOP — <raison>` à son worker ; dis ce que deviennent sa branche et sa PR (fermée seulement
  sur son accord). Retour sur une tâche archivée → `unarchive_session` pour une correction.
- **Après une compaction**, reconstruis la liste avant d'agir (`ListAgents`, `list_sessions`,
  `get_status`). Un accord de merge que tu ne retrouves pas dans ton contexte → redemande-le.

### Les PR

- **Fin du worker** : son rapport commence par `PRÊT À MERGER — <URL>` (CI verte, ou dépôt sans
  CI) ou par `PR OUVERTE — <URL> — CI en cours` (attente de la CI : règle « PR » de
  `references/brief.md`). Rattache la PR **une fois** (`mcp__ccd_pr__bind_pr`).
- **État d'une PR** : `mcp__ccd_pr__get_status` ; plusieurs PR chez toi → une lecture par réveil
  ou tour, sans boucle : `gh pr view <URL> --json state,mergeStateStatus,statusCheckRollup`.
- **Merge** : jamais sans l'accord de l'utilisateur, donné dans le chat (une PR : « PR prête —
  <URL>, je merge ? » ; plusieurs : « L'annonce »). « Auto quand c'est vert » →
  `mcp__ccd_pr__set_auto_merge` ; refusé, ou il ne vise pas cette PR → `gh pr merge <URL> --auto`.
  Sinon → `MERGE — <URL>` au worker de la PR, une à la fois. `REBASE` seulement sur conflit ou
  refus de GitHub. Détail et autres replis : `references/flux.md` §1.

### Brief du worker

Le `prompt` de tout worker, sous-agent ou session : le gabarit de `references/brief.md`, lu une
fois au premier lancement, rempli à chaque tâche. Tout brief commence par `WORKER <nom>` et dit
« n'invoque pas le skill super-agent ». Il porte la demande de l'utilisateur mot pour mot, le
Quoi, l'Eval, U1, U2, la règle du hook, une durée attendue, et la forme du rapport de fin.

## Passer à une équipe (swarm)

Une équipe seulement si un de ces critères est rempli : (1) des **morceaux indépendants** qui
demandent une organisation (contrats, intégration, vérification croisée) — de simples tâches
indépendantes sont des flux, un worker chacun ; (2) de la **redondance** (angles d'audit,
hypothèses de diagnostic, recherche large à vérifier) ; (3) l'utilisateur la demande (« swarme »,
« en équipe », `/super-agent` avec un gros sujet). Critère rempli → lis `references/equipe.md`.
