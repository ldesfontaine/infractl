# ADR 0012 — CrowdSec : bouncer plugin en tête d'entrypoint

Statut : accepté · 2026-06

## Contexte
La Slice 3 met une couche réputation devant le SSO : une IP bannie doit être
rejetée avant le portail (l'ordre des middlewares de l'entrypoint est
significatif, ADR 0008). Deux mécanismes d'application possibles : un
conteneur bouncer interrogé en forwardAuth, ou le plugin Traefik
`maxlerebourg/crowdsec-bouncer-traefik-plugin`.

## Décision
- **Plugin Traefik épinglé `v1.6.0`** (`experimental.plugins`, archive
  téléchargée au démarrage dans `/plugins-storage`, d'où le volume
  `traefik/plugins` — Traefik est read_only). Le conteneur forwardAuth est
  rejeté : un hop HTTP par requête, et le projet de référence est legacy.
- **Mode `stream`, rafraîchissement 60 s** : le plugin tient un cache local
  des décisions, aucun appel LAPI sur le chemin de la requête ; une décision
  se propage en ≤ 60 s (constaté en 3-A).
- **LAPI sans `ports:`** sur le réseau `proxy` (convention produit, seul
  Traefik publie) ; image `crowdsecurity/crowdsec:v1.7.8` — 1.7.8 corrige un
  bypass WAF et un DoS LAPI (recensée à l'ADR 0005).
- **Clé bouncer = secret machine** : `secrets/crowdsec.env`
  (`BOUNCER_KEY_traefik=…`), généré au premier run, `force: false`, jamais
  réécrit — pattern cloudflare.env. Le plugin la lit via
  `crowdsecLapiKeyFile` (`secrets/crowdsec.key`, owner 65532, mode 0400,
  monté `:ro`) : la clé ne figure jamais dans la conf dynamic. Elle est lue
  à l'init du plugin : une rotation exige un restart de Traefik.
- **Acquisition par fichier** : accessLog JSON de Traefik partagé via volume
  `:ro` (`acquis.d/traefik.yaml`, `labels: type: traefik`). Jamais de
  docker.sock côté CrowdSec. Limite V1 : pas de rotation des logs,
  l'access.log grossit sans borne.

## Fail-closed (assumé)
Défauts du plugin : `UpdateMaxFailure: 0` (configuration.go:148) et
`StreamStartupBlock: true` — LAPI injoignable ⇒ trafic bloqué ; c'est
`updateMaxFailure: -1` qui ouvrirait. Constaté : ~30 s de « connection
refused » entre les restarts traefik puis crowdsec d'un deploy —
transitoire, auto-résorbé au cycle suivant. Cohérent avec le fail-closed de
l'ADR 0008 : l'indisponibilité d'une couche de sécurité ferme, n'ouvre pas.

## Écart durcissement
`read_only: true` et user non-root ne sont pas supportés par l'image :
l'entrypoint réécrit `config.yaml` à chaque démarrage et l'init copie des
fichiers 0600 root (issues crowdsec#3303, #3562). Non forcés —
`cap_drop: [ALL]` + `no-new-privileges` conservés (précédent : healthcheck
Authelia, ADR 0010).

## CAPI/console désactivées par défaut
`crowdsec_online_api: false` rend `DISABLE_ONLINE_API` : un lab jetable ne
partage pas de signaux. Checklist d'activation pour une instance durable :
1. `crowdsec_online_api: true` dans `/srv/infra/config.yml` (+ enrôlement
   console éventuel) ;
2. rotation des logs AVANT (lever la limite V1 ci-dessus) ;
3. allowlist des IP opérateur — une remédiation automatique ne doit pas
   pouvoir verrouiller l'admin ;
4. en topologie dmz : garantir la vraie IP cliente jusqu'à Traefik (PROXY
   protocol), sinon les bans frappent l'IP du tunnel — piège du 127.0.0.1
   banni.

## Whitelist des IP privées
Les parsers du hub whitelistent le LAN : en lab, aucun auto-ban par les
scénarios — les preuves passent par des décisions manuelles
(`cscli decisions add`), qui s'appliquent malgré la whitelist. Sur instance
durable exposée, les vraies IP publiques sont auto-remédiées normalement.

## Note — version auto-déclarée
`cscli bouncers list` affiche `1.5.0` pour le plugin `v1.6.0` (version.go:4
au tag v1.6.0 : constante upstream non bumpée). L'épingle qui fait foi est
`version:` dans traefik.yml et l'archive `v1.6.0.zip` téléchargée.
