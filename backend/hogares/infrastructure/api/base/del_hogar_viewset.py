# hogares/infrastructure/api/base/del_hogar_viewset.py — la base de los recursos anidados en /hogares/{h}/… (módulos 33, 36, 87 y 88)
#
# Es una de las piezas de hogares que las APIs de las demás apps SÍ pueden importar (contrato de import-linter).
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar


class DelHogarViewSet(HogarDesdeUrlMixin, viewsets.ModelViewSet):
    """Base de los recursos anidados en /hogares/{h}/…: permisos por rol, contexto y hogar automáticos."""

    permission_classes = [IsAuthenticated, RolEnHogar]
    modelo = None

    def get_queryset(self):
        if self.es_esquema():
            return self.modelo.objects.none()
        return self.modelo.objects.filter(hogar=self.hogar)

    def get_serializer_context(self):
        contexto = super().get_serializer_context()
        if not self.es_esquema():
            contexto["hogar"] = self.hogar
        return contexto

    def perform_create(self, serializer):
        serializer.save(hogar=self.hogar)

    @property
    def actor(self) -> Actor:
        """Quién pide el use case (módulo 87): el usuario y su rol en ESTE hogar (la membresía ya resuelta)."""
        return Actor(usuario_id=self.request.user.pk, rol=Rol(self.membresia.rol))
