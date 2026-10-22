# finanzas/tests/fakes/movimiento_command_repository_fake.py — IMovimientoCommandRepository en memoria (módulo 87)
from finanzas.domain.exceptions.movimiento_no_encontrado_exception import MovimientoNoEncontradoException
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository
from finanzas.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia


class MovimientoCommandRepositoryFake(AlmacenEnMemoria, IMovimientoCommandRepository):
    def obtener(self, hogar_id, movimiento_id):
        m = self._datos.get(movimiento_id)
        if m is None or m.hogar_id != hogar_id:
            raise MovimientoNoEncontradoException()
        return copia(m)

    def obtener_varios(self, hogar_id, ids):
        return [
            copia(self._datos[i]) for i in sorted(set(ids)) if i in self._datos and self._datos[i].hogar_id == hogar_id
        ]

    def guardar(self, movimiento):
        self._asignar_id(movimiento)
        self._datos[movimiento.id] = copia(movimiento)

    def eliminar(self, movimiento):
        self._datos.pop(movimiento.id, None)

    def actualizar_en_bloque(self, hogar_id, ids, cambios):
        afectados = sorted(i for i in set(ids) if i in self._datos and self._datos[i].hogar_id == hogar_id)
        for i in afectados:
            for campo, valor in cambios.items():
                setattr(self._datos[i], campo, valor)
        return afectados, {self._datos[i].mes for i in afectados}
