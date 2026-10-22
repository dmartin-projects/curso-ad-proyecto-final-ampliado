# hogares/tests/fakes/hogar_command_repository_fake.py — IHogarCommandRepository en memoria (módulo 88)
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia
from hogares.domain.exceptions.hogar_no_encontrado_exception import HogarNoEncontradoException
from hogares.domain.repositories.i_hogar_command_repository import IHogarCommandRepository


class HogarCommandRepositoryFake(AlmacenEnMemoria, IHogarCommandRepository):
    def obtener(self, hogar_id):
        if hogar_id not in self._datos:
            raise HogarNoEncontradoException()
        return copia(self._datos[hogar_id])

    def guardar(self, hogar):
        self._asignar_id(hogar)
        self._datos[hogar.id] = copia(hogar)

    def eliminar(self, hogar):
        self._datos.pop(hogar.id, None)
