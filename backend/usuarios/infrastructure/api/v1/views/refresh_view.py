# usuarios/infrastructure/api/v1/views/refresh_view.py — adapter de entrada HTTP (simplejwt) (módulos 35 y 88)
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from usuarios.infrastructure.api.v1.views.cookie_refresh import poner_cookie_refresh
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class RefreshView(VistaPublicaAuth):
    def post(self, request, **kwargs):
        refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE["key"])
        if not refresh:
            return Response({"detail": "Sin sesión."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = TokenRefreshSerializer(data={"refresh": refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc
        response = Response({"access": serializer.validated_data["access"]})
        poner_cookie_refresh(response, serializer.validated_data["refresh"])  # rotación
        return response
