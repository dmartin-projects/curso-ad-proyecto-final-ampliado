# Gastos — proyecto final de referencia

El código completo del proyecto final del curso (módulos 70-83), tal como queda al terminar el módulo 83. Úsalo para **comparar** cuando algo no te funcione, no para copiarlo de golpe: el curso explica por qué cada archivo es como es.

Estado comprobado: 173 tests de *backend* (cobertura 93,6 %), 20 de *frontend* (Vitest) y 8 de punta a punta (Playwright), todos en verde.

## Estructura

```
backend/            Django 6.1 + DRF + Celery + Channels (módulos 71-79)
frontend/           Angular 22 (módulos 80-81), Playwright en e2e/ (módulo 82)
infra/              Caddyfile, csp.mjs, desplegar.sh, backup.sh (módulos 83 y 86); entornos/, secretos/, terraform/ (86)
compose.yaml        infraestructura de desarrollo: PostgreSQL, Redis, RabbitMQ, S3 (RustFS), Mailpit
compose.prod.yaml   un entorno de la VM: producción o staging (módulos 83 y 86); compose.edge.yaml: Caddy (86)
docs/               runbook.md (operar producción, módulos 83 y 86)
.github/workflows/  ci.yml (con el job E2E) y release.yml
```

## Plan por fases (módulo 70)

| Fase | Módulo | Resultado |
|---|---|---|
| 1. Base | 71 | Proyecto, usuario, hogares y roles, infraestructura de desarrollo |
| 2. Dominio | 72 | Modelos, migraciones, datos por defecto, *seed* |
| 3. API | 73 | CRUD con permisos por hogar, filtros, paginación, exportación |
| 4. Tickets | 74 | Subida → OCR → IA → gasto, con revisión |
| 5. Extractos | 75 | Importación idempotente |
| 6. Tiempo real | 76 | Notificaciones y alertas de presupuesto |
| 7. Dashboard | 77 | Agregaciones y caché |
| 8. Informes | 78 | PDF mensual, email, tareas programadas |
| 9. *Backoffice* | 79 | API de soporte dentro de la app (sin Django admin) |
| 10. *Frontend* | 80, 81 | App Angular completa |
| 11. Calidad | 82 | Tests de todo el *stack* |
| 12. Producción | 83 | Despliegue gratuito con CI/CD (`docs/runbook.md` para operarlo) |

## Arrancar en local

Requisitos (módulo 00): Docker Desktop, `uv`, Node 24, y para el OCR y los PDF `brew install tesseract tesseract-lang pango`.

```bash
# 1. Infraestructura
docker compose up -d
# bucket "gastos" en el S3 local (o créalo en la consola: http://localhost:9001/rustfs/console/, rustfs / rustfs12345)
(cd backend && uv run python -c "import boto3; boto3.client('s3', endpoint_url='http://localhost:9000', aws_access_key_id='rustfs', aws_secret_access_key='rustfs12345', region_name='us-east-1').create_bucket(Bucket='gastos')")

# 2. Backend
cd backend
cp .env.example .env              # pon tu IA_API_KEY de Gemini si quieres leer tickets con IA
uv sync
uv run python manage.py migrate
uv run python manage.py seed      # demo@example.com / demo12345-demo, con datos de ejemplo
uv run python manage.py runserver # API en http://localhost:8000/api/docs/

# 3. Procesos en segundo plano (cada uno en su terminal, desde backend/)
uv run celery -A config worker -l info -Q default,ocr
uv run celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
uv run python manage.py db_worker --queue-name "*"

# 4. Frontend
cd ../frontend
npm ci
npx ng serve                      # http://localhost:4200 (el proxy envía /api y /ws a Django)
```

Personal de soporte (el *backoffice* está dentro de la app, no hay Django admin): regístrate o usa el usuario demo y ejecuta `uv run python manage.py personal demo@example.com`.

## Tests

```bash
cd backend && uv run pytest -n 4 --cov                 # 172 tests
cd frontend && npx ng test --watch=false                # 10 tests
# punta a punta (módulo 82): una vez, crea la BD de E2E
docker compose exec db createdb -U gastos gastos_e2e
cd backend && DJANGO_SETTINGS_MODULE=config.settings.e2e uv run python manage.py migrate
cd ../frontend && npx playwright install chromium && npx playwright test
```

## Ampliaciones (Parte 6 del curso)

Cada módulo es un commit (`git log --oneline`), con sus ejercicios resueltos en el siguiente.

**84 · OpenTelemetry y Grafana.** Apagado por defecto. Para verlo en local:

```bash
docker compose -f compose.yaml -f compose.observabilidad.yaml up -d   # Grafana en http://localhost:3000
# en backend/.env: OTEL_ENABLED=true, OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318, OTEL_METRIC_EXPORT_INTERVAL=5000
OTEL_SERVICE_NAME=gastos-web uv run python manage.py runserver
OTEL_SERVICE_NAME=gastos-worker uv run celery -A config worker -l info -Q ocr,default
```

En producción, el servicio `collector` de `compose.prod.yaml` envía a Grafana Cloud con las variables `GRAFANA_CLOUD_*` de `.env.example`.

**86 · Despliegue profesional.** El *frontend* en Vercel (una preview por *pull request*), la API en la VM de Oracle con dos entornos (staging y producción) detrás de un único Caddy, la infraestructura en Terraform y los secretos cifrados con SOPS:

```
frontend/vercel.json          rewrite de /api y /estadisticas a la API de cada entorno, cabeceras, CSP y caché
compose.prod.yaml             UN entorno (el .env dice cuál); compose.edge.yaml: Caddy, la puerta de los dos
infra/entornos/*.env          configuración en claro;  infra/secretos/*.env: secretos cifrados (SOPS + age)
infra/terraform/              VM y red (Oracle), proyecto y variables (Vercel), DNS (Hostinger); terraform test
infra/local/vercel-local.mjs  un "Vercel" local para ensayar la topología entera en tu máquina
.github/workflows/            preview.yml (PR), staging.yml (main), produccion.yml (etiqueta v*, con aprobación)
```

Los pasos con tus cuentas (Oracle, Vercel, Hostinger, GitHub) están en el módulo 86 del curso.
