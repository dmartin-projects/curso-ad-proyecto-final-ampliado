# usuarios/infrastructure/api/v1/views/login_view.py — adapter de entrada HTTP (simplejwt) (módulos 35, 88 y 91)
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.cookie_refresh import poner_cookie_refresh
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class LoginView(VistaPublicaAuth):
    throttle_scope = "login"  # 5/min (DEFAULT_THROTTLE_RATES)

    def post(self, request, **kwargs):
        # 1. ¿Quién es? Campos: email (USERNAME_FIELD) y password. Malas, sin contraseña o inactiva → 401
        credenciales = TokenObtainSerializer(data=request.data, context={"request": request})
        credenciales.is_valid(raise_exception=True)
        # 2. La sesión: el mismo sitio que tras un proveedor (vuelta_social_view.py), IniciarSesionUseCase
        sesion = container.iniciar_sesion().ejecutar(IniciarSesionInputDTO(credenciales.user.pk))
        response = Response({"access": sesion.access})
        poner_cookie_refresh(response, sesion.refresh)
        return response
