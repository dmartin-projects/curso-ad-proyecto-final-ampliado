# usuarios/infrastructure/auth/sesiones_simple_jwt.py — ISesiones con la lista negra de simplejwt (módulo 88)
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from usuarios.application.ports.i_sesiones import ISesiones


class SesionesSimpleJWT(ISesiones):
    def cerrar_todas(self, usuario_id):
        for t in OutstandingToken.objects.filter(user_id=usuario_id):
            BlacklistedToken.objects.get_or_create(token=t)
