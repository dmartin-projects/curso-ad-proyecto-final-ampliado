# asistente/infrastructure/api/v1/views/carpeta_viewset.py — las carpetas de quien pregunta (módulo 97)
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from asistente.application.crear_carpeta_use_case.dtos.crear_carpeta_input_dto import CrearCarpetaInputDTO
from asistente.application.eliminar_carpeta_use_case.dtos.eliminar_carpeta_input_dto import EliminarCarpetaInputDTO
from asistente.application.listar_carpetas_use_case.dtos.listar_carpetas_input_dto import ListarCarpetasInputDTO
from asistente.application.modificar_carpeta_use_case.dtos.modificar_carpeta_input_dto import ModificarCarpetaInputDTO
from asistente.infrastructure import container
from asistente.infrastructure.api.v1.serializers.carpeta_serializer import CarpetaSerializer
from asistente.infrastructure.api.v1.views.conversacion_viewset import TODOS
from core.infrastructure.api.views import consultas
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar


class CarpetaViewSet(HogarDesdeUrlMixin, viewsets.ViewSet):
    """Las carpetas de quien pide, para ordenar sus conversaciones."""

    permission_classes = [IsAuthenticated, RolEnHogar]
    lookup_field, lookup_url_kwarg, lookup_value_regex = "pk", None, r"\d+"
    roles_por_metodo = TODOS
    serializer_class = CarpetaSerializer

    @extend_schema(responses=CarpetaSerializer(many=True))
    def list(self, request, *args, **kwargs):
        carpetas = container.listar_carpetas().ejecutar(ListarCarpetasInputDTO(self.hogar.pk, self.actor))
        return Response(CarpetaSerializer(carpetas, many=True).data)

    @extend_schema(request=CarpetaSerializer, responses={201: CarpetaSerializer})
    def create(self, request, *args, **kwargs):
        datos = CarpetaSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        entrada = CrearCarpetaInputDTO(self.hogar.pk, self.actor, datos.validated_data["nombre"])
        return Response(
            CarpetaSerializer(container.crear_carpeta().ejecutar(entrada)).data, status=status.HTTP_201_CREATED
        )

    @extend_schema(request=CarpetaSerializer, responses=CarpetaSerializer)
    def partial_update(self, request, *args, **kwargs):  # ejercicio 1: renombrar
        datos = CarpetaSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        entrada = ModificarCarpetaInputDTO(
            self.hogar.pk, self.actor, consultas.id_de_la_url(self), datos.validated_data["nombre"]
        )
        return Response(CarpetaSerializer(container.modificar_carpeta().ejecutar(entrada)).data)

    def destroy(self, request, *args, **kwargs):
        entrada = EliminarCarpetaInputDTO(self.hogar.pk, self.actor, consultas.id_de_la_url(self))
        container.eliminar_carpeta().ejecutar(entrada)
        return Response(status=status.HTTP_204_NO_CONTENT)
