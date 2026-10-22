# tickets/infrastructure/database/models/linea_ticket_model.py (módulos 74 y 88)
from django.db import models
from django.db.models import F

from tickets.infrastructure.database.models.ticket_model import Ticket


class LineaTicket(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="lineas")
    orden = models.PositiveSmallIntegerField()
    descripcion = models.CharField(max_length=200)
    cantidad = models.DecimalField(max_digits=8, decimal_places=3, default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    # GeneratedField (módulo 06): la base de datos calcula y guarda el importe; nunca se desincroniza
    importe = models.GeneratedField(
        expression=F("cantidad") * F("precio_unitario"),
        output_field=models.DecimalField(max_digits=12, decimal_places=2),
        db_persist=True,
    )

    class Meta:
        ordering = ["orden"]
        constraints = [models.UniqueConstraint(fields=["ticket", "orden"], name="linea_orden_unico")]

    def __str__(self):
        return self.descripcion
