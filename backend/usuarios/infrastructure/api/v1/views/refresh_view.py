# usuarios/infrastructure/api/v1/views/refresh_view.py — adapter de entrada HTTP (simplejwt) (módulos 35, 88 y 92)
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from usuarios.application.renovar_sesion_use_case.dtos.renovar_sesion_input_dto import RenovarSesionInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.sessions.peticion import contexto_de
from usuarios.infrastructure.api.v1.views.cookie_refresh import poner_cookie_refresh
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class RefreshView(VistaPublicaAuth):
    def post(self, request, **kwargs):
        refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE["key"])
        if not refresh:
            return Response({"detail": "Sin sesión."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = TokenRefreshSerializer(data={"refresh": refresh})
        try:
            presentado = RefreshToken(refresh)  # firma, caducidad y tipo
            serializer.is_valid(raise_exception=True)
            nuevo = RefreshToken(serializer.validated_data["refresh"])  # el rotado: el mismo sid, otro jti
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc
        # Módulo 92: la sesión decide. Cerrada (desde otro dispositivo, al cambiar la contraseña) o con un refresh
        # que ya no es el vigente (reutilizado: la cierra) → SesionCerradaException, 401
        entrada = RenovarSesionInputDTO(
            presentado.get("sid", ""), presentado["jti"], nuevo["jti"], contexto_de(request)
        )
        rotar = container.renovar_sesion().ejecutar(entrada)
        response = Response({"access": serializer.validated_data["access"]})
        if rotar:  # (si no, otra pestaña acaba de rotarlo: su cookie ya trae el nuevo)
            poner_cookie_refresh(response, serializer.validated_data["refresh"])
        return response
