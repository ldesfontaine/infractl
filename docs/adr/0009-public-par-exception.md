# ADR 0009 — Public par exception

Statut : accepté · 2026-06

## Contexte
L'ADR 0008 protège tout ce que sert Traefik derrière le SSO, mécaniquement.
Il faut donc un endroit — un seul — où l'opérateur déclare ce qui y échappe,
sans toucher au moteur ni aux templates.

## Décision
`/srv/infra/public.yml` est de l'état opérateur et la **source de vérité
unique** des exceptions au SSO. À chaque convergence, son contenu est rendu
en règles `bypass` Authelia dans la configuration générée.

Schéma d'une entrée :
- `host` : FQDN sous `lab_domain` (obligatoire) ;
- `reason` : justification de l'exception (obligatoire, non vide) ;
- `paths` : liste de regex de chemins (optionnel) — sans `paths`, tout
  l'hôte est public ; avec, le bypass ne vaut que pour les chemins qui
  matchent, le reste retombe sur la politique par défaut.

La validation est bloquante au deploy : une entrée hors contrat (host hors
domaine, `reason` absent ou vide) fait échouer la convergence. Une exception
se justifie ou se refuse.

Le bypass du portail `auth.<lab_domain>` est de la machinerie moteur, codé
en dur dans le template de configuration — il n'a pas sa place dans ce
fichier (sans lui, le portail boucle sur lui-même).

## Conséquences
- Modifier le fichier ⇒ redéployer ⇒ restart Authelia ⇒ sessions en mémoire
  perdues (re-login). Assumé en V1 ; le stockage de sessions dans Redis est
  l'évolution documentée si cela devient gênant.
- Ce contrat est conçu comme le frère de `routes.yml` (slice ultérieure) et
  comme l'API d'une éventuelle UI d'admin future : l'UI écrirait CE fichier,
  jamais autre chose.
