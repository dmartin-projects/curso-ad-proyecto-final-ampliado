# usuarios/infrastructure/database/cifrado.py — los secretos TOTP, cifrados en la base de datos (módulo 92)
#
# Un secreto TOTP no se puede guardar con hash, como una contraseña: Gastos lo necesita EN CLARO para calcular el
# código que espera. Así que se cifra (Fernet: AES-128-CBC + HMAC-SHA256, con la versión y el momento dentro) con una
# clave que NO está en la base de datos: MFA_CLAVES, del entorno (SOPS en staging y producción). MultiFernet admite
# varias: cifra con la primera y descifra con cualquiera. Rotar = poner una nueva delante, ejecutar
# `manage.py rotar_clave_mfa` (vuelve a cifrar todo con ella) y, en el siguiente despliegue, quitar la vieja.
from cryptography.fernet import Fernet, MultiFernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _cifrador() -> MultiFernet:
    if not settings.MFA_CLAVES:
        raise ImproperlyConfigured("Falta MFA_CLAVES: uv run python manage.py generar_clave_mfa")
    return MultiFernet([Fernet(clave) for clave in settings.MFA_CLAVES])


def cifrar(texto: str) -> str:
    return _cifrador().encrypt(texto.encode()).decode()


def descifrar(cifrado: str) -> str:
    return _cifrador().decrypt(cifrado.encode()).decode()  # InvalidToken si no es de ninguna de las claves


def recifrar(cifrado: str) -> str:
    """Con la clave nueva (la primera), venga de la que venga: la rotación."""
    return _cifrador().rotate(cifrado.encode()).decode()
