# usuarios/infrastructure/database/models/sesion_model.py — una sesión de Gastos: desde dónde, cuándo, con qué factores (módulo 92)
from django.conf import settings
from django.db import models
from django.utils import timezone


class Sesion(models.Model):
    """Una sesión abierta: la de la SPA (sus refresh tokens rotan, el `sid` se queda) o la del authorization server
    (la de Django, en /api/oauth/). Desde dónde, cuándo y con qué factores: para la lista de «Sesiones», el step-up
    (`autenticada` es el auth_time) y el aviso de dispositivo nuevo."""

    sid = models.UUIDField(primary_key=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sesiones")
    canal = models.CharField(max_length=20)
    factores = models.JSONField(default=list)
    passkey_sincronizada = models.BooleanField(default=False)
    autenticada = models.DateTimeField()  # la última vez que demostró quién es (al entrar o en un step-up)
    creada = models.DateTimeField(default=timezone.now)
    ultimo_uso = models.DateTimeField(default=timezone.now)  # en la SPA, la última rotación de su refresh
    caduca = models.DateTimeField()  # sin usarse hasta entonces, ya no está abierta (SesionesDjango.vida)
    dispositivo = models.CharField(max_length=64)  # SHA-256 de la cookie `dispositivo`, no la cookie
    descripcion = models.CharField(max_length=100, blank=True)  # "Chrome en macOS"
    ip = models.CharField(max_length=50, blank=True)  # aproximada: la red, no la máquina
    refresh_jti = models.CharField(max_length=64, blank=True)  # el del refresh vigente: solo ese la renueva
    refresh_jti_anterior = models.CharField(max_length=64, blank=True)  # el rotado (el de otra pestaña, al momento)
    cerrada = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "sesión"
        verbose_name_plural = "sesiones"
        indexes = [models.Index(fields=["usuario", "dispositivo"], name="sesion_usuario_dispositivo")]

    def __str__(self):
        return f"{self.sid} ({self.usuario_id}, {self.canal})"
