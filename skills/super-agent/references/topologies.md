# Catalogue des topologies

Quatre patrons, un par famille. Chacun fixe : la forme des vagues, la règle de redondance, la
méthode de vérification et le livrable par défaut. Un cinquième (§5, goal ouvert) s'ajoute à la
famille quand le livrable est une collection qui peut grandir : apporteurs de sujets,
exécutants, rédacteurs. Combine-les en séquence si le problème l'exige
(ex. diagnostic → code), en comptant les agents de toutes les séquences dans le total.

Dans tous les patrons, tu es le **router** et les agents qui font le travail sont les
**workers** (SKILL.md, « Router et workers »). Les rôles spécialisés (watchdog, merger, checker,
tester, reproducer) sont décrits au §6 et s'ajoutent à n'importe quel patron.

Ordres de grandeur indiqués pour un problème moyen ; adapte au découpage réel.

---

## 1. Recherche / analyse — « carte puis fusion »

**Quand** : question large, plusieurs sources ou sous-questions indépendantes.

**Vagues**

1. **Exploration** (3 à 6 agents) : une sous-question par agent. Les sous-questions sont
   disjointes et, ensemble, couvrent la question. Chaque agent rend des `FINDING` sourcés.
2. **Vérification** (1 à 3 agents) : sur les constats qui portent la conclusion, un vérificateur
   va relire la source primaire et rend un `VERDICT`.
3. **Synthèse** (1 agent) : fusion selon la règle de SKILL.md, étape 6.

**Redondance** : par diversité de méthode, pas par duplication. Pour une sous-question critique,
deux agents avec des angles différents (ex. sources académiques vs retours terrain ; recherche
par entité vs recherche par période). Option « critique de complétude » : un agent final qui
cherche ce qui manque (source non lue, angle non exploré) ; ce qu'il trouve devient une vague
supplémentaire si le budget approuvé le permet.

**Vérification** : une affirmation est confirmée si sa source primaire la soutient vraiment.
Écarte les affirmations dont la seule source est une reprise d'une autre.

**Livrable par défaut** : rapport markdown sourcé, ou tableau de comparaison.

**Piège** : sous-questions qui se recouvrent, ce qui produit des doublons qui ressemblent à une
confirmation indépendante. Dédoublonne avant de compter les accords.

---

## 2. Audit / revue — « angles multiples puis contre-expertise »

**Quand** : un objet fixe (code, PR, schéma, configuration, document) à examiner.

**Vagues**

1. **Revue par angle** (3 à 5 agents) : un angle par agent (ex. correction, sécurité,
   performance, cohérence avec l'existant, couverture de tests). Pour un objet volumineux,
   croise angle × partition (mais surveille le total). Chaque agent rend des `FINDING` avec
   localisation précise (`fichier:ligne`).
2. **Dédoublonnage** (code, pas d'agent) : même localisation + même défaut = un seul constat.
3. **Contre-expertise** (1 agent par constat grave, borne haute à prévoir) : un vérificateur
   chargé de **réfuter**, avec un angle distinct de celui qui a trouvé (ex. « est-ce que ça se
   reproduit ? », « est-ce que le contexte appelant l'empêche ? »). Constat retenu s'il n'est pas
   réfuté. Les constats mineurs passent sans contre-expertise, marqués « non confirmé ».
4. **Synthèse** (1 agent) : classement par gravité.

**Redondance** : concentrée sur les constats graves (vérification), pas sur la recherche.

**Livrable par défaut** : rapport de constats classés, avec localisation et scénario d'échec.

**Piège** : un vérificateur prompté pour confirmer confirme. Prompte toujours pour réfuter, avec
« réfuté par défaut si incertain ».

---

## 3. Diagnostic / debug — « hypothèses concurrentes »

**Quand** : un symptôme observé, une cause inconnue.

**Vagues**

0. **Repérage** (toi, inline) : rassemble le symptôme, les logs, la chronologie, le périmètre.
   Liste 3 à 5 hypothèses réellement distinctes.
1. **Enquête** (1 agent par hypothèse) : chaque agent cherche des preuves **pour et contre** son
   hypothèse, et une expérience qui la départagerait. Rend un `HYPOTHESIS`.
2. **Réfutation croisée** (1 agent par hypothèse encore debout) : chaque agent reçoit toutes les
   conclusions de la vague 1 et tente de réfuter une hypothèse **autre que la sienne d'origine**.
   C'est une barrière : elle a besoin de tous les résultats. Lance-la dans un second workflow,
   après avoir lu ceux de la vague 1.
3. **Synthèse** (1 agent) : hypothèse survivante, preuves, expérience de confirmation proposée.

**Redondance** : c'est le désaccord organisé. Si toutes les hypothèses de départ se ressemblent,
le patron ne sert à rien ; reformule-les avant de lancer.

**Vérification** : la reproduction ou une preuve directe (log, trace, requête), jamais le vote.
Une hypothèse confirmée par 3 agents sans preuve reste « non confirmée ».

**Livrable par défaut** : réponse dans le chat ou court rapport : cause, preuves, correctif
proposé. Si le correctif est du code, enchaîne sur le patron 4 (nouveau plan, nouvelle validation).

**Piège** : en production, aucun agent n'agit (redémarrage, écriture, purge). Lecture seule.

---

## 4. Implémentation de code — « contrats, parallèle, intégration »

**Quand** : construire ou modifier du code découpable en morceaux qui touchent des fichiers
disjoints.

**Vagues**

1. **Contrats** (1 agent, sans isolation, lecture seule) : à partir du besoin et du code existant,
   définit les interfaces entre morceaux (signatures, types, formats d'échange), découpe en
   tâches et attribue à chaque tâche une liste de fichiers **disjointe**. Rend un `CONTRACT_PLAN`.
   S'il détecte un fichier partagé incontournable ou un couplage fort, il le signale
   (`separable: false`) et **le swarm s'arrête** : propose une session unique.
   Présente ce découpage à l'utilisateur avant la vague 2 (il fait partie du plan validé).
2. **Implémentation** (1 worker par tâche, `isolation: 'worktree'`) : chaque worker ne modifie que
   ses fichiers, écrit ou adapte les tests de son morceau, les exécute, **committe** dans son
   worktree et rend un `CHANGESET` (branche, commit, fichiers touchés, tests lancés et résultat).
   Un agent qui a besoin de toucher un fichier hors de sa liste s'arrête et le signale dans
   `blocked_on`, il ne le modifie pas.
   Un worker peut s'appuyer sur un **tester** (§6) pour les tests dans le navigateur.
3. **Intégration** (le **merger**, §6 ; `isolation: 'worktree'` lui aussi, pour ne jamais
   déplacer le HEAD ni toucher le checkout de l'utilisateur) : crée une branche d'intégration
   depuis la branche de départ, y merge les branches des `CHANGESET` une par une, résout les
   conflits triviaux, lance la suite de tests complète et le lint. Rend un `INTEGRATION`.
4. **Vérification** (le **checker**, §6, et 1 relecteur si le diff est gros) : le checker teste
   les fonctionnalités mergées pour de vrai, contre l'Eval de chaque tâche ; le relecteur relit
   le diff d'intégration contre les contrats (patron 2 réduit).
5. **Synthèse** : c'est toi qui rapportes, pas un agent (branche, tests, revue, restes).

Un **reproducer** (§6) peut tourner pendant tout le run : quand une partie de l'app casse, il
reproduit le bug et propose un correctif.

**Une PR par worker** → tapis roulant (`references/flux.md`), qui remplace ou complète
l'intégration par le merger.

**Redondance** : rare. Seulement pour une pièce petite et critique (algorithme délicat) : deux
implémentations avec des approches différentes, départagées par les tests et une revue.
Sinon la redondance est dans la vérification : tests + revue.

**Vérification** : les tests passent sur la branche d'intégration. Une revue d'agent ne remplace
jamais un test qui échoue.

**Livrable par défaut** : branche d'intégration + diff + sortie des tests. Pas de merge dans la
branche principale, pas de push, pas de PR sans accord explicite.

**Pièges**

- Un worktree sans changement est supprimé automatiquement : un agent qui n'a rien committé ne
  laisse rien à intégrer ; son `CHANGESET` doit le dire.
- Les agents isolés ne voient pas les fichiers non commités du checkout principal : committe ou
  passe dans le prompt ce dont ils ont besoin.
- Les dépendances entre tâches (B utilise le module de A) se gèrent par le contrat (interface
  fixée en vague 1), pas en faisant attendre B sur A. Si B a vraiment besoin du code de A,
  ce sont deux vagues distinctes, ou une seule tâche.

---

## 5. Goal ouvert — « apporteurs, exécutants, rédacteurs »

**Quand** : le goal est une **collection qui peut grandir** : une doc de questions (« qu'est-ce
qui se passe quand je fais X ? »), une FAQ, des cas de test, des points d'audit, des pages à
écrire. Ce patron **s'ajoute** à la famille retenue : les exécutants suivent ses règles de
vérification (une doc de questions suit en général le patron 1, recherche).

Hors de ce cas (goal fermé : un bug, une décision), le plan peut s'en passer, mais il le dit :
`Apporteurs : aucun — <raison>`.

**Le goal, comme filtre** (en tête de `plan.md` et de chaque brief) :

- une phrase : à quoi sert le travail, pour qui ;
- 2 à 3 exemples de sujets qui le remplissent (souvent ceux donnés par l'utilisateur) ;
- ce qui **n'est pas** un sujet (ex. « comment installer » : une procédure, pas une conséquence).

**Rôles**

1. **Apporteurs de sujets** (1 à 2, chacun avec un angle différent : ex. l'un lit le code pour
   trouver les actions qui ont des effets, l'autre lit tickets, Slack et doc existante pour trouver
   les questions déjà posées ou sans réponse). Ils cherchent **d'autres sujets du même type** que
   les exemples du goal. Ils ne traitent jamais un sujet.
   - Ils proposent par **lots de 5 au plus**, au coordinateur, message `SUJETS`, au schéma `SUJET`
     de `schemas.md` (le sujet, pourquoi il remplit le goal, où ils l'ont vu).
   - Avant d'envoyer, ils filtrent eux-mêmes avec le goal et retirent les doublons de
     `sujets.md` (même sujet reformulé = doublon).
   - Ils attendent la réponse du coordinateur avant le lot suivant (elle leur apprend ce qui
     est accepté, et pourquoi le reste ne l'est pas).
   - S'ils ne trouvent plus rien : message `RIEN DE NOUVEAU`.
2. **Coordinateur** (toi) : **seul** à écrire `sujets.md` (id stable `s-01`, `s-02`…, statut :
   proposé, accepté, refusé + raison, en cours <nom>, matière prête, rédigé). Tu acceptes ou
   refuses chaque sujet selon le goal, tu donnes chaque sujet accepté à un exécutant libre
   (message `SUJET`), et tu tiens le budget de sujets.
3. **Exécutants** (le gros de l'équipe) : un sujet à la fois. Ils cherchent, tracent,
   reproduisent, prouvent, selon les règles de la famille. Ils **ne rédigent pas** : pas de
   compte rendu, pas de prose. Ils écrivent la matière brute dans
   `~/.claude/swarm-runs/<slug>/matiere/<id>.json` (schéma `MATIERE` : faits, preuves, commandes,
   sources, points ouverts), envoient `MATIÈRE — <id>` à leur rédacteur, puis `LIBRE — <id>` au
   coordinateur, et attendent le sujet suivant.
4. **Rédacteurs** (1 pour 2 à 3 exécutants) : ils transforment la matière en texte, au format du
   livrable fixé à l'étape 3 (une fiche par sujet, un CR…), dans
   `~/.claude/swarm-runs/<slug>/livrable/<id>.md`. Ils n'inventent rien : un trou ou un doute →
   `QUESTION` à l'exécutant qui a fourni la matière. Puis `RÉDIGÉ — <id>` au coordinateur.
   Le premier rédacteur (`redac-1`) est aussi **rédacteur en chef** : il fixe le style commun au
   début et assemble le livrable final à la fin.

**Boucle et arrêt**

- Tous les rôles démarrent **dans la vague 1** : pendant le run, on ne lance pas de nouvelle
  session (voir `sessions-mode.md`). Les sujets circulent par messages vers les sessions qui
  tournent déjà ; jamais « une session par sujet ».
- Personne ne finit après un sujet : il attend le suivant. `FAIT` n'arrive qu'après un `STOP`.
- Arrêt quand : le **budget de sujets** est atteint, ou les apporteurs ont dit deux fois
  `RIEN DE NOUVEAU`, ou l'utilisateur dit stop. Tu envoies alors `STOP` à chacun : apporteurs et
  exécutants écrivent leur `<nom>.json` et finissent ; les rédacteurs finissent leurs fiches en
  cours, `redac-1` assemble le livrable, puis ils finissent.

**Avancement** (panneau Swarm) : exécutants et rédacteurs = sujets finis / sujets reçus ;
apporteurs = sujets acceptés / budget de sujets.

**Exemple** — doc « qu'est-ce qui se passe quand je fais X ? » : 2 apporteurs (code ; tickets
et Slack), 3 exécutants qui tracent chaque action dans le code et la reproduisent si possible,
1 rédacteur qui écrit une fiche par question au même format (la question, ce qui se passe étape
par étape, les effets visibles, les pièges). Total 6 agents, budget 20 sujets.

**Redondance et vérification** : celles de la famille, portées sur la **matière** (avant la
rédaction). Un vérificateur peut relire quelques fiches contre leur matière, pour attraper ce que
la rédaction a déformé.

**Pièges**

- Le même sujet reformulé deux fois : dédoublonne avec l'id, pas avec le texte.
- La dérive hors goal : un sujet intéressant mais hors goal est refusé, avec la raison.
- Le rédacteur qui comble un trou par une supposition : il demande, il ne devine pas.
- Le mode rapide (`Workflow`) ne fait pas de boucle ouverte : là, le patron devient trois
  phases fermées (apporteurs jusqu'au budget, puis exécutants, puis rédacteurs).

---

## 6. Rôles spécialisés — watchdog, merger, checker, tester, reproducer

Ils s'ajoutent au **router** (toi) et aux **workers**. Chacun a un seul métier, et aucun ne parle
à l'utilisateur. Ne prends que ceux qui servent le problème : chacun compte dans le total.

| Rôle | Son métier | Quand le prendre | Rend |
|---|---|---|---|
| **Worker** | Fait une tâche, et une seule à la fois, dans son propre contexte. | Toujours : c'est le gros de l'équipe. | le schéma de la famille (`FINDING`, `HYPOTHESIS`, `CHANGESET`, `MATIERE`) |
| **Watchdog** | Surveille les autres sessions. Il repère une session muette depuis trop longtemps, une session qui tourne en rond, ou deux sessions qui s'attendent l'une l'autre. Il prévient le router. Il ne corrige rien ; il archive les sessions que le router lui signale finies. | Voir « Seuils » dans SKILL.md : lancé en premier, comme infrastructure du flux. | des messages `ALERTE` et `ARCHIVÉ` ; à la fin, un `FINDING` des alertes |
| **Merger** | Rassemble les branches des workers sur une branche d'intégration, résout les conflits triviaux, lance les tests et le lint. Ne pousse rien. | Code, dès 2 workers qui committent. | `INTEGRATION` |
| **Checker** | Vérifie le résultat **mergé**, pour de vrai, contre l'Eval de chaque tâche : il lance l'app, ouvre le navigateur, rejoue chaque vérification. Pour la recherche et l'audit, c'est le vérificateur qui relit la source primaire. | Dès qu'il y a un résultat à accepter. | `VERDICT` par tâche |
| **Tester** | Teste au fil de l'eau pour les workers, avant le merge : tests dans le navigateur, cas limites. Il dit au worker ce qui ne marche pas. | Code avec une interface ou des parcours à cliquer, et 3 workers ou plus. Sinon, chaque worker teste lui-même. | `VERDICT` |
| **Reproducer** | Quand quelque chose casse pendant le run, il rejoue les étapes jusqu'à voir le bug, trouve la cause, et, si le correctif est petit, le fait sur sa propre branche. Sinon, il rend un rapport. | Code ou diagnostic, run long, app qu'on peut lancer en local. | `HYPOTHESIS` (cause et preuve) et, s'il corrige, `CHANGESET` |

**Différence avec les rôles déjà là** : le merger est l'« intégrateur » du §4, le checker est le
« vérificateur » ou le « contre-expert » des §1 et §2. Les noms courts servent à fixer leur
métier ; leurs règles ne changent pas.

**Règles communes**

- **Le router ne fait aucun de ces métiers lui-même.** Il lance les rôles, lit leurs résultats,
  et tranche.
- **Ordre en fin de tâche (code)** : worker « tout est commité » → merger → checker. Un échec
  du checker repart **au worker de la tâche** (`À CORRIGER — <tâche>`), avec la vérification qui
  échoue, puis repasse par le merger et le checker.
- **Le checker et le tester sont promptés pour trouver ce qui ne marche pas**, pas pour
  confirmer. Une vérification qu'ils n'ont pas pu rejouer est « non vérifiée », jamais « OK ».
- **PR par worker** → tapis roulant (`references/flux.md`), à la place du merger ou en plus.
- **Le reproducer ne touche pas aux branches des workers.** Son correctif est une branche à
  lui, que le merger intègre comme les autres.
- **Le watchdog est bon marché** : modèle le moins cher, effort `low`, contexte court. Il ne
  lit pas le travail des autres, seulement leurs signes de vie.

**Comment le watchdog surveille (mode sessions)** : le mod swarm-view écrit l'activité de chaque
session dans `~/.claude/swarm-runs/<slug>/view/<nom>.json`. Le watchdog lance en arrière-plan
(`run_in_background`) une boucle qui se réveille toutes les 10 minutes et s'arrête dès qu'elle
trouve une session sans activité depuis 15 minutes qui n'a pas encore écrit son `<nom>.json` ;
son arrêt réveille le watchdog, qui regarde de plus près et écrit au router. Sans dossier
`view/`, il lit les outils de sessions ; en mode sous-agents sans `view/`, ne prévois pas de
watchdog. Le brief (avec sa « source de l'état ») est dans `sessions-mode.md`.

**Exemple (code, 3 tâches)** : router (toi) ; 3 workers sur leurs branches ; 1 watchdog ;
1 merger ; 1 checker qui teste dans le navigateur ; 1 reproducer. Total 7 agents.
