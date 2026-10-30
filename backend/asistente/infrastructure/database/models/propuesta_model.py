# asistente/infrastructure/database/models/propuesta_model.py (módulo 97)
from django.conf import settings
from django.db import models

from asistente.infrastructure.database.models.conversacion_model import Conversacion
from core.models import ModeloConFechas
from hogares.models import Hogar


class Propuesta(ModeloConFechas):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente"
        CONFIRMADA = "confirmada"
        DESCARTADA = "descartada"

    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name="propuestas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="+")
    tipo = models.CharField(max_length=20)
    resumen = models.CharField(max_length=300)
    datos = models.JSONField()
    estado = models.CharField(max_length=10, choices=Estado, default=Estado.PENDIENTE)
    resultado = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.resumen
