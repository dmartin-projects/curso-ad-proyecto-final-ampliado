# asistente/infrastructure/database/models/recuerdo_model.py — lo que el asistente recuerda de alguien (módulo 99)
from django.conf import settings
from django.db import models

from hogares.models import Hogar


class Recuerdo(models.Model):
    """De una persona en un hogar, como sus conversaciones: si se borra una de las dos, se borra (CASCADE)."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="+")
    texto = models.CharField(max_length=200)
    creado = models.DateTimeField()

    class Meta:
        ordering = ["creado", "id"]
        indexes = [models.Index(fields=["usuario", "hogar"], name="asistente_recuerdo_persona")]

    def __str__(self):
        return self.texto
