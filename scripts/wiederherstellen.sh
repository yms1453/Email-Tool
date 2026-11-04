#!/usr/bin/env bash
# Eine Sicherung von scripts/sicherung.sh zurückspielen (auf dem Server, als root).
#   /opt/sanda-mail/scripts/wiederherstellen.sh /var/backups/sanda-mail/sanda-mail-JJJJ-MM-TT-HHMM.tar.gz
# Ersetzt ALLE aktuellen Daten (Datenbank, Anhänge, vapid.json) und .env/Caddyfile durch den Stand der Sicherung.
set -euo pipefail

DATEI="$(readlink -f "${1:?Pfad zur Sicherung angeben, z. B. /var/backups/sanda-mail/sanda-mail-….tar.gz}")"
[ -f "$DATEI" ] || { echo "Nicht gefunden: $DATEI" >&2; exit 1; }
cd "$(dirname "$(readlink -f "$0")")/.."
COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.https.yml)

if [ -z "${JA:-}" ]; then
  printf 'Alle aktuellen Daten werden durch %s ersetzt. Fortfahren? [j/N] ' "$(basename "$DATEI")"
  read -r antwort
  [ "$antwort" = j ] || [ "$antwort" = J ] || { echo "Abgebrochen."; exit 1; }
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
tar -xzf "$DATEI" -C "$TMP"
[ -f "$TMP/daten.tar.gz" ] || { echo "Keine SANDA-Mail-Sicherung: daten.tar.gz fehlt" >&2; exit 1; }

"${COMPOSE[@]}" stop sanda-mail
for f in .env Caddyfile; do [ -f "$TMP/$f" ] && cp "$TMP/$f" "./$f"; done
chmod 600 .env Caddyfile 2>/dev/null || true
# Daten-Volume leeren und befüllen – mit dem App-Image, damit Besitzer und Rechte stimmen
"${COMPOSE[@]}" run --rm --no-deps -T --entrypoint sh sanda-mail -c \
  'find /data -mindepth 1 -delete && tar -xzf - -C /data && mv /data/.sicherung.db /data/sanda-mail.db' < "$TMP/daten.tar.gz"
"${COMPOSE[@]}" up -d
echo "Wiederhergestellt aus $(basename "$DATEI")"
