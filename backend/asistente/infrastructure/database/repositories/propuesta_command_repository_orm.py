# asistente/infrastructure/database/repositories/propuesta_command_repository_orm.py (módulo 97)
from asistente.domain.exceptions.propuesta_no_encontrada_exception import PropuestaNoEncontradaException
from asistente.domain.repositories.i_propuesta_command_repository import IPropuestaCommandRepository
from asistente.infrastructure.database.mappers.propuesta_mapper import propuesta_a_bo
from asistente.infrastructure.database.models.propuesta_model import Propuesta as PropuestaModel
from core.infrastructure.database.guardado import guardar_fila


class PropuestaCommandRepositoryORM(IPropuestaCommandRepository):
    def obtener(self, usuario_id, hogar_id, propuesta_id, bloquear=False):
        filas = PropuestaModel.objects.filter(pk=propuesta_id, usuario_id=usuario_id, hogar_id=hogar_id)
        fila = (filas.select_for_update() if bloquear else filas).first()
        if fila is None:
            raise PropuestaNoEncontradaException()
        return propuesta_a_bo(fila)

    def guardar(self, propuesta):
        fila = PropuestaModel(
            pk=propuesta.id,
            conversacion_id=propuesta.conversacion_id,
            usuario_id=propuesta.usuario_id,
            hogar_id=propuesta.hogar_id,
            tipo=str(propuesta.tipo),
            resumen=propuesta.resumen,
            datos=propuesta.datos,
            estado=str(propuesta.estado),
            resultado=propuesta.resultado,
        )
        guardar_fila(fila, ["estado", "resultado"], {})
        propuesta.id = fila.pk
