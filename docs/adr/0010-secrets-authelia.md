# ADR 0010 — Secrets Authelia : machine vs opérateur

Statut : accepté · 2026-06

## Contexte
Authelia a besoin de trois secrets machine (jwt de reset, session,
chiffrement du storage) et d'une base d'utilisateurs (`users.yml`).
Le moteur est en connexion locale ; l'état vit sur la cible.

## Décision
- Secrets machine : auto-générés au premier run par `lookup('password',
  ... create=true)` directement sur la cible, jamais réécrits ensuite,
  mode 0400, owner 65533 (UID conteneur dédié). Injectés dans le conteneur
  par variables d'environnement `AUTHELIA_*_FILE`, jamais dans
  configuration.yml.
- `users.yml` : fourni par l'opérateur, jamais créé par le moteur — le
  moteur ne crée jamais d'identité. Le rôle échoue proprement (assert avec
  procédure dans le message) s'il est absent.

## Conséquences
- Aucun secret ne transite par le dépôt ni par la sortie Ansible
  (`no_log` sur la génération).
- SOPS reprendra la gestion de l'ensemble en Slice 6.
- (Le numéro 0009 est réservé au contrat de `public.yml`, brief 2B.)
