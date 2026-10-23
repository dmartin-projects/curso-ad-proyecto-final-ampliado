# usuarios/infrastructure/database/models/identidad_externa_model.py — una cuenta de otro proveedor vinculada (módulo 91)
from django.conf import settings
from django.db import models
from django.utils import timezone


class IdentidadExterna(models.Model):
    """Módulo 91: una cuenta de Google, GitHub o Apple vinculada a un usuario de Gastos.

    La clave es (proveedor, sub), nunca el email: el `sub` es el identificador estable de la persona en ESE proveedor.
    Ni un token del proveedor: Gastos solo los usa durante la vuelta, para saber quién es.
    """

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="identidades")
    proveedor = models.CharField(max_length=20)  # Proveedor del dominio (sin choices: uno nuevo no es una migración)
    sub = models.CharField(max_length=255)
    email = models.EmailField(blank=True)  # el que dio el proveedor al vincularla: para que la persona la reconozca
    creada = models.DateTimeField(default=timezone.now)
    ultimo_uso = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "identidad externa"
        verbose_name_plural = "identidades externas"
        constraints = [
            # Una identidad del proveedor es de UNA cuenta de Gastos
            models.UniqueConstraint(fields=["proveedor", "sub"], name="identidad_externa_unica"),
            # Y cada cuenta tiene como mucho una de cada proveedor (la pantalla «Métodos de acceso» lo da por hecho)
            models.UniqueConstraint(fields=["usuario", "proveedor"], name="un_proveedor_por_usuario"),
        ]

    def __str__(self):
        return f"{self.proveedor}:{self.sub} → {self.usuario_id}"
