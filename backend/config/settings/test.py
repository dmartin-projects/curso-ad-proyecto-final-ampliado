from cryptography.fernet import Fernet

from oauth.infrastructure.crypto.claves import nueva_clave_pem

from .base import *  # noqa: F403

ALLOWED_HOSTS = ["testserver", "localhost"]  # el validador de origen del WebSocket lo lee al importar asgi.py
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
TASKS = {"default": {"BACKEND": "django.tasks.backends.immediate.ImmediateBackend", "QUEUES": ["default", "emails"]}}
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
MAILERS = {"default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}}

EVENTOS_EXIGIR_TRANSACCION = True  # módulo 85: un evento fuera de atomic() rompe el test
EXIGIR_CASOS_DE_USO = True  # módulo 88: una escritura sin use case (sin sus eventos) rompe el test
# Módulo 90: una clave de firma nueva en cada ejecución (cada worker de xdist, la suya); nada que configurar
OAUTH2_PROVIDER["OIDC_RSA_PRIVATE_KEY"] = nueva_clave_pem()
# Módulo 92: una clave nueva para cifrar los secretos TOTP; las de los tests nunca han cifrado nada fuera de ellos
MFA_CLAVES = [Fernet.generate_key().decode()]
