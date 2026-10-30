"""Ajustes comunes a todos los entornos."""

from datetime import timedelta
from pathlib import Path

import environ
from celery.schedules import crontab
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
# Rotar la clave sin invalidar al instante sesiones, enlaces de recuperación… (módulos 29 y 67, runbook)
SECRET_KEY_FALLBACKS = env.list("DJANGO_SECRET_KEY_FALLBACKS", default=[])
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

DJANGO_APPS = [
    "daphne",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]
TERCEROS = [
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "channels",
    "django_celery_beat",
    "django_tasks_db",
    "oauth2_provider",  # módulo 90: Gastos como authorization server (OAuth 2.1 + OpenID Connect)
]
PROPIAS = [
    "core",
    "usuarios",
    "hogares",
    "finanzas",
    "tickets",
    "importaciones",
    "notificaciones",
    "informes",
    "backoffice",
    "eventos",  # módulo 85: outbox → Kafka
    "oauth",  # módulo 90: clientes, scopes, login y consentimiento del authorization server
    "asistente",  # Parte 7: el agente de IA
]
INSTALLED_APPS = DJANGO_APPS + TERCEROS + PROPIAS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "core.infrastructure.logging.request_id.request_id_middleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "oauth.infrastructure.web.middleware.sesion_vigente.SesionVigente",  # módulo 92: la sesión del authorization server, viva
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Módulo 90: los templates del authorization server viven con su adapter de entrada (oauth/infrastructure/web)
        "DIRS": [BASE_DIR / "templates", BASE_DIR / "oauth" / "infrastructure" / "web" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
# Módulo 101: el text-to-SQL del asistente se conecta a la MISMA base de datos con OTRO usuario: un rol que solo lee
# unas columnas y, por Row Level Security, solo las filas de un hogar (asistente/migrations/0005_consultas_sql.py).
# Sin contraseña no hay conexión (ni la tool consultar_sql): manage.py preparar_rol_sql se la pone al rol
ASISTENTE_SQL_USUARIO = "gastos_asistente_sql"
ASISTENTE_SQL_PASSWORD = env("ASISTENTE_SQL_PASSWORD", default="")

AUTH_USER_MODEL = "usuarios.Usuario"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es"
LANGUAGES = [("es", _("Español")), ("en", _("Inglés"))]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default='"Gastos" <no-responder@gastos.example>')
MAILERS = {"default": {"BACKEND": "django.core.mail.backends.console.EmailBackend"}}
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:4200")

# ── Caché, Channels, Celery ──
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6379/1"),
        "KEY_PREFIX": "gastos",
    }
}
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        # socket_timeout > 5: con redis-py 8 un WebSocket sin mensajes se cae cada 5 s (ver nota)
        "CONFIG": {
            "hosts": [{"address": env("REDIS_CHANNELS_URL", default="redis://localhost:6379/2"), "socket_timeout": 10}]
        },
    }
}
# ── WebSocket con el frontend en Vercel (módulo 86) ──
# Vercel no hace de proxy de WebSockets: el navegador abre el socket DIRECTAMENTE contra la API. Por eso
# la URL pública viaja en el ticket (WS_URL) y el Origin que llega es el de Vercel, no el de la API.
# Sin configurar (desarrollo, E2E, tests): el mismo host que la página y orígenes = ALLOWED_HOSTS, como antes.
WS_URL = env("WS_URL", default="")  # wss://api.gastos.tudominio.com/ws/notificaciones/
WS_ORIGENES = env.list("WS_ORIGENES", default=[])  # orígenes exactos: https://gastos.tudominio.com
# Las previews de UN proyecto de Vercel: https://<proyecto>-<9 letras o cifras>-<equipo>.vercel.app (staging)
VERCEL_PREVIEW_PROYECTO = env("VERCEL_PREVIEW_PROYECTO", default="")
VERCEL_PREVIEW_EQUIPO = env("VERCEL_PREVIEW_EQUIPO", default="")
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="amqp://guest:guest@localhost:5672//")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_SERIALIZER = CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_HIJACK_ROOT_LOGGER = False  # el worker usa nuestro LOGGING (con request_id)
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 270
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_ROUTES = {"tickets.tasks.*": {"queue": "ocr"}}  # el resto (importaciones…) va a "default"
# Tareas periódicas (módulo 78). Con el DatabaseScheduler de django-celery-beat se copian a la BD al
# arrancar Beat y se pueden pausar desde el backoffice (módulo 79). Horas en CELERY_TIMEZONE (Europe/Madrid).
CELERY_BEAT_SCHEDULE = {
    "informes-mensuales": {
        "task": "informes.tasks.generar_informes_mensuales",
        "schedule": crontab(minute=0, hour=7, day_of_month=1),
    },
    "limpiar-resultados-de-tareas": {
        "task": "core.tasks.limpiar_resultados_de_tareas",
        "schedule": crontab(minute=30, hour=3),
    },
    "limpiar-eventos-publicados": {  # módulo 85
        "task": "eventos.tasks.limpiar_eventos_publicados",
        "schedule": crontab(minute=45, hour=3),
    },
}

# core/infrastructure/tasks/agrupar.py: debounce de tareas repetidas (módulo 76). Solo se desactiva en E2E.
AGRUPAR_TAREAS = True

TASKS = {"default": {"BACKEND": "django_tasks_db.DatabaseBackend", "QUEUES": ["default", "emails"]}}

# ── DRF ──
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # El JWT de simplejwt; desde el módulo 92, el access de una sesión cerrada se rechaza ya (no a los 10 min)
        "usuarios.infrastructure.api.authentication.jwt_con_sesion.JWTConSesion",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser", "rest_framework.parsers.MultiPartParser"],
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.infrastructure.api.pagination.paginacion_estandar.PaginacionEstandar",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.ScopedRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {
        "login": "5/min",
        "registro": "5/hour",
        "recuperar": "3/hour",
        "subidas": "60/hour",
        "social": "20/min",  # módulo 91: empezar un inicio de sesión con un proveedor
        "mfa": "10/min",  # módulo 92: el segundo factor y el step-up (además del bloqueo por cuenta)
        "passkey": "20/min",  # módulo 92: entrar con una passkey (cada reto se guarda en Redis)
        "asistente": "20/min",  # módulo 97: cada pregunta cuesta tokens (las cuotas por plan, módulo 98)
    },
    "EXCEPTION_HANDLER": "core.infrastructure.api.exceptions.manejador_errores.manejador_errores",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    # Módulo 92: el refresh rotado deja de valer porque su Sesion ya recuerda otro (refresh_jti), y uno reutilizado
    # cierra la sesión: la lista negra de simplejwt (que guardaba cada refresh entero en la BD) ya no hace falta
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "SIGNING_KEY": env("JWT_SIGNING_KEY"),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
JWT_REFRESH_COOKIE = {
    "key": "refresh",
    "path": "/api/v1/auth/",
    "httponly": True,
    "secure": not DEBUG,
    "samesite": "Strict",
}
# ── OAuth 2.1 y OpenID Connect: Gastos como authorization server (módulo 90) ──
# La SPA NO usa esto para su propio login (sigue con el JWT de arriba): es para OTRAS aplicaciones (el CLI, la app
# móvil, el agente de la Parte 7) que actúan en nombre de un usuario, y para servicios (client credentials).
# El emisor es la URL pública: en producción, la del dominio de la app (Vercel reenvía /api/* a Django).
OAUTH_ISSUER = env("OAUTH_ISSUER", default="http://localhost:8000/api/oauth")
LOGIN_URL = "/api/oauth/login/"  # el login del authorization server (páginas de Django), no el de la SPA
# Su sesión de Django (y su cookie CSRF) solo viajan a /api/oauth/: la API nunca las recibe
SESSION_COOKIE_PATH = CSRF_COOKIE_PATH = "/api/oauth/"
# El modelo Application de django-oauth-toolkit es "swappable": la migración de oauth (ClienteOAuth) lo referencia
# por este ajuste, que tiene que existir aunque usemos el de serie
OAUTH2_PROVIDER_APPLICATION_MODEL = "oauth2_provider.Application"


def urls_del_emisor(emisor: str) -> dict:
    """Lo que depende de la URL pública del authorization server (e2e.py y prod.py la cambian: lo vuelven a aplicar)."""
    return {
        "OIDC_ISS_ENDPOINT": emisor,
        # Ejercicio 3 (device flow): adónde va la persona a escribir el código; con él ya puesto, para un QR
        "OAUTH_DEVICE_VERIFICATION_URI": f"{emisor}/device/",
        "OAUTH_DEVICE_VERIFICATION_URI_COMPLETE": f"{emisor}/device/?user_code={{user_code}}",
    }


OAUTH2_PROVIDER = {
    "OIDC_ENABLED": True,
    **urls_del_emisor(OAUTH_ISSUER),
    # La clave privada que firma los ID tokens (RS256); la pública, en el JWKS. `manage.py generar_clave_oidc`
    "OIDC_RSA_PRIVATE_KEY": env.str("OIDC_RSA_PRIVATE_KEY", multiline=True, default=""),
    # Ejercicio 2: las claves que ya no firman (o todavía no), pero se publican en el JWKS: rotar sin cortes (runbook)
    "OIDC_RSA_PRIVATE_KEYS_INACTIVE": [
        clave.replace("\\n", "\n") for clave in env.list("OIDC_RSA_PRIVATE_KEYS_INACTIVE", default=[])
    ],
    "OIDC_RESPONSE_TYPES_SUPPORTED": ["code"],  # solo authorization code: ni implicit ni hybrid
    "OIDC_TOKEN_ENDPOINT_AUTH_METHODS_SUPPORTED": ["client_secret_basic", "client_secret_post", "none"],
    "OAUTH2_GRANT_TYPES_SUPPORTED": [
        "authorization_code",
        "refresh_token",
        "client_credentials",
        "urn:ietf:params:oauth:grant-type:device_code",  # ejercicio 3
    ],
    "DEVICE_FLOW_INTERVAL": 5,  # segundos entre consultas del dispositivo (más deprisa: slow_down)
    "OAUTH2_RESPONSE_TYPES_SUPPORTED": ["code"],
    "SCOPES": {
        "openid": _("Saber quién eres (tu identificador en Gastos)"),
        "profile": _("Ver tu nombre, tu idioma y tu zona horaria"),
        "email": _("Ver tu email"),
        "gastos:leer": _("Ver los movimientos, las cuentas y el resumen de tus hogares"),
        "gastos:escribir": _("Apuntar movimientos en tus hogares"),
        "operaciones:leer": _("Ver el estado de las colas y los procesos (solo servicios internos)"),
    },
    "SCOPES_BACKEND_CLASS": "oauth.infrastructure.server.scopes_por_cliente.ScopesPorCliente",
    "OAUTH2_VALIDATOR_CLASS": "oauth.infrastructure.server.validador_gastos.ValidadorGastos",
    "ACCESS_TOKEN_GENERATOR": "oauth.infrastructure.server.generadores_de_tokens.generar_access_token",
    "REFRESH_TOKEN_GENERATOR": "oauth.infrastructure.server.generadores_de_tokens.generar_refresh_token",
    "AUTHORIZATION_CODE_EXPIRE_SECONDS": 60,  # el code vive segundos: se canjea al momento
    "ACCESS_TOKEN_EXPIRE_SECONDS": 600,  # 10 min, como el de la SPA
    "ID_TOKEN_EXPIRE_SECONDS": 600,
    "REFRESH_TOKEN_EXPIRE_SECONDS": 30 * 24 * 3600,  # 30 días SIN USARSE (cada uso lo rota y empieza de nuevo)
    "ROTATE_REFRESH_TOKEN": True,
    "REFRESH_TOKEN_REUSE_PROTECTION": True,  # un refresh token reutilizado revoca toda su familia (RFC 9700 §4.14)
    "REFRESH_TOKEN_GRACE_PERIOD_SECONDS": 0,
    "PKCE_REQUIRED": True,  # todos los clientes, también los confidenciales (OAuth 2.1)
    "REQUEST_APPROVAL_PROMPT": "force",  # el consentimiento, siempre
    # http solo para las redirect URIs de loopback de las apps nativas (RFC 8252): lo exige el dominio
    # (oauth/domain/services/redirect_uris.py), no esta lista. Sin comodines: comparación exacta.
    "ALLOWED_REDIRECT_URI_SCHEMES": ["https", "http"],
    "ALLOW_URI_WILDCARDS": False,
    # RFC 9700 (OAuth 2.0 Security BCP): todo lo que django-oauth-toolkit 3.4 deja activar ya (en la 4.0, por defecto)
    "COMPLIANT_BCP_RFC9700_IMPLICIT_GRANT": True,  # implicit: rechazado
    "COMPLIANT_BCP_RFC9700_PASSWORD_GRANT": True,  # password: rechazado
    "COMPLIANT_BCP_RFC9700_PKCE_METHOD": True,  # solo S256 (nada de "plain")
    "COMPLIANT_BCP_RFC9700_ACCESS_TOKEN_TRANSPORT": True,  # el token, en la cabecera; nunca en la URL
    "COMPLIANT_BCP_RFC9700_AUTHZ_RESPONSE_ISS": True,  # `iss` en la respuesta de /authorize (RFC 9207: mix-up)
    "COMPLIANT_BCP_RFC9700_TOKEN_STORAGE": True,  # en la BD, solo el hash de cada token
    "COMPLIANT_BCP_RFC9700_REFRESH_TOKEN": True,
    "COMPLIANT_BCP_RFC9700_REDIRECT_URI_MATCHING": True,
    "COMPLIANT_BCP_RFC9700_PKCE_REQUIRED": True,
}

# ── Social login: Gastos como cliente (Relying Party) de Google, GitHub y Apple (módulo 91) ──
# Un proveedor aparece en el login solo si tiene client_id. Su redirect URI, la que se registra en su consola, es
# {FRONTEND_URL}/api/v1/auth/social/<proveedor>/vuelta/ (el dominio de la app: Vercel reenvía /api/* a Django).
# En local y en los E2E, un proveedor OIDC falso (compose.yaml: oidc) hace de Google y de Apple.
SOCIAL_LOGIN = {
    "google": {
        "client_id": env("GOOGLE_CLIENT_ID", default=""),
        "client_secret": env("GOOGLE_CLIENT_SECRET", default=""),
        "emisor": env("GOOGLE_EMISOR", default="https://accounts.google.com"),
    },
    "github": {
        "client_id": env("GITHUB_CLIENT_ID", default=""),
        "client_secret": env("GITHUB_CLIENT_SECRET", default=""),
        "web": env("GITHUB_WEB", default="https://github.com"),
        "api": env("GITHUB_API", default="https://api.github.com"),
    },
    "apple": {
        "client_id": env("APPLE_SERVICES_ID", default=""),  # el Services ID: com.tudominio.gastos.web
        "equipo": env("APPLE_TEAM_ID", default=""),
        "clave_id": env("APPLE_KEY_ID", default=""),
        "clave_privada": env.str("APPLE_PRIVATE_KEY", multiline=True, default=""),  # el .p8, en una línea con \n
        "emisor": env("APPLE_EMISOR", default="https://appleid.apple.com"),
    },
    "microsoft": {  # ejercicio 1: Microsoft Entra ID, cuentas personales y de empresa (el endpoint `common`)
        "client_id": env("MICROSOFT_CLIENT_ID", default=""),
        "client_secret": env("MICROSOFT_CLIENT_SECRET", default=""),
        "emisor": env("MICROSOFT_EMISOR", default="https://login.microsoftonline.com/common/v2.0"),
    },
}
SOCIAL_LOGIN_SEGUNDOS = 600  # lo que puede tardar la persona en el proveedor (la transacción y su cookie)

# ── MFA, passkeys, step-up y sesiones (módulo 92) ──
# Las claves (Fernet) que cifran los secretos TOTP en la base de datos: cifra la primera, descifran todas (rotación:
# docs/runbook.md). `manage.py generar_clave_mfa`. Sin ellas no se puede activar el MFA.
MFA_CLAVES = env.list("MFA_CLAVES", default=[])
MFA_PENDIENTE_SEGUNDOS = 300  # entre la contraseña (o el proveedor) y el segundo factor
REAUTENTICACION_SEGUNDOS = 300  # una acción sensible exige haberse autenticado hace menos de esto (step-up)
# El rp_id de WebAuthn: por defecto, el host de FRONTEND_URL (las passkeys quedan atadas a ese dominio). El origen que
# se comprueba en cada ceremonia es el de FRONTEND_URL
WEBAUTHN_RP_ID = env("WEBAUTHN_RP_ID", default="")

SPECTACULAR_SETTINGS = {
    "TITLE": "API Gastos",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
    # dos modelos con un campo "estado" de opciones distintas: nombres explícitos para sus enums
    "ENUM_NAME_OVERRIDES": {
        "EstadoTicketEnum": "tickets.models.Ticket.Estado",
        "EstadoImportacionEnum": "importaciones.models.Importacion.Estado",
        # Módulo 97: dos campos "rol" con valores distintos (el de una membresía y el de un mensaje del chat)
        "RolEnum": "hogares.models.Membresia.Rol",
        "RolMensajeEnum": "asistente.infrastructure.api.v1.serializers.mensaje_serializer.ROLES",
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_id": {"()": "core.infrastructure.logging.request_id.RequestIdFilter"}},
    "formatters": {
        "texto": {"format": "{asctime} {levelname} {name} [{request_id}] [{traza}] {message}", "style": "{"},
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(request_id)s %(traza)s %(message)s",
        },
    },
    "handlers": {
        "consola": {
            "class": "logging.StreamHandler",
            "formatter": env("LOG_FORMAT", default="texto"),
            "filters": ["request_id"],
        }
    },
    "root": {"handlers": ["consola"], "level": "INFO"},
    "loggers": {
        "django.db.backends": {"level": "WARNING"},
        "httpx": {"level": "WARNING"},
        "httpx2": {"level": "WARNING"},  # el fork de httpx que usa el SDK de OpenAI (Parte 7): una línea por petición
        "weasyprint": {"level": "WARNING"},  # registra cada paso de cada PDF en INFO
        "fontTools": {"level": "WARNING"},
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Tickets: OCR + IA (módulo 74) ──
# Cualquier API compatible con Chat Completions de OpenAI. Por defecto, Gemini; en local, Ollama:
# IA_BASE_URL=http://localhost:11434/v1/  IA_MODELO=<un modelo multimodal descargado>  IA_API_KEY=ollama
IA_BASE_URL = env("IA_BASE_URL", default="https://generativelanguage.googleapis.com/v1beta/openai/")
IA_API_KEY = env("IA_API_KEY", default="")
IA_MODELO = env("IA_MODELO", default="gemini-3.8-flash")
IA_TIMEOUT = env.float("IA_TIMEOUT", default=30.0)
TICKETS_UMBRAL_CONFIANZA = env.float("TICKETS_UMBRAL_CONFIANZA", default=0.8)
TICKETS_TAMANO_MAXIMO = 10 * 1024 * 1024  # 10 MB

# ── Asistente: el agente de IA (Parte 7) ──
# Cualquier API compatible con Chat Completions. Por defecto, Groq (capa gratuita; la clave: console.groq.com/keys).
# En local, sin clave ni límites: ASISTENTE_BASE_URL=http://localhost:11434/v1 (Ollama) y un modelo con tools.
ASISTENTE_BASE_URL = env("ASISTENTE_BASE_URL", default="https://api.groq.com/openai/v1")
ASISTENTE_API_KEY = env("ASISTENTE_API_KEY", default="")
ASISTENTE_MODELO = env("ASISTENTE_MODELO", default="openai/gpt-oss-120b")
ASISTENTE_TIMEOUT = env.float("ASISTENTE_TIMEOUT", default=30.0)  # segundos por intento
# Módulo 94: si el principal no está disponible (o se ha quedado sin cuota), estos, en orden. En Groq, cada modelo
# tiene su propia cuota: el de reserva suele estar libre cuando el principal devuelve 429.
ASISTENTE_MODELOS_RESERVA = env.list("ASISTENTE_MODELOS_RESERVA", default=["openai/gpt-oss-20b"])
# Módulo 97: el modelo de las tareas fáciles (títulos; resúmenes en el 99): más rápido, más barato y con su propia cuota
ASISTENTE_MODELO_AUXILIAR = env("ASISTENTE_MODELO_AUXILIAR", default="openai/gpt-oss-20b")
ASISTENTE_SEGUNDOS_POR_PREGUNTA = env.float("ASISTENTE_SEGUNDOS_POR_PREGUNTA", default=60.0)
# Ejercicio 1 del 94: tokens (entrada + salida) por pregunta; pasados, la siguiente vuelta es la última. Con la capa
# gratuita de Groq (8.000 por minuto), una pregunta que pasa de aquí deja sin cuota a las demás de ese minuto.
ASISTENTE_TOKENS_POR_PREGUNTA = env.int("ASISTENTE_TOKENS_POR_PREGUNTA", default=10000)
# Módulo 95: los servicios externos de las tools (sin clave). Configurables para los tests y por si cambian de sitio
ASISTENTE_FRANKFURTER_URL = env("ASISTENTE_FRANKFURTER_URL", default="https://api.frankfurter.dev/v1/")
ASISTENTE_EUROSTAT_URL = env(
    "ASISTENTE_EUROSTAT_URL", default="https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
)
ASISTENTE_NAGER_URL = env("ASISTENTE_NAGER_URL", default="https://date.nager.at/api/v3/")  # ejercicio 1 del 95
# Dólares por millón de tokens: entrada, salida (con el razonamiento) y entrada desde la caché. Los publicados en
# console.groq.com/docs/models en octubre de 2026. Un modelo que no esté aquí sale con "coste desconocido".
ASISTENTE_PRECIOS = {
    "openai/gpt-oss-120b": ("0.15", "0.60", "0.075"),
    "openai/gpt-oss-20b": ("0.075", "0.30", "0.037"),
    "qwen/qwen3.8-27b": ("0.80", "4.00", "0.80"),  # ejercicio 2 (sin precio de caché publicado: el de entrada)
}
# Módulo 99: tokens (estimados) de conversación sin resumir a partir de los que se resume lo antiguo (con el modelo
# auxiliar, en una tarea de Celery). Por debajo de la ventana (3.000): se resume antes de tener que quitar nada
ASISTENTE_TOKENS_PARA_RESUMIR = env.int("ASISTENTE_TOKENS_PARA_RESUMIR", default=1500)
# Módulo 100: el modelo de embeddings de la búsqueda en la ayuda (fastembed, local). Vacío: sin vectores (solo
# búsqueda por texto). Se descarga la primera vez a la caché; en producción, al construir la imagen
ASISTENTE_EMBEDDINGS = env(
    "ASISTENTE_EMBEDDINGS", default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
ASISTENTE_EMBEDDINGS_CACHE = env("ASISTENTE_EMBEDDINGS_CACHE", default=str(BASE_DIR / ".cache" / "embeddings"))
# Módulo 101: la tool consultar_sql (text-to-SQL) en el chat. Apagada por defecto: las tools hacen lo mismo con menos
# riesgo (el módulo 101 lo mide); se enciende para comparar, o para preguntas que ninguna tool contesta
ASISTENTE_TEXT_TO_SQL = env.bool("ASISTENTE_TEXT_TO_SQL", default=False)
ASISTENTE_SQL_FILAS = 200  # como mucho, por consulta (la interfaz); al modelo, 50
ASISTENTE_SQL_SEGUNDOS = 2  # statement_timeout: una consulta que tarda más es una consulta mal hecha
ASISTENTE_SQL_COSTE_MAXIMO = 100_000  # ejercicio 2 del 101: el coste estimado (EXPLAIN) a partir del que ni se ejecuta
# Módulo 102: el clasificador de prompt injection para el texto de terceros (tickets, extractos, adjuntos), en el mismo
# proveedor (Groq). Vacío: sin clasificador (las demás defensas siguen). El umbral: la puntuación desde la que se retira
ASISTENTE_DETECTOR_INYECCION = env("ASISTENTE_DETECTOR_INYECCION", default="meta-llama/llama-prompt-guard-2-86m")
ASISTENTE_UMBRAL_INYECCION = env.float("ASISTENTE_UMBRAL_INYECCION", default=0.5)
# Módulo 104: MCP. La URI canónica del servidor MCP de Gastos (la que los clientes piden con `resource` al autorizar y
# la que tiene que llevar el token), bajo /api como el resto: en producción, {FRONTEND_URL}/api/mcp
ASISTENTE_MCP_URL = env("ASISTENTE_MCP_URL", default="http://localhost:8000/api/mcp")
# Los servidores MCP de OTROS de los que el agente usa tools: [{"nombre", "url", "token", "aprobadas": {tool: huella}}]
# (manage.py huellas_mcp para aprobar). El token de cada uno, el que ESE servidor emite: nunca el de la persona
ASISTENTE_MCP_SERVIDORES = env.json("ASISTENTE_MCP_SERVIDORES", default=[])
# Ejercicio 1 del 104: llamadas por minuto al servidor MCP, por persona y cliente
ASISTENTE_MCP_LLAMADAS_POR_MINUTO = env.int("ASISTENTE_MCP_LLAMADAS_POR_MINUTO", default=60)
# Ejercicio 2 del 105: los tokens de todo un análisis del mes (orquestador y especialistas); se para al pasarlo
ASISTENTE_ANALISIS_MAX_TOKENS = env.int("ASISTENTE_ANALISIS_MAX_TOKENS", default=60_000)
# Módulo 98: el proveedor, como lo nombran las convenciones GenAI de OpenTelemetry (gen_ai.provider.name)
ASISTENTE_PROVEEDOR = env("ASISTENTE_PROVEEDOR", default="groq")
# Las cuotas de cada plan: tokens al día por persona (entrada + salida) y dólares al mes por hogar. Una pregunta del chat
# gasta entre 3.000 y 15.000 tokens (módulo 96): el básico da para unas 10 preguntas al día por persona.
ASISTENTE_PLANES = {
    "basico": {"tokens_dia_persona": 80_000, "coste_mes_hogar": "0.50"},
    "plus": {"tokens_dia_persona": 400_000, "coste_mes_hogar": "5.00"},
}

# ── Importación de extractos (módulo 75) ──
IMPORTACION_TAMANO_MAXIMO = 5 * 1024 * 1024  # 5 MB
IMPORTACION_TAMANO_LOTE = 500  # filas por tarea del chord
IMPORTACION_DIAS_CONCILIACION = 3  # un gasto manual o de ticket y la fila del banco pueden diferir unos días

# ── Eventos: outbox → Kafka (módulo 85) ──
KAFKA_BOOTSTRAP_SERVERS = env("KAFKA_BOOTSTRAP_SERVERS", default="localhost:9092")
# ¿Fallar si un evento se guarda fuera de transaction.atomic()? En dev y tests sí (dev.py, test.py);
# en producción se registra el error y se sigue: perder el evento es malo, tirar la petición, peor.
EVENTOS_EXIGIR_TRANSACCION = False

# ¿Fallar si se escribe con el ORM algo cuyos eventos solo publica un use case? En dev, tests y E2E sí; en producción
# se registra el error y se sigue (core/infrastructure/signals/red_de_seguridad.py, módulo 88).
EXIGIR_CASOS_DE_USO = False
