# finanzas/infrastructure/tasks/comprobar_presupuestos_task.py — adapter de entrada de Celery (módulos 26, 76 y 87)
from celery import shared_task

from core.domain.vo.mes import Mes
from finanzas.application.comprobar_presupuestos_use_case.dtos.comprobar_presupuestos_input_dto import (
    ComprobarPresupuestosInputDTO,
)
from finanzas.infrastructure import container


# name= explícito: el nombre de una tarea sale de su módulo, y este módulo no es <app>/tasks.py. Sin él, los
# mensajes que ya estuvieran en la cola de RabbitMQ al desplegar llegarían a un worker que no conoce
# "finanzas.tasks.comprobar_presupuestos_tarea" (Received unregistered task) y se perderían.
@shared_task(name="finanzas.tasks.comprobar_presupuestos_tarea", acks_late=True, ignore_result=True)
def comprobar_presupuestos_tarea(hogar_id: int, meses: list[str]) -> None:
    entrada = ComprobarPresupuestosInputDTO(hogar_id, tuple(Mes.desde_texto(m) for m in meses))  # "2026-10-01"
    container.comprobar_presupuestos().ejecutar(entrada)
