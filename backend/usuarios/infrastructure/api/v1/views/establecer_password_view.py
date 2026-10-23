# usuarios/infrastructure/api/v1/views/establecer_password_view.py — poner contraseña a una cuenta sin ella (módulos 91 y 92)
from rest_framework import generics
from rest_framework.response import Response

from usuarios.application.establecer_contrasena_use_case.dtos.establecer_contrasena_input_dto import (
    EstablecerContrasenaInputDTO,
)
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.serializers.establecer_password_serializer import EstablecerPasswordSerializer
from usuarios.infrastructure.api.v1.views.con_step_up import ConStepUp


class EstablecerPasswordView(generics.GenericAPIView):
    serializer_class = EstablecerPasswordSerializer
    permission_classes = ConStepUp.permission_classes  # módulo 92: añade una forma de entrar

    def post(self, request, **kwargs):
        datos = self.get_serializer(data=request.data)
        datos.is_valid(raise_exception=True)
        container.establecer_contrasena().ejecutar(
            EstablecerContrasenaInputDTO(request.user.pk, datos.validated_data["nueva"])
        )
        return Response(status=204)
