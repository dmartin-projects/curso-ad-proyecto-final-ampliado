#!/usr/bin/env bash
# infra/desplegar.sh — se ejecuta EN el servidor: VERSION=v1.4.0 ./infra/desplegar.sh (módulos 66 y 83)
set -euo pipefail
cd /opt/gastos
NUEVA="${VERSION:?Indica la versión: VERSION=v1.4.0 $0}"   # antes de leer .env, que también define VERSION
set -a                                         # exporta lo que se lea de .env: DOMINIO, GHCR_OWNER…
# shellcheck source=/dev/null
. ./.env
set +a
export VERSION="${NUEVA#v}"                    # v1.4.0 → 1.4.0 (la etiqueta de la imagen)
COMPOSE="docker compose -f compose.prod.yaml"
SERVICIOS="web worker worker-ocr beat tasks-worker relay estadisticas-api estadisticas-consumidor proxy"  # 85: relay y estadísticas

echo "▶ Desplegando $VERSION"
ANTERIOR=$(cat .version-actual 2>/dev/null || echo latest)

$COMPOSE pull --quiet
$COMPOSE up -d db redis rabbitmq collector kafka   # collector: módulo 84; kafka: módulo 85
$COMPOSE run --rm migrate                      # con el código NUEVO, mientras sirve el viejo
$COMPOSE run --rm topics                       # módulo 85: los topics (si ya existen, no hace nada)
$COMPOSE run --rm estadisticas-bd              # módulo 85: usuario y BD del servicio (idempotente)
$COMPOSE run --rm estadisticas-migrate         # módulo 85: migraciones de Alembic del servicio
# --no-deps: migrate ya se ejecutó. Sin él, compose lo vuelve a lanzar (su imagen ha cambiado) con la web y
# el proxy YA parados: ~12 s más sin servicio (medido en el ejercicio 3). Y || : si algo no arranca, con set -e
# el script terminaría AQUÍ, sin volver atrás; quien decide es la comprobación de salud de abajo.
# shellcheck disable=SC2086
$COMPOSE up -d --no-deps --remove-orphans $SERVICIOS || echo "⚠️  docker compose up terminó con error"

echo "▶ Comprobando salud…"
for _ in $(seq 1 30); do
  if curl -fsS "https://${DOMINIO}/health/ready/" >/dev/null; then
    echo "$VERSION" > .version-actual
    # y en .env: cualquier "docker compose …" que se lance después a mano (run, up -d) usará ESTA
    # versión y no la que hubiera en .env (latest, que tras una vuelta atrás puede ser la rota)
    sed -i "s/^VERSION=.*/VERSION=$VERSION/" .env
    docker image prune -f >/dev/null
    echo "✅ $VERSION desplegada"
    exit 0
  fi
  sleep 2
done

echo "❌ La versión $VERSION no responde: volviendo a $ANTERIOR"
# shellcheck disable=SC2086
VERSION=$ANTERIOR $COMPOSE up -d --no-deps $SERVICIOS
sed -i "s/^VERSION=.*/VERSION=$ANTERIOR/" .env
exit 1
