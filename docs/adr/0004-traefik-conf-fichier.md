# ADR 0004 — Conf statique Traefik en fichier, pas en flags

Statut : accepté · 2026-06

## Contexte
Deux formes possibles : flags `command:` dans le compose, ou traefik.yml
monté :ro. Le guide montre les deux ; l'arborescence d'état référence le fichier.

## Décision
Conf statique dans /srv/infra/traefik/traefik.yml (template Ansible,
handler de restart). Routes/middlewares dynamiques dans traefik/dynamic/
(file provider, rechargé à chaud, sans restart).

## Conséquences
- Diffable et lisible par l'opérateur ; seul un changement de conf statique
  redémarre Traefik (handler), le dynamique est sans coupure.
- Pas de dashboard Traefik au MVP : il n'entrera qu'en Slice 2,
  derrière Authelia. Jamais « ouvert temporairement ».
