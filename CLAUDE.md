# infractl — règles pour Claude Code

## Nature du projet
CLI Python mince (« moteur ») wrappant ansible-playbook en connexion locale.
Le moteur est versionné ici ; l'ÉTAT (/srv/infra : compose, config, secrets)
vit sur la machine cible et n'entre JAMAIS dans ce dépôt.

## Interdits absolus
- Ne jamais exécuter `ansible-playbook` sans `--syntax-check` : le playbook
  (become + connection locale) modifierait CETTE machine.
- Ne jamais écrire hors du dépôt (exceptions : ~/.ansible/collections, .venv/).
- Ne jamais committer de secret, de .env applicatif, ni d'élément de /srv/infra.
- Pas de dépendance, fichier ou abstraction non demandés.

## Conventions
- Idempotence obligatoire : un 2ᵉ run doit donner changed=0
  (vérifié sur la VM jetable — par l'humain, ou par Claude Code via SSH
  quand l'IP est fournie ; JAMAIS sur cette machine).
- Convention produit : aucun service ne déclare `ports:` sauf traefik.
- Images Docker épinglées (jamais latest) ; toute MAJ de version = ADR 0005 mis à jour.
- Toute décision structurante = un ADR dans docs/adr/.
- Jamais de trailer `Co-Authored-By` dans les messages de commit.
- Ne jamais exécuter tools/labctl (sudo + hyperviseur : réservé à l'humain).
- Accès SSH à la VM de lab autorisé UNIQUEMENT si l'humain fournit l'IP dans sa
demande (options : StrictHostKeyChecking=no, UserKnownHostsFile=/dev/null).
- Ne jamais lire, afficher ou copier le contenu de /srv/infra/secrets/.
