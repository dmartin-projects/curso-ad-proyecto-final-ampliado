#!/usr/bin/env bash
# infra/desplegar.sh — se ejecuta EN el servidor, en el directorio de un entorno (módulos 66, 83 y 86):
#   cd /opt/gastos/staging    && VERSION=sha-1a2b3c4 ./infra/desplegar.sh
#   cd /opt/gastos/produccion && VERSION=v1.4.0      ./infra/desplegar.sh
# Qué entorno es lo dice su .env (ENTORNO, COMPOSE_PROJECT_NAME, API_HOST…), que el workflow acaba de generar
# a partir de infra/entornos/<entorno>.env y de infra/secretos/<entorno>.env (SOPS).
set -euo pipefail
cd "$(dirname "$0")/.."                         # /opt/gastos/<entorno>
NUEVA="${VERSION:?Indica la versión: VERSION=v1.4.0 $0}"

# Del .env, solo lo que necesita el script (sin "source": un valor con espacios lo rompería)
valor() { grep -E "^$1=" .env | tail -n 1 | cut -d= -f2- | sed -E 's/[[:space:]]+#.*$//; s/^"(.*)"$/\1/'; }
ENTORNO=$(valor ENTORNO)
API_HOST=$(valor API_HOST)
case "$ENTORNO" in produccion | staging) ;; *) echo "❌ ENTORNO desconocido en .env: '$ENTORNO'"; exit 1 ;; esac

export VERSION="${NUEVA#v}"                     # v1.4.0 → 1.4.0 (la etiqueta de la imagen)
COMPOSE="docker compose"                        # COMPOSE_FILE y COMPOSE_PROJECT_NAME, del .env
# La puerta, con SU directorio y SU nombre: si no, se aplicarían el .env y el COMPOSE_PROJECT_NAME de este entorno
EDGE="docker compose --project-directory ../edge -p gastos-edge -f ../edge/compose.edge.yaml"
SERVICIOS="web worker worker-ocr beat tasks-worker relay estadisticas-api estadisticas-consumidor"

echo "▶ $ENTORNO: desplegando $VERSION"
ANTERIOR=$(cat .version-actual 2>/dev/null || echo latest)

# ── 1. La puerta (Caddy, compartida): registrar este entorno y que esté arriba ──
docker network inspect gastos-edge >/dev/null 2>&1 || docker network create gastos-edge
MAYUS=$(echo "$ENTORNO" | tr '[:lower:]' '[:upper:]')
(
  umask 077                                     # lleva el secreto de Vercel: solo para este usuario
  printf 'ACME_EMAIL=%s\nAPI_HOST_%s=%s\nORIGEN_SECRETO_%s=%s\n' \
    "$(valor ACME_EMAIL)" "$MAYUS" "$API_HOST" "$MAYUS" "$(valor ORIGEN_SECRETO)" > edge.env
)
mkdir -p ../edge/caddy
cp compose.edge.yaml ../edge/compose.edge.yaml
cp infra/Caddyfile ../edge/caddy/Caddyfile
$EDGE up -d --quiet-pull                        # recrea Caddy solo si cambió su entorno (un edge.env nuevo)
$EDGE exec -T caddy caddy reload --config /etc/caddy/Caddyfile   # y si solo cambió el Caddyfile, sin cortes

# ── 2. El entorno (módulos 83-85) ──
$COMPOSE pull --quiet
$COMPOSE up -d db redis rabbitmq collector kafka   # collector: módulo 84; kafka: módulo 85
$COMPOSE run --rm migrate                      # con el código NUEVO, mientras sirve el viejo
$COMPOSE run --rm topics                       # módulo 85: los topics (si ya existen, no hace nada)
$COMPOSE run --rm estadisticas-bd              # módulo 85: usuario y BD del servicio (idempotente)
$COMPOSE run --rm estadisticas-migrate         # módulo 85: migraciones de Alembic del servicio
# --no-deps: migrate ya se ejecutó. Y || : si algo no arranca, con set -e el script terminaría AQUÍ, sin
# volver atrás; quien decide es la comprobación de salud de abajo.
# shellcheck disable=SC2086
$COMPOSE up -d --no-deps --remove-orphans $SERVICIOS || echo "⚠️  docker compose up terminó con error"

# ── 3. ¿Responde a través de Caddy, con su certificado? ──
# --resolve: a este mismo servidor, sin depender del DNS (ni de que la VM se alcance a sí misma por su IP pública)
echo "▶ Comprobando salud en https://$API_HOST …"
for _ in $(seq 1 30); do
  if curl -fsS --resolve "$API_HOST:443:127.0.0.1" "https://$API_HOST/health/ready/" >/dev/null; then
    echo "$VERSION" > .version-actual
    # y en .env: cualquier "docker compose …" que se lance después a mano usará ESTA versión
    sed -i "s/^VERSION=.*/VERSION=$VERSION/" .env
    grep -q '^VERSION=' .env || echo "VERSION=$VERSION" >> .env
    docker image prune -f >/dev/null
    echo "✅ $ENTORNO: $VERSION desplegada"
    exit 0
  fi
  sleep 2
done

echo "❌ $ENTORNO: la versión $VERSION no responde: volviendo a $ANTERIOR"
# shellcheck disable=SC2086
VERSION=$ANTERIOR $COMPOSE up -d --no-deps $SERVICIOS
sed -i "s/^VERSION=.*/VERSION=$ANTERIOR/" .env
exit 1
