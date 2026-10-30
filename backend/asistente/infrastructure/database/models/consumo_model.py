# asistente/infrastructure/database/models/consumo_model.py — el libro de cuentas del asistente (módulo 98)
from django.conf import settings
from django.db import models

from hogares.models import Hogar


class Consumo(models.Model):
    """Una fila por pregunta y modelo (y una por título). Solo se añaden. Sin el texto de la pregunta ni de la respuesta:
    es contabilidad, no un registro de conversaciones (privacidad, módulo 107).

    Si se borra la persona o el hogar, la fila se queda sin ellos (SET_NULL): el dinero se gastó, y el total del mes no
    puede cambiar porque alguien se dé de baja."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    hogar = models.ForeignKey(Hogar, on_delete=models.SET_NULL, null=True, related_name="+")
    conversacion_id = models.BigIntegerField(null=True, blank=True)  # sin FK: borrar la conversación no borra el gasto
    canal = models.CharField(max_length=20)
    modelo = models.CharField(max_length=100)
    tokens_entrada = models.PositiveIntegerField()  # incluye los de la caché
    tokens_cache = models.PositiveIntegerField(default=0)
    tokens_salida = models.PositiveIntegerField()  # incluye el razonamiento
    tokens_razonamiento = models.PositiveIntegerField(default=0)
    coste = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)  # USD; null: sin precio
    momento = models.DateTimeField()

    class Meta:
        indexes = [
            # la cuota de una persona (hoy) y la de un hogar (este mes): por hogar y momento, y la persona dentro
            models.Index(fields=["hogar", "momento"], name="asistente_consumo_hogar"),
            models.Index(fields=["usuario", "hogar", "momento"], name="asistente_consumo_persona"),
            models.Index(fields=["momento"], name="asistente_consumo_momento"),  # el informe de costes de un mes
        ]

    def __str__(self):
        return f"{self.modelo}: {self.tokens_entrada}+{self.tokens_salida}"
