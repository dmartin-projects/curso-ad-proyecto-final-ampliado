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
| **90 · OAuth 2.1 y OpenID Connect** | Gastos como *authorization server* (django-oauth-toolkit): *authorization code* + PKCE, *refresh tokens* con rotación y detección de reutilización, *client credentials*, ID tokens RS256 con JWKS y *discovery*, y el RFC 9700 activado; login y consentimiento en páginas de Django; la API como *resource server* (scope **y** rol en el hogar); `gastos-cli`, un cliente nativo escrito a mano | `backend/oauth/`, `cli/gastos_cli.py`, `docs/arquitectura.md` §1 y §3 |
| **91 · Social login (Google, GitHub, Apple)** | Gastos como **cliente** OIDC (*Relying Party*) con Authlib y el patrón BFF: Django hace la ida y la vuelta (`state`, `nonce`, PKCE), canjea el *code* con su secreto y valida el ID token; los *tokens* del proveedor no llegan al navegador y la SPA recibe los mismos *tokens* que con la contraseña. Google (OIDC), GitHub (OAuth 2.0 + su API, solo emails verificados) y Apple (`form_post` y *client secret* JWT ES256). Identidades por (proveedor, `sub`), sin vincular nunca por email; «Métodos de acceso» para vincular, desvincular (nunca el último) y establecer contraseña | `backend/usuarios/infrastructure/providers/`, `backend/usuarios/application/empezar_login_social_use_case/` y `completar_login_social_use_case/`, `frontend/src/app/features/cuenta/pages/acceso/acceso.ts` |
| **92 · MFA y login moderno** | Verificación en dos pasos con TOTP (secreto cifrado con Fernet, un código una vez, ±30 s) y códigos de recuperación con hash; *passkeys* (WebAuthn con py_webauthn y la API nativa del navegador) como segundo factor y para entrar sin contraseña (también en el autorrelleno); un único `IniciarSesionUseCase` para las cuatro puertas (contraseña y proveedor, en la SPA y en el *authorization server*), con `amr`/`acr` en el ID token; *step-up* (RFC 9470) para las acciones sensibles; sesiones con nombre (dispositivo, red, último uso), «cerrar las demás», caducidad y detección de reutilización del *refresh token* (RFC 9700, sin guardar ningún *token* en la base de datos); aviso por email de un dispositivo nuevo y de los fallos del segundo factor; bloqueo progresivo del segundo factor con techo (NIST SP 800-63B-4) | `backend/usuarios/application/iniciar_sesion_use_case/` (y los demás *use cases* de sesiones, MFA y *passkeys*), `backend/usuarios/infrastructure/mfa/`, `frontend/src/app/features/cuenta/pages/seguridad/seguridad.ts`, `frontend/src/app/core/auth/reautenticacion.ts` |
| **93 · LLMs para developers** | La app `asistente` (Parte 7) con su núcleo hexagonal: el *port* `ILLM` (una petición con instrucciones, historial, *tools*, *structured output* y razonamiento; un turno del modelo con sus *tokens* y su coste) y su *adapter* `OpenAICompatibleLLM` con el SDK `openai` sobre la API Chat Completions de **Groq** (`openai/gpt-oss-120b`; cualquier proveedor compatible cambiando la URL, la clave y el modelo), reintentos con tenacity solo de lo transitorio (el 429 dice cuánto esperar), `LLMFake` con guion para los tests y **cassettes** (pytest-recording) de llamadas reales: los tests no necesitan red ni clave. `manage.py probar_llm` para ver *tokens*, latencia, coste, *temperature*, razonamiento y *structured output* | `backend/asistente/`, `backend/asistente/tests/management/commands/cassettes/` |
| **94 · El *agent loop*** | El bucle del agente escrito a mano (`application/agent/agente.py`), sin *frameworks*: el modelo pide *tools*, se ejecutan y sus resultados (o sus errores, para que se corrija) vuelven al historial hasta que contesta. Guardas: `MAX_ITERATIONS` con la última vuelta sin *tools*, tiempo por pregunta, cuota por *tool*, llamadas repetidas y resultados recortados. `LLMConReserva`: `gpt-oss-20b` si `gpt-oss-120b` no está disponible, con un *circuit breaker* por modelo (un 429 lo abre lo que diga `retry-after`). Las dos primeras *tools* (`resumen_mes`, `gasto_por_categoria`) sobre los *use cases* de consulta de finanzas con un `Actor` limitado a LECTOR, y `manage.py preguntar` | `backend/asistente/application/agent/`, `backend/asistente/application/tools/`, `backend/asistente/infrastructure/llm/llm_con_reserva.py` |

Estado comprobado al terminar el módulo 94: 967 tests de *backend* (1 se salta sin Kafka; con Kafka, los 24 de eventos pasan), 75 del servicio de estadísticas (sin cambios desde el 89), 48 de *frontend* (Vitest) y 21 de punta a punta (Playwright), todos en verde; `uv run lint-imports` sin violaciones (30 contratos).

## Estructura

```
backend/            Django 6.1 + DRF + Celery + Channels (módulos 71-79)
estadisticas/       microservicio FastAPI que consume los events de Kafka (módulos 85 y 89)
frontend/           Angular 22 (módulos 80-81), Playwright en e2e/ (módulo 82)
cli/                gastos-cli: un cliente OAuth 2.1 + OIDC de la API, en un solo archivo (módulo 90)
infra/              Caddyfile, csp.mjs, desplegar.sh, backup.sh (módulos 83 y 86); entornos/, secretos/, terraform/ (86)
compose.yaml        infraestructura de desarrollo: PostgreSQL, Redis, RabbitMQ, S3 (RustFS), Mailpit, un proveedor OIDC falso (91)
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
cd backend && uv run pytest -n 4 --cov                 # 965 tests (+1 que se salta sin Kafka)
cd frontend && npx ng test --watch=false                # 38 tests
# punta a punta (módulo 82): una vez, crea la BD de E2E
docker compose exec db createdb -U gastos gastos_e2e
cd backend && DJANGO_SETTINGS_MODULE=config.settings.e2e uv run python manage.py migrate
cd ../frontend && npx playwright install chromium && npx playwright test   # arranca también el proveedor OIDC falso (91)
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

**90 · OAuth 2.1 y OpenID Connect.** Gastos es además un *authorization server*: otras aplicaciones (aquí, el CLI) piden acceso en nombre de un usuario. La SPA sigue con su login de siempre.

```bash
cd backend
uv run python manage.py generar_clave_oidc >> .env   # una vez: la clave que firma los ID tokens
uv run python manage.py migrate
uv run python manage.py crear_cliente_oauth "Gastos CLI" --tipo nativa --client-id gastos-cli \
    --scopes "openid email gastos:leer gastos:escribir" --redirect-uri http://127.0.0.1/callback
uv run python manage.py runserver                    # discovery: http://localhost:8000/api/oauth/.well-known/openid-configuration

# en otra terminal, desde la raíz del repositorio
uv run cli/gastos_cli.py login     # abre el navegador: entra (demo@example.com) y pulsa «Permitir»
uv run cli/gastos_cli.py hogares
uv run cli/gastos_cli.py gasto 1 --cuenta 1 --importe -3.20 --concepto Café
uv run cli/gastos_cli.py logout    # revoca el refresh token en el servidor
```

Ejercicios: «Aplicaciones conectadas» en el menú de la cuenta (retirar el acceso a una aplicación), la rotación de la clave de los ID tokens (`docs/runbook.md`) y el *device flow* para una máquina sin navegador:

```bash
uv run python manage.py crear_cliente_oauth "Gastos CLI (dispositivo)" --tipo dispositivo \
    --client-id gastos-cli-dispositivo --scopes "gastos:leer gastos:escribir"
uv run cli/gastos_cli.py login --dispositivo   # te da un código para http://localhost:8000/api/oauth/device/
```

En producción, el emisor es `https://gastos.tudominio.com/api/oauth` (`OAUTH_ISSUER` en `infra/entornos/`, la clave en `infra/secretos/`) y el CLI se apunta allí con `GASTOS_EMISOR`.

**91 · Social login (Google, GitHub, Apple).** Gastos es además **cliente** de otros proveedores: «Continuar con Google» en el login y «Métodos de acceso» en el menú de la cuenta. En local, un proveedor OpenID Connect falso (`compose.yaml`: `oidc`) hace de Google (y de Apple en los E2E): su pantalla de login acepta cualquier usuario y los *claims* que escribas.

```bash
docker compose up -d oidc                            # http://localhost:8089/google/.well-known/openid-configuration
# en backend/.env (están comentadas en .env.example):
#   GOOGLE_CLIENT_ID=gastos-local  GOOGLE_CLIENT_SECRET=gastos-local  GOOGLE_EMISOR=http://localhost:8089/google
cd backend && uv run python manage.py migrate && uv run python manage.py runserver
cd ../frontend && npx ng serve                       # http://localhost:4200/login → «Continuar con Google»
# en la pantalla del proveedor falso: un usuario cualquiera y, en claims, p. ej.
#   {"email": "ana@gmail.com", "email_verified": true, "given_name": "Ana"}
```

La vuelta es siempre `{FRONTEND_URL}/api/v1/auth/social/<proveedor>/vuelta/` (en local, a través del *proxy* de `ng serve`). GitHub admite `http://localhost:4200/…` como vuelta: crea una OAuth App (o una GitHub App) y pon `GITHUB_CLIENT_ID` y `GITHUB_CLIENT_SECRET`. Apple solo acepta vueltas `https` con dominio: se prueba en staging. Los pasos con tus cuentas de Google, GitHub y Apple están en el módulo 91 del curso; en producción, los `client_id` van en `infra/entornos/` y los secretos (y la clave `.p8` de Apple) en `infra/secretos/`. Las *previews* de Vercel no ofrecen el login social: su URL no está registrada en ningún proveedor.

Ejercicios: Microsoft Entra ID como cuarto proveedor (`MICROSOFT_CLIENT_ID` y `MICROSOFT_CLIENT_SECRET`; vuelta `…/social/microsoft/vuelta/`), un aviso por email al vincular un proveedor (en local llega a Mailpit, http://localhost:8025) y «Continuar con Google» también en el login del *authorization server* del módulo 90, para que una cuenta sin contraseña pueda autorizar el CLI (`uv run cli/gastos_cli.py login` y, en la pantalla de Gastos, «Continuar con Google»).

**92 · MFA, passkeys, step-up y sesiones.** En «Mi cuenta → Seguridad», la verificación en dos pasos (escanea el QR con cualquier app TOTP: Google Authenticator, 1Password, Aegis…) y las *passkeys*; en «Mi cuenta → Sesiones», dónde está abierta la cuenta. En local hace falta la clave que cifra los secretos TOTP (en `.env.example` hay una de desarrollo):

```bash
cd backend
grep -q MFA_CLAVES .env || uv run python manage.py generar_clave_mfa >> .env   # si tu .env es de antes del 92
uv run python manage.py migrate && uv run python manage.py runserver
cd ../frontend && npx ng serve                       # http://localhost:4200 → Mi cuenta → Seguridad
```

Las *passkeys* funcionan en `http://localhost` (el navegador lo trata como un origen seguro) y quedan atadas a `localhost`: las de staging y producción son de su dominio (el `rp_id` es el host de `FRONTEND_URL`) y en las *previews* de Vercel no se ofrecen. Sin móvil a mano, Chrome tiene un autenticador virtual en DevTools (*More tools → WebAuthn*). Las acciones sensibles (cambiar la contraseña, activar el MFA, añadir una *passkey*, borrar un hogar…) piden confirmar quién eres si entraste hace más de 5 minutos (`REAUTENTICACION_SEGUNDOS`). Los avisos («nuevo inicio de sesión», «has activado…») llegan a Mailpit (http://localhost:8025). En producción, `MFA_CLAVES` va en `infra/secretos/` (rotarla: `docs/runbook.md`); al desplegar, los *refresh tokens* anteriores al 92 no llevan sesión y se vuelve a entrar una vez.

Ejercicios: el *backoffice* exige al personal una sesión de dos factores (`manage.py personal` y, después, activar el MFA en «Seguridad»; una sesión abierta antes se sube de nivel confirmando con la app), códigos de recuperación nuevos desde «Seguridad» y el *step-up* de una cuenta sin contraseña con su proveedor (`max_age=0` y `auth_time` del ID token; con el proveedor falso de `compose.yaml`, escribe `"auth_time"` en los *claims*). En los E2E, `soporte@example.com` tiene el MFA activo con el secreto `JBSWY3DPEHPK3PXP` (`manage.py mfa_e2e`, solo con los ajustes de E2E).

**93 · El LLM del asistente.** Hace falta una clave de Groq (gratis, en https://console.groq.com/keys) en `backend/.env`; los tests no la necesitan: reproducen llamadas reales grabadas (cassettes).

```bash
cd backend
echo "ASISTENTE_API_KEY=gsk_…" >> .env
uv run python manage.py probar_llm "Explica qué es un presupuesto doméstico en una frase"
uv run python manage.py probar_llm "ayer pagué 23,40 en el Mercadona con la tarjeta" --estructurado
uv run python manage.py probar_llm "¿Qué variación hay entre 1.240 € y 1.116 €?" --esfuerzo alto --ver-razonamiento
# volver a grabar un cassette (con la clave en el entorno): uv run pytest asistente -k groq --record-mode=rewrite
```

Otro proveedor compatible con Chat Completions: `ASISTENTE_BASE_URL`, `ASISTENTE_API_KEY` y `ASISTENTE_MODELO` (por ejemplo, Ollama en local: `http://localhost:11434/v1`, clave `ollama`).

Ejercicios: el *structured output* validado con un modelo de pydantic que además genera el JSON Schema que se pide (`--estructurado`: un importe de 0 €, una fecha del futuro o una cuenta que no existe se rechazan), la misma extracción con tres modelos (`--modelo openai/gpt-oss-20b`, `--modelo qwen/qwen3.8-27b`) y el coste mensual del asistente.

**94 · El agente.** Con la clave de Groq en `.env` y los datos de ejemplo (`manage.py seed`):

```bash
cd backend
uv run python manage.py preguntar "¿Cuánto gastamos en septiembre y en qué categoría se fue más dinero?" --email demo@example.com --hogar 1
uv run python manage.py preguntar "¿En qué categoría gastamos más en septiembre que en agosto?" --email demo@example.com --hogar 1 --resultados
```

Cada vuelta del agente sale en la terminal (el modelo, las *tools* que pide, lo que devuelven) y al final las vueltas, los *tokens* y el coste. La reserva y los límites, en `.env`: `ASISTENTE_MODELOS_RESERVA` (por defecto `openai/gpt-oss-20b`) y `ASISTENTE_SEGUNDOS_POR_PREGUNTA` (60).

Ejercicios: un presupuesto de *tokens* por pregunta (`ASISTENTE_TOKENS_POR_PREGUNTA`, 10.000: pasado, la siguiente vuelta es la última), *tool calls* en paralelo con un modelo que las pide (`--modelo qwen/qwen3.8-27b`) y por qué se ejecutan en serie, y una línea de *log* por pregunta (`asistente.application.agent.agente`: vueltas, *tools*, modelos y *tokens*, sin la pregunta ni la respuesta).
