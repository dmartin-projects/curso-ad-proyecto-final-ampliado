# asistente/infrastructure/database/repositories/carpeta_command_repository_orm.py (módulo 97)
from asistente.domain.exceptions.carpeta_no_encontrada_exception import CarpetaNoEncontradaException
from asistente.domain.exceptions.carpeta_repetida_exception import CarpetaRepetidaException
from asistente.domain.repositories.i_carpeta_command_repository import ICarpetaCommandRepository
from asistente.infrastructure.database.mappers.conversacion_mapper import carpeta_a_bo
from asistente.infrastructure.database.models.carpeta_model import Carpeta as CarpetaModel
from core.infrastructure.database.guardado import guardar_fila


class CarpetaCommandRepositoryORM(ICarpetaCommandRepository):
    def obtener(self, usuario_id, hogar_id, carpeta_id):
        fila = CarpetaModel.objects.filter(pk=carpeta_id, usuario_id=usuario_id, hogar_id=hogar_id).first()
        if fila is None:
            raise CarpetaNoEncontradaException()
        return carpeta_a_bo(fila)

    def guardar(self, carpeta):
        fila = CarpetaModel(
            pk=carpeta.id, usuario_id=carpeta.usuario_id, hogar_id=carpeta.hogar_id, nombre=carpeta.nombre
        )
        guardar_fila(fila, ["nombre"], {"asistente_carpeta_unica": CarpetaRepetidaException})
        carpeta.id = fila.pk

    def eliminar(self, carpeta):
        CarpetaModel.objects.filter(pk=carpeta.id).delete()  # sus conversaciones: SET NULL, fuera de toda carpeta
