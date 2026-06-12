# ADR 0011 — Backends externes via routes.yml

Statut : accepté · 2026-06

## Contexte
Le provider docker de Traefik (via socket-proxy) ne voit que les conteneurs.
Or l'existant à fronter n'est pas toujours un conteneur : binaire sur l'hôte,
machine distante. Il faut pouvoir le mettre derrière Traefik sans le
modifier, et la thèse de l'ADR 0008 (SSO mécanique à l'entrypoint) doit
s'appliquer telle quelle à ces backends.

## Décision
`/srv/infra/routes.yml` est le contrat opérateur des backends externes —
le frère de `public.yml` (ADR 0009). Schéma d'une entrée : `host` (FQDN sous
`lab_domain`), `backend` (URL http(s)://), `reason` (obligatoire, non vide).

À chaque convergence, son contenu est rendu en configuration file-provider
(`traefik/dynamic/routes.yml`), rechargée à chaud. Les clés router/service
sont le FQDN slugifié : l'unicité est obtenue par construction. Les hôtes
réservés `auth`, `traefik` et `whoami` sont refusés : une entrée écraserait
un router du socle, et `auth.*` en particulier verrouillerait tout le socle
(fail-closed de l'ADR 0008).

`host.docker.internal` est résolu dans le conteneur traefik via
`extra_hosts: host.docker.internal:host-gateway` — constat : **172.17.0.1**,
la passerelle du bridge Docker par défaut.

Le MÊME contrat sera réutilisé par la topologie dmz (backend = IP
WireGuard) : la valeur change, pas le contrat.

## Propriétés prouvées
- Validation avant rendu : un deploy en échec laisse le dernier état valide
  servi (fail-safe).
- Jamais de fichier dynamic vide (comportement Traefik non garanti sur un
  fichier vide ⇒ `routes: []` produit `state: absent`).
- Hot-reload : `StartedAt` du conteneur traefik inchangé après convergence.

## Limites assumées
- Pas de healthcheck des backends externes : backend éteint = 502 constaté
  au runtime, le deploy n'en sait rien.
- Trafic Traefik→backend en HTTP clair : local en topologie solo ; dans le
  tunnel WireGuard en dmz — TLS terminé à l'edge, à réévaluer à la dmz.
- Le bind du backend (sur quelle interface il écoute) est à la charge de
  l'opérateur.
