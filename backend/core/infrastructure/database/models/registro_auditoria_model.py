# core/infrastructure/database/models/registro_auditoria_model.py (módulos 15, 17 y 88)
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models


class RegistroAuditoria(models.Model):
    """Quién cambió qué y cuándo, sobre cualquier modelo (módulos 15 y 17)."""

    class Accion(models.TextChoices):
        CREAR = "crear"
        MODIFICAR = "modificar"
        BORRAR = "borrar"

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    accion = models.CharField(max_length=10, choices=Accion)
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.CharField(max_length=40)
    objeto = GenericForeignKey("content_type", "object_id")
    representacion = models.CharField(max_length=200)
    cambios = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["content_type", "object_id", "-fecha"])]
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.fecha:%Y-%m-%d %H:%M} {self.accion} {self.representacion}"
