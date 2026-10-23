# usuarios/infrastructure/api/v1/views/login_view.py — adapter de entrada HTTP (simplejwt) (módulos 35, 88, 91 y 92)
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.domain.enums.factor import Factor
from usuarios.infrastructure import container
from usuarios.infrastructure.api.sessions.peticion import contexto_de
from usuarios.infrastructure.api.v1.views.responder import responder
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class LoginView(VistaPublicaAuth):
    throttle_scope = "login"  # 5/min (DEFAULT_THROTTLE_RATES)

    def post(self, request, **kwargs):
        # 1. ¿Quién es? Campos: email (USERNAME_FIELD) y password. Malas, sin contraseña o inactiva → 401
        credenciales = TokenObtainSerializer(data=request.data, context={"request": request})
        credenciales.is_valid(raise_exception=True)
        # 2. La sesión (o el segundo paso): el mismo sitio que tras un proveedor (vuelta_social_view.py),
        #    IniciarSesionUseCase
        entrada = IniciarSesionInputDTO(credenciales.user.pk, Factor.CONTRASENA, contexto=contexto_de(request))
        return responder(container.iniciar_sesion().ejecutar(entrada))
