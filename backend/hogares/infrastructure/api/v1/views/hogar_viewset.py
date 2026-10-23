# hogares/infrastructure/api/v1/views/hogar_viewset.py — adapter de entrada HTTP (módulos 36, 71, 88, 90 y 92)
#
# Escribir: serializer → InputDTO → use case de comando. Leer (el listado, el detalle y la response de un POST o un
# PATCH): use case de consulta → OutputDTO → presenter → el mismo serializer. Sigue siendo un ModelViewSet: rutas,
# esquema OpenAPI y permisos de DRF intactos.
from rest_framework import viewsets
from rest_framework.response import Response

from core.domain.vo.actor import Actor
from core.infrastructure.api.views import consultas
from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.application.eliminar_hogar_use_case.dtos.eliminar_hogar_input_dto import EliminarHogarInputDTO
from hogares.application.listar_hogares_use_case.dtos.listar_hogares_input_dto import ListarHogaresInputDTO
from hogares.application.modificar_hogar_use_case.dtos.modificar_hogar_input_dto import ModificarHogarInputDTO
from hogares.application.obtener_hogar_use_case.dtos.obtener_hogar_input_dto import ObtenerHogarInputDTO
from hogares.infrastructure import container
from hogares.infrastructure.api.base.actor_de import actor_de
from hogares.infrastructure.api.v1.presenters.hogar_presenter import presentar
from hogares.infrastructure.api.v1.serializers.hogar_serializer import HogarSerializer
from hogares.infrastructure.database.models.hogar_model import Hogar as HogarModel
from hogares.infrastructure.database.models.membresia_model import Membresia as MembresiaModel
from oauth.domain.enums.scope import Scope
from oauth.infrastructure.api.views.acepta_oauth import AceptaOAuth
from usuarios.infrastructure.api.permissions.autenticacion_reciente import AutenticacionReciente


class HogarViewSet(AceptaOAuth, viewsets.ModelViewSet):
    """Mis hogares. Crear lo puede cualquiera; editar y borrar, solo administradores."""

    serializer_class = HogarSerializer
    scopes_por_accion = {"list": Scope.GASTOS_LEER, "retrieve": Scope.GASTOS_LEER}  # módulo 90

    def get_queryset(self):
        return HogarModel.objects.none()  # solo para el esquema OpenAPI y los filtros: se lee con use cases

    def _leer(self, hogar_id: int):
        leido = container.obtener_hogar().ejecutar(ObtenerHogarInputDTO(self.request.user.pk, hogar_id))
        if leido is None:
            raise consultas.no_encontrado(HogarModel)  # no es uno de sus hogares: el mismo 404 que get_object()
        return presentar(leido)

    def get_object(self):
        hogar = self._leer(consultas.id_de_la_url(self))
        self.check_object_permissions(self.request, hogar)
        return hogar

    def _actor(self, hogar) -> Actor:
        return actor_de(self.request, hogar.mi_rol)  # su rol, leído con el hogar

    def list(self, request, *args, **kwargs):
        entrada = ListarHogaresInputDTO(
            request.user.pk, consultas.orden(self, request, HogarModel), self.paginator.paginacion(request)
        )
        pagina = container.listar_hogares().ejecutar(entrada)
        datos = self.get_serializer([presentar(h) for h in pagina.results], many=True).data
        return self.paginator.respuesta(request, pagina, datos)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.get_object()).data)

    def perform_create(self, serializer):
        entrada = CrearHogarInputDTO(usuario_id=self.request.user.pk, **serializer.validated_data)
        hogar = container.crear_hogar().ejecutar(entrada)
        serializer.instance = self._leer(hogar.id)  # con mi_rol y num_miembros

    def perform_update(self, serializer):
        entrada = ModificarHogarInputDTO(
            serializer.instance.pk, self._actor(serializer.instance), serializer.validated_data
        )
        container.modificar_hogar().ejecutar(entrada)
        serializer.instance = self._leer(serializer.instance.pk)

    def perform_destroy(self, instance):
        container.eliminar_hogar().ejecutar(EliminarHogarInputDTO(instance.pk, self._actor(instance)))

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method not in ("GET", "HEAD", "OPTIONS") and obj.mi_rol != MembresiaModel.Rol.ADMIN:
            self.permission_denied(request, message="Solo los administradores pueden modificar el hogar.")
        if self.action == "destroy":  # módulo 92: borrar un hogar es irreversible: step-up (y después del rol)
            AutenticacionReciente().has_permission(request, self)
