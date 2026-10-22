# finanzas/infrastructure/database/models/cuenta_model.py — modelo de Django: el esquema de la tabla (módulos 72 y 87)
#
# Los modelos son PERSISTENCIA, no el dominio: las reglas viven en finanzas/domain y los repositorios traducen entre
# un BO y su fila. El archivo lleva el sufijo _model; la clase conserva su nombre (Cuenta): es el nombre del modelo
# para Django (tabla finanzas_cuenta, ContentType, permisos, migraciones).
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import ModeloConFechas
from hogares.models import Hogar


class Cuenta(ModeloConFechas):
    class Tipo(models.TextChoices):
        BANCO = "banco", _("Cuenta bancaria")
        TARJETA = "tarjeta", _("Tarjeta")
        EFECTIVO = "efectivo", _("Efectivo")

    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="cuentas")
    nombre = models.CharField(_("nombre"), max_length=80)
    tipo = models.CharField(_("tipo"), max_length=10, choices=Tipo, default=Tipo.BANCO)
    iban = models.CharField(_("IBAN"), max_length=34, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("cuenta")
        constraints = [models.UniqueConstraint(fields=["hogar", "nombre"], name="cuenta_nombre_unico_por_hogar")]

    def __str__(self):
        return self.nombre
