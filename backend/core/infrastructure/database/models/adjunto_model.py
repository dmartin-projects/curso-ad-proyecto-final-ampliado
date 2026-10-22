# core/infrastructure/database/models/adjunto_model.py (módulos 15, 17 y 88)
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from core.infrastructure.database.models.modelo_con_fechas_model import ModeloConFechas


class Adjunto(ModeloConFechas):
    """Archivo adjunto a CUALQUIER objeto (movimiento, presupuesto…) mediante contenttypes (módulo 17)."""

    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    objeto = GenericForeignKey("content_type", "object_id")
    archivo = models.FileField(upload_to="adjuntos/%Y/%m/")
    nombre = models.CharField(max_length=200)
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")

    class Meta:
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return self.nombre
