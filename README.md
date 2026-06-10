# infractl

Socle self-hosted **secure by default** : une CLI mince qui pilote Ansible en
local pour transformer une machine Debian en socle conteneurisé durci —
Traefik seul publieur de ports, HTTPS wildcard (ACME DNS-01), services
joignables uniquement à travers le reverse proxy.

Projet en construction (Slice 1 : socle Traefik + démo whoami). Les couches
SSO (Authelia), CrowdSec, WireGuard et secrets chiffrés (SOPS/age) arrivent
dans les slices suivantes.

## Principes

- **Séparation moteur / état** : ce dépôt est le moteur (versionné, installé
  via pipx) ; l'état (`/srv/infra/` : compose, config, secrets) vit sur la
  machine cible et n'entre jamais ici.
- **Convention centrale** : aucun service ne déclare `ports:` sauf Traefik.
  Pas de port publié = pas de DNAT = injoignable depuis l'extérieur.
- **Idempotence** : un second `deploy` doit donner `changed=0`.
- Les décisions structurantes sont tracées dans [`docs/adr/`](docs/adr/).

## Installation (sur la machine cible)

```bash
pipx install git+https://github.com/ldesfontaine/infractl.git
mkdir -p /srv/infra && $EDITOR /srv/infra/config.yml   # domain, acme_email
export CF_DNS_API_TOKEN='<token scopé zone>'           # premier deploy uniquement
infractl deploy
```

## Commandes

`init` · `deploy` · `status` · `upgrade` · `audit` — seul `deploy` est
implémenté à ce stade ; les autres arrivent slice par slice.

---

*Relu et co-écrit avec l'aide de Claude (Anthropic).*
