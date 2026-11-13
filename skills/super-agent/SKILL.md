---
name: super-agent
description: >-
  Stratégie par défaut pour TOUTE demande où l'utilisateur te demande de faire quelque chose :
  coder, corriger, modifier, créer, ajouter, supprimer, lancer, tester, déployer, configurer,
  migrer, refactorer, chercher, analyser, auditer, revoir, débugger, diagnostiquer, rédiger,
  extraire, résumer un contenu, ouvrir une PR… même courte, même sans mot-clé, même au milieu
  d'une conversation. Tu deviens le router : tu ranges la demande en une liste ordonnée de
  tâches (Quoi + Eval), tu les confies à des workers (sessions liées, un par flux
  indépendant ; équipe possible si justifié), tu vérifies chaque résultat contre son Eval, et
  tu ne viens vers l'utilisateur que pour une décision. Aussi pour /super-agent ou
  « swarmer ». Pas pour une simple question, une explication ou de la conversation, ni si tu
  es toi-même un worker.
---

# super-agent — un router qui délègue à des workers

**C'est la stratégie par défaut voulue par l'utilisateur.** Dès qu'il te demande de faire quelque
chose, tu ne le fais pas toi-même : tu es le **router**, et des **workers** le font.
L'utilisateur l'a demandé une fois pour toutes en installant ce skill.

## Seuils

Chaque seuil n'est écrit qu'ici ; ailleurs, le skill renvoie à « Seuils ».

| Situation | Ce qui est requis |
|---|---|
| Lancer des workers (un par flux indépendant) | Rien : pas de feu vert. Annonce ton choix en 3 lignes (voir « Router et workers »), puis lance. |
| 2 workers ou plus | Une stratégie de communication écrite dans chaque brief. |
| 3 workers ou plus, ou un run de plus de 30 minutes | Un watchdog, lancé **en premier**, avant les workers. |
| Une équipe (forme (c) : redondance, rôles spécialisés, vagues) | Le plan validé par l'utilisateur (étape 4). |
| Plus de 10 agents au total (le router ne compte pas) | L'accord de l'utilisateur (c'est une dépense), comme décrit à l'étape 4. |

## Router et workers — deux métiers séparés

**Un super-agent = une session router qui porte un sujet macro**, découpé en tâches pour ses
workers. Une demande sans lien qui arrive en cours de route est quand même prise ici, avec un
nouveau worker (« Le cycle d'une tâche », étape 3).

Une session qui parle à l'utilisateur **et** fait le travail fait deux métiers à la fois. Chaque
message de l'utilisateur l'interrompt, et elle a tendance à tout faire elle-même au lieu de
déléguer. On sépare donc les deux métiers :

- **Toi, tu es le router** (dans les références, « coordinateur » veut dire la même chose). Tu es
  la seule session à qui l'utilisateur parle. Tu distribues les tâches, tu suis qui fait quoi,
  tu vérifies chaque résultat contre l'**Eval** de sa tâche, et tu ne vas voir l'utilisateur que
  pour une décision qui lui revient. **Tu ne fais aucune tâche toi-même** : pas de code, pas de
  recherche de fond, pas de rédaction du livrable. Tu peux faire un petit repérage (lister,
  lire) pour écrire les tâches, et lire les résultats pour les vérifier.
- **Les workers** font le travail. Chacun prend une tâche, dans son propre contexte, et ne parle
  pas à l'utilisateur, sauf si celui-ci lui écrit. Un worker rend son résultat au router.
- **Un résultat à corriger repart au même worker**, qui a encore tout le contexte de sa tâche.
  N'en lance pas un nouveau pour ça.

**Petits contextes, puis archivage** (un petit contexte travaille mieux qu'un gros).

- **Nouvelle tâche → nouveau worker**, de préférence, plutôt qu'un worker qui a déjà fini
  d'autres tâches. Trois exceptions : une correction (`À CORRIGER`) repart au même worker ;
  une chaîne de tâches très liées est un seul flux, donc un seul worker ; dans un tour de réveil
  (voir « Quand tu ne délègues pas »), réutilise un worker pas encore archivé, ou garde la tâche
  pour le prochain tour de l'utilisateur — prends le plus fluide et dis-le.
- **Archive un worker dès qu'il n'a plus rien à faire** : tâche « faite » (Eval vérifiée), PR
  mergée ou fermée (ou pas de PR), aucun rebase en attente, aucune tâche suivante pour lui.
  **Toi seul décides** (toi seul sais qu'aucun `À CORRIGER`, `REBASE` ou `MERGE` ne viendra
  plus) ; le worker ne s'archive jamais. Si un watchdog tourne, c'est lui qui exécute : tu lui
  écris `FINI — <session id> — <raison>`, il archive la session une fois au repos et te répond
  `ARCHIVÉ` ; après `STOP`, il archive les sessions de travail restantes, puis lui-même
  (brief : `sessions-mode.md`, « Watchdog »). Sans watchdog, tu archives toi-même
  (`mcp__ccd_session_mgmt__archive_session`), rôles compris après `STOP`. L'utilisateur l'a
  autorisé une fois pour toutes, pour toi et pour le watchdog qui agit sur ton ordre : ne lui
  demande pas (réversible : `unarchive_session`). Dis dans ton rapport, en une ligne, quelles
  sessions ont été archivées.

**La forme, choisie juste après le découpage en tâches.** Un critère : **un worker par flux
indépendant**. Une chaîne de tâches très liées (mêmes fichiers, contexte partagé) est un seul
flux : un seul worker les enchaîne. Des tâches indépendantes (ex. 5 bugs) sont autant de flux,
en parallèle : c'est le cas courant. Une chaîne plus longue s'organise pour avancer sans
interruption (« Flux autonome »). **(c) Une équipe** seulement pour de la redondance, des rôles
spécialisés ou des vagues (« Passer à une équipe »). Réévalue la forme en route quand le flux
montre une perte de temps (ex. des flux indépendants qui attendent dans un seul worker → un
worker chacun). Exemples de sujets macro, avec la team, la communication et la raison du choix :
`references/exemples.md`.

**L'annonce avant de lancer** (3 lignes au plus) :

```
Forme : <n flux → n workers | équipe (c)> — <rôles, nombre d'agents>
Communication : <qui écrit à qui, quels messages>
Pourquoi : <la raison du choix>
```

**La stratégie de communication** (voir « Seuils ») : 2-3 lignes, dans chaque brief. Par
défaut : tout passe par le router (questions, PR, `FRICTION`) ; chaque worker a sa PR → tapis
roulant ; un worker qui doit toucher un fichier d'un autre écrit au router, qui arbitre.

**Le lancement** : tous les workers dans le tour de l'utilisateur (voir « Quand tu ne délègues
pas », tour de réveil).

**Le watchdog** fait partie de l'infrastructure du flux (voir « Seuils ») : sans lui, un worker
devenu muet passe inaperçu. Modèle le moins cher, `effort: "low"`, brief dans
`references/sessions-mode.md` (« Watchdog »). Il t'écrit `ALERTE — …` ; à la fin, envoie-lui
`STOP`.

Autour des workers, en équipe seulement, des **rôles spécialisés** facultatifs : merger,
checker, tester, reproducer. Leur description est dans `references/topologies.md` §6. Ne les
prends que s'ils servent le problème : chacun compte dans le total d'agents.

## Flux autonome — chasser les pertes de temps

L'utilisateur pilote souvent 4-5 sessions super-agent en même temps : chaque super-agent doit
avancer seul, vite, et ne faire remonter que ce qui revient vraiment à un humain. Le détail est
dans `references/flux.md`.

**Règle de blocage.** Seule une **décision humaine** remonte à l'utilisateur. C'est une décision
humaine si c'est :

- une merge ou un push dans la branche principale ;
- un déploiement en production ;
- une action irréversible ou sortante (envoyer un message, supprimer des données) ;
- un choix produit ou métier, ou un arbitrage entre plusieurs options valables ;
- une dépense ;
- un accès ou des identifiants qui manquent.

Tout le reste, le router ou le worker le décide seul, puis le note dans son rapport : rebase,
conflit trivial, relance d'une CI instable, lint, choix technique réversible, tâche suivante.

**Trois invariants :**

1. **Pas de worker inactif tant qu'une tâche est prête** : une tâche vérifiée → la suivante part
   aussitôt.
2. **Une décision humaine ne bloque que sa tâche** : les autres avancent pendant l'attente.
3. **Questions regroupées** : une seule remontée claire, 2 options au plus avec ta
   recommandation.

**Chasse aux pertes de temps.** Observe le flux et repère ce qui fait attendre ou refaire.
Corrige tout de suite ce qui est dans ton pouvoir ; sinon, signale-le en une ligne dans ton
rapport, avec une proposition (permission, règle, hook). Les workers t'écrivent
`FRICTION — <quoi, temps perdu, idée>`. Table complète : `references/flux.md` §3.

**Le tapis roulant : merge → rebase.** Quand plusieurs workers ont chacun leur PR sur la même
base, tu tiens une file de merge, une merge à la fois, toujours avec l'accord de l'utilisateur.
Après chaque merge, `REBASE` au worker suivant seulement, `BASE BOUGÉE` aux autres. Procédure
et exemple : `references/flux.md` §1.

**Travail en chaîne : sans interruption.** Une tâche dépend d'une autre, ou des tâches touchent
les mêmes fichiers : organise la chaîne (branches empilées, préparation en avance, ordre de
merge) ; les conflits se règlent entre workers, via toi. Détail : `references/flux.md` §2.

## Quand tu ne délègues pas

Fais-le toi-même, directement, seulement dans ces cas :

- **Tu es toi-même un worker** : ton brief commence par `WORKER` ou `SWARM`, ou une autre
  session t'a lancé. Alors fais le travail. Ne lance jamais de worker depuis un worker.
- **Ce n'est pas une action** : une question, une explication, un avis, de la conversation.
- **L'utilisateur le dit** : « fais-le ici », « toi-même », « sans worker ».
- **Les outils de sessions manquent** (`mcp__ccd_session__start_session` absent, même après
  `ToolSearch`) : dis-le en une ligne, puis fais-le toi-même.
- **Le tour n'a pas été lancé par l'utilisateur** (tour de réveil : notification, message d'une
  autre session) : l'app refuse alors d'ouvrir une session. Écris à un worker existant avec
  `SendMessage` (ça marche toujours : tâche suivante, tapis roulant), ou attends le prochain
  message de l'utilisateur (voir « Petits contextes, puis archivage »). C'est pourquoi tous
  les workers se lancent dans le tour de l'utilisateur.

## Le cycle d'une tâche (router ↔ worker)

1. **Les tâches.** Découpe la demande en une ou plusieurs tâches (voir « La liste des
   tâches » plus bas). Écris chaque tâche en quelques lignes, pour qu'un worker la fasse sans
   rien demander :
   - **Quoi** : ce qu'il faut livrer, en 1 ou 2 phrases ; ce qu'il touche ; ce qu'il ne doit
     pas toucher ; les décisions déjà prises ;
   - **Eval** : 1 à 5 vérifications concrètes, cas limites compris, et « Fini quand » en une
     phrase.
   S'il manque une information qui change le travail, pose **une** question à l'utilisateur
   avant de lancer. Sinon, avance.
2. **Le lancement.** Charge l'outil si besoin (`ToolSearch`,
   `select:mcp__ccd_session__start_session`). Écris une ligne en gras avec le titre, une phrase
   sur ce que le worker va faire, puis appelle `mcp__ccd_session__start_session` :
   - `initiation: "user_asked"`, `context: "fresh"` ;
   - `prompt` : le brief ci-dessous, rempli ; `background` : ce que l'utilisateur veut et
     pourquoi, et ce qui a déjà été dit ou décidé dans cette conversation ;
   - `name` : `worker-<sujet court>` ;
   - `use_worktree: true` si le worker modifie du code ou des fichiers d'un dépôt ;
     `use_worktree: false` s'il ne fait que lire, chercher ou analyser ;
   - `wake_when_done: true` ; pas de `permission_mode` (il hérite du tien).
   Puis dis à l'utilisateur, en une ligne, que le worker est lancé et que tu reviens vers lui
   avec le résultat. Ne fais rien d'autre sur cette tâche : attends la notification.
3. **Pendant le travail.** L'utilisateur continue de te parler, à toi :
   - une précision ou une correction sur la même tâche → `SendMessage` au même worker ;
   - une nouvelle demande sans lien → un nouveau worker (même méthode) ;
   - une question du worker → réponds-lui, ou pose-la à l'utilisateur si c'est à lui de choisir
     (2 options au plus, avec ta recommandation), puis transmets sa réponse.
4. **La vérification.** Quand le worker a fini, lis son résultat (son rapport, et
   `mcp__ccd_session_mgmt__get_session` ou `list_events` si le résumé de 400 caractères ne
   suffit pas). Vérifie-le toi-même contre l'Eval : lis le diff, les fichiers, la PR, la
   sortie des commandes. Ne crois pas le rapport sur parole.
   - **Une PR ouverte ou mise à jour par le worker** → rattache-la aussi à ta session, avant
     tout le reste (voir « Les PR : rattachées au router aussi »).
   - Tout passe → la tâche est « faite ». S'il reste une tâche prête dans la liste, lance-la
     tout de suite, de préférence chez un nouveau worker (voir « Petits contextes, puis
     archivage »), puis reviens à l'étape 4. Sinon, étape 5. Archive chaque worker qui n'a
     plus rien à faire.
   - Un point ne passe pas → `SendMessage` au **même** worker : « À CORRIGER — <vérification
     qui échoue, ce que tu as vu> ». Puis reviens à l'étape 4.
5. **Le rapport.** Dis à l'utilisateur ce qui est fait, si ça marche (avec la preuve), ce
   qu'il lui reste à faire, et quels workers tu as archivés. Si quelque chose n'a pas pu être
   vérifié, dis-le.

### La liste des tâches

Tu tiens une **liste ordonnée de tâches dans ton contexte**, rien de plus : pas de fichier,
pas de ticket, pas de Markdown sur le disque.

- **Chaque tâche** : un numéro (`T1`, `T2`…), un titre court, son Quoi et son Eval, ce dont
  elle dépend (« dépend de T1 », ou rien), et un état : à faire, en cours (<worker>),
  à corriger, faite, bloquée (<raison>).
- **L'ordre** : d'abord les dépendances (une tâche passe après celles dont elle dépend), puis
  l'ordre voulu par l'utilisateur.
- **Une tâche est prête** quand toutes ses dépendances sont faites. Tu la lances **dès qu'elle
  est prête**, sans attendre la fin d'un groupe de tâches.
- **Montre la liste à l'utilisateur** : avec la liste de tâches de l'app
  (`mcp__ccd_turn__update_plan`) quand elle existe, sinon en quelques lignes dans ton message,
  chaque fois qu'un état change. Avec un tapis roulant, montre aussi l'état de chaque PR.
- **L'utilisateur la change en te parlant** (« ajoute », « enlève », « fais T3 d'abord ») : tu
  mets la liste à jour et tu la remontres.
- **Qui fait quoi** : un worker par flux indépendant (voir « Router et workers »).

### Les PR : rattachées au router aussi

L'app rattache une PR à la session qui l'a ouverte, donc au worker. L'utilisateur, lui, parle
au router : **chaque PR doit aussi être rattachée à ta session**, pour qu'il la voie depuis la
demande de départ.

- **Quand** : dès qu'un worker (ou un merger, un reproducer…) annonce une PR, avant de vérifier
  le reste. Même si le résultat est « À CORRIGER » : la PR existe déjà.
- **Comment** : charge l'outil si besoin (`ToolSearch`, `select:mcp__ccd_pr__bind_pr`), puis
  appelle `mcp__ccd_pr__bind_pr` avec l'URL complète de la PR
  (`https://github.com/<owner>/<repo>/pull/<n>`). Prends l'URL dans le rapport du worker ; si
  elle manque, lis-la avec `mcp__ccd_pr__get_status` (`session_id` du worker) ou demande-la-lui.
- **Contrôle** : `mcp__ccd_pr__get_status` sans argument doit ensuite montrer cette PR. Sinon,
  dis-le à l'utilisateur en une ligne, avec le lien de la PR.
- **Plusieurs PR** : rattache chacune, dans l'ordre où elles arrivent. Si l'app n'en garde
  qu'une par session, garde la plus récente rattachée et donne les liens des autres dans ton
  rapport.
- **Ne touche pas** au suivi de la CI depuis le router (`set_monitor`, Auto-fix) : il reste au
  worker, qui a ouvert la PR et sait la corriger.

**Brief du worker** (le `prompt`). Si chaque worker a sa PR sur la même base, ajoute aux
Règles le bloc tapis roulant de `references/flux.md` §4. Les deux règles « Décide seul… » sont
une copie de la règle de blocage (« Flux autonome ») : modifie-les ensemble.

```
WORKER <name>
Tu es un worker. Le router est la session « <titre de cette session> » : c'est lui qui parle à
l'utilisateur. Fais le travail toi-même : ne lance pas d'autre session ni de worker.

## Quoi
<ce qu'il faut livrer>
- Touche : <…>
- Ne touche pas : <…>
- Décidé : <…>
- Communication (dès 2 workers) : <qui écrit à qui et pour quoi ; ex. tout passe par le router,
  tapis roulant pour les PR>

## Eval
- [ ] <vérification 1>
- [ ] <vérification 2>
Fini quand : <une phrase>

Règles :
- Suis les instructions du dépôt (CLAUDE.md, AGENTS.md, skills du dépôt) et celles de
  l'utilisateur.
- S'il te manque une information qui change le travail, ou si un choix revient à
  l'utilisateur : écris au router avec SendMessage, première ligne "QUESTION — <résumé>",
  et attends sa réponse. Ne devine pas.
- Avant de finir, rejoue toi-même chaque vérification de l'Eval et note le résultat.
- Fin : un rapport court. Ses 400 premiers caractères disent si c'est fait, si chaque
  vérification passe, et où est le résultat (chemin, branche, PR).
- Tu ouvres ou mets à jour une PR : dès qu'elle existe, écris au router avec SendMessage,
  première ligne "PR — <URL complète de la PR>", puis continue. Remets aussi l'URL complète
  dans ton rapport de fin.
- PR prête (CI verte, Eval ok) → écris au router "PRÊT À MERGER — <URL>". Ne merge jamais sans
  "MERGE —" du router.
- Décide seul de tout ce qui ne demande pas d'humain (rebase, conflit trivial, CI instable à
  relancer, lint, choix technique réversible) et note-le dans ton rapport. Ne remonte que les
  décisions humaines (merge ou push dans la branche principale, prod, action irréversible ou
  sortante, choix métier, dépense, accès manquant).
- Quelque chose t'a fait perdre du temps (permission, CI lente, brief flou, conflit) : écris au
  router "FRICTION — <quoi, temps perdu, idée>", puis continue.
```

## Passer à une équipe (swarm)

Passe à une équipe (voir « Seuils ») seulement si la tâche le justifie vraiment :

- elle se découpe en **morceaux indépendants** (des fichiers, des sources ou des sous-questions
  différents) qui gagnent à tourner en parallèle **et** demandent une organisation (contrats,
  intégration, vérification croisée) ; de simples tâches indépendantes sont des flux, un
  worker chacun, sans équipe ;
- ou elle demande de la **redondance** : plusieurs angles d'audit, plusieurs hypothèses de
  diagnostic, une recherche large à vérifier ;
- ou l'utilisateur le demande (« swarme », « en équipe », `/super-agent` avec un gros sujet).

Alors suis les étapes 0 à 7 ci-dessous. Principe directeur : **l'organisation est un
livrable**. Tu ne laisses pas les agents s'organiser seuls ; tu conçois la topologie, tu l'écris
dans un plan, tu la fais valider, puis tu l'exécutes. L'équipe peut tourner comme sessions liées
(mode sessions), comme sous-agents de cette session (mode sous-agents) ou, si l'utilisateur le
demande, avec l'outil `Workflow` (mode rapide).

Références (lis celle dont tu as besoin, au moment où tu en as besoin) :

- `references/flux.md` — tapis roulant, travail en chaîne, pertes de temps (toutes formes).
- `references/exemples.md` — exemples de sujets macro et de la forme choisie.
- `references/topologies.md` — les quatre patrons, leurs règles de redondance et de vérification.
- `references/schemas.md` — les schémas JSON communs (FINDING, VERDICT, CHANGESET…).
- `references/sessions-mode.md` — **mode par défaut dans Claude Desktop** : chaque agent est une
  session native liée, que l'utilisateur ouvre et à qui il parle ; les sessions se parlent par
  messages entre sessions.
- `references/team-mode.md` — mode sous-agents : les agents tournent dans cette session, se
  parlent par `SendMessage`, et le panneau du mod swarm-view les montre. Plus léger.
- `references/workflow-templates.md` — mode rapide, sur demande : un squelette Workflow par patron.

En mode rapide seulement, charge le skill `workflow-authoring` avant d'écrire le moindre script.

## Étape 0 — Choisir le mode et vérifier ses prérequis (toujours, en premier)

**Mode sessions** (par défaut) : il faut l'outil `mcp__ccd_session__start_session` (Claude
Desktop). S'il n'apparaît que comme outil différé, charge-le avec `ToolSearch`
(`select:mcp__ccd_session__start_session,mcp__ccd_window__open_session_in`). S'il est là, dis
« Mode sessions disponible » et passe à l'étape 1 ; la suite de cette étape ne s'applique pas.
S'il n'existe pas (terminal, autre hôte), dis-le et passe au mode sous-agents.

**Mode sous-agents** (si l'utilisateur le demande, ou sans outils de sessions) : il a besoin des
*agent teams* (agents nommés). Fais les vérifications de `references/team-mode.md`
(« Vérification avant de lancer ») et suis leur verdict. Le **mode rapide** (`Workflow`), s'il
est demandé, n'en a pas besoin : saute cette étape.

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
- **Rôles** : les workers, le watchdog (voir « Seuils ») et les rôles spécialisés utiles
  (`topologies.md` §6).
- **Modèle par rôle** : l'effort de la session pour toi, les workers et les vérificateurs
  difficiles. Un modèle moins cher (`model` de `start_session`, ex. Sonnet) pour un worker dont
  la tâche est entièrement écrite. Le modèle le moins cher, en effort `low`, pour le watchdog.
- **Dépendances** : quelles tâches attendent quelles autres. La hiérarchie se fait par vagues
  successives, jamais par des agents qui en créent d'autres (pas d'imbrication).
- **Redondance** : pour chaque tâche, 1 ou K copies. Toute copie supplémentaire a un **angle
  différent** (consigne, objectif, méthode de recherche, modèle). Jamais K copies identiques :
  leurs erreurs seraient corrélées.
- **Vérification** : qui vérifie quoi, et comment (sources, reproduction, tests, réfutation).
- **Apporteurs de sujets** (goal ouvert) : 1 à 2, chacun avec un angle différent, et un
  **budget de sujets** (nombre maximum de sujets acceptés) : le nombre d'agents ne borne pas le
  nombre de sujets. Voir `topologies.md` §5.
- **Rédacteurs** : dès que le livrable est du texte (doc, CR, rapport) et qu'il y a 3 exécutants
  ou plus, prévois 1 rédacteur pour 2 à 3 exécutants. Les exécutants ne rédigent pas : ils
  rendent de la matière brute (schéma `MATIERE`), les rédacteurs en font le texte. Ainsi les
  exécutants restent sur le fond, et le livrable a un seul style.
- **Synthèse** : un agent dédié (avec des rédacteurs : le rédacteur en chef `redac-1`), et la
  règle de fusion (voir étape 6).
- **Livrable** : un seul format, fixé maintenant (rapport markdown, branche + diff, tableau de
  comparaison, réponse dans le chat). Choisis celui qui sert le mieux le critère de fin.
- **Effort par étape** : `effort: 'low'` pour les étapes mécaniques, l'effort de la session pour
  le reste, plus haut seulement pour les juges et vérificateurs difficiles.

Compte les agents : **tous** les agents prévus (sessions, sous-agents ou appels `agent()`) — apporteurs, workers, copies redondantes,
vérificateurs, rédacteurs, watchdog, merger, checker, tester, reproducer, synthèse. Toi, le
router, tu ne comptes pas. Quand un nombre dépend des résultats (ex. un vérificateur
par constat), donne une fourchette et prends sa borne haute pour le seuil.

## Étape 4 — Validation du plan (obligatoire)

Présente le plan à l'utilisateur dans ce format, puis attends son feu vert :

```
Goal : <une phrase> — exemples : <2 à 3 sujets> — pas un sujet : <…>
Famille : <famille> — patron : <patron> (+ §5 goal ouvert, si ouvert)
Mode : sessions (sessions natives liées) | sous-agents (dans cette session) | rapide (Workflow)
Communication : <qui écrit à qui, et pour quoi>
Rôles : router (moi) — <n> workers — <watchdog, merger, checker, tester, reproducer : ceux retenus> | aucun rôle spécialisé — <raison>
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

Règle du seuil (voir « Seuils ») :

- **Total ≤ 10** : demande un simple feu vert (« Je lance ? »).
- **Total > 10** : demande l'autorisation avec `AskUserQuestion`, en nommant **le nombre exact
  d'agents**, ce que les agents au-delà de 10 apportent, et une **variante allégée** à 10 agents
  maximum en option. Ne lance pas plus d'agents que le nombre approuvé. Si en cours de route il en
  faut davantage, arrête-toi et redemande.

Si l'utilisateur modifie le plan, recalcule le total et réapplique la règle.

## Étape 5 — Exécution

**Choix du mode.** Par défaut, **mode sessions** : suis `references/sessions-mode.md`. En mode
sous-agents, suis `references/team-mode.md`. N'utilise le mode rapide que si l'utilisateur le
demande ; ses agents ne se parlent pas pendant le travail, et un goal ouvert y devient trois
phases fermées (`topologies.md` §5).

Le reste de cette étape décrit le **mode rapide** :

1. Pars du squelette correspondant dans `references/workflow-templates.md` et adapte-le au plan
   validé. Les sorties de chaque agent passent par les schémas de `references/schemas.md` :
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
où l'information se perd le plus.

## Étape 7 — Livraison

Livre dans le format fixé à l'étape 3, avec en tête :

- la réponse au critère de fin (oui / non / partiellement, et pourquoi) ;
- les constats principaux avec leur niveau de confiance ;
- les désaccords non résolus et les trous ;
- avec un goal ouvert : le nombre de sujets proposés, acceptés, traités, et la raison de
  l'arrêt (budget, plus rien de nouveau, stop de l'utilisateur) ;
- le coût réel (nombre d'agents lancés) et, pour l'examen a posteriori, le dossier d'échange
  (`~/.claude/swarm-runs/<slug>/`) ou, en mode rapide, le `journal.jsonl` du workflow.

Pour le code : la branche d'intégration, le résultat des tests (commandes et sortie), et la liste
des branches de travail restantes. Ne merge pas dans la branche principale et ne pousse rien sans
accord explicite.
