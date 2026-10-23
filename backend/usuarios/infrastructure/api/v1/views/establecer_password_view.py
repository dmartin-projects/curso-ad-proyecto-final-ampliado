# usuarios/infrastructure/api/v1/views/establecer_password_view.py — poner contraseña a una cuenta sin ella (módulo 91)
from rest_framework import generics
from rest_framework.response import Response

from usuarios.application.establecer_contrasena_use_case.dtos.establecer_contrasena_input_dto import (
    EstablecerContrasenaInputDTO,
)
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.serializers.establecer_password_serializer import EstablecerPasswordSerializer


class EstablecerPasswordView(generics.GenericAPIView):
    serializer_class = EstablecerPasswordSerializer

    def post(self, request, **kwargs):
        datos = self.get_serializer(data=request.data)
        datos.is_valid(raise_exception=True)
        container.establecer_contrasena().ejecutar(
            EstablecerContrasenaInputDTO(request.user.pk, datos.validated_data["nueva"])
        )
        return Response(status=204)
