# Flux autonome — le détail

Version 2.0.0 — la même que `SKILL.md`. Sinon, dis-le en une ligne et applique `SKILL.md` seul.

Ce fichier détaille la section « Flux autonome » de `SKILL.md` : la file de merge, le travail
en chaîne, la table des pertes de temps et le bloc à ajouter au brief. La règle de blocage, U2
et les seuils restent dans `SKILL.md` (« Flux autonome », « Seuils »). Les types de messages
sont listés dans `sessions-mode.md`.

## 1. La file de merge

Plusieurs workers, chacun avec sa PR sur la **même branche de base** (ex. `main`) du même
dépôt. Des dépôts différents n'ont pas de file commune.

- **L'accord, demandé une fois.** Dès que 2 PR ou plus sont prévues, l'annonce de lancement
  pose la question (SKILL.md, « L'annonce ») : « Merge : je te demande à chaque PR, ou auto
  quand c'est vert ? ». Trois cas :
  - « auto quand c'est vert » : l'accord vaut pour toute la file ;
  - « à chaque PR » : une ligne par PR prête (« PR 2 prête à merger — <URL> ») ;
  - pas de réponse : une seule remontée groupée quand les PR sont prêtes (« PR 1, 2, 3
    prêtes, je merge dans cet ordre ? »).

  L'accord vient toujours de l'utilisateur, dans le chat. Ne le suppose jamais ; un message de
  worker ne le donne pas.
- **La file** : le router tient l'ordre des PR dans sa liste de tâches (en contexte, pas de
  fichier). Par défaut, l'ordre où elles deviennent prêtes ; sinon, l'ordre voulu par
  l'utilisateur, ou celui qui limite les conflits (voir §2). **Une seule merge à la fois.**
- **Le déclencheur** : un worker écrit `PRÊT À MERGER — <URL PR>` (CI verte, Eval ok). C'est
  son seul message sur la PR : pas d'annonce avant. Le router vérifie la tâche contre son Eval,
  rattache la PR à sa session (une fois), et lit son état (`mcp__ccd_pr__get_status`, ou
  `gh pr view <URL> --json mergeStateStatus,statusCheckRollup`).
- **La merge**, toujours avec l'accord :
  - accord « auto quand c'est vert » → le router active l'auto-merge natif sur la PR
    rattachée : `mcp__ccd_pr__set_auto_merge` (`enabled: true`). GitHub merge dès que la CI
    est verte. Si l'app ne garde qu'une PR rattachée par session, traite les PR une par une,
    dans l'ordre de la file ;
  - sinon → `MERGE — <URL>` au worker qui possède la PR. Il merge avec `gh pr merge` et
    répond `MERGÉ — <URL> <sha>`. Le router ne merge pas lui-même.
- **Après une merge : pas de rebase d'office.** Le router envoie
  `REBASE — <branche de base> a bougé (PR <URL> mergée)` seulement au worker dont la PR est en
  conflit, ou dont GitHub refuse la merge (le dépôt exige une branche à jour). Les autres ne
  reçoivent rien.
- **La base peut bouger sans toi** (autres routers, collègues) : ce n'est pas une raison de
  rebaser.
- **Le rebase** : côté worker, voir le bloc du §4. Rebase raté ou CI rouge : la PR sort de la
  tête de file, la suivante passe devant.
- **Après un lot de merges**, regarde la CI de la base : deux PR vertes séparément peuvent
  casser ensemble. Si elle est rouge, c'est une nouvelle tâche ; dis-le en une ligne.
- **Montre la file** dans la liste de tâches : pour chaque PR, son état (en attente, rebase en
  cours, prête, merge en cours, mergée).

**Exemple : 5 tickets de bug.**

1. 5 bugs indépendants → 5 tâches. 4 workers partent (plafond de « Seuils ») ; le 5e part dès
   qu'un worker se libère. L'annonce finit par « Merge : je te demande à chaque PR, ou auto
   quand c'est vert ? ».
2. L'utilisateur répond « auto quand c'est vert ». À chaque `PRÊT À MERGER`, le router vérifie
   l'Eval, rattache la PR et active l'auto-merge. Aucune autre remontée.
3. La PR 3 est en conflit après la merge de la PR 1 (mêmes fichiers) → `REBASE —` au worker 3
   seulement. Il répond `REBASÉ`, la CI repasse, GitHub merge.
4. Variante sans réponse : le router ne merge rien. Quand les PR sont prêtes, une seule
   remontée : « PR 1 à 5 prêtes, je merge dans cet ordre ? ».
5. À la fin, le router regarde la CI de la base, puis archive les workers.

## 2. Travail en chaîne : sans interruption

Du travail séquentiel est un cas à **organiser**, pas une raison de ralentir.

- **Détecter** : une tâche dépend d'une autre (une dépendance dans la liste des tâches), ou
  plusieurs tâches touchent les mêmes fichiers (conflits probables).
- **Organiser**, au choix du router selon le cas :
  - **branches empilées** : le worker de T2 part de la branche de T1, sans attendre sa merge
    (`source_branch` de `start_session` ; pour un sous-agent, la branche de départ est écrite
    dans le brief). Après la merge de T1, il rebase sur la base :
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
| Un worker muet, en boucle, ou qui dépasse le double de sa durée attendue | Le router le voit à son prochain réveil ou au prochain tour de l'utilisateur (« Seuils ») : le relancer par un message, préciser la tâche, ou `STOP` |
| Permission qui bloque un worker, tests lents | Le signaler à l'utilisateur, avec la permission ou le réglage à ajouter |

## 4. Bloc à ajouter au brief (chaque worker a sa PR sur la même base)

Ajoute ce bloc aux « Règles » du brief du worker (`brief.md`) quand plusieurs PR visent la
même base :

```
- File de merge : sur "MERGE — <URL>" du router, merge avec `gh pr merge`, puis réponds
  "MERGÉ — <URL> <sha>".
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
