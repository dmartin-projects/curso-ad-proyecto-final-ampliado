# eventos/infrastructure/database/models/evento_pendiente_model.py — la tabla del outbox (módulos 85 y 88)
from django.db import models
from django.db.models import Q


class EventoPendiente(models.Model):
    """Outbox (módulo 85): un mensaje para Kafka, guardado en la MISMA transacción que el cambio que cuenta.

    Si la transacción se deshace, el evento desaparece con ella; si se confirma, el relay
    (`manage.py publicar_eventos`) lo publica en Kafka tarde o temprano, aunque Kafka esté caído ahora.
    El id hace de número de versión: es creciente y el relay publica en ese orden.
    """

    topic = models.CharField(max_length=100)
    clave = models.CharField(max_length=100)  # misma clave → misma partición → mismo orden
    valor = models.JSONField(null=True)  # None = "tombstone": este objeto ya no existe
    tipo = models.CharField(max_length=50)  # movimiento.creado, movimiento.actualizado…
    traceparent = models.CharField(max_length=55, blank=True)  # la traza de quien hizo el cambio (módulo 84)
    creado = models.DateTimeField(auto_now_add=True)
    publicado = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "evento pendiente"
        verbose_name_plural = "eventos pendientes"
        indexes = [
            # El relay solo busca los no publicados: índice parcial, pequeño aunque la tabla crezca
            models.Index(fields=["id"], condition=Q(publicado__isnull=True), name="evento_sin_publicar"),
            models.Index(fields=["publicado"], condition=Q(publicado__isnull=False), name="evento_publicado"),
        ]

    def __str__(self):
        return f"{self.tipo} {self.clave} (#{self.pk})"
