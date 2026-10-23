# oauth/infrastructure/database/models/autenticacion_de_concesion_model.py — cómo se autenticó quien dio el acceso
# (módulo 92)
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


class AutenticacionDeConcesion(models.Model):
    """Módulo 92: cómo se autenticó la persona que dio el acceso. Sale en los ID tokens de esa concesión (amr, acr y
    auth_time): en el del canje del code y en los que se renuevan con sus refresh tokens. Se guarda primero con el hash
    del code y, al canjearlo, pasa a la familia de sus refresh tokens (token_family de django-oauth-toolkit)."""

    # SHA-256 del code, hasta que se canjea. NULL (y no ""): único entre los que lo tienen, y hay muchos sin él
    codigo = models.CharField(max_length=64, unique=True, null=True)  # noqa: DJ001
    familia = models.UUIDField(unique=True, null=True)
    amr = ArrayField(models.CharField(max_length=10))
    acr = models.CharField(max_length=40)
    auth_time = models.DateTimeField()
    creada = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.acr} ({', '.join(self.amr)})"
