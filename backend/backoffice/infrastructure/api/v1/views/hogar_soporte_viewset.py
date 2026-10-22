# backoffice/infrastructure/api/v1/views/hogar_soporte_viewset.py — adapter de entrada HTTP del personal de soporte (módulos 79 y 88)
from rest_framework import viewsets
from rest_framework.response import Response

from backoffice.application.listar_hogares_soporte_use_case.dtos.listar_hogares_soporte_input_dto import (
    ListarHogaresSoporteInputDTO,
)
from backoffice.application.obtener_hogar_soporte_use_case.dtos.obtener_hogar_soporte_input_dto import (
    ObtenerHogarSoporteInputDTO,
)
from backoffice.infrastructure import container
from backoffice.infrastructure.api.permissions.personal import PERSONAL
from backoffice.infrastructure.api.v1.presenters import soporte_presenters as presentar
from backoffice.infrastructure.api.v1.serializers.hogar_detalle_soporte_serializer import HogarDetalleSoporteSerializer
from backoffice.infrastructure.api.v1.serializers.hogar_soporte_serializer import HogarSoporteSerializer
from backoffice.infrastructure.api.v1.views.listado_soporte_mixin import ListadoSoporteMixin
from core.infrastructure.api.views import consultas
from hogares.models import Hogar as HogarModel


class HogarSoporteViewSet(ListadoSoporteMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = PERSONAL
    permisos_por_accion = {"list": ["hogares.view_hogar"], "retrieve": ["hogares.view_hogar", "hogares.view_membresia"]}
    modelo = HogarModel
    search_fields = ["nombre", "=id", "membresias__usuario__email"]
    ordering_fields = ["creado", "num_movimientos"]
    ordering = ["-creado"]

    def get_serializer_class(self):
        return HogarDetalleSoporteSerializer if self.action == "retrieve" else HogarSoporteSerializer

    def list(self, request, *args, **kwargs):
        entrada = ListarHogaresSoporteInputDTO(self._query(request))
        return self._pagina(request, container.listar_hogares_soporte().ejecutar(entrada), presentar.hogar)

    def retrieve(self, request, *args, **kwargs):
        entrada = ObtenerHogarSoporteInputDTO(consultas.id_de_la_url(self))
        leido = self._o_404(container.obtener_hogar_soporte().ejecutar(entrada))
        return Response(self.get_serializer(presentar.hogar(leido)).data)
