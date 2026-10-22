# hogares/infrastructure/database/repositories/hogar_command_repository_orm.py — IHogarCommandRepository con el ORM (módulo 88)
from core.infrastructure.database.guardado import guardar_fila
from hogares.domain.bo.hogar import Hogar
from hogares.domain.exceptions.hogar_no_encontrado_exception import HogarNoEncontradoException
from hogares.domain.repositories.i_hogar_command_repository import IHogarCommandRepository
from hogares.infrastructure.database.mappers.hogar_mapper import hogar_a_bo, hogar_a_modelo
from hogares.infrastructure.database.models.hogar_model import Hogar as HogarModel

CAMPOS = ["nombre", "moneda", "zona_horaria"]


class HogarCommandRepositoryORM(IHogarCommandRepository):
    def obtener(self, hogar_id: int) -> Hogar:
        fila = HogarModel.objects.filter(pk=hogar_id).first()
        if fila is None:
            raise HogarNoEncontradoException()
        return hogar_a_bo(fila)

    def guardar(self, hogar: Hogar) -> None:
        fila = hogar_a_modelo(hogar)
        guardar_fila(fila, CAMPOS, {})
        hogar.id = fila.pk

    def eliminar(self, hogar: Hogar) -> None:
        # delete() de una instancia: Django borra en cascada todo lo del hogar (y emite post_delete con origin=hogar)
        HogarModel(pk=hogar.id).delete()
