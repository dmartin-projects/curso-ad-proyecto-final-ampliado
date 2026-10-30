# asistente/infrastructure/database/repositories/recuerdo_command_repository_orm.py (módulo 99)
from asistente.domain.bo.recuerdo import Recuerdo
from asistente.domain.exceptions.recuerdo_no_encontrado_exception import RecuerdoNoEncontradoException
from asistente.domain.repositories.i_recuerdo_command_repository import IRecuerdoCommandRepository
from asistente.infrastructure.database.models.recuerdo_model import Recuerdo as RecuerdoModel


class RecuerdoCommandRepositoryORM(IRecuerdoCommandRepository):
    def obtener(self, usuario_id, hogar_id, recuerdo_id):
        f = RecuerdoModel.objects.filter(pk=recuerdo_id, usuario_id=usuario_id, hogar_id=hogar_id).first()
        if f is None:
            raise RecuerdoNoEncontradoException()
        return Recuerdo(f.usuario_id, f.hogar_id, f.texto, f.creado, id=f.pk)

    def guardar(self, recuerdo):  # un recuerdo no se edita: se olvida y se pide otro
        fila = RecuerdoModel.objects.create(
            usuario_id=recuerdo.usuario_id, hogar_id=recuerdo.hogar_id, texto=recuerdo.texto, creado=recuerdo.creado
        )
        recuerdo.id = fila.pk

    def eliminar(self, recuerdo):
        RecuerdoModel.objects.filter(pk=recuerdo.id).delete()

    def contar(self, usuario_id, hogar_id):
        return RecuerdoModel.objects.filter(usuario_id=usuario_id, hogar_id=hogar_id).count()
