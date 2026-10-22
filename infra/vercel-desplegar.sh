#!/usr/bin/env bash
# infra/vercel-desplegar.sh — construye el frontend y lo publica en Vercel con su CLI (módulo 86).
# Lo usan los workflows (preview.yml, staging.yml, produccion.yml), desde la raíz del repositorio:
#   infra/vercel-desplegar.sh preview                                 → una preview; imprime su URL
#   infra/vercel-desplegar.sh preview staging.gastos.tudominio.com    → y además le asigna ese dominio
#   infra/vercel-desplegar.sh production                              → gastos.tudominio.com
# Necesita VERCEL_TOKEN, VERCEL_ORG_ID y VERCEL_PROJECT_ID (la CLI lee los dos últimos del entorno).
set -euo pipefail
ENTORNO="${1:?Uso: $0 preview|production [dominio]}"
DOMINIO="${2:-}"
: "${VERCEL_TOKEN:?Falta VERCEL_TOKEN}" "${VERCEL_ORG_ID:?Falta VERCEL_ORG_ID}" "${VERCEL_PROJECT_ID:?Falta VERCEL_PROJECT_ID}"
vercel() { npx --yes vercel@65.1.0 "$@" --token="$VERCEL_TOKEN"; }   # versión fija, como cualquier dependencia

# La configuración del proyecto (directorio raíz, variables de ESE entorno) → .vercel/
vercel pull --yes --environment="$ENTORNO" >&2
# El build, aquí en el runner (mismo Node, mismos tests que el CI); a Vercel solo se sube el resultado
if [ "$ENTORNO" = production ]; then
  vercel build --prod >&2
  node infra/csp.mjs .vercel/output >&2           # la CSP, con los hashes de ESTE index.html (autoCsp)
  URL=$(vercel deploy --prebuilt --prod --archive=tgz)
else
  vercel build >&2
  node infra/csp.mjs .vercel/output >&2
  # githubCommitRef: el despliegue "es de la rama", para el dominio asignado a main (vercel.tf)
  URL=$(vercel deploy --prebuilt --archive=tgz \
    --meta githubDeployment=1 --meta "githubCommitRef=${GITHUB_HEAD_REF:-${GITHUB_REF_NAME:-local}}")
fi
if [ -n "$DOMINIO" ]; then
  vercel alias set "$URL" "$DOMINIO" >&2
fi
echo "$URL"                                      # stdout: solo la URL (el resto, a stderr)
