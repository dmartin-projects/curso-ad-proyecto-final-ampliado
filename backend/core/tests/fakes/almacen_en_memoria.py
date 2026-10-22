# core/tests/fakes/almacen_en_memoria.py — lo que comparten los fakes de los command repositories (módulos 87 y 88)
import copy


def copia(bo):
    """Los fakes guardan y devuelven COPIAS: un test no puede cambiar el "almacén" por accidente."""
    return copy.deepcopy(bo)


class AlmacenEnMemoria:
    def __init__(self):
        self._datos: dict[int, object] = {}
        self._siguiente = 1

    def _asignar_id(self, bo) -> None:
        if bo.id is None:
            bo.id = self._siguiente
            self._siguiente += 1

    def todos(self) -> list:
        return [copia(b) for b in self._datos.values()]
