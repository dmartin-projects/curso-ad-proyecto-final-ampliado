# asistente/infrastructure/database/repositories/recuerdo_query_service_orm.py (módulo 99)
from asistente.domain.read_models.recuerdo_listado import RecuerdoListado
from asistente.domain.repositories.i_recuerdo_query_service import IRecuerdoQueryService
from asistente.infrastructure.database.models.recuerdo_model import Recuerdo as RecuerdoModel


class RecuerdoQueryServiceORM(IRecuerdoQueryService):
    def listar(self, usuario_id, hogar_id):
        filas = RecuerdoModel.objects.filter(usuario_id=usuario_id, hogar_id=hogar_id).order_by("creado", "id")
        return tuple(RecuerdoListado(f.pk, f.texto, f.creado) for f in filas)
