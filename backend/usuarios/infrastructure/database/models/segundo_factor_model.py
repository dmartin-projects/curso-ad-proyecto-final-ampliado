# usuarios/infrastructure/database/models/segundo_factor_model.py — el TOTP de una cuenta y su contador de fallos (módulo 92)
from django.conf import settings
from django.db import models


class SegundoFactor(models.Model):
    """El TOTP de una cuenta y su contador de fallos. El secreto, cifrado (Fernet con MFA_CLAVES): quien lea la base
    de datos (una copia de seguridad, un volcado) no puede generar códigos."""

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    secreto = models.TextField(blank=True)  # el token de Fernet: versión, momento, IV, cifrado y HMAC
    activo = models.BooleanField(default=False)
    ultimo_paso = models.BigIntegerField(null=True, blank=True)
    fallos = models.PositiveIntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "segundo factor"
        verbose_name_plural = "segundos factores"

    def __str__(self):
        return f"{self.usuario_id}: {'activo' if self.activo else 'inactivo'}"
