# informes/infrastructure/tasks/generar_informes_mensuales_task.py — la coordinadora de Celery Beat (módulos 26, 78 y 88)
import logging

from celery import shared_task
from django.utils import timezone

from core.domain.vo.mes import Mes
from informes.application.listar_hogares_sin_informe_use_case.dtos.listar_hogares_sin_informe_input_dto import (
    ListarHogaresSinInformeInputDTO,
)
from informes.infrastructure import container
from informes.infrastructure.tasks.generar_informe_task import generar_informe

logger = logging.getLogger(__name__)


# name= explícito: el nombre de siempre, el que usa CELERY_BEAT_SCHEDULE (y la tabla de django-celery-beat)
@shared_task(name="informes.tasks.generar_informes_mensuales", ignore_result=True)
def generar_informes_mensuales() -> int:
    """Coordinadora (Celery Beat, día 1 a las 7:00): encola UNA tarea por hogar, no un bucle de horas (módulo 26)."""
    mes = Mes.de(timezone.localdate()).anterior()  # TIME_ZONE del proyecto (Madrid)
    pendientes = container.listar_hogares_sin_informe().ejecutar(ListarHogaresSinInformeInputDTO(mes))
    for hogar_id in pendientes:
        generar_informe.delay(hogar_id, mes.inicio.isoformat())
    logger.info("Informes de %s encolados: %s", mes, len(pendientes))
    return len(pendientes)
