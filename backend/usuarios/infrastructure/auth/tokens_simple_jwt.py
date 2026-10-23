# usuarios/infrastructure/auth/tokens_simple_jwt.py — ITokens con simplejwt (módulos 91 y 92)
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from usuarios.application.ports.i_tokens import ITokens
from usuarios.domain.vo.par_de_tokens import ParDeTokens


class TokensSimpleJWT(ITokens):
    """El mismo par que daba el login con contraseña (TokenObtainPairSerializer), para cualquier forma de entrar."""

    def emitir(self, usuario_id, sid):
        usuario = get_user_model().objects.get(pk=usuario_id)
        refresh = RefreshToken.for_user(usuario)
        # Módulo 92: la sesión a la que pertenece. Al rotar, simplejwt copia los claims al refresh nuevo (y al
        # access): el sid acompaña a la sesión de principio a fin
        refresh["sid"] = sid
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, usuario)
        return ParDeTokens(access=str(refresh.access_token), refresh=str(refresh), jti=refresh["jti"])
