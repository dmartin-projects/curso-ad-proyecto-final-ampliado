# finanzas/infrastructure/api/v1/views/presupuesto_viewset.py — adapter de entrada HTTP (módulos 33-38, 76, 87 y 88)
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.domain.vo.mes import Mes
from core.infrastructure.api.views import consultas
from core.infrastructure.api.views.roles import roles_de
from finanzas.application.crear_presupuesto_use_case.crear_presupuesto_use_case import CrearPresupuestoUseCase
from finanzas.application.crear_presupuesto_use_case.dtos.crear_presupuesto_input_dto import CrearPresupuestoInputDTO
from finanzas.application.eliminar_presupuesto_use_case.dtos.eliminar_presupuesto_input_dto import (
    EliminarPresupuestoInputDTO,
)
from finanzas.application.eliminar_presupuesto_use_case.eliminar_presupuesto_use_case import (
    EliminarPresupuestoUseCase,
)
from finanzas.application.listar_presupuestos_use_case.dtos.listar_presupuestos_input_dto import (
    ListarPresupuestosInputDTO,
)
from finanzas.application.modificar_presupuesto_use_case.dtos.modificar_presupuesto_input_dto import (
    ModificarPresupuestoInputDTO,
)
from finanzas.application.modificar_presupuesto_use_case.modificar_presupuesto_use_case import (
    ModificarPresupuestoUseCase,
)
from finanzas.application.obtener_presupuesto_use_case.dtos.obtener_presupuesto_input_dto import (
    ObtenerPresupuestoInputDTO,
)
from finanzas.infrastructure import container
from finanzas.infrastructure.api.v1.presenters.presupuesto_presenter import presentar
from finanzas.infrastructure.api.v1.serializers.presupuesto_serializer import PresupuestoSerializer
from finanzas.infrastructure.database.models.presupuesto_model import Presupuesto as PresupuestoModel
from hogares.infrastructure.api.base.del_hogar_viewset import DelHogarViewSet
from hogares.models import Membresia


class PresupuestoViewSet(DelHogarViewSet):
    modelo = PresupuestoModel
    serializer_class = PresupuestoSerializer
    pagination_class = None
    roles_por_metodo = {"GET": Membresia.Rol.LECTOR}  # lo demás, el de los use cases:
    roles_por_accion = roles_de(CrearPresupuestoUseCase, ModificarPresupuestoUseCase, EliminarPresupuestoUseCase)

    def _leer(self, presupuesto_id: int):
        entrada = ObtenerPresupuestoInputDTO(self.hogar.pk, self.actor, presupuesto_id)
        leido = container.obtener_presupuesto().ejecutar(entrada)
        if leido is None:
            raise consultas.no_encontrado(PresupuestoModel)
        return presentar(leido)  # con `gastado`, como en el listado

    @extend_schema(parameters=[OpenApiParameter("mes", str, description="Mes en formato AAAA-MM")])
    def list(self, request, *args, **kwargs):
        texto = request.query_params.get("mes")
        try:
            mes = Mes.desde_texto(texto) if texto else None
        except ValueError:
            raise ValidationError({"mes": ["Mes en formato AAAA-MM."]}) from None
        orden = consultas.orden(self, request, PresupuestoModel)
        presupuestos = container.listar_presupuestos().ejecutar(
            ListarPresupuestosInputDTO(self.hogar.pk, self.actor, mes, orden)
        )
        return Response(self.get_serializer([presentar(p) for p in presupuestos], many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(self._leer(consultas.id_de_la_url(self))).data)

    def perform_create(self, serializer):
        entrada = CrearPresupuestoInputDTO(hogar_id=self.hogar.pk, actor=self.actor, **serializer.a_dominio())
        presupuesto = container.crear_presupuesto().ejecutar(entrada)
        serializer.instance = self._leer(presupuesto.id)

    def perform_update(self, serializer):
        entrada = ModificarPresupuestoInputDTO(
            self.hogar.pk, self.actor, serializer.instance.pk, serializer.a_dominio()
        )
        container.modificar_presupuesto().ejecutar(entrada)
        serializer.instance = self._leer(serializer.instance.pk)

    def perform_destroy(self, instance):
        container.eliminar_presupuesto().ejecutar(EliminarPresupuestoInputDTO(self.hogar.pk, self.actor, instance.pk))
