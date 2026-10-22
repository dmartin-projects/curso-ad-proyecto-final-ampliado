# finanzas/infrastructure/api/v1/views/comercio_viewset.py — adapter de entrada HTTP (módulos 74 y 87)
from rest_framework import filters, mixins, viewsets

from finanzas.application.listar_comercios_use_case.dtos.listar_comercios_input_dto import ListarComerciosInputDTO
from finanzas.infrastructure import container
from finanzas.infrastructure.api.v1.serializers.comercio_serializer import ComercioSerializer
from finanzas.infrastructure.api.v1.views import consultas
from finanzas.infrastructure.database.models.comercio_model import Comercio as ComercioModel


class ComercioViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Autocompletado de comercios (global): /comercios/?search=merca"""

    queryset = ComercioModel.objects.none()  # solo para el esquema OpenAPI: los datos, del use case
    serializer_class = ComercioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre"]

    def list(self, request, *args, **kwargs):
        entrada = ListarComerciosInputDTO(consultas.busqueda(request), self.paginator.paginacion(request))
        pagina = container.listar_comercios().ejecutar(entrada)
        return self.paginator.respuesta(request, pagina, self.get_serializer(pagina.results, many=True).data)
