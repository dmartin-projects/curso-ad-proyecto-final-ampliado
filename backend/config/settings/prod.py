"""Producción (módulo 83): lo del módulo 67, con lo propio de este proyecto."""

from .base import *  # noqa: F403

DEBUG = False
# + localhost: el healthcheck de Docker llama a http://localhost:8000/health/live/ desde dentro del contenedor
ALLOWED_HOSTS = [*env.list("DJANGO_ALLOWED_HOSTS"), "localhost"]
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS")
FRONTEND_URL = env("FRONTEND_URL")  # enlaces de los correos: sin valor por defecto, que no salgan a localhost

# ── HTTPS detrás del proxy (módulos 29 y 65) ──
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # lo pone Caddy (no se fía del que llega)
# USE_X_FORWARDED_HOST sigue en False (módulo 86): el Host que valida Django es el de la API, el que pone Vercel
# al reenviar. Las URLs que el navegador ve (los enlaces de los correos) salen de FRONTEND_URL.
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^health/"]  # las sondas de Docker hablan HTTP dentro de la red interna
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=3600)  # súbelo a 1 año cuando todo funcione
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# La lista "preload" de los navegadores es casi irreversible: solo cuando HTTPS lleve meses funcionando bien
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)
SILENCED_SYSTEM_CHECKS = [
    # Módulo 90: el CLI (una app nativa) recibe el code en http://127.0.0.1:<puerto> (RFC 8252 §7.3), así que "http"
    # tiene que estar entre los esquemas permitidos. Que sea SOLO loopback lo exige el dominio al registrar el
    # cliente (oauth/domain/services/redirect_uris.py). Decisión consciente, no un aviso olvidado.
    "oauth2_provider.W008",
]
if not SECURE_HSTS_PRELOAD:
    SILENCED_SYSTEM_CHECKS.append("security.W021")  # decisión consciente, no un aviso olvidado
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
JWT_REFRESH_COOKIE["secure"] = True  # módulo 35

# ── Authorization server (módulo 90): sin valores por defecto, que no se despliegue con los de desarrollo ──
OAUTH_ISSUER = env("OAUTH_ISSUER")  # https://gastos.tudominio.com/api/oauth
OAUTH2_PROVIDER.update(urls_del_emisor(OAUTH_ISSUER))
OAUTH2_PROVIDER["OIDC_RSA_PRIVATE_KEY"] = env.str("OIDC_RSA_PRIVATE_KEY", multiline=True)
# (OIDC_RSA_PRIVATE_KEYS_INACTIVE, el de base.py: vacío salvo mientras se rota la clave, ejercicio 2 y runbook)

# ── MFA (módulo 92): sin la clave, nadie podría activar la verificación en dos pasos. Sin valor por defecto ──
MFA_CLAVES = env.list("MFA_CLAVES")

# ── Base de datos: pool en la web (ASGI) ──
# Con gunicorn + UvicornWorker cada petición síncrona corre en un hilo, y con CONN_MAX_AGE cada hilo se
# queda SU conexión abierta hasta 60 s: con carga, PostgreSQL responde "too many clients" (medido en el
# módulo 83: un 20 % de errores con 8 clientes). La documentación de Django lo dice: con ASGI, nada de
# conexiones persistentes; un pool. Solo en la web (DB_POOL_MAX en compose): los workers de Celery son
# procesos de un hilo, donde CONN_MAX_AGE va bien, y un pool (con su hilo) no se lleva bien con fork().
if POOL := env.int("DB_POOL_MAX", default=0):
    DATABASES["default"]["CONN_MAX_AGE"] = 0  # obligatorio con pool
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = False
    DATABASES["default"]["OPTIONS"] = {
        **DATABASES["default"].get("OPTIONS", {}),
        "pool": {"min_size": 1, "max_size": POOL, "timeout": 10},  # si se agota, espera hasta 10 s
    }

# ── Archivos: S3 compatible (Cloudflare R2 u Oracle Object Storage, módulo 68) con URLs firmadas ──
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": env("S3_BUCKET"),
            "endpoint_url": env("S3_ENDPOINT_URL"),
            "access_key": env("S3_ACCESS_KEY"),
            "secret_key": env("S3_SECRET_KEY"),
            "region_name": env("S3_REGION", default="auto"),  # R2 usa "auto"
            "signature_version": "s3v4",  # sin esto, en AWS las URLs firmadas salen con la firma v2 (obsoleta)
            "default_acl": None,
            "querystring_auth": True,  # los tickets y los extractos son privados
            "querystring_expire": 300,
            "file_overwrite": False,
            # Módulo 84: sin hilos. Con ellos (lo normal en boto3), cada subida va en otro hilo, el contexto de
            # OpenTelemetry no lo cruza y el S3.PutObject sale como una traza suelta. Con ficheros de ≤10 MB
            # los hilos (subida en paralelo por partes) no aportan nada.
            "use_threads": False,
        },
    },
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ── Email (módulo 22) ──
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": env("SMTP_HOST"),
            "port": env.int("SMTP_PORT", default=587),
            "username": env("SMTP_USER"),
            "password": env("SMTP_PASSWORD"),
            "use_tls": True,
            "timeout": 10,
        },
    },
}

# ── IA (módulo 74): sin clave no hay tickets; que falle al arrancar, no con el primer ticket ──
IA_API_KEY = env("IA_API_KEY")

# ── Logs en JSON (módulo 30) ──
LOGGING["handlers"]["consola"]["formatter"] = "json"

# ── DRF (módulos 32 y 36) ──
# La IP del navegador, para el throttling, en X-Forwarded-For. Con el frontend en Vercel (módulo 86) hay DOS
# proxies (Vercel → Caddy), pero Caddy deja UNA sola IP: la que manda Vercel si la petición trae su secreto, o
# la de quien conecta si no. Si Caddy añadiera la suya, la última sería la de Vercel: un contador para todos.
REST_FRAMEWORK["NUM_PROXIES"] = 1
# El esquema y Swagger, solo para el personal (en desarrollo, abiertos)
SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"] = ["rest_framework.permissions.IsAdminUser"]

# ── Sentry (módulo 30) ──
if dsn := env("SENTRY_DSN", default=""):
    import sentry_sdk

    from core.infrastructure.telemetry.telemetria import enlazar_sentry

    sentry_sdk.init(
        dsn=dsn,
        environment="produccion",
        release=env("VERSION", default=None),
        # Con OpenTelemetry activo (módulo 84) las trazas van a Grafana: Sentry solo para errores
        traces_sample_rate=0.0 if env.bool("OTEL_ENABLED", default=False) else 0.1,
        # sin datos personales: es el comportamiento por defecto (send_default_pii está obsoleto)
        before_send=enlazar_sentry,  # cada error lleva el trace_id de su traza en Grafana (módulo 84)
    )
