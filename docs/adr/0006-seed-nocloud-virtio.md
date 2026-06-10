# ADR 0006 — Seed NoCloud générée par labctl, attachée en virtio

Statut : accepté · 2026-06

## Contexte (incident)
Avec `virt-install --cloud-init`, la seed est attachée en CD-ROM SATA et un
marqueur DMI "ds=nocloud" (sans données) est injecté. Au boot, cloud-init
init-local cherche le label cidata avant que le CD SATA soit visible
(course de modules), trouve le marqueur DMI, et valide NoCloud À VIDE :
instance-id par défaut, aucun user-data appliqué, zéro erreur loggée.
Preuves : logs cloud-init ([seed=dmi], 3 blkid bredouilles), seed extraite
via /proc/<pid>/fd (user-data valide, meta-data vide), disque monté en
qemu-nbd + ext4 noload.

## Décision
labctl génère sa propre seed (cloud-localds) avec meta-data complet
(instance-id unique par création + local-hostname) et l'attache en disque
VIRTIO readonly. Plus de --cloud-init, donc plus de marqueur DMI.

## Conséquences
- virtio_blk est dans l'initramfs des images cloud : la seed est visible
  dès le premier scan, la course disparaît.
- La seed persiste dans le pool (diagnostic trivial) et est supprimée
  par labctl destroy.
- Dépendance d'outillage poste : cloud-image-utils.
