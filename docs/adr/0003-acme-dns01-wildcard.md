# ADR 0003 — ACME : DNS-01 + wildcard, staging par défaut en dev

Statut : accepté · 2026-06

## Contexte
Let's Encrypt rate-limite les émissions (≈50 certs/domaine enregistré/semaine,
et limite « exact set of domains » qui frappe les cycles destroy/replay).
Les renouvellements sont exemptés. Le dev détruit la VM en boucle.

## Décision
- Challenge DNS-01 (provider variable, ici cloudflare via token scopé) ;
  aucun enregistrement A requis, aucune connexion entrante nécessaire.
- Un wildcard unique *.lab.<domain> couvre toutes les apps
  (≈0 consommation de quota, pas de fuite de noms d'hôtes dans les logs CT).
- caServer = staging LE tant qu'on développe ; bascule prod (Slice 8) =
  retirer caServer + vider acme.json.

## Conséquences
- HTTP-01 (sans API DNS) = mode dégradé non couvert en V1 : un cert par app,
  noms publiés en CT — à documenter comme limite produit.
- traefik/acme/ est hors Git, mode 0700, owner 65532.
