# finanzas/infrastructure/database/models/comercio_model.py (módulos 72 y 87)
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import ModeloConFechas
from finanzas.domain.services.normalizacion import normalizar


class Comercio(ModeloConFechas):
    """Comercio global (compartido entre hogares), con nombre normalizado para reconocerlo."""

    nombre = models.CharField(_("nombre"), max_length=120)
    nombre_normalizado = models.CharField(max_length=120, unique=True, editable=False)
    nif = models.CharField(_("NIF"), max_length=15, blank=True)
    categoria_sugerida = models.CharField(_("categoría sugerida"), max_length=60, blank=True)

    class Meta:
        verbose_name = _("comercio")
        indexes = [GinIndex(fields=["nombre_normalizado"], opclasses=["gin_trgm_ops"], name="comercio_trgm")]

    def save(self, *args, **kwargs):
        self.nombre_normalizado = normalizar(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
