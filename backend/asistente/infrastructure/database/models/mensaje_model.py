# asistente/infrastructure/database/models/mensaje_model.py (módulo 97)
from django.db import models

from asistente.infrastructure.database.models.conversacion_model import Conversacion


class Mensaje(models.Model):
    """Un Mensaje del dominio tal cual (`contenido`, lo que se reenvía al modelo) y lo que pinta la interfaz."""

    class Rol(models.TextChoices):
        USUARIO = "usuario"
        MODELO = "modelo"
        TOOL = "tool"

    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name="mensajes")
    rol = models.CharField(max_length=10, choices=Rol)
    contenido = models.JSONField()  # el Mensaje del dominio (mappers/mensaje_mapper.py)
    texto = models.TextField(blank=True)
    visible = models.BooleanField(default=False)
    incompleto = models.BooleanField(default=False)
    motivo = models.CharField(max_length=20, blank=True)  # por qué quedó incompleto: cancelada, sin_modelo, error
    datos = models.JSONField(default=dict, blank=True)
    adjunto = models.CharField(max_length=255, blank=True)  # la ruta en el almacenamiento (nunca el nombre del cliente)
    nombre_adjunto = models.CharField(max_length=255, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.rol}: {self.texto[:40]}"
