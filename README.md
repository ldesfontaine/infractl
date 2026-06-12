# infractl

Socle self-hosted **secure by default** : une CLI mince qui pilote Ansible en
local pour transformer une machine Debian en socle conteneurisé durci —
Traefik seul publieur de ports, HTTPS wildcard (ACME DNS-01), services
joignables uniquement à travers le reverse proxy.

Projet en construction (Slice 2 : socle Traefik + SSO Authelia, public par
exception). Les couches CrowdSec, WireGuard et secrets chiffrés (SOPS/age)
arrivent dans les slices suivantes.

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
apt-get update && apt-get install -y --no-install-recommends git pipx
pipx install git+https://github.com/ldesfontaine/infractl.git
export PATH="$PATH:/root/.local/bin"
mkdir -p /srv/infra
cat > /srv/infra/config.yml <<'EOF'                     # remplacer les deux valeurs
domain: exemple.com
acme_email: vous@exemple.com
EOF
read -rsp 'CF_DNS_API_TOKEN : ' CF_DNS_API_TOKEN; echo; export CF_DNS_API_TOKEN  # premier deploy uniquement
infractl deploy
```

`--no-install-recommends` est important : sans lui, pipx tire ~79 paquets
(~202 Mo) superflus. Le token Cloudflare est saisi via `read -rsp` pour ne
jamais finir dans l'historique shell.

## SSO (Authelia)

Le socle déploie Authelia (portail `auth.<lab_domain>`) et attache son
middleware forwardAuth à l'entrypoint `websecure` de Traefik : tout ce que
sert Traefik est protégé par défaut, aucune app ne peut « oublier » de
l'être ([ADR 0008](docs/adr/0008-sso-par-defaut-entrypoint.md)). Les secrets
machine (JWT, session, chiffrement du storage) sont générés au premier run ;
seul le fichier des utilisateurs est créé par l'opérateur :

```bash
mkdir -p -m 0700 /srv/infra/secrets/authelia
read -rsp 'Mot de passe SSO : ' PW; echo
HASH=$(docker run --rm authelia/authelia:4.39.20 authelia crypto hash generate argon2 --password "$PW" | awk '{print $2}')
unset PW
printf 'users:\n  lucas:\n    displayname: "Lucas"\n    password: "%s"\n    email: lucas.desfontaine1@gmail.com\n    groups: [admins]\n' "$HASH" > /srv/infra/secrets/authelia/users.yml
unset HASH
chown -R 65533:65533 /srv/infra/secrets/authelia
chmod 0500 /srv/infra/secrets/authelia
chmod 0400 /srv/infra/secrets/authelia/users.yml
grep -c 'argon2' /srv/infra/secrets/authelia/users.yml   # attendu : 1
```

Adapter identifiant et email. Si le `grep` final ne rend pas `1`, la sortie
de la commande de hash a changé de forme — la coller telle quelle pour
diagnostic.

Les mails de réinitialisation de mot de passe atterrissent dans
`/srv/infra/authelia/notification.txt` (notifier filesystem, pas de SMTP).

Caveat : toute modification de la config Authelia redémarre le service et
déconnecte les sessions (stockées en mémoire en V1).

## Public par exception

Tout est derrière le SSO par défaut ; `/srv/infra/public.yml` est la liste
exhaustive de ce qui y échappe ; une exception se justifie (`reason`) ou se
refuse ([ADR 0009](docs/adr/0009-public-par-exception.md)).

```yaml
public:
  - host: status.lab.<domaine>     # FQDN sous lab.<domaine>
    reason: "page de statut publique"   # obligatoire, non vide
    paths: ["^/api/health$"]       # optionnel : regex de chemins ;
                                   # sans paths, tout l'hôte est public
```

Procédure : éditer le fichier puis `infractl deploy`. Une entrée sans
`reason` (ou hors domaine) fait échouer le déploiement — c'est voulu.

Exemple complet du cycle, sur `whoami` (réellement déployé, donc les codes
sont vérifiables) :

```bash
# Rendre whoami public le temps d'un test
cat > /srv/infra/public.yml <<'EOF'
public:
  - host: whoami.lab.<domaine>
    reason: "test du cycle public"
EOF
infractl deploy
curl -sk -o /dev/null -w '%{http_code}\n' https://whoami.lab.<domaine>          # 200 (anonyme)

# Retirer l'exception : tout repasse derrière le SSO
cat > /srv/infra/public.yml <<'EOF'
public: []
EOF
infractl deploy
curl -sk -o /dev/null -w '%{http_code} %{redirect_url}\n' https://whoami.lab.<domaine>   # 302 → auth.lab.<domaine>

# Chaque deploy de ce cycle redémarre Authelia : les sessions SSO sont
# déconnectées (voir le caveat de la section « SSO (Authelia) »).
```

## Vérifier le socle

Ces vérifications se lancent depuis le laptop : c'est son `/etc/hosts` qui
résout `*.lab.<domaine>` vers l'IP de la VM (le bloc « top départ » du drill
réécrit cette ligne).

```bash
curl -sk -o /dev/null -w '%{http_code} %{redirect_url}\n' https://whoami.lab.<domaine>   # 302 → auth.lab.<domaine>
curl -sk -o /dev/null -w '%{http_code}\n' https://auth.lab.<domaine>                      # 200
curl -sk -o /dev/null -w '%{http_code} %{redirect_url}\n' https://traefik.lab.<domaine>  # 302 → auth.lab.<domaine>
```

Lancées depuis la VM, ou avec un `/etc/hosts` périmé, ces curl renvoient
`000` : curl met `000` dans `%{http_code}` quand il n'obtient aucune réponse
HTTP (nom non résolu, connexion refusée). C'est un faux négatif, pas un
socle cassé.

Alternative indépendante de `/etc/hosts` — forcer la résolution à la volée :

```bash
IP=<IP-de-la-VM>
curl --resolve whoami.lab.<domaine>:443:$IP -sk -o /dev/null \
  -w '%{http_code} %{redirect_url}\n' https://whoami.lab.<domaine>
```

(le port = `HTTPS_PORT` publié, 443 par défaut — vérifier dans
`/srv/infra/.env` en cas de doute.)

## Commandes

`init` · `deploy` · `status` · `upgrade` · `audit` — seul `deploy` est
implémenté à ce stade ; les autres arrivent slice par slice.

---

*Relu et co-écrit avec l'aide de Claude (Anthropic).*
