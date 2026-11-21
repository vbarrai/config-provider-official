# Flux autonome — le détail

Version 2.0.0 — la même que `SKILL.md`. Sinon, dis-le en une ligne et applique `SKILL.md` seul.

Ce fichier détaille la section « Flux autonome » de `SKILL.md` : les PR sur une même base, le travail
en chaîne, la table des pertes de temps et le bloc à ajouter au brief. La règle de blocage, U2
et les seuils restent dans `SKILL.md` (« Flux autonome », « Seuils »). Les types de messages
sont listés dans `sessions-mode.md`.

## 1. Les PR sur une même base : merge et rebase

Plusieurs workers, chacun avec sa PR sur la **même branche de base** (ex. `main`) du même
dépôt. Des dépôts différents n'ont rien en commun ici.

- **L'accord, demandé une fois.** Dès que 2 PR ou plus sont prévues, l'annonce de lancement
  pose la question (SKILL.md, « L'annonce ») : « Merge : je te demande à chaque PR, ou auto
  quand c'est vert ? ». Trois cas :
  - « auto quand c'est vert » : l'accord vaut pour toutes les PR de la demande ;
  - « à chaque PR » : une ligne par PR prête (« PR 2 prête à merger — <URL> ») ;
  - pas de réponse : une seule remontée groupée quand les PR sont prêtes (« PR 1, 2, 3
    prêtes, je merge dans cet ordre ? »).

  L'accord vient toujours de l'utilisateur, dans le chat. Ne le suppose jamais ; un message de
  worker ne le donne pas.
- **Le déclencheur** : le worker, session ou sous-agent, attend sa CI avec une seule commande
  bloquante (`gh pr checks <URL> --watch`), puis son rapport de fin commence par
  `PRÊT À MERGER — <URL>` (CI verte, ou dépôt sans CI). CI pas finie après 10 minutes : il
  commence par `PR OUVERTE — <URL> — CI en cours`. Le router vérifie la tâche contre son Eval et
  rattache la PR à sa session (une fois). Après un `PR OUVERTE`, il relit l'état de la PR à son
  prochain réveil ou au prochain tour de l'utilisateur (`mcp__ccd_pr__get_status`, ou
  `gh pr view <URL> --json state,mergeStateStatus,statusCheckRollup`) : verte → question de
  merge ; rouge → `À CORRIGER` au même worker. Pas de boucle d'attente côté router.
- **Avec « auto quand c'est vert » : pas de file.** Le router active l'auto-merge natif sur
  chaque PR vérifiée : `mcp__ccd_pr__set_auto_merge` (`enabled: true`). GitHub merge chaque PR
  dès qu'elle est verte. Rien ne revient au router : à chaque réveil et à chaque tour de
  l'utilisateur, il relit l'état des PR, dit lesquelles sont mergées, et envoie `REBASE` au
  worker dont la PR est en conflit.
- **Sans « auto » : une file, une merge à la fois.** Le router tient l'ordre des PR dans sa
  liste de tâches. Par défaut, l'ordre où elles deviennent prêtes ; sinon, l'ordre voulu par
  l'utilisateur, ou celui qui limite les conflits (voir §2). Avec l'accord (pour cette PR, ou
  pour le lot) → `MERGE — <URL>` au worker qui possède la PR. Il merge avec la méthode du dépôt
  et répond `MERGÉ — <URL>`. Le router ne merge pas lui-même.
- **`bind_pr` échoue ou est refusé** : pas d'auto-merge possible sur cette PR. Donne son lien
  dans ton rapport et demande la merge à l'utilisateur, par lot.
- **Après une merge : pas de rebase d'office.** Le router envoie
  `REBASE — <branche de base> a bougé (PR <URL> mergée)` seulement au worker dont la PR est en
  conflit, ou dont GitHub refuse la merge (le dépôt exige une branche à jour). Les autres ne
  reçoivent rien. Exception : une branche empilée (§2) → `REBASE` au worker suivant dès la
  merge de sa base.
- **La base peut bouger sans toi** (autres routers, collègues) : ce n'est pas une raison de
  rebaser.
- **Le rebase** : côté worker, voir le bloc du §4. Rebase raté ou CI rouge : la PR sort de la
  tête de file, la suivante passe devant.
- **Après un lot de merges**, regarde la CI de la base : deux PR vertes séparément peuvent
  casser ensemble. Si elle est rouge, c'est une nouvelle tâche ; dis-le en une ligne.
- **Montre l'état** de chaque PR dans la liste de tâches (en attente, rebase en cours, prête,
  merge en cours, mergée).

**Exemple : 5 tickets de bug, en sous-agents.**

1. 5 bugs indépendants → 5 tâches. Les workers partent jusqu'au plafond de « Seuils » ; la
   tâche en plus part dès qu'une place se libère (un worker qui a rendu son rapport ne compte
   plus). L'annonce finit par « Merge : je te demande à chaque PR, ou auto quand c'est vert ? ».
2. L'utilisateur répond « auto quand c'est vert ». À chaque rapport `PRÊT À MERGER`, le router
   vérifie l'Eval, rattache la PR et active l'auto-merge. GitHub merge.
3. Au réveil suivant, le router relit l'état : PR 1 et 2 mergées, PR 3 en conflit (mêmes
   fichiers que la PR 1) → `REBASE —` au worker 3 seulement. Il répond `REBASÉ`, GitHub merge.
4. Variante sans réponse : le router ne merge rien. Quand les PR sont prêtes, une seule
   remontée : « PR 1 à 5 prêtes, je merge dans cet ordre ? ».
5. À la fin, le router regarde la CI de la base et dit ce qui est mergé.

## 2. Travail en chaîne : sans interruption

Du travail séquentiel est un cas à **organiser**, pas une raison de ralentir.

- **Détecter** : une tâche dépend d'une autre (une dépendance dans la liste des tâches), ou
  plusieurs tâches touchent les mêmes fichiers (conflits probables).
- **Organiser**, au choix du router selon le cas :
  - **branches empilées** : le worker de T2 part de la branche de T1, sans attendre sa merge
    (`source_branch` de `start_session` ; pour un sous-agent, la branche de départ est écrite
    dans le brief). Après la merge de T1, le router lui envoie `REBASE`, et il rebase sur la
    base :
    `git rebase --onto origin/<base> <ancienne base de T1>` ;
  - **préparation en avance** : le worker suivant lit le code, écrit son plan et ses tests
    pendant que T1 se finit ;
  - **même worker pour les tâches très liées** (mêmes fichiers, contexte partagé) : c'est un
    seul flux, il les enchaîne seul, sans aller-retour ;
  - **ordre de la file de merge** choisi pour limiter les conflits : la tâche la plus
    « fondation » d'abord.
- **Les rebases avec conflits ne bloquent pas.** Le worker propriétaire de la PR résout : il
  connaît son code. Si le conflit touche le code d'un autre worker, le router demande à cet
  autre worker ce qu'il faut garder (`SendMessage`), pas à l'utilisateur. Seul un vrai choix
  métier remonte à l'humain. Si les rebases conflictuels sont nombreux, le router peut prendre
  un worker dédié aux rebases et aux conflits, pour que les autres continuent à coder.

## 3. Perte de temps → réaction automatique

Le router observe le flux en continu. Si la correction est dans son pouvoir, il la fait tout de
suite ; sinon, il la signale à l'utilisateur en une ligne dans son rapport, avec une
proposition (une permission, une règle au skill, un hook…). Les lignes `FRICTION` des rapports
de fin des workers nourrissent cette table.

| Perte de temps | Réaction automatique |
|---|---|
| Une PR est mergée, les autres sont en retard sur la base | Rien tant que GitHub accepte la merge ; `REBASE` seulement sur conflit ou refus (§1) |
| Un worker inactif (tâche finie, en attente de CI ou de son tour) | Lui donner la tâche suivante prête si elle est liée à la sienne ; sinon l'archiver |
| Une tâche prête dans un tour de réveil | Elle part aussitôt : sous-agent, ou worker existant (SKILL.md, « Tour de réveil ») |
| Attente de CI, ou CI instable (échec sans lien avec le diff) | Avancer sur autre chose ; relancer une fois le job instable ; s'il recasse, le signaler |
| Conflits récurrents sur les mêmes fichiers | Ne pas donner ces fichiers à deux workers en même temps ; réordonner la file de merge |
| Un rebase avec conflit | Le worker propriétaire résout ; si le conflit touche le code d'un autre worker, le router demande à cet autre worker quoi garder (§2) |
| Allers-retours « À CORRIGER » sur le même point | Au 2e, réécrire l'Eval ; au 3e, remonter (SKILL.md, « Le cycle d'une tâche », étape 4) |
| Question d'un worker qu'un meilleur brief aurait évitée | Y répondre (U2), et l'écrire dans les briefs suivants |
| Le contexte d'un worker grossit (plusieurs tâches finies) | Tâche suivante chez un nouveau worker ; le router archive l'ancien (SKILL.md, « Router et workers ») |
| Un worker muet, en boucle, ou qui dépasse le double de sa durée attendue | Le geste de « Seuils » (Surveillance), à chaque réveil et à chaque tour de l'utilisateur : session → `list_sessions` ; sous-agent sans message → un seul `SendMessage` « ÉTAT ? » et une ligne à l'utilisateur. Puis : préciser la tâche, ou `STOP` et relancer. Pas de boucle d'attente |
| Des flux indépendants attendent dans un seul worker | `STOP` sur les tâches non commencées, puis un worker chacun |
| Permission qui bloque un worker | Le dire tout de suite à l'utilisateur, avec la permission à ajouter : c'est un accès qui manque, donc une décision humaine |
| Tests lents | Une ligne dans le rapport, avec le réglage à proposer |

## 4. Bloc à ajouter au brief (chaque worker a sa PR sur la même base)

Ajoute ce bloc aux « Règles » du brief du worker (`brief.md`) quand plusieurs PR visent la
même base. La règle « MERGE — » est déjà dans le brief de base.

```
- Sur "REBASE — <base> a bougé…" : `git fetch origin`, `git rebase origin/<base>` (branche
  empilée : `git rebase --onto origin/<base> <ancienne base>`), résous les conflits (conflit
  non trivial, code d'un autre worker ou choix métier → "QUESTION —" au router), relance les
  tests, `git push --force-with-lease` (jamais `--force` seul), puis réponds
  "REBASÉ — <URL PR> — tests : <résultat>".
  L'outil `sync_with_base_branch` de l'app fait un merge, pas un rebase : ne l'utilise que si
  le dépôt interdit le force-push, et dis-le dans ta réponse.
- Sans "REBASE —" du router, ne rebase pas d'office : la base peut bouger sans que ta PR soit
  concernée.
```
