# notificaciones/infrastructure/tasks/emitir_evento_hogar_task.py — el aviso agrupado a un hogar (Celery) (módulos 26, 76 y 88)
from celery import shared_task

from notificaciones.infrastructure.realtime.tiempo_real import emitir_a_hogar


@shared_task(name="notificaciones.tasks.emitir_evento_hogar", ignore_result=True)  # name=: el de siempre (módulo 87)
def emitir_evento_hogar(hogar_id: int, evento: str) -> None:
    """Se encola con `agrupar` (debounce): un aviso por ventana, aunque cambien 500 movimientos."""
    emitir_a_hogar(hogar_id, evento)
