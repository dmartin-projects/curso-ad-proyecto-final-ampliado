# informes/infrastructure/tasks/generar_informe_task.py — adapter de entrada de Celery (módulos 26, 78 y 88)
from datetime import date

from celery import shared_task

from core.domain.vo.mes import Mes
from informes.application.generar_informe_use_case.dtos.generar_informe_input_dto import GenerarInformeInputDTO
from informes.infrastructure import container
from informes.infrastructure.messaging.publicador_eventos_django import GENERAR


@shared_task(name=GENERAR, acks_late=True, autoretry_for=(OSError,), retry_backoff=60, max_retries=3)
def generar_informe(hogar_id: int, mes: str, usuario_id: int | None = None, enviar: bool = True) -> int:
    entrada = GenerarInformeInputDTO(hogar_id, Mes.de(date.fromisoformat(mes)), usuario_id=usuario_id, enviar=enviar)
    informe = container.generar_informe().ejecutar(entrada)
    return informe.id
