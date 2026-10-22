# finanzas/tests/fakes/movimiento_command_repository_fake.py — IMovimientoCommandRepository en memoria (módulos 87 y 88)
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia
from finanzas.domain.exceptions.movimiento_no_encontrado_exception import MovimientoNoEncontradoException
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository


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

    # ── En bloque (módulo 88) ──
    def crear_varios(self, movimientos):
        huellas = {(m.cuenta_id, m.huella) for m in self._datos.values() if m.huella}
        for m in movimientos:
            if m.huella and (m.cuenta_id, m.huella) in huellas:
                raise ValueError("huella repetida en la cuenta")  # la UniqueConstraint movimiento_huella_unica
            huellas.add((m.cuenta_id, m.huella))
        for m in movimientos:
            self.guardar(m)

    def eliminar_varios(self, hogar_id, ids):
        for m in self.obtener_varios(hogar_id, ids):
            self._datos.pop(m.id)

    def guardar_huellas(self, movimientos):
        for m in movimientos:
            self._datos[m.id].huella = m.huella
