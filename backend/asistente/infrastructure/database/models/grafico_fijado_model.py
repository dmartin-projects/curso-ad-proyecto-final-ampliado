# asistente/infrastructure/database/models/grafico_fijado_model.py (módulo 97)
from django.conf import settings
from django.db import models

from core.models import ModeloConFechas
from hogares.models import Hogar


class GraficoFijado(ModeloConFechas):
    """QUÉ dibujar (la tool de datos y sus argumentos), no los números: se recalculan al mirarlo."""

    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="+")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    tipo = models.CharField(max_length=10)
    titulo = models.CharField(max_length=80)
    fuente = models.CharField(max_length=40)
    argumentos = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["creado", "id"]

    def __str__(self):
        return self.titulo
