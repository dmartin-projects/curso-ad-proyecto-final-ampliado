# hogares/infrastructure/api/v1/views/miembros_viewset.py — adapter de entrada HTTP (módulos 36, 71, 88 y 90)
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.infrastructure.api.views import consultas
from hogares.application.cambiar_rol_use_case.dtos.cambiar_rol_input_dto import CambiarRolInputDTO
from hogares.application.expulsar_miembro_use_case.dtos.expulsar_miembro_input_dto import ExpulsarMiembroInputDTO
from hogares.application.invitar_use_case.dtos.invitar_input_dto import InvitarInputDTO
from hogares.application.listar_miembros_use_case.dtos.listar_miembros_input_dto import ListarMiembrosInputDTO
from hogares.application.obtener_invitacion_use_case.dtos.obtener_invitacion_input_dto import (
    ObtenerInvitacionInputDTO,
)
from hogares.application.obtener_miembro_use_case.dtos.obtener_miembro_input_dto import ObtenerMiembroInputDTO
from hogares.application.salir_del_hogar_use_case.dtos.salir_del_hogar_input_dto import SalirDelHogarInputDTO
from hogares.application.salir_del_hogar_use_case.salir_del_hogar_use_case import SalirDelHogarUseCase
from hogares.infrastructure import container
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar
from hogares.infrastructure.api.v1.presenters import invitacion_presenter
from hogares.infrastructure.api.v1.presenters.miembro_presenter import presentar
from hogares.infrastructure.api.v1.serializers.invitacion_serializer import InvitacionSerializer
from hogares.infrastructure.api.v1.serializers.invitar_serializer import InvitarSerializer
from hogares.infrastructure.api.v1.serializers.miembro_serializer import MiembroSerializer
from hogares.infrastructure.database.models.membresia_model import Membresia as MembresiaModel


class MiembrosViewSet(
    HogarDesdeUrlMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """/hogares/{h}/miembros/: ver (todos), cambiar rol y expulsar (admin), salir (cualquiera)."""

    serializer_class = MiembroSerializer
    permission_classes = [IsAuthenticated, RolEnHogar]
    roles_por_metodo = {
        "GET": MembresiaModel.Rol.LECTOR,
        "PATCH": MembresiaModel.Rol.ADMIN,
        "PUT": MembresiaModel.Rol.ADMIN,
        "DELETE": MembresiaModel.Rol.ADMIN,
        "POST": MembresiaModel.Rol.ADMIN,
    }
    roles_por_accion = {"salir": SalirDelHogarUseCase.rol_minimo}  # el del use case: 403 antes de nada
    pagination_class = None

    def get_queryset(self):
        return MembresiaModel.objects.none()  # solo para el esquema OpenAPI y los filtros: se lee con use cases

    def _leer(self, membresia_id: int):
        leido = container.obtener_miembro().ejecutar(ObtenerMiembroInputDTO(self.hogar.pk, self.actor, membresia_id))
        if leido is None:
            raise consultas.no_encontrado(MembresiaModel)
        return presentar(leido)

    def get_object(self):
        return self._leer(consultas.id_de_la_url(self))

    def list(self, request, *args, **kwargs):
        entrada = ListarMiembrosInputDTO(self.hogar.pk, self.actor, consultas.orden(self, request, MembresiaModel))
        miembros = container.listar_miembros().ejecutar(entrada)
        return Response(self.get_serializer([presentar(m) for m in miembros], many=True).data)

    def perform_update(self, serializer):
        entrada = CambiarRolInputDTO(
            self.hogar.pk, self.actor, serializer.instance.pk, serializer.validated_data["rol"]
        )
        container.cambiar_rol().ejecutar(entrada)
        serializer.instance = self._leer(serializer.instance.pk)

    def perform_destroy(self, instance):
        container.expulsar_miembro().ejecutar(ExpulsarMiembroInputDTO(self.hogar.pk, self.actor, instance.pk))

    @extend_schema(request=InvitarSerializer, responses={201: InvitacionSerializer})
    @action(detail=False, methods=["post"])
    def invitar(self, request, *args, **kwargs):
        datos = InvitarSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        invitacion = container.invitar().ejecutar(InvitarInputDTO(self.hogar.pk, self.actor, **datos.validated_data))
        leida = container.obtener_invitacion().ejecutar(
            ObtenerInvitacionInputDTO(self.hogar.pk, self.actor, invitacion.id)
        )
        respuesta = InvitacionSerializer(invitacion_presenter.presentar(leida)).data
        return Response(respuesta, status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses={204: None})
    @action(detail=False, methods=["post"])
    def salir(self, request, *args, **kwargs):
        container.salir_del_hogar().ejecutar(SalirDelHogarInputDTO(self.hogar.pk, self.actor))
        return Response(status=status.HTTP_204_NO_CONTENT)
