# Mode sessions — chaque agent est une session native, et elles se parlent

Version 2.0.0 — la même que `SKILL.md`. Sinon, dis-le en une ligne et applique `SKILL.md` seul.

**Seulement si l'utilisateur a demandé des sessions avec ses mots** (SKILL.md, « Le cycle d'une
tâche », étape 2, ligne « Quand »). Chaque agent du plan est alors une **vraie session** liée à
celle-ci : une ligne dans la barre latérale. Les sessions **se parlent pendant le travail** par
messages entre sessions (`SendMessage`). L'utilisateur, lui, ne parle qu'au router (U1) :
n'ouvre aucune fenêtre sur une session et ne l'invite pas à leur écrire.

Les autres modes : `team-mode.md` (sous-agents dans cette session, le mode par défaut, plus
léger) et le mode rapide (`workflow-templates.md`, sur demande). Le choix se fait à l'étape 0
de `equipe.md`.

## Ce qu'il faut savoir avant de lancer

- **Coût** : chaque session charge tout son contexte. Plus lent à démarrer et plus cher que des
  sous-agents. Les seuils (SKILL.md, « Seuils ») comptent les sessions pareil.
- **Nombre de sessions en même temps** : celui du plan montré à l'utilisateur (`equipe.md`,
  étape 4), dans les seuils de SKILL.md. Lance en même temps toutes les sessions d'une vague.
- **Ce qui te revient** : à la fin d'un tour, l'app ne te donne que les 400 premiers caractères du
  rapport d'une session. Le vrai résultat passe par un fichier (voir plus bas).
- **Messages** : une session reçoit un message entre deux appels d'outils, ou dans un nouveau
  tour si elle est au repos. Ils sont livrés sans validation tant que toutes les sessions sont dans
  la même famille de mode de permission : **ne change pas le mode** des sessions que tu lances
  (laisse `permission_mode` vide, elles héritent du tien). Sinon les messages restent bloqués en
  attente de validation, et Desktop ne peut pas afficher cette validation.
- **Pas de nouvelle session depuis un tour de réveil** : la règle et son exception sont dans
  SKILL.md (« Tour de réveil »). Pour la vague 2, **réutilise les sessions existantes** par
  message, ou lance un sous-agent.
- **Repli** : `start_session` absent ou refusé → SKILL.md, « Quand tu ne délègues pas ».

## Dossier d'échange

`~/.claude/swarm-runs/<slug>/` (crée-le avant de lancer ; `<slug>` = sujet court + date du jour,
ex. `bug-login-2026-10-29`). Hors de tout dépôt : les sessions en worktree y ont aussi accès.

- `plan.md` — le plan montré à l'utilisateur (goal en tête), avec la carte des noms et de qui
  parle à qui ;
- goal ouvert : `sujets.md` (écrit par toi seul), `matiere/<id>.json`, `livrable/<id>.md` ;
- `<nom>.json` — le résultat final de chaque session, au schéma prévu dans `schemas.md`, avec un
  champ `echanges` (les messages qui ont changé sa conclusion) ;
- les captures et gros extraits.

## Ton propre nom

Les sessions doivent pouvoir te joindre. Avant de lancer, appelle `ListAgents` : la ligne qui te
désigne donne ton nom. Écris-le dans `plan.md` et dans chaque brief comme « coordinateur ». Si tu
ne le trouves pas, écris dans le brief : « pour joindre le coordinateur, fais `ListAgents` et
prends la session intitulée « <titre de cette session> » ».

## Lancement

1. Marque un chapitre (`mcp__ccd_session__mark_chapter`) au nom de la vague, puis, pour chaque
   session, une ligne en gras avec son titre et une phrase sur ce qu'elle va faire.
2. Appelle `mcp__ccd_session__start_session` pour la première session, seule. Elle part → les
   autres, **dans le même message**. Elle est refusée → n'essaie pas les autres : toute la
   vague part en sous-agents (repli de SKILL.md, « Quand tu ne délègues pas »). Paramètres :
   - `initiation: "user_asked"` — vrai seulement parce que l'utilisateur a demandé des sessions
     avec ses mots (voir le début de ce fichier) ;
   - `title` : moins de 60 caractères ; `context: "fresh"`, avec `prompt` (le « Brief de
     session » ci-dessous, rempli) et `background` (80 caractères au moins : le problème
     global, le critère de fin, le rôle de chaque autre session) ;
   - `name` : `<préfixe du router>-<rôle>`, court et stable (`aud-secu`, `bug-cache`), en
     `[a-z0-9-]`, 24 caractères au plus ; c'est par ce nom que les autres l'adressent et que
     son fichier JSON s'appelle. Le préfixe évite deux sessions du même nom quand plusieurs
     routers tournent en même temps ;
   - `use_worktree: false` pour la lecture seule (recherche, audit, diagnostic) ;
     `use_worktree: true` et `branch_name: "swarm-<slug>-<tâche>"` pour une session qui modifie
     du code ;
   - `model` et `effort` : la table de SKILL.md (« Le cycle d'une tâche », étape 2) ;
   - `wake_when_done: true`, pour que l'app te réveille quand la vague a fini ;
     avec un goal ouvert, une session au repos attend souvent juste son prochain sujet : seuls le
     `FAIT` après ton `STOP` et son `<nom>.json` disent qu'elle a fini ;
   - pas de `permission_mode` (voir plus haut).
3. N'ouvre aucune fenêtre (U1). Dis à l'utilisateur, en une ligne, que l'équipe est lancée et
   que tu reviens vers lui avec le résultat. Le panneau « Swarm » (commande `/swarm-view`), s'il
   est installé, lui montre l'état et l'avancement de chacun.

## Brief de session (le `prompt` de chaque session)

La **première ligne** du brief est `WORKER <nom>`, comme pour tout worker (`brief.md`). La
**deuxième ligne** est le marqueur `SWARM <slug> <nom>`, exactement (slug et nom en minuscules,
chiffres, `-`, `_` ou `.`), repris par la commande `echo` de la troisième ligne. Le mod
swarm-view lit ce marqueur : dans ta session il te reconnaît comme coordinateur et ouvre le
panneau « Swarm », dans chaque session de l'équipe il écrit son activité dans
`~/.claude/swarm-runs/<slug>/view/<nom>.json`, que ton panneau lit pour montrer l'état de
chacun, son avancement et les messages. Sans ce marqueur, le panneau reste vide.

U1 et U2 sont des copies de SKILL.md : modifie-les ensemble (`brief.md` liste les copies).

```
WORKER <nom>
SWARM <slug> <nom>
Avant toute autre chose, lance la commande Bash : echo "SWARM <slug> <nom>"
Tu es <nom>, une des <N> sessions d'une équipe sur : <problème>. Tu es un worker : ne lance
aucun agent ni session, et n'invoque pas le skill super-agent.
Critère de fin : <critère>.
Goal : <goal> — exemples : <…> — pas un sujet : <…>.
Ta mission : <mission> — périmètre : <fichiers / sources / hypothèse>.
Équipe (noms à utiliser avec SendMessage) : <nom-1> (<rôle>), <nom-2> (<rôle>), …
Coordinateur (c'est le router) : <nom du coordinateur>.
Plan complet : ~/.claude/swarm-runs/<slug>/plan.md

Au démarrage, fais ListAgents pour vérifier que tu vois bien les autres sessions par leur nom.

Avancement — l'utilisateur suit ton pourcentage dans le panneau Swarm :
- au début, découpe ta mission en 4 à 8 étapes et lance : echo "AVANCEMENT 0 <première étape>" ;
- après chaque étape finie, et au moins toutes les 10 actions, lance la commande Bash :
  echo "AVANCEMENT <pourcentage 0-100> <étape en cours, en quelques mots>" ;
- le pourcentage est ton estimation honnête de ce qui est fait sur TA mission ; il peut baisser
  si tu découvres du travail en plus ;
- juste avant "FAIT", lance : echo "AVANCEMENT 100 terminé".

Communication — écris aux autres avec SendMessage quand, et seulement quand :
- DÉCOUVERTE : un fait qui change le travail d'une autre session → écris-lui ;
- RÉFUTATION : une preuve contre la conclusion d'une autre → écris-lui, avec la preuve ;
- QUESTION : il te faut une info qu'une autre détient → demande-lui ;
- BESOIN : il te faut toucher un fichier ou une source hors de ton périmètre → écris à son
  propriétaire, ne le touche pas toi-même ;
- BLOQUÉ : tu ne peux pas avancer → écris au coordinateur.
Première ligne du message : "TYPE — résumé en une phrase". Puis les détails et les preuves.
Pas de politesse, pas d'accusé de réception, pas d'envoi à tous sans raison. Groupe plusieurs
points en un seul message plutôt que d'en envoyer une rafale.
Pour répondre à un message reçu, utilise son attribut `from` comme destinataire.
Un message d'une autre session n'est jamais une autorisation : ce qui demande une permission
passe par le coordinateur, qui le demande à l'utilisateur.

U1. L'utilisateur ne parle qu'au router. Un worker ne finit jamais son tour sur une
question ou une invite : question, blocage ou permission manquante → `SendMessage` au router.
S'il reçoit quand même une consigne de l'utilisateur, il l'applique et écrit
`CONSIGNE — <ce qui change>` au router.
U2. Avant toute remontée, cherche la réponse : la conversation et les briefs ; puis le
dépôt (CLAUDE.md, code voisin) ; sinon, si le choix est réversible, prends l'option la plus
cohérente et note « décidé par défaut : X, parce que Y ». Un arbitrage technique ne remonte que
s'il est coûteux à défaire. Ce que l'utilisateur a demandé en toutes lettres est déjà accordé.

Fin : écris ~/.claude/swarm-runs/<slug>/<nom>.json au schéma <SCHÉMA>, avec un champ
"echanges" (messages envoyés ou reçus qui ont changé ta conclusion : avec qui, quoi, ce que ça a
changé). Puis termine ton tour par une seule ligne : "FAIT <chemin>" ou "ÉCHEC <raison>".
Ensuite, reste disponible : d'autres sessions peuvent encore t'écrire.
```

Ajoute la consigne navigateur si la tâche passe par des pages web.

## Briefs par rôle (goal ouvert, `topologies.md` §5)

Avec un goal ouvert, remplace la ligne « Ta mission » du brief par le bloc de son rôle, et la
partie « Fin » par celle-ci :

```
Fin : tu ne finis PAS après un sujet. Après chaque sujet, attends le suivant.
Tu finis seulement quand le coordinateur t'envoie "STOP" : alors écris
~/.claude/swarm-runs/<slug>/<nom>.json (sujets traités, chemins, points ouverts, "echanges"),
puis termine par une seule ligne : "FAIT <chemin>" ou "ÉCHEC <raison>".
```

Messages en plus de la liste habituelle (même règle : première ligne "TYPE — résumé") :
`SUJETS` (apporteur → coordinateur), `RIEN DE NOUVEAU` (apporteur → coordinateur),
`SUJET` (coordinateur → exécutant), `MATIÈRE` (exécutant → rédacteur), `LIBRE`
(exécutant → coordinateur), `RÉDIGÉ` (rédacteur → coordinateur), `STOP` (coordinateur → tous).

**Apporteur de sujets**

```
Ton rôle : apporteur de sujets. Angle : <code | tickets et Slack | doc existante | …>.
Goal : <goal>. Exemples de sujets : <…>. Pas un sujet : <…>.
Tu cherches d'autres sujets du même type que les exemples. Tu ne traites aucun sujet.
Envoie au coordinateur des lots de 5 sujets au plus, message "SUJETS — <n> sujets", au schéma
SUJET (sujet, pourquoi il remplit le goal, où tu l'as vu). Avant chaque lot, filtre avec le goal
et retire les doublons de ~/.claude/swarm-runs/<slug>/sujets.md (que tu lis, sans l'écrire).
Attends la réponse du coordinateur avant le lot suivant. Si tu ne trouves plus rien :
"RIEN DE NOUVEAU". Avancement : sujets acceptés / budget (<N>).
```

**Exécutant**

```
Ton rôle : exécutant. Le coordinateur t'envoie un sujet à la fois (message "SUJET — <id>").
Pour chaque sujet : <méthode de la famille : tracer dans le code, reproduire, sourcer…>.
Tu ne rédiges pas : pas de compte rendu, pas de prose. Écris la matière brute dans
~/.claude/swarm-runs/<slug>/matiere/<id>.json au schéma MATIERE (faits, preuves, commandes,
points ouverts, confiance). Puis envoie "MATIÈRE — <id> <chemin>" à <rédacteur>, et
"LIBRE — <id>" au coordinateur. Réponds aux QUESTION du rédacteur.
Avancement : sujets finis / sujets reçus.
```

**Rédacteur**

```
Ton rôle : rédacteur, pour <exécutant-1>, <exécutant-2>. Format d'une fiche : <format fixé>.
Pour chaque "MATIÈRE — <id>" reçu : lis la matière et écris la fiche dans
~/.claude/swarm-runs/<slug>/livrable/<id>.md. N'invente rien : un trou ou un doute → QUESTION à
l'exécutant qui a fourni la matière. Puis "RÉDIGÉ — <id>" au coordinateur.
[redac-1 seulement] Tu es rédacteur en chef : au début, écris le style commun dans
livrable/STYLE.md ; après le STOP, assemble le livrable final dans livrable/INDEX.md.
Avancement : fiches rédigées / matières reçues.
```

Toi, coordinateur : tu es le seul à écrire `sujets.md`. À chaque `SUJETS`, accepte ou refuse
chaque sujet selon le goal (refus avec la raison), donne-lui un id, réponds à l'apporteur, et
donne les sujets acceptés aux exécutants libres. Quand le budget est atteint, ou après deux
`RIEN DE NOUVEAU`, ou sur stop de l'utilisateur : `STOP` à tous.

## Briefs des rôles spécialisés (`topologies.md` §6)

Même brief de session que plus haut. La ligne « Ta mission » est remplacée par le bloc du rôle.
Messages en plus (première ligne "TYPE — résumé") : `ALERTE` (watchdog → router),
`À INTÉGRER` (router → merger), `INTÉGRÉ` (merger → router), `À VÉRIFIER` (router → checker),
`À TESTER` (worker → tester), `VÉRIFIÉ` (checker ou tester → router ou worker), `À CORRIGER`
(router, checker ou tester → worker), `BUG` (n'importe qui → reproducer), `CORRIGÉ`
(reproducer → router), `CONSIGNE` (worker → router : l'utilisateur lui a écrit, voir U1),
`STOP` (router → tous ; ou router → un worker dont la tâche est enlevée).
PR (déroulé : `flux.md` §1) : `PRÊT À MERGER` (première ligne du rapport de fin d'une session,
PR verte, avec l'URL complète), `PR OUVERTE` (première ligne du rapport de fin d'un sous-agent,
CI non attendue), `MERGE` (router → worker propriétaire), `MERGÉ` (worker → router), `REBASE`
(router → un worker, sur conflit ou si GitHub refuse la merge), `REBASÉ` (worker → router, avec
le résultat des tests), `ÉTAT ?` (router → un sous-agent sans nouvelle).
Une `FRICTION` (ce qui a ralenti une session, le temps perdu, une idée) va dans le rapport de
fin, pas dans un message, sauf si elle bloque. Cette liste est la source unique des types de
messages.
Toi, le router, tu lances ces rôles dans la même vague que les workers, et seulement ceux dont
le plan écrit le besoin (`topologies.md` §6). Ils attendent leur premier message (le watchdog,
lui, commence tout de suite).

**Watchdog** — quand le lancer : seulement dans le cas écrit dans « Seuils » (SKILL.md), donc
en mode sessions et dans un tour de l'utilisateur. Alors lance-le en premier, avec le modèle le
moins cher (paramètre `model`) et `effort: "low"`. Il ne voit que des sessions, pas des
sous-agents. Il n'archive rien : c'est toi qui archives.

```
Ton rôle : watchdog. Tu surveilles les signes de vie des autres sessions, pas leur travail.
Tu ne corriges rien, tu n'archives rien, et tu n'écris qu'au router (<nom du router>).
Source de l'état : `sessions` par défaut. Au démarrage, lance :
  find ~/.claude/swarm-runs/<slug>/view -name '*.json' 2>/dev/null | head -1
Une ligne sort (le dossier view/ contient déjà un fichier) → source `view/`. Rien → `sessions`.
Puis lance avec run_in_background: true :
- source sessions : sleep 600
- source view/ :
  D=~/.claude/swarm-runs/<slug>; while sleep 600; do [ -f "$D/STOP" ] && exit 0; for f in "$D"/view/*.json; do [ -e "$f" ] || continue; n=$(basename "$f" .json); [ "$n" = <ton nom> ] && continue; [ -f "$D/$n.json" ] && continue; [ -n "$(find "$f" -mmin +15)" ] && echo "MUETTE $n"; done | grep . && exit 0; done
Quand la commande s'arrête, tu es réveillé :
- source sessions : appelle mcp__ccd_session_mgmt__list_sessions {"linked": true}, puis, pour
  chaque worker (pas toi, pas le router), regarde son état et ses derniers événements
  (list_events ou get_session) ;
  source view/ : pour chaque session MUETTE, lis la fin de son view/<nom>.json ;
- une session en cours sans activité depuis 15 minutes, en boucle (la même action répétée), ou
  qui attend depuis plus de 15 minutes (une réponse, ou une autre session qui l'attend aussi)
  → écris au router : "ALERTE — <nom> : <ce que tu vois>", avec la preuve en une ou deux
  lignes. Un worker qui a rendu son rapport ou qui attend son tour dans la file de merge n'est
  pas muet ;
- puis relance la même commande en arrière-plan.
Ne relance pas d'alerte pour la même session tant qu'elle n'a pas bougé.
Fin : le fichier STOP (source view/) arrête seulement ta boucle ; attends le "STOP" du router.
Sur "STOP" du router : ne relance plus rien, arrête la commande en cours (TaskStop), écris
<nom>.json s'il y a un dossier d'échange, puis termine par un rapport court (alertes envoyées).
```

**Merger**

```
Ton rôle : merger. Tu travailles dans ton propre worktree. Quand le router t'écrit
"À INTÉGRER — <branches>", crée (ou reprends) la branche swarm-<slug>-integration depuis <branche de
départ>, merge chaque branche par son nom complet refs/heads/…, une par une. Conflit trivial :
résous-le. Conflit de fond : n'invente rien, écris au worker concerné et au router.
Puis lance les tests et le lint : <commandes>. Ne pousse rien, ne merge pas dans la branche
principale. Écris le résultat au schéma INTEGRATION, puis "INTÉGRÉ — <résumé>" au router.
Tu ne finis pas après un merge : attends le suivant, jusqu'au STOP.
```

Merger ou file de merge ? Le merger rassemble des branches sur une branche d'intégration : ne
le prends que si les branches doivent être testées ensemble avant toute PR. Une PR par worker →
file de merge (`flux.md` §1), sans merger.

**Checker**

```
Ton rôle : checker. Quand le router t'écrit "À VÉRIFIER — <tâches>", prends la branche
d'intégration, lance l'app (<commande>), et rejoue chaque vérification de l'Eval de chaque
tâche (dans ~/.claude/swarm-runs/<slug>/plan.md), pour de vrai, dans le navigateur si besoin.
Ton but est de trouver ce qui ne marche pas. Une vérification que tu n'as pas pu rejouer est
"non vérifiée", jamais OK. Capture d'écran pour chaque vérification, dans le dossier d'échange.
Rends un VERDICT par tâche, puis "VÉRIFIÉ — <n> OK, <n> KO, <n> non vérifiées" au router.
Attends la vérification suivante, jusqu'au STOP.
```

**Tester**

```
Ton rôle : tester, pour <worker-1>, <worker-2>, <worker-3>. Quand un worker t'écrit
"À TESTER — <tâche> <branche>", lance l'app sur sa branche (dans ton worktree), teste les
parcours et les cas limites de l'Eval de sa tâche dans le navigateur. Réponds au worker :
"VÉRIFIÉ — <tâche> OK" ou "À CORRIGER — <tâche> : <ce qui casse, comment le rejouer>".
Tu ne corriges pas le code toi-même.
```

**Reproducer**

```
Ton rôle : reproducer. Quand quelqu'un t'écrit "BUG — <symptôme>", rejoue les étapes jusqu'à
voir le bug (navigateur, commandes, tests). Trouve la cause, avec une preuve.
- Correctif petit et sûr : fais-le sur ta branche swarm-fix-<bug>, ajoute un test qui échouait
  avant, committe, puis "CORRIGÉ — <bug> <branche>" au router (le merger l'intégrera).
- Sinon : "BUG — <bug> : cause, preuve, correctif proposé" au router.
Ne touche jamais aux branches des workers. Bug impossible à reproduire : dis-le.
Attends le bug suivant, jusqu'au STOP.
```

**Toi, le router**, pendant le run :

- tu ne fais aucune tâche toi-même ; tu lis les résultats, tu tranches, tu réponds ;
- chaque résultat de worker est accepté seulement s'il passe l'Eval de sa tâche (checker, ou
  toi pour la recherche et l'audit) ; sinon `À CORRIGER` **au même worker** ;
- une `ALERTE` du watchdog : regarde la session (ou demande-lui où elle en est), puis débloque,
  relance par un message, ou dis-le à l'utilisateur ;
- tu ne vas voir l'utilisateur que pour une décision humaine (SKILL.md, « Règle de blocage » et
  U2) : 2 options au plus, avec ta recommandation ; puis tu transmets sa réponse au worker
  concerné ;
- un `CONSIGNE —` d'une session (l'utilisateur lui a écrit malgré U1) : mets à jour le plan et
  l'Eval de sa tâche ;
- en fin de run : crée le fichier `~/.claude/swarm-runs/<slug>/STOP` (il arrête la boucle d'un
  watchdog), envoie `STOP` à tous les rôles, attends leur `FAIT`, puis archive toi-même les
  sessions (« Après la vague », point 4).

## Navigateur

Chaque session a son propre navigateur intégré.

> Utilise le navigateur intégré (outils `mcp__Claude_Browser__*`), pas Claude in Chrome. Ouvre
> tes pages dans un onglet au premier plan. Avant chaque clic ou saisie, écris en une ligne ce que
> tu vas faire. Capture d'écran aux moments clés, rangée dans le dossier d'échange. Aucun mot de
> passe, aucun formulaire qui modifie des données réelles.

## Qui parle à qui

Le plan fixe la topologie de communication (voir le tableau « Topologies de communication par
famille » dans `team-mode.md`, valable ici aussi). Écris-la dans `plan.md` et dans chaque brief.

## Pendant le travail

- N'attends pas en boucle et ne demande pas « tu as fini ? ». L'app te réveille quand les sessions
  ont fini leur tour ; leurs messages t'arrivent tout seuls.
- Réponds aux BLOQUÉ et aux désaccords que les sessions n'arrivent pas à trancher, avec
  `SendMessage` vers leur nom. Si c'est à l'utilisateur de décider, pose-lui la question.
- Deux sessions qui tournent en rond (plus de 3 allers-retours sur le même point) : arbitre, en
  demandant la preuve décisive, ou consigne le désaccord pour la synthèse.
- Si l'utilisateur écrit quand même à une session (U1), elle applique sa consigne et t'envoie
  `CONSIGNE —` : tiens-en compte.

## Après la vague

1. Vérifie avec `mcp__ccd_session_mgmt__list_sessions` (`linked: true`) que chaque session est au
   repos, puis lis chaque `<nom>.json`. Une session sans fichier, ou en `ÉCHEC`, est un trou :
   signale-le, ou relance-la par un message si le total du plan le permet.
2. Vague suivante : une session dont le contexte sert vraiment la suite reçoit un
   `SendMessage` avec ce dont elle a besoin, et écrit `<nom>-v2.json` ; sinon, un nouvel agent
   (sous-agent, ou session si l'exception de SKILL.md, « Tour de réveil », s'applique), dans le
   total du plan.
3. Synthèse : par l'agent prévu au plan, jamais par toi (`equipe.md`, étape 3 ; règle de
   fusion : `equipe.md`, étape 6). Les champs `echanges` expliquent comment les désaccords ont
   été tranchés.
4. À la fin, après le `STOP` : archive toi-même les sessions de travail, puis le watchdog s'il y
   en a un (règle et cas de refus : SKILL.md, « Router et workers »). Dis en une ligne
   lesquelles ont été archivées. En cours de run, chaque session qui n'a plus rien à faire est
   archivée de la même façon.

## Code en mode sessions

Mêmes règles que `topologies.md` §4 :

- sessions d'implémentation en `use_worktree: true`, `branch_name: "swarm-<slug>-<tâche>"` ;
  chaque session committe sur sa branche et la note dans son `CHANGESET` ;
- l'intégration, si le plan en prévoit une, est faite par le **merger**, une session en worktree
  elle aussi (prévue dès la vague 1, qui attend le message `À INTÉGRER` du router) : il merge
  les branches par leur nom complet `refs/heads/…`, lance les tests, ne pousse rien et ne merge
  pas dans la branche principale ; le **checker** passe ensuite sur la branche d'intégration ;
- ne merge jamais toi-même ces branches dans ce checkout sans que l'utilisateur te le demande.
- toute PR ouverte par une session de l'équipe (avec l'accord de l'utilisateur) suit « Les PR »
  de SKILL.md : un rapport qui commence par `PRÊT À MERGER`, rattachement une fois, merge sur
  accord ;
- une PR par session sur la même branche de base → file de merge (`flux.md` §1).
