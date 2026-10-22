# finanzas/infrastructure/database/models/presupuesto_model.py (módulos 76 y 87)
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.models import ModeloConFechas
from finanzas.infrastructure.database.models.categoria_model import Categoria
from finanzas.infrastructure.database.querysets.presupuesto_queryset import PresupuestoQuerySet
from hogares.models import Hogar


class Presupuesto(ModeloConFechas):
    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="presupuestos")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="presupuestos")
    mes = models.DateField(_("mes"))  # siempre día 1
    importe = models.DecimalField(_("importe"), max_digits=10, decimal_places=2)
    alerta_enviada = models.BooleanField(default=False, editable=False)

    objects = PresupuestoQuerySet.as_manager()

    class Meta:
        verbose_name = _("presupuesto")
        constraints = [
            models.UniqueConstraint(fields=["hogar", "categoria", "mes"], name="presupuesto_unico"),
            models.CheckConstraint(condition=Q(mes__day=1), name="presupuesto_mes_dia_1"),
            models.CheckConstraint(condition=Q(importe__gt=0), name="presupuesto_importe_positivo"),
        ]
