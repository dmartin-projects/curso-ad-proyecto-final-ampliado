# usuarios/infrastructure/database/models/codigo_recuperacion_model.py — un código de recuperación, con hash (módulo 92)
from django.conf import settings
from django.db import models


class CodigoRecuperacion(models.Model):
    """Un código de un solo uso para cuando no tienes el móvil. Selector + verificador: el selector (4 caracteres)
    encuentra la fila; el verificador (12) se guarda con PBKDF2 y sal (pbkdf2_sha256$iteraciones$sal$hash), como una
    contraseña: una copia de la base de datos no los descubre."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="codigos_recuperacion")
    selector = models.CharField(max_length=4)
    verificador = models.CharField(max_length=128)
    usado = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "código de recuperación"
        verbose_name_plural = "códigos de recuperación"
        constraints = [models.UniqueConstraint(fields=["usuario", "selector"], name="codigo_recuperacion_unico")]

    def __str__(self):
        return f"{self.usuario_id}: {self.selector}…"
