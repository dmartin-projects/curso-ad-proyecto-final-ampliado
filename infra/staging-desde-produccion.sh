#!/usr/bin/env bash
# infra/staging-desde-produccion.sh — staging con los datos de producción, anonimizados (módulo 86, ejercicio 2).
# En el servidor:  /opt/gastos/staging/infra/staging-desde-produccion.sh
# Staging se queda SIN sus datos actuales. Producción solo se lee (pg_dump no bloquea a nadie).
set -euo pipefail
cd "$(dirname "$0")/.."                           # /opt/gastos/staging
grep -qx 'ENTORNO=staging' .env || { echo "❌ Esto se ejecuta en el directorio de STAGING"; exit 1; }
PROD=../produccion
COPIA=$(mktemp /tmp/staging-desde-produccion.XXXXXX)
trap 'rm -f "$COPIA"' EXIT
APP="web worker worker-ocr beat tasks-worker relay estadisticas-api estadisticas-consumidor"

echo "▶ Copia de producción"
(cd "$PROD" && docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner') > "$COPIA"

echo "▶ Staging, parado y restaurado"
# shellcheck disable=SC2086
docker compose stop $APP
docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner' < "$COPIA"
docker compose run --rm migrate                   # staging puede ir por delante de producción
docker compose run --rm web python manage.py anonimizar --si

echo "▶ Kafka de staging: los topics viejos tienen movimientos que ya no existen"
K="docker compose exec -T kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092"
for topic in gastos.movimientos gastos.membresias; do
  $K --delete --if-exists --topic "$topic"
done
until ! $K --list | grep -qx 'gastos.movimientos\|gastos.membresias'; do sleep 1; done  # el borrado es asíncrono
docker compose run --rm topics
docker compose run --rm estadisticas-api python -m estadisticas.reconstruir --si

echo "▶ Arriba, y los eventos de lo que ahora hay"
# shellcheck disable=SC2086
docker compose up -d --no-deps $APP
docker compose exec -T web python manage.py publicar_estado
echo "✅ Staging con los datos de producción (anonimizados). Todos entran con STAGING_PASSWORD."
