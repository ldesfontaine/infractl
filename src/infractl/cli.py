import argparse
import os
import subprocess
import sys
from pathlib import Path

ANSIBLE_DIR = Path(__file__).resolve().parent / "ansible"
SITE = ANSIBLE_DIR / "site.yml"
INVENTORY = ANSIBLE_DIR / "inventory" / "hosts.yml"
REQUIREMENTS = ANSIBLE_DIR / "requirements.yml"


def _ansible_env():
    return {**os.environ, "ANSIBLE_CONFIG": str(ANSIBLE_DIR / "ansible.cfg")}


def _ensure_collections():
    return subprocess.run(
        ["ansible-galaxy", "collection", "install", "-r", str(REQUIREMENTS)],
        env=_ansible_env(), check=False,
    ).returncode


def _run_playbook(tags=None, ask_become_pass=False):
    cmd = ["ansible-playbook", "-i", str(INVENTORY), str(SITE)]
    if ask_become_pass:
        cmd.append("--ask-become-pass")
    if tags:
        cmd += ["--tags", ",".join(tags)]
    return subprocess.run(cmd, env=_ansible_env(), check=False).returncode


def cmd_init(_):
    print("init : preflight + pose de /srv/infra — à implémenter (Slice 7)")
    return 0


def cmd_deploy(args):
    rc = _ensure_collections()
    if rc != 0:
        return rc
    return _run_playbook(tags=args.only, ask_become_pass=args.ask_become_pass)


def cmd_status(_):
    print("status : à implémenter")
    return 0


def cmd_upgrade(_):
    print("upgrade : à implémenter")
    return 0


def cmd_audit(_):
    print("audit : à implémenter")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="infractl", description="Socle self-hosted secure-by-default")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Prépare la machine").set_defaults(func=cmd_init)

    d = sub.add_parser("deploy", help="Converge l'infrastructure (Ansible)")
    d.add_argument("--only", nargs="+", metavar="ROLE", help="Limiter à certains rôles (tags)")
    d.add_argument("-K", "--ask-become-pass", action="store_true",
                   help="Demander le mot de passe sudo")
    d.set_defaults(func=cmd_deploy)

    sub.add_parser("status", help="État courant").set_defaults(func=cmd_status)
    sub.add_parser("upgrade", help="Migre moteur/état").set_defaults(func=cmd_upgrade)
    sub.add_parser("audit", help="Vérifie la surface exposée").set_defaults(func=cmd_audit)
    return p


def main():
    args = build_parser().parse_args()
    sys.exit(args.func(args))
