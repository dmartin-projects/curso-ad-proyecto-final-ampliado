# usuarios/infrastructure/api/v1/views/registro_view.py — adapter de entrada HTTP de las cuentas (módulos 35 y 88)
from rest_framework import generics, permissions
from rest_framework.response import Response

from usuarios.application.solicitar_registro_use_case.dtos.solicitar_registro_input_dto import SolicitarRegistroInputDTO
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.serializers.registro_serializer import RegistroSerializer


class RegistroView(generics.GenericAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_scope = "registro"

    def post(self, request, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        container.solicitar_registro().ejecutar(SolicitarRegistroInputDTO(**s.validated_data))
        # 🔐 misma respuesta para un email nuevo, pendiente o con cuenta: no revela cuáles existen
        return Response({"detail": "Revisa tu email: te hemos enviado un enlace para continuar."}, status=202)
