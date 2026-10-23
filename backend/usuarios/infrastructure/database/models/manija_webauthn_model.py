# usuarios/infrastructure/database/models/manija_webauthn_model.py — el user handle de WebAuthn de una cuenta (módulo 92)
from django.conf import settings
from django.db import models


class ManijaWebAuthn(models.Model):
    """El user handle de WebAuthn de una cuenta: 32 bytes aleatorios, ni el id ni el email (el autenticador lo guarda
    con la passkey y lo devuelve al entrar: así Gastos sabe de quién es sin que nadie escriba su email)."""

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    manija = models.BinaryField(unique=True)

    def __str__(self):
        return f"{self.usuario_id}"
