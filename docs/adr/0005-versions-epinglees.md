# ADR 0005 — Versions épinglées

Statut : accepté · 2026-06

## Règle
Jamais de tag flottant (latest, v3) en dehors du tout premier run de dev.
Toute mise à jour de version passe par une modification ici + changelog.

## Versions au bootstrap

| Composant | Version épinglée | Source | Date |
|---|---|---|---|
| traefik | v3.7.4 | hub.docker.com | 2026-06-10 |
| tecnativa/docker-socket-proxy | v0.4.2 | hub.docker.com | 2026-06-10 |
| traefik/whoami | v1.11.0 | hub.docker.com | 2026-06-10 |
| authelia | 4.39.20 | github releases | 2026-06-11 |
| community.docker | 5.2.1 | github releases | 2026-06-10 |
| ansible-core (installé) | 2.21.0 | pip show | 2026-06-10 |
