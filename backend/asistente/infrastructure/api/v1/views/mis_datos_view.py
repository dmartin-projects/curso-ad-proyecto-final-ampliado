# asistente/infrastructure/api/v1/views/mis_datos_view.py — todo lo suyo, en un JSON (ejercicio 2 del 107)
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from asistente.application.exportar_mis_datos_use_case.dtos.exportar_mis_datos_input_dto import (
    ExportarMisDatosInputDTO,
)
from asistente.infrastructure import container
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar
from hogares.models import Membresia


class MisDatosView(HogarDesdeUrlMixin, APIView):
    permission_classes = [IsAuthenticated, RolEnHogar]
    roles_por_metodo = {"GET": Membresia.Rol.LECTOR}

    @extend_schema(responses={200: OpenApiResponse(description="Conversaciones y recuerdos de quien pide, en JSON")})
    def get(self, request, hogar_pk: int, **kwargs):
        datos = container.exportar_mis_datos().ejecutar(ExportarMisDatosInputDTO(self.hogar.pk, self.actor))
        respuesta = Response(datos)
        respuesta["Content-Disposition"] = f'attachment; filename="asistente-hogar-{self.hogar.pk}.json"'
        return respuesta
