#!/bin/sh
# infra/estadisticas-bd.sh — usuario y base de datos del servicio de estadísticas (módulo 85). Idempotente.
# Lo ejecuta el servicio estadisticas-bd de compose.prod.yaml con el usuario administrador de PostgreSQL.
# El servicio solo puede tocar SU base de datos: ni ve ni puede abrir la de Django.
set -eu
psql -v ON_ERROR_STOP=1 -v clave="$ESTADISTICAS_DB_PASSWORD" -v bd_django="$PGDATABASE" <<'SQL'
SELECT format('CREATE ROLE estadisticas LOGIN PASSWORD %L', :'clave')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'estadisticas') \gexec
-- La contraseña, siempre la del .env (por si se ha rotado)
SELECT format('ALTER ROLE estadisticas PASSWORD %L', :'clave') \gexec
SELECT 'CREATE DATABASE estadisticas OWNER estadisticas'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'estadisticas') \gexec
-- Por defecto, cualquier usuario puede CONECTARSE a cualquier base de datos (luego no ve las tablas sin
-- permisos, pero mejor que ni entre): solo el dueño de la de Django puede abrirla
SELECT format('REVOKE CONNECT ON DATABASE %I FROM PUBLIC', :'bd_django') \gexec
SQL
echo "Base de datos de estadísticas lista"
