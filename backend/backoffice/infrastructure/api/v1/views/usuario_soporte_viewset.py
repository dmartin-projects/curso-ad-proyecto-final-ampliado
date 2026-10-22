# backoffice/infrastructure/api/v1/views/usuario_soporte_viewset.py — adapter de entrada HTTP del personal de soporte (módulos 79 y 88)
#
# Activar o desactivar una cuenta es CRUD (sin reglas de negocio ni efectos), con su registro de auditoría.
from django.contrib.auth import get_user_model
from django.db import transaction
from django.forms.models import model_to_dict
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from backoffice.application.listar_usuarios_soporte_use_case.dtos.listar_usuarios_soporte_input_dto import (
    ListarUsuariosSoporteInputDTO,
)
from backoffice.application.obtener_usuario_soporte_use_case.dtos.obtener_usuario_soporte_input_dto import (
    ObtenerUsuarioSoporteInputDTO,
)
from backoffice.infrastructure import container
from backoffice.infrastructure.api.permissions.personal import PERSONAL
from backoffice.infrastructure.api.v1.presenters import soporte_presenters as presentar
from backoffice.infrastructure.api.v1.serializers.usuario_soporte_serializer import UsuarioSoporteSerializer
from backoffice.infrastructure.api.v1.views.listado_soporte_mixin import ListadoSoporteMixin
from core.infrastructure.api.views import consultas
from core.infrastructure.database.auditoria_de_modelos import registrar
from core.models import RegistroAuditoria as RegistroAuditoriaModel


class UsuarioSoporteViewSet(ListadoSoporteMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    """Ver usuarios; activar o desactivar (solo quien tenga usuarios.change_usuario, no el grupo Soporte)."""

    serializer_class = UsuarioSoporteSerializer
    permission_classes = PERSONAL
    permisos_por_accion = {
        "list": ["usuarios.view_usuario"],
        "retrieve": ["usuarios.view_usuario"],
        "partial_update": ["usuarios.change_usuario"],
    }
    http_method_names = ["get", "patch", "head", "options"]
    modelo = get_user_model()
    filterset_fields = ["is_active", "is_staff"]
    search_fields = ["email", "nombre", "apellidos"]

    def get_queryset(self):
        # partial_update (CRUD) trabaja con el modelo; leer, con los use cases de consulta
        return get_user_model().objects.order_by("-fecha_alta")

    def list(self, request, *args, **kwargs):
        entrada = ListarUsuariosSoporteInputDTO(self._query(request))
        return self._pagina(request, container.listar_usuarios_soporte().ejecutar(entrada), presentar.usuario)

    def retrieve(self, request, *args, **kwargs):
        entrada = ObtenerUsuarioSoporteInputDTO(consultas.id_de_la_url(self))
        leido = self._o_404(container.obtener_usuario_soporte().ejecutar(entrada))
        return Response(self.get_serializer(presentar.usuario(leido)).data)

    @transaction.atomic  # el cambio y su registro de auditoría, o los dos o ninguno (como en el módulo 73)
    def perform_update(self, serializer):
        if serializer.instance == self.request.user:
            raise ValidationError({"is_active": ["No puedes desactivar tu propia cuenta."]})
        antes = model_to_dict(serializer.instance, fields=["is_active"])
        usuario = serializer.save()
        # un usuario desactivado deja de poder usar su access token en la siguiente petición:
        # JWTAuthentication rechaza a los usuarios inactivos (módulo 35)
        registrar(usuario, RegistroAuditoriaModel.Accion.MODIFICAR, self.request.user, antes=antes)
