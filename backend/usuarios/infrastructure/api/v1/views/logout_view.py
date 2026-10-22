# usuarios/infrastructure/api/v1/views/logout_view.py — adapter de entrada HTTP (simplejwt) (módulos 35 y 88)
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class LogoutView(VistaPublicaAuth):
    def post(self, request, **kwargs):
        cfg = settings.JWT_REFRESH_COOKIE
        if refresh := request.COOKIES.get(cfg["key"]):
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                pass  # ya caducado o inválido: da igual
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(cfg["key"], path=cfg["path"], samesite=cfg["samesite"])
        return response
