# usuarios/infrastructure/database/models/passkey_model.py — una passkey registrada (módulo 92)
from django.conf import settings
from django.db import models
from django.utils import timezone


class Passkey(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="passkeys")
    credencial_id = models.BinaryField(unique=True)
    clave_publica = models.BinaryField()
    contador = models.BigIntegerField(default=0)
    nombre = models.CharField(max_length=60)
    sincronizada = models.BooleanField(default=False)
    transportes = models.JSONField(default=list, blank=True)
    creada = models.DateTimeField(default=timezone.now)
    ultimo_uso = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "passkey"

    def __str__(self):
        return f"{self.usuario_id}: {self.nombre}"
