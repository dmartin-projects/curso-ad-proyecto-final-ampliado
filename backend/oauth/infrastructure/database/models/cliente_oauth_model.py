# oauth/infrastructure/database/models/cliente_oauth_model.py — lo que Gastos añade a cada Application de django-oauth-toolkit (módulo 90)
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from oauth2_provider.settings import APPLICATION_MODEL


class ClienteOAuth(models.Model):
    """El tipo de cliente y los scopes que puede pedir. django-oauth-toolkit no guarda scopes por aplicación: sin
    esto, cualquier cliente podría pedir cualquier scope (el ScopesPorCliente del servidor los lee de aquí)."""

    class Tipo(models.TextChoices):
        NATIVA = "nativa", _("Aplicación nativa (CLI, escritorio, móvil)")
        WEB = "web", _("Aplicación web con backend")
        SERVICIO = "servicio", _("Servicio (máquina a máquina)")

    aplicacion = models.OneToOneField(APPLICATION_MODEL, on_delete=models.CASCADE, related_name="cliente_gastos")
    tipo = models.CharField(_("tipo"), max_length=10, choices=Tipo)
    scopes = ArrayField(models.CharField(max_length=40), verbose_name=_("scopes permitidos"))
    creado = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("cliente OAuth")
        verbose_name_plural = _("clientes OAuth")

    def __str__(self):
        return f"{self.aplicacion.name} ({self.tipo})"
