# backoffice/infrastructure/database/repositories/tarea_programada_soporte_query_service_orm.py — ITareaProgramadaSoporteQueryService con el ORM (módulo 88)
from django_celery_beat.models import PeriodicTask

from backoffice.domain.read_models.tarea_programada_soporte import TareaProgramadaSoporte
from backoffice.domain.repositories.i_tarea_programada_soporte_query_service import (
    ITareaProgramadaSoporteQueryService,
)


def _a_read_model(t: PeriodicTask) -> TareaProgramadaSoporte:
    horario = None if t.crontab is None else str(t.crontab)
    return TareaProgramadaSoporte(t.pk, t.name, t.task, horario, t.enabled, t.last_run_at, t.total_run_count)


class TareaProgramadaSoporteQueryServiceORM(ITareaProgramadaSoporteQueryService):
    @staticmethod
    def _todas():
        return PeriodicTask.objects.select_related("crontab").order_by("name")

    def listar(self):
        return [_a_read_model(t) for t in self._todas()]

    def detalle(self, tarea_id):
        fila = self._todas().filter(pk=tarea_id).first()
        return None if fila is None else _a_read_model(fila)
