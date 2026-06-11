# ADR 0008 — SSO par défaut au niveau entrypoint

Statut : accepté · 2026-06

## Contexte
Deux façons de protéger les apps derrière Authelia : attacher le middleware
forwardAuth à chaque router (politique, chaque app doit y penser), ou
l'attacher à l'entrypoint `websecure` (mécanique, tout ce que Traefik sert
est protégé d'office).

## Décision
Middleware `authelia@file` attaché à l'entrypoint `websecure` — mécanique,
pas politique. Aucune app ne peut « oublier » d'être protégée ; preuve :
whoami est passé derrière le SSO sans modification de son manifest.

Les exceptions passent uniquement par des règles `bypass` Authelia, rendues
depuis `/srv/infra/public.yml` (brief 2B). Le bypass du portail
`auth.<lab_domain>` est de la machinerie moteur, codé en dur dans le
template de configuration (sinon boucle de redirection).

## Conséquences
- Fail-closed assumé : Authelia down ⇒ tout est down, y compris le futur
  « public ». Documenté, accepté.
- L'ordre des middlewares de l'entrypoint est significatif : la Slice 3
  préfixera `crowdsec@file` en tête de liste, avant `authelia@file`.
