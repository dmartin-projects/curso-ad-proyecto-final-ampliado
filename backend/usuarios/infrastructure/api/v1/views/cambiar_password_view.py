# usuarios/infrastructure/api/v1/views/cambiar_password_view.py — adapter de entrada HTTP de las cuentas (módulos 35, 88 y 92)
from rest_framework import generics, permissions
from rest_framework.response import Response

from usuarios.application.cambiar_contrasena_use_case.dtos.cambiar_contrasena_input_dto import CambiarContrasenaInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.permissions.autenticacion_reciente import AutenticacionReciente
from usuarios.infrastructure.api.v1.serializers.cambiar_password_serializer import CambiarPasswordSerializer


class CambiarPasswordView(generics.GenericAPIView):
    serializer_class = CambiarPasswordSerializer
    permission_classes = [permissions.IsAuthenticated, AutenticacionReciente]  # módulo 92: step-up

    def post(self, request, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        entrada = CambiarContrasenaInputDTO(request.user.pk, s.validated_data["actual"], s.validated_data["nueva"])
        container.cambiar_contrasena().ejecutar(entrada)  # y cierra las demás sesiones
        return Response(status=204)
