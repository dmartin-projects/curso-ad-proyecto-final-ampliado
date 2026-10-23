"""Backend para las pruebas de punta a punta (Playwright, módulo 82): todo en un proceso, sin servicios externos.

DJANGO_SETTINGS_MODULE=config.settings.e2e uv run python manage.py runserver 8000
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from oauth.infrastructure.crypto.claves import nueva_clave_pem

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
ROOT_URLCONF = "config.urls_e2e"
DATABASES["default"]["NAME"] = env("E2E_DB_NAME", default="gastos_e2e")

STORAGES["default"] = {"BACKEND": "django.core.files.storage.FileSystemStorage"}
MEDIA_ROOT = BASE_DIR / "media-e2e"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}  # un solo proceso (daphne)
CELERY_TASK_ALWAYS_EAGER = True  # las tareas se ejecutan al encolarlas (en on_commit, tras responder)
CELERY_TASK_EAGER_PROPAGATES = False
# Con "eager" no hay countdown: la tarea agrupada se ejecutaría al PRINCIPIO de la ventana y los cambios
# de los 10 s siguientes se descartarían (un presupuesto creado y, justo después, el gasto que lo supera:
# el aviso no llegaría nunca). En E2E cada cambio lanza su tarea (módulo 82).
AGRUPAR_TAREAS = False
TASKS = {"default": {"BACKEND": "django.tasks.backends.immediate.ImmediateBackend", "QUEUES": ["default", "emails"]}}
MAILERS = {"default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}}

# La "IA" es una vista de este mismo servidor que contesta como Chat Completions (config/urls_e2e.py)
IA_BASE_URL = "http://localhost:8000/e2e/ia/"
IA_API_KEY = "e2e"

# Los tests entran muchas veces por minuto: el límite real de "login" (5/min, módulo 35) los haría fallar
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {**REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"], "login": "1000/min"}
EXIGIR_CASOS_DE_USO = True  # módulo 88: los E2E también fallan si algo escribe sin use case
# Módulo 90: el authorization server, en el origen de la app (como en producción, donde Vercel reenvía /api/*),
# y una clave de firma nueva en cada arranque
OAUTH_ISSUER = "http://localhost:4200/api/oauth"
OAUTH2_PROVIDER.update(urls_del_emisor(OAUTH_ISSUER))
OAUTH2_PROVIDER["OIDC_RSA_PRIVATE_KEY"] = nueva_clave_pem()
# Módulo 91: Google y Apple son el proveedor OIDC falso (ghcr.io/navikt/mock-oauth2-server, compose.yaml: oidc), un
# emisor por proveedor. El "secreto" de Apple es un JWT ES256 firmado con una clave nueva en cada arranque
OIDC_FALSO = env("OIDC_FALSO", default="http://localhost:8089")
SOCIAL_LOGIN["google"] |= {"client_id": "gastos-e2e", "client_secret": "secreto-e2e", "emisor": f"{OIDC_FALSO}/google"}
SOCIAL_LOGIN["apple"] |= {
    "client_id": "com.example.gastos.web",
    "equipo": "EQUIPO1234",
    "clave_id": "CLAVE12345",
    "clave_privada": ec.generate_private_key(ec.SECP256R1())
    .private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    .decode(),
    "emisor": f"{OIDC_FALSO}/apple",
}
