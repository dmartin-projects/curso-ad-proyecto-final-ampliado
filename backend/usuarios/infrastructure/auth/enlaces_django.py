# usuarios/infrastructure/auth/enlaces_django.py — IEnlaces con el generador de tokens de Django (módulos 35 y 88)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from usuarios.application.ports.i_enlaces import IEnlaces


class EnlacesDjango(IEnlaces):
    def crear(self, usuario_id: int, ruta: str) -> str:
        usuario = get_user_model().objects.get(pk=usuario_id)
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        token = default_token_generator.make_token(usuario)  # depende del hash y del último login: un solo uso
        return f"{settings.FRONTEND_URL}/{ruta}?uid={uid}&token={token}"  # una página de Angular

    def usuario_de(self, uid: str, token: str) -> int | None:
        Usuario = get_user_model()
        try:
            usuario = Usuario.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
        except (Usuario.DoesNotExist, ValueError, TypeError, OverflowError):
            return None
        return usuario.pk if default_token_generator.check_token(usuario, token) else None
