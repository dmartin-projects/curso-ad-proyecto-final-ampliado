# Gastos ampliado — el proyecto final con las ampliaciones del curso

Es Gastos (módulos 70-83) con las ampliaciones de las Partes 6 y 7 encima. **Cada módulo es un commit**, y sus ejercicios resueltos van en el commit siguiente (`git log --oneline`). Para ver qué añade un módulo: `git show <commit> --stat`. Para ver el proyecto tal como queda al terminar un módulo: `git switch --detach <commit>`.

## Resumen de las ampliaciones

| Módulo | Qué añade | Dónde mirar |
|---|---|---|
| **84 · OpenTelemetry y Grafana** | *Observability*: *traces*, *logs* y *metrics* de la web, Celery y la IA (atributos `gen_ai.*`) en Grafana (Tempo, Loki, Prometheus), con un panel y alertas provisionados. Apagado por defecto | `backend/core/telemetria.py`, `compose.observabilidad.yaml`, `infra/observabilidad/` |
| **85 · Kafka y FastAPI** | *Event-driven architecture*: *transactional outbox* en Django, un *relay* que publica en Kafka y un microservicio FastAPI (`estadisticas/`) que consume los *events*, mantiene su propia proyección en PostgreSQL y sirve estadísticas (tendencias, días de la semana). *Dead letter queue* para los mensajes venenosos | `backend/eventos/`, `estadisticas/`, `compose.eventos.yaml` |
| **86 · Despliegue profesional** | El *frontend* en Vercel (una *preview* por *pull request*), la API en una VM de Oracle con staging y producción detrás de un único Caddy, Terraform (Oracle, Vercel, Hostinger), secretos cifrados con SOPS + age y GitHub Environments | `frontend/vercel.json`, `compose.prod.yaml`, `compose.edge.yaml`, `infra/`, `.github/workflows/` |
| **87 · Arquitectura hexagonal (finanzas)** | *Hexagonal architecture* con CQRS y estructura explícita en la app `finanzas`, un archivo por clase: `domain/` (`bo/`, `vo/`, `enums/`, `exceptions/`, `events/`, `read_models/`, `repositories/` con las interfaces `I*CommandRepository` e `I*QueryService`), `application/` (un paquete por *use case* con su interfaz `I*UseCase` y sus `dtos/` `*InputDTO`/`*OutputDTO`; `ports/`) e `infrastructure/` (`api/v1/` con *views*, *serializers* y `urls.py`; `database/` con `models/` y `repositories/`; `container.py` como *composition root*); `config/api_v1.py` como router principal; capas vigiladas por import-linter en el CI | `docs/arquitectura.md`, `backend/finanzas/` |
| **88 · Hexagonal en el resto del monolito** | Las mismas convenciones en hogares, usuarios, tickets, importaciones, informes, notificaciones, eventos y *backoffice*; *anti-corruption layer* entre apps; 22 contratos de import-linter | `backend/*/domain`, `backend/*/application`, `backend/pyproject.toml` |
| **89 · Hexagonal en el microservicio FastAPI** | El servicio de estadísticas con **la misma estructura** que las apps del monolito: interfaces ABC, un paquete por *use case* con DTOs de Pydantic, `database/` con modelos y repositorios de SQLAlchemy, `api/v1|v2/` con *routers* y *schemas*, `Depends` sobre `container.py` como *composition root*, API versionada y Alembic comprobado en los tests | `estadisticas/estadisticas/`, `docs/arquitectura.md` §12 |

La Parte 7 (el agente de IA) se añadirá aquí con el mismo formato cuando esté terminada.

Estado comprobado al terminar el módulo 89: 432 tests de *backend* (1 se salta sin Kafka; con Kafka, los 24 de eventos pasan), 75 del servicio de estadísticas (Kafka y PostgreSQL reales), 26 de *frontend* (Vitest) y 10 de punta a punta (Playwright), todos en verde; `uv run lint-imports` sin violaciones.

## Estructura

```
backend/            Django 6.1 + DRF + Celery + Channels (módulos 71-79)
estadisticas/       microservicio FastAPI que consume los events de Kafka (módulos 85 y 89)
frontend/           Angular 22 (módulos 80-81), Playwright en e2e/ (módulo 82)
infra/              Caddyfile, csp.mjs, desplegar.sh, backup.sh (módulos 83 y 86); entornos/, secretos/, terraform/ (86)
compose.yaml        infraestructura de desarrollo: PostgreSQL, Redis, RabbitMQ, S3 (RustFS), Mailpit
compose.prod.yaml   un entorno de la VM: producción o staging (módulos 83 y 86); compose.edge.yaml: Caddy (86)
docs/               runbook.md (operar producción, módulos 83 y 86), arquitectura.md (estructura hexagonal y convenciones, módulos 87-92)
.github/workflows/  ci.yml (tests, E2E, lint-imports); preview, staging y producción (módulo 86)
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
cd backend && uv run pytest -n 4 --cov                 # 431 tests (+1 que se salta sin Kafka)
cd frontend && npx ng test --watch=false                # 16 tests
# punta a punta (módulo 82): una vez, crea la BD de E2E
docker compose exec db createdb -U gastos gastos_e2e
cd backend && DJANGO_SETTINGS_MODULE=config.settings.e2e uv run python manage.py migrate
cd ../frontend && npx playwright install chromium && npx playwright test
```

## Arrancar las ampliaciones en local

**84 · OpenTelemetry y Grafana.** Apagado por defecto. Para verlo en local:

```bash
docker compose -f compose.yaml -f compose.observabilidad.yaml up -d   # Grafana en http://localhost:3000
# en backend/.env: OTEL_ENABLED=true, OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318, OTEL_METRIC_EXPORT_INTERVAL=5000
OTEL_SERVICE_NAME=gastos-web uv run python manage.py runserver
OTEL_SERVICE_NAME=gastos-worker uv run celery -A config worker -l info -Q ocr,default
```

En producción, el servicio `collector` de `compose.prod.yaml` envía a Grafana Cloud con las variables `GRAFANA_CLOUD_*` de `.env.example`.

**85 · Kafka y el servicio de estadísticas.**

```bash
docker compose -f compose.yaml -f compose.eventos.yaml up -d   # Kafka en localhost:9092; panel en http://localhost:8090
cd backend
uv run python manage.py crear_topics
uv run python manage.py publicar_estado     # una vez: un event por cada movimiento que ya existía
uv run python manage.py publicar_eventos    # el relay del outbox (déjalo en su terminal)
cd ../estadisticas
uv run python -m estadisticas.consumidor    # en otra terminal
uv run uvicorn estadisticas.api:app --port 8100 --reload
```

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

**87-89 · Arquitectura hexagonal.** No hay nada nuevo que arrancar: es el mismo comportamiento con otra organización del código. Las reglas están en `docs/arquitectura.md`, y el CI las comprueba:

```bash
cd backend && uv run lint-imports        # capas y apps del monolito
cd estadisticas && uv run lint-imports   # capas del microservicio
```
