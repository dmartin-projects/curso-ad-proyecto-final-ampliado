#!/usr/bin/env bash
# infra/duckdns.sh — la ALTERNATIVA sin dominio propio (módulo 86): apunta tus subdominios de Duck DNS a la VM.
# Duck DNS no tiene provider de Terraform: se actualiza con una URL. Una vez tras crear la VM (la IP es
# reservada y no cambia), o a mano si algún día cambia:
#   DUCKDNS_TOKEN=… ./infra/duckdns.sh gastos-api-tunombre,gastos-api-staging-tunombre 203.0.113.10
set -euo pipefail
SUBDOMINIOS="${1:?Uso: $0 sub1,sub2 [ip]  (sin .duckdns.org)}"
IP="${2:-}"                                     # vacía: Duck DNS usa la IP desde la que llamas
: "${DUCKDNS_TOKEN:?Falta DUCKDNS_TOKEN (está en https://www.duckdns.org al iniciar sesión)}"

respuesta=$(curl -fsS --get "https://www.duckdns.org/update" \
  --data-urlencode "domains=$SUBDOMINIOS" --data-urlencode "token=$DUCKDNS_TOKEN" --data-urlencode "ip=$IP")
if [ "$respuesta" != "OK" ]; then                 # Duck DNS responde 200 también cuando falla: "KO"
  echo "❌ Duck DNS respondió '$respuesta' (¿token o subdominio mal?)" >&2
  exit 1
fi
echo "✅ $SUBDOMINIOS → ${IP:-la IP de este equipo}"
