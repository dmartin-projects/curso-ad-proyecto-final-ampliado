# hogares/infrastructure/database/models/membresia_model.py (módulos 36, 71 y 88)
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import ModeloConFechas
from hogares.infrastructure.database.models.hogar_model import Hogar


class Membresia(ModeloConFechas):
    class Rol(models.TextChoices):
        ADMIN = "admin", _("Administrador")
        MIEMBRO = "miembro", _("Miembro")
        LECTOR = "lector", _("Solo lectura")

    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="membresias")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="membresias")
    rol = models.CharField(_("rol"), max_length=10, choices=Rol, default=Rol.MIEMBRO)

    class Meta:
        verbose_name = _("membresía")
        constraints = [models.UniqueConstraint(fields=["hogar", "usuario"], name="membresia_unica")]

    def __str__(self):
        return f"{self.usuario} en {self.hogar} ({self.rol})"
