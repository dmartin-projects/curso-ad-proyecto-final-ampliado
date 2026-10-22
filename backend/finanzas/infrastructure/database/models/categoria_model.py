# finanzas/infrastructure/database/models/categoria_model.py (módulos 72 y 87)
#
# Las constraints se quedan: son la última línea de defensa (y el repositorio traduce las que puede saltar el
# usuario a errores del dominio).
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.models import ModeloConFechas
from hogares.models import Hogar


class Categoria(ModeloConFechas):
    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="categorias")
    padre = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="hijas")
    nombre = models.CharField(_("nombre"), max_length=60)
    color = models.CharField(_("color"), max_length=7, default="#607d8b")
    icono = models.CharField(_("icono"), max_length=40, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)
    es_ingreso = models.BooleanField(_("es de ingresos"), default=False)

    class Meta:
        verbose_name = _("categoría")
        ordering = ["orden", "nombre"]
        constraints = [
            # nulls_distinct=False: dos categorías raíz (padre NULL) con el mismo nombre también chocan
            models.UniqueConstraint(
                fields=["hogar", "padre", "nombre"], nulls_distinct=False, name="categoria_unica_por_nivel"
            ),
            models.CheckConstraint(condition=Q(color__regex=r"^#[0-9a-fA-F]{6}$"), name="categoria_color_hex"),
        ]

    def __str__(self):
        return f"{self.padre} › {self.nombre}" if self.padre_id else self.nombre
