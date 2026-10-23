# usuarios/infrastructure/api/v1/views/logout_view.py — adapter de entrada HTTP (simplejwt) (módulos 35, 88 y 92)
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.domain.exceptions.dominio_exception import DominioException
from usuarios.application.cerrar_sesion_use_case.dtos.cerrar_sesion_input_dto import CerrarSesionInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class LogoutView(VistaPublicaAuth):
    def post(self, request, **kwargs):
        cfg = settings.JWT_REFRESH_COOKIE
        if refresh := request.COOKIES.get(cfg["key"]):
            try:
                token = RefreshToken(refresh)
                entrada = CerrarSesionInputDTO(token["user_id"], token.get("sid", ""))
                container.cerrar_sesion().ejecutar(entrada)  # su refresh ya no renueva
            except (TokenError, DominioException, KeyError):
                pass  # ya caducado, inválido o cerrado: da igual
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(cfg["key"], path=cfg["path"], samesite=cfg["samesite"])
        return response
