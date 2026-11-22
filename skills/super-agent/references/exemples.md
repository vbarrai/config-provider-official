# Exemples de sujets macro

Version 2.0.0.

Règles et seuils : `SKILL.md`.

| Sujet | Forme | Remonte à l'humain |
|---|---|---|
| 1. Une typo dans le titre du README | 1 sous-agent (outil `Agent`), modèle moins cher, `effort` bas, sans `isolation` : il écrit dans le dossier de l'utilisateur. | Rien : le router rejoue une commande (`git diff --stat`) et le dit. |
| 2. 5 bugs indépendants, une PR par bug | 5 flux, lancés jusqu'au plafond de « Seuils » : des sous-agents en worktree, 5 PR, pas de watchdog. Merges : `flux.md` §1. | La question de merge, une fois ; un choix produit (`QUESTION`). |
| 3. Un champ en chaîne : migration DB → API → UI | Un simple champ sur 3 couches : un seul worker, une seule PR. Chaque couche est un vrai chantier : 3 workers en chaîne (`flux.md` §2), le contrat (nom et type du champ) dans les 3 briefs. | L'accord de merge ; le déploiement de la migration en production. |
| 4. Un renommage qui touche les mêmes fichiers partout | Un seul flux : 1 worker enchaîne modèles, services et tests. Un nom ambigu sans enjeu : il choisit et le note (U2). | La merge ; un renommage visible des clients (API publique) : choix produit. |
| 5. Le même changement dans 8 dépôts | 8 flux, jusqu'au plafond de « Seuils », un gabarit commun (étapes, commandes, Eval) dans chaque brief, modèle moins cher. Chaque worker dans son dépôt (sous-agent : chemin du dépôt dans le brief ; session : `cwd`). Un piège commun trouvé par un worker va dans les briefs suivants, et aux workers en cours par `SendMessage`. | L'accord de merge ; un dépôt qui ne peut pas suivre sans changement de comportement. |
| 6. Un audit de sécurité « en équipe », avant une mise en prod | L'équipe est demandée : plan montré et lancé dans le même tour. Patron audit (`topologies.md` §2), mode sous-agents : 3 relecteurs, 1 checker (contre-expert), 1 agent de synthèse, soit 5 agents. | Bloquer ou non la mise en prod. |
| 7. Un incident en production à cause inconnue | Le router propose l'équipe : il attend le feu vert. Patron diagnostic (`topologies.md` §3), mode sous-agents : 3 enquêteurs, 1 reproducer (besoin écrit : confirmer la cause), 1 sous-agent de synthèse (livrable court), soit 5 agents. | Le feu vert ; toute action en production. |
| 8. Un rapport qui compare 4 outils | Sans équipe si chaque part tient en une page et qu'aucun constat ne demande une vérification croisée : 4 sous-agents qui rédigent chacun leur part. Sinon, patron recherche (`topologies.md` §1) : 4 explorateurs, 1 vérificateur, 1 agent de synthèse qui écrit le rapport, soit 6 agents. Des rédacteurs seulement si le rapport est long et doit avoir un seul style. | Le choix final de l'outil (arbitrage métier). |
