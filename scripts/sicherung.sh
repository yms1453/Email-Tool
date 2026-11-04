#!/usr/bin/env bash
# Sicherung von SANDA Mail (auf dem Server, als root). Läuft täglich über den systemd-Timer, den install.sh einrichtet.
#   /opt/sanda-mail/scripts/sicherung.sh
# Sichert Datenbank (konsistent im laufenden Betrieb), Anhänge, vapid.json, .env und Caddyfile nach
# SICHERUNG_ORDNER/sanda-mail-JJJJ-MM-TT-HHMM.tar.gz und behält die neuesten SICHERUNG_BEHALTEN Stück.
set -euo pipefail

ORDNER="${SICHERUNG_ORDNER:-/var/backups/sanda-mail}"
BEHALTEN="${SICHERUNG_BEHALTEN:-14}"
cd "$(dirname "$(readlink -f "$0")")/.."

mkdir -p "$ORDNER"
chmod 700 "$ORDNER"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"; docker compose exec -T sanda-mail rm -f /data/.sicherung.db >/dev/null 2>&1 || true' EXIT

# SQLite-Backup-API statt Datei kopieren: liefert auch bei laufendem Schreiben (WAL) einen sauberen Stand
docker compose exec -T sanda-mail node --input-type=module -e \
  "import { DatabaseSync, backup } from 'node:sqlite'; await backup(new DatabaseSync('/data/sanda-mail.db'), '/data/.sicherung.db');"
docker compose exec -T sanda-mail tar -czf - -C /data \
  --exclude ./sanda-mail.db --exclude ./sanda-mail.db-wal --exclude ./sanda-mail.db-shm . > "$TMP/daten.tar.gz"
for f in .env Caddyfile; do [ -f "$f" ] && cp "$f" "$TMP/"; done

NAME="sanda-mail-$(date +%F-%H%M).tar.gz"
umask 077
tar -czf "$ORDNER/$NAME.teil" -C "$TMP" .
mv "$ORDNER/$NAME.teil" "$ORDNER/$NAME"

# Alte Sicherungen entfernen, die neuesten BEHALTEN bleiben
ls -1t "$ORDNER"/sanda-mail-*.tar.gz | tail -n +"$((BEHALTEN + 1))" | xargs -r rm -f
echo "Sicherung: $ORDNER/$NAME ($(du -h "$ORDNER/$NAME" | cut -f1))"
