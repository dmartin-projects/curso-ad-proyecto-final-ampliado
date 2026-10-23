# usuarios/infrastructure/api/v1/views/proveedores_sociales_view.py — el social login: con qué se puede entrar (módulo 91)
#
# La ida y la vuelta del social login son NAVEGACIONES del navegador (no llamadas de la SPA con su JWT): responden con
# redirecciones (entrar_social_view.py, vuelta_social_view.py). Las demás vistas son API de siempre.
from django.conf import settings
from rest_framework.response import Response

from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.vista_publica_auth import VistaPublicaAuth


class ProveedoresSocialesView(VistaPublicaAuth):
    """Los proveedores con los que se puede entrar, y el origen de la app: fuera de él, la SPA no los ofrece."""

    def get(self, request, **kwargs):
        disponibles = container.listar_proveedores().ejecutar()
        return Response(
            {"origen": settings.FRONTEND_URL, "proveedores": [{"id": p.id, "nombre": p.nombre} for p in disponibles]}
        )
