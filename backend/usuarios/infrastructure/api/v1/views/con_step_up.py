# usuarios/infrastructure/api/v1/views/con_step_up.py — la base de las acciones sensibles (módulo 92)
from rest_framework import permissions
from rest_framework.views import APIView

from usuarios.infrastructure.api.permissions.autenticacion_reciente import AutenticacionReciente


class ConStepUp(APIView):
    """Una acción sensible: con la sesión de la SPA y una autenticación reciente (si no: 401 y el reto del RFC 9470)."""

    permission_classes = [permissions.IsAuthenticated, AutenticacionReciente]
