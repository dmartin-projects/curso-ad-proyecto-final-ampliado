# hogares/infrastructure/database/models/hogar_model.py — la tabla de los hogares (módulos 71 y 88)
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import ModeloConFechas


class Hogar(ModeloConFechas):
    nombre = models.CharField(_("nombre"), max_length=100)
    moneda = models.CharField(_("moneda"), max_length=3, default="EUR")
    zona_horaria = models.CharField(_("zona horaria"), max_length=50, default="Europe/Madrid")
    miembros = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Membresia", related_name="hogares")

    class Meta:
        verbose_name = _("hogar")
        verbose_name_plural = _("hogares")

    def __str__(self):
        return self.nombre
