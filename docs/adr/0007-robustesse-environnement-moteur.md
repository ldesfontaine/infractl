# ADR 0007 — Le moteur fixe son environnement d'exécution

Statut : accepté · 2026-06

## Contexte (trois incidents du premier deploy réel, VM jetable)
1. pipx n'expose dans le PATH que les commandes du paquet — pas les binaires
de ses dépendances : `ansible-galaxy` introuvable en nom nu.
2. `bin/python` d'un venv est un symlink vers le python système :
`Path(sys.executable).resolve()` en sort et fabrique `/usr/bin/ansible-galaxy`.
3. SSH forwarde les locales du client (SendEnv/AcceptEnv) ; l'image cloud
minimale ne les a pas générées ; Ansible vérifie strictement sa locale
et refuse de démarrer.

## Décision
`cli.py` résout les binaires ansible via `Path(sys.executable).parent`
(sans resolve) et force `LC_ALL=LANG=C.UTF-8` dans l'environnement de tous
les subprocess Ansible.

## Conséquences
- Le moteur fonctionne en pipx, venv classique ou editable, sur toute machine,
quelle que soit la locale de l'opérateur.
- Écrasement volontaire de la locale : sorties Ansible uniformes (anglais),
comparables en CI, googlables en support.
