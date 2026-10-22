# hogares/api/base.py — la base de los recursos anidados en /hogares/{h}/… (módulos 33, 36 y 87)
# Vivía en finanzas/api: la usan también tickets, importaciones e informes, y es del hogar, no de las finanzas.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor

from ..permissions import HogarDesdeUrlMixin, RolEnHogar


class DelHogarMixin:
    """Limita los campos relacionados al hogar de la URL: no se puede apuntar a datos de otro hogar (módulo 33)."""

    campos_del_hogar: dict[str, type] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hogar = self.context.get("hogar")
        for campo, modelo in self.campos_del_hogar.items():
            if campo in self.fields and hogar is not None:
                self.fields[campo].queryset = modelo.objects.filter(hogar=hogar)


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
