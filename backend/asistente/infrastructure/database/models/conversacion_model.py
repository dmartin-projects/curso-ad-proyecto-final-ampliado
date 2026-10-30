# asistente/infrastructure/database/models/conversacion_model.py (módulos 97 y 99)
from django.conf import settings
from django.db import models

from asistente.infrastructure.database.models.carpeta_model import Carpeta
from core.models import ModeloConFechas
from hogares.models import Hogar


class Conversacion(ModeloConFechas):
    """De UNA persona en UN hogar. Si deja el hogar, sus conversaciones de ese hogar se quedan (no las ve: el
    contexto exige ser miembro); si se borra el hogar o la cuenta, se borran (CASCADE)."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="+")
    carpeta = models.ForeignKey(
        Carpeta, on_delete=models.SET_NULL, null=True, blank=True, related_name="conversaciones"
    )
    titulo = models.CharField(max_length=80, blank=True)
    titulo_manual = models.BooleanField(default=False)
    resumen = models.TextField(blank=True)  # módulo 99: lo antiguo, resumido (ver Conversacion.resumir)
    resumido_hasta = models.BigIntegerField(null=True, blank=True)  # el id del último mensaje que cuenta el resumen

    class Meta:
        ordering = ["-actualizado", "-id"]
        indexes = [models.Index(fields=["usuario", "hogar", "-actualizado"], name="asistente_conv_reciente")]

    def __str__(self):
        return self.titulo or f"Conversación {self.pk}"
