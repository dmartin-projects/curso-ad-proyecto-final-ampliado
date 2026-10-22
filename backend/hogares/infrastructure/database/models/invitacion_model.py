# hogares/infrastructure/database/models/invitacion_model.py — _token y _caducidad viven aquí: la migración 0001 los usa como hogares.models._token y ._caducidad (módulos 71 y 88)
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import ModeloConFechas
from hogares.infrastructure.database.models.hogar_model import Hogar
from hogares.infrastructure.database.models.membresia_model import Membresia


def _token():
    return secrets.token_urlsafe(32)


def _caducidad():
    return timezone.now() + timedelta(days=7)


class Invitacion(ModeloConFechas):
    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="invitaciones")
    email = models.EmailField()
    rol = models.CharField(max_length=10, choices=Membresia.Rol, default=Membresia.Rol.MIEMBRO)
    token = models.CharField(max_length=64, unique=True, default=_token)
    invitado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    caduca = models.DateTimeField(default=_caducidad)
    aceptada = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("invitación")
        verbose_name_plural = _("invitaciones")
        constraints = [
            models.UniqueConstraint(
                fields=["hogar", "email"], condition=models.Q(aceptada__isnull=True), name="invitacion_pendiente_unica"
            ),
        ]

    @property
    def vigente(self) -> bool:
        return self.aceptada is None and self.caduca > timezone.now()
