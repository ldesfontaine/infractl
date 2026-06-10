# ADR 0001 — Séparation moteur / état

Statut : accepté · 2026-06

## Contexte
Le produit doit pouvoir se mettre à jour sans jamais toucher aux données
de l'utilisateur, et l'utilisateur ne doit jamais committer ses secrets.

## Décision
Le MOTEUR (ce dépôt : CLI + rôles Ansible) est versionné et installé via pipx.
L'ÉTAT (/srv/infra : compose rendus, config.yml, secrets, acme) vit sur la
machine cible, posé par les rôles, jamais présent dans le dépôt.

## Conséquences
- `upgrade` pourra évoluer le moteur indépendamment de l'état
  (migrations futures pilotées par /srv/infra/.state-version — Slice 6).
- Aucun secret dans Git par construction.
