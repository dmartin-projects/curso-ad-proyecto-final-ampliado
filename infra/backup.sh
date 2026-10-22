#!/usr/bin/env bash
# infra/backup.sh — cron diario en el servidor (módulo 67): copia de PostgreSQL a R2
# Módulo 86: solo producción (staging no guarda nada que no se pueda volver a crear):
#   15 3 * * * /opt/gastos/produccion/infra/backup.sh
set -euo pipefail
cd "$(dirname "$0")/.."                         # el directorio del entorno: su .env dice qué compose usar
FECHA=$(date +%F-%H%M)
ARCHIVO="/tmp/gastos-${FECHA}.dump"
trap 'rm -f "$ARCHIVO"' EXIT

# Usuario y base de datos, los del contenedor (sus variables): el script no necesita leer el .env
docker compose exec -T db \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner' > "$ARCHIVO"

rclone copy "$ARCHIVO" r2:gastos-backups/postgres/     # otro bucket que el de los archivos, con su propia clave
rclone delete --min-age 30d r2:gastos-backups/postgres/

if [ -n "${HEALTHCHECK_BACKUP_UUID:-}" ]; then           # "la copia se hizo" (healthchecks.io, módulo 68)
  curl -fsS -m 10 --retry 3 "https://hc-ping.com/${HEALTHCHECK_BACKUP_UUID}" >/dev/null
fi
