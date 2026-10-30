# asistente/infrastructure/database/models/carpeta_model.py (módulo 97)
from django.conf import settings
from django.db import models

from core.models import ModeloConFechas
from hogares.models import Hogar


class Carpeta(ModeloConFechas):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="+")
    nombre = models.CharField(max_length=60)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["usuario", "hogar", "nombre"], name="asistente_carpeta_unica"),
        ]

    def __str__(self):
        return self.nombre
