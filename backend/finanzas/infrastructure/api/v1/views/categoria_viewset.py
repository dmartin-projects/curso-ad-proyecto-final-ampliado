# finanzas/infrastructure/api/v1/views/categoria_viewset.py — adapter de entrada HTTP (módulos 33-38, 87 y 88)
#
# Una view hace tres cosas: traduce la request (serializer o query params → InputDTO), llama al use case que le da
# el container y traduce el resultado (OutputDTO → presenter → serializer de salida). Sin reglas, sin
# transaction.atomic, sin auditoría, sin eventos y sin try/except: los errores del dominio los traduce core.
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.infrastructure.api.views import consultas
from core.infrastructure.api.views.roles import roles_de
from finanzas.application.crear_categoria_use_case.crear_categoria_use_case import CrearCategoriaUseCase
from finanzas.application.crear_categoria_use_case.dtos.crear_categoria_input_dto import CrearCategoriaInputDTO
from finanzas.application.eliminar_categoria_use_case.dtos.eliminar_categoria_input_dto import (
    EliminarCategoriaInputDTO,
)
from finanzas.application.eliminar_categoria_use_case.eliminar_categoria_use_case import EliminarCategoriaUseCase
from finanzas.application.listar_categorias_use_case.dtos.listar_categorias_input_dto import ListarCategoriasInputDTO
from finanzas.application.modificar_categoria_use_case.dtos.modificar_categoria_input_dto import (
    ModificarCategoriaInputDTO,
)
from finanzas.application.modificar_categoria_use_case.modificar_categoria_use_case import ModificarCategoriaUseCase
from finanzas.application.obtener_categoria_use_case.dtos.obtener_categoria_input_dto import ObtenerCategoriaInputDTO
from finanzas.application.reordenar_categorias_use_case.dtos.reordenar_categorias_input_dto import (
    ReordenarCategoriasInputDTO,
)
from finanzas.infrastructure import container
from finanzas.infrastructure.api.v1.presenters.categoria_presenter import presentar
from finanzas.infrastructure.api.v1.serializers.categoria_serializer import CategoriaSerializer
from finanzas.infrastructure.api.v1.serializers.reordenar_serializer import ReordenarSerializer
from finanzas.infrastructure.database.models.categoria_model import Categoria as CategoriaModel
from hogares.infrastructure.api.base.del_hogar_viewset import DelHogarViewSet


class CategoriaViewSet(DelHogarViewSet):
    modelo = CategoriaModel
    serializer_class = CategoriaSerializer
    pagination_class = None
    roles_por_accion = roles_de(CrearCategoriaUseCase, ModificarCategoriaUseCase, EliminarCategoriaUseCase)

    def _leer(self, categoria_id: int):
        leida = container.obtener_categoria().ejecutar(
            ObtenerCategoriaInputDTO(self.hogar.pk, self.actor, categoria_id)
        )
        if leida is None:
            raise consultas.no_encontrado(CategoriaModel)
        return presentar(leida)

    def list(self, request, *args, **kwargs):
        entrada = ListarCategoriasInputDTO(self.hogar.pk, self.actor, consultas.orden(self, request, CategoriaModel))
        categorias = container.listar_categorias().ejecutar(entrada)
        return Response(self.get_serializer([presentar(c) for c in categorias], many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(self._leer(consultas.id_de_la_url(self))).data)

    def perform_create(self, serializer):
        entrada = CrearCategoriaInputDTO(hogar_id=self.hogar.pk, actor=self.actor, **serializer.a_dominio())
        categoria = container.crear_categoria().ejecutar(entrada)
        serializer.instance = self._leer(categoria.id)

    def perform_update(self, serializer):
        entrada = ModificarCategoriaInputDTO(self.hogar.pk, self.actor, serializer.instance.pk, serializer.a_dominio())
        container.modificar_categoria().ejecutar(entrada)
        serializer.instance = self._leer(serializer.instance.pk)

    def perform_destroy(self, instance):
        container.eliminar_categoria().ejecutar(EliminarCategoriaInputDTO(self.hogar.pk, self.actor, instance.pk))

    @extend_schema(request=ReordenarSerializer, responses={204: None})
    @action(detail=False, methods=["post"])
    def reordenar(self, request, *args, **kwargs):
        datos = ReordenarSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        entrada = ReordenarCategoriasInputDTO(self.hogar.pk, self.actor, tuple(datos.validated_data["ids"]))
        container.reordenar_categorias().ejecutar(entrada)
        return Response(status=status.HTTP_204_NO_CONTENT)
