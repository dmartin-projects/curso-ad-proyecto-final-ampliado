# backoffice/infrastructure/api/v1/views/tarea_programada_viewset.py — adapter de entrada HTTP del personal de soporte (módulos 79 y 88)
#
# Pausar o reanudar una tarea es CRUD (PeriodicTask.save avisa a Beat), con su registro de auditoría.
from django.db import transaction
from django.forms.models import model_to_dict
from django_celery_beat.models import PeriodicTask
from rest_framework import mixins, viewsets
from rest_framework.response import Response

from backoffice.application.listar_tareas_programadas_use_case.dtos.listar_tareas_programadas_input_dto import (
    ListarTareasProgramadasInputDTO,
)
from backoffice.application.obtener_tarea_programada_use_case.dtos.obtener_tarea_programada_input_dto import (
    ObtenerTareaProgramadaInputDTO,
)
from backoffice.infrastructure import container
from backoffice.infrastructure.api.permissions.personal import PERSONAL
from backoffice.infrastructure.api.v1.presenters import soporte_presenters as presentar
from backoffice.infrastructure.api.v1.serializers.tarea_programada_serializer import TareaProgramadaSerializer
from core.infrastructure.api.views import consultas
from core.infrastructure.database.auditoria_de_modelos import registrar
from core.models import RegistroAuditoria as RegistroAuditoriaModel


class TareaProgramadaViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    """Las tareas de Celery Beat (DatabaseScheduler): verlas y pausarlas/reanudarlas."""

    serializer_class = TareaProgramadaSerializer
    permission_classes = PERSONAL
    permisos_por_accion = {
        "list": ["django_celery_beat.view_periodictask"],
        "retrieve": ["django_celery_beat.view_periodictask"],
        "partial_update": ["django_celery_beat.change_periodictask"],
    }
    http_method_names = ["get", "patch", "head", "options"]
    queryset = PeriodicTask.objects.select_related("crontab").order_by("name")  # partial_update (CRUD)
    pagination_class = None

    def list(self, request, *args, **kwargs):
        tareas = container.listar_tareas_programadas().ejecutar(ListarTareasProgramadasInputDTO())
        return Response(self.get_serializer([presentar.tarea(t) for t in tareas], many=True).data)

    def retrieve(self, request, *args, **kwargs):
        leida = container.obtener_tarea_programada().ejecutar(
            ObtenerTareaProgramadaInputDTO(consultas.id_de_la_url(self))
        )
        if leida is None:
            raise consultas.no_encontrado(PeriodicTask)
        return Response(self.get_serializer(presentar.tarea(leida)).data)

    @transaction.atomic
    def perform_update(self, serializer):
        antes = model_to_dict(serializer.instance, fields=["enabled"])
        tarea = serializer.save()  # PeriodicTask.save avisa a Beat de que la programación cambió
        registrar(tarea, RegistroAuditoriaModel.Accion.MODIFICAR, self.request.user, antes=antes)
