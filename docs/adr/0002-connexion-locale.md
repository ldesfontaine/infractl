# ADR 0002 — Ansible en connexion locale

Statut : accepté · 2026-06

## Contexte
Topologie solo = 1 machine. Un mode push SSH depuis un poste de contrôle
ajouterait inventaire distant, clés et bootstrap pour zéro gain ici.

## Décision
Le moteur s'installe SUR la machine cible et converge localhost
(ansible_connection: local).

## Conséquences
- `infractl deploy` s'exécute sur la machine elle-même.
- Le multi-hôte (--host) n'arrivera qu'avec la topologie dmz.
