# usuarios/infrastructure/api/v1/views/login_view.py — adapter de entrada HTTP (simplejwt) (módulos 35 y 88)
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from usuarios.infrastructure.api.v1.views.cookie_refresh import poner_cookie_refresh
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class LoginView(VistaPublicaAuth):
    throttle_scope = "login"  # 5/min (DEFAULT_THROTTLE_RATES)

    def post(self, request, **kwargs):
        serializer = TokenObtainPairSerializer(data=request.data)  # campos: email (USERNAME_FIELD) y password
        serializer.is_valid(raise_exception=True)  # credenciales malas → 401
        tokens = serializer.validated_data
        response = Response({"access": tokens["access"]})
        poner_cookie_refresh(response, tokens["refresh"])
        return response
