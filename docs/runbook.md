# Runbook de Gastos (producción y staging)

Servidor: `/opt/gastos` (usuario `despliegue`), con un directorio por entorno (módulo 86):

```
/opt/gastos/produccion   compose.prod.yaml, infra/, .env (lo genera el despliegue), .version-actual
/opt/gastos/staging      lo mismo, con su .env: otro proyecto de Compose (gastos-staging), otra BD
/opt/gastos/edge         Caddy: la única puerta (80/443) para api.gastos.… y api.staging.gastos.…
```

Todo se hace desde el directorio del entorno. Su `.env` dice qué archivo y qué proyecto de Compose usar:

```bash
cd /opt/gastos/produccion     # o /opt/gastos/staging
alias dc='docker compose'     # COMPOSE_FILE, COMPOSE_PROJECT_NAME y VERSION, del .env
```

El `.env` del servidor **no se edita a mano**: lo regenera cada despliegue a partir de `infra/entornos/<entorno>.env` (en claro) e `infra/secretos/<entorno>.env` (cifrado con SOPS). Un cambio a mano se pierde en el siguiente despliegue.

## Ver el estado

```bash
dc ps                                   # todo "Up"; web, worker y worker-ocr "(healthy)"
curl -fsS https://api.gastos.tudominio.com/health/ready/   # 200 = BD y Redis bien
dc logs --since 15m web | grep '"levelname": "ERROR"'
docker stats --no-stream && df -h /
```

## Desplegar una versión

Lo normal (módulo 86): cada *merge* a `main` que pasa el CI va solo a **staging** (`staging.yml`). Para **producción**, una etiqueta en un commit que ya está en staging: `git tag v1.4.0 && git push --tags`; `produccion.yml` espera tu aprobación en GitHub (*environment* `produccion`) y despliega las mismas imágenes. A mano, en el servidor (con el `.env` ya generado):

```bash
cd /opt/gastos/produccion && VERSION=v1.4.0 ./infra/desplegar.sh
```

El script registra el entorno en Caddy, descarga las imágenes, ejecuta las migraciones con el código nuevo, levanta los servicios y comprueba `https://<API_HOST>/health/ready/` a través de Caddy durante 60 s. Si no responde, **vuelve solo** a la versión anterior (`.version-actual`) y termina con error.

## Volver atrás

```bash
cat .version-actual                    # la que está desplegada
VERSION=v1.3.2 ./infra/desplegar.sh    # cualquier versión anterior publicada en GHCR
```

Las migraciones **no** se deshacen: el código anterior debe tolerar el esquema nuevo (migraciones compatibles hacia atrás, módulo 10). Si una migración no lo era, restaura la copia de antes del despliegue (siguiente apartado) con la web parada.

## Restaurar una copia de la base de datos

Las copias se hacen a las 03:15 (`crontab -l`) en `r2:gastos-backups/postgres/` (30 días).

```bash
rclone ls r2:gastos-backups/postgres/ | sort -k2 | tail -5
rclone copy r2:gastos-backups/postgres/gastos-2026-10-18-0315.dump /tmp/
dc stop web worker worker-ocr beat tasks-worker           # que nadie escriba mientras tanto
dc exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner' \
  < /tmp/gastos-2026-10-18-0315.dump
dc up -d web worker worker-ocr beat tasks-worker
rm /tmp/gastos-2026-10-18-0315.dump
```

Ensayo (una vez al trimestre, fuera de producción): restaurar la última copia en un PostgreSQL vacío y comparar recuentos (`select count(*) from finanzas_movimiento`) con producción.

## Rotar `DJANGO_SECRET_KEY`

Si se ha filtrado o toca rotarla. Sin cortes para los usuarios:

1. Generar la nueva: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`.
2. En tu máquina, `sops edit infra/secretos/produccion.env`: la nueva en `DJANGO_SECRET_KEY` y la **vieja** en `DJANGO_SECRET_KEY_FALLBACKS`. Commit y PR.
3. Desplegar (nueva versión, o volver a lanzar el job de producción): el `.env` se regenera y `desplegar.sh` recrea los contenedores con el entorno nuevo.
4. Pasados unos días (lo que duran los enlaces de recuperación y las sesiones), vaciar `DJANGO_SECRET_KEY_FALLBACKS` y repetir los pasos 2 y 3.

Con la vieja en *fallbacks*, lo firmado antes (enlaces de recuperación de contraseña, valores firmados) sigue valiendo; sin ella, deja de valer (comprobado). **Si la clave se filtró**, sáltate el periodo de gracia: vacía *fallbacks* desde el principio.

Los JWT se firman con `JWT_SIGNING_KEY`, no con `SECRET_KEY`: rotar esta no cierra las sesiones de la app. Para cerrarlas todas (filtración de `JWT_SIGNING_KEY`), cambia `JWT_SIGNING_KEY`: todos los usuarios tendrán que volver a entrar.

## La cola de OCR crece sin parar

```bash
dc exec rabbitmq rabbitmqctl list_queues name messages consumers   # ocr con muchos mensajes y 0-1 consumidores
dc logs --since 30m worker-ocr | tail -50                         # ¿errores de la IA (cuota, clave)?
dc restart worker-ocr
```

Si la IA está caída o sin cuota, los tickets se reintentan solos y acaban en "Revisar" en el *backoffice* (Soporte → Tickets atascados), desde donde se reprocesan.

## El disco se llena

```bash
df -h / && docker system df
docker image prune -a -f --filter "until=168h"   # imágenes de versiones de hace más de una semana
docker builder prune -f
```

Los logs de los contenedores rotan solos (10 MB × 3 por servicio). Si es PostgreSQL: `dc exec db psql -U gastos -c "select pg_size_pretty(pg_database_size('gastos'))"`.

## Contactos y accesos

- Errores: Sentry (proyecto `gastos`). Disponibilidad: UptimeRobot. Copias y tareas: Healthchecks.io.
- Secretos: cifrados en el repositorio (`infra/secretos/`, SOPS + age). Las claves age: la tuya en el gestor de contraseñas ("Gastos — clave age personal"); las de cada entorno, en GitHub → Settings → Environments → `staging`/`produccion` → `SOPS_AGE_KEY` (y una copia en el gestor).
- Rotar el secreto entre Vercel y Caddy (`ORIGEN_SECRETO`): `sops edit` → `terraform apply` con `version_secretos` + 1 (Vercel) → desplegar el entorno (Caddy). Entre los dos pasos, la web de ese entorno recibe 403 de la API: hazlo seguido.
