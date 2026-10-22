"""IMembresiaCommandRepository en memoria (módulo 89)."""

from estadisticas.domain.bo.membresia import Membresia
from estadisticas.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository
from tests.fakes.memoria import Memoria


class MembresiaCommandRepositoryFake(IMembresiaCommandRepository):
    def __init__(self, memoria: Memoria):
        self.memoria = memoria

    def guardar(self, membresia: Membresia) -> bool:
        clave = (membresia.hogar_id, membresia.usuario_id)
        actual = self.memoria.membresias.get(clave)
        if actual is not None and actual.version >= membresia.version:
            return False
        self.memoria.membresias[clave] = membresia
        return True

    def eliminar(self, hogar_id: int, usuario_id: int, version: int) -> bool:
        actual = self.memoria.membresias.get((hogar_id, usuario_id))
        if actual is None or actual.version >= version:
            return False
        del self.memoria.membresias[(hogar_id, usuario_id)]
        return True

    def vaciar(self) -> None:
        self.memoria.membresias.clear()
