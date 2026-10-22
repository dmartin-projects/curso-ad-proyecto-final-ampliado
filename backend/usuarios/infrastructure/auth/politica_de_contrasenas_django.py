# usuarios/infrastructure/auth/politica_de_contrasenas_django.py — IPoliticaDeContrasenas con los AUTH_PASSWORD_VALIDATORS de Django (módulo 88)
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError

from usuarios.application.ports.i_politica_de_contrasenas import IPoliticaDeContrasenas


class PoliticaDeContrasenasDjango(IPoliticaDeContrasenas):
    """Los AUTH_PASSWORD_VALIDATORS de Django (longitud, comunes, parecida al email…)."""

    def incumplimientos(self, password, *, usuario_id):
        usuario = get_user_model().objects.get(pk=usuario_id)
        try:
            password_validation.validate_password(password, user=usuario)
        except ValidationError as error:
            return list(error.messages)
        return []
