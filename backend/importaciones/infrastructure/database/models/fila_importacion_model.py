# importaciones/infrastructure/database/models/fila_importacion_model.py (módulos 75 y 88)
from django.db import models
from django.utils.translation import gettext_lazy as _

from finanzas.models import Movimiento
from importaciones.infrastructure.database.models.importacion_model import Importacion


class FilaImportacion(models.Model):
    """Área de preparación (*staging*): lo leído del archivo, ya normalizado, antes de crear nada."""

    class Accion(models.TextChoices):
        CREAR = "crear", _("Crear")
        DUPLICADA = "duplicada", _("Ya existe")
        CONCILIAR = "conciliar", _("Coincide con un gasto existente")

    importacion = models.ForeignKey(Importacion, on_delete=models.CASCADE, related_name="filas")
    numero = models.PositiveIntegerField()  # línea del archivo (para los mensajes)
    fecha = models.DateField()
    concepto = models.CharField(max_length=255)
    importe = models.DecimalField(max_digits=12, decimal_places=2)
    huella = models.CharField(max_length=64)
    accion = models.CharField(max_length=10, choices=Accion)
    coincide_con = models.ForeignKey(Movimiento, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    movimiento = models.ForeignKey(Movimiento, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")

    class Meta:
        ordering = ["numero"]
        constraints = [models.UniqueConstraint(fields=["importacion", "numero"], name="fila_numero_unico")]
        indexes = [models.Index(fields=["importacion", "accion"], name="fila_importacion_accion")]

    def __str__(self):
        return f"{self.fecha} {self.concepto} {self.importe}"
