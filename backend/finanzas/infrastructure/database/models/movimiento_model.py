# finanzas/infrastructure/database/models/movimiento_model.py (módulos 72, 76 y 87)
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.models import ModeloConFechas
from finanzas.infrastructure.database.models.categoria_model import Categoria
from finanzas.infrastructure.database.models.comercio_model import Comercio
from finanzas.infrastructure.database.models.cuenta_model import Cuenta
from finanzas.infrastructure.database.querysets.movimiento_queryset import MovimientoQuerySet
from hogares.models import Hogar


class Movimiento(ModeloConFechas):
    class Origen(models.TextChoices):
        MANUAL = "manual", _("Manual")
        TICKET = "ticket", _("Ticket")
        EXTRACTO = "extracto", _("Extracto bancario")

    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="movimientos")
    cuenta = models.ForeignKey(Cuenta, on_delete=models.RESTRICT, related_name="movimientos")
    fecha = models.DateField(_("fecha"))
    importe = models.DecimalField(_("importe"), max_digits=12, decimal_places=2)  # < 0 gasto, > 0 ingreso
    concepto = models.CharField(_("concepto"), max_length=255)
    comercio = models.ForeignKey(Comercio, on_delete=models.SET_NULL, null=True, blank=True, related_name="movimientos")
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name="movimientos"
    )
    etiquetas = ArrayField(models.CharField(max_length=30), default=list, blank=True)
    notas = models.TextField(blank=True)
    origen = models.CharField(max_length=10, choices=Origen, default=Origen.MANUAL)
    huella = models.CharField(max_length=64, blank=True, editable=False)  # importaciones (módulo 75)
    revisado = models.BooleanField(_("revisado"), default=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    adjuntos = GenericRelation("core.Adjunto", related_query_name="movimiento")  # módulo 17

    objects = MovimientoQuerySet.as_manager()

    class Meta:
        verbose_name = _("movimiento")
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["hogar", "-fecha", "-id"], name="mov_hogar_fecha"),  # listado + cursor
            models.Index(fields=["hogar", "categoria", "fecha"], name="mov_hogar_cat_fecha"),  # dashboard
            models.Index(fields=["hogar"], condition=Q(revisado=False), name="mov_pendientes_revision"),
            GinIndex(fields=["etiquetas"], name="mov_etiquetas"),
        ]
        constraints = [
            models.CheckConstraint(condition=~Q(importe=Decimal("0")), name="movimiento_importe_no_cero"),
            models.UniqueConstraint(
                fields=["cuenta", "huella"], condition=~Q(huella=""), name="movimiento_huella_unica"
            ),
        ]

    def __str__(self):
        return f"{self.fecha} {self.concepto} {self.importe}"

    @property
    def es_gasto(self) -> bool:
        return self.importe < 0

    @classmethod
    def from_db(cls, db, field_names, values, **kwargs):
        """Recuerda la fecha con la que se cargó: si se edita, el mes ANTERIOR también cambia (módulo 76)."""
        # **kwargs: Django 6.1 añadió fetch_mode=…; reenviar lo que llegue evita romperse con la próxima
        instancia = super().from_db(db, field_names, values, **kwargs)
        instancia._fecha_cargada = instancia.__dict__.get("fecha")  # None si se cargó con only()/defer() sin fecha
        return instancia

    def meses_afectados(self) -> set:
        meses = {self.fecha.replace(day=1)}
        if (antes := getattr(self, "_fecha_cargada", None)) is not None:
            meses.add(antes.replace(day=1))
        return meses
