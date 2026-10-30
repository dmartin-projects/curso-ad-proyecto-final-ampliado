# asistente/infrastructure/tasks/analizar_mes_task.py — adapter de entrada de Celery (módulo 105)
import logging

from celery import shared_task

from asistente.application.analizar_mes_use_case.dtos.analizar_mes_input_dto import AnalizarMesInputDTO
from asistente.infrastructure import container
from asistente.infrastructure.messaging.programador_de_analisis_celery import ANALIZAR

logger = logging.getLogger(__name__)


# Sin reintentos automáticos: un análisis gasta cuota en cada intento, y si falla la persona lo ve y decide.
# time_limit: un análisis atascado no ocupa un worker para siempre (soft: avisa; hard: lo mata)
@shared_task(name=ANALIZAR, ignore_result=True, soft_time_limit=240, time_limit=300)
def analizar_mes(usuario_id: int, hogar_id: int, mes: str, tarea: str) -> None:
    try:
        container.analizar_mes().ejecutar(AnalizarMesInputDTO(usuario_id, hogar_id, mes, tarea))
    except Exception:
        logger.exception("Análisis %s fallido", tarea)
        container.avisos_de_progreso().avisar(
            usuario_id, hogar_id, tarea, {"estado": "fallido", "paso": "Algo ha fallado al preparar el análisis."}
        )
        raise
