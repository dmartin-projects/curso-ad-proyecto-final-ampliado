# usuarios/infrastructure/api/v1/views/yo_view.py — los datos de quien ha iniciado sesión (módulos 35 y 88)
#
# CRUD sobre request.user, que ya ha cargado la autenticación (JWT): ni reglas ni efectos, sin use case (como las
# cuentas de finanzas, módulo 87).
from rest_framework import generics

from usuarios.infrastructure.api.v1.serializers.usuario_serializer import UsuarioSerializer


class YoView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer

    def get_object(self):
        return self.request.user
