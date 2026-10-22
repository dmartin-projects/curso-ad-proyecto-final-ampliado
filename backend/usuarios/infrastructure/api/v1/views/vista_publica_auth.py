# usuarios/infrastructure/api/v1/views/vista_publica_auth.py — la base de las vistas públicas de autenticación (módulos 35 y 88)
from rest_framework import permissions
from rest_framework.views import APIView


class VistaPublicaAuth(APIView):
    """Base para login/refresh/registro: no autentica la petición, pero responde 401 (no 403)."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # un access caducado en la cabecera no debe estorbar

    def get_authenticate_header(self, request):
        return 'Bearer realm="api"'
