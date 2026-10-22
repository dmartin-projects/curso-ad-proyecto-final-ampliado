# finanzas/tests/fakes/unidad_de_trabajo_fake.py — IUnidadDeTrabajo en memoria que deshace de verdad (módulo 87)
import copy

from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo


class UnidadDeTrabajoFake(IUnidadDeTrabajo):
    """Una transacción de verdad para los fakes: si el bloque falla, todo vuelve a como estaba."""

    def __init__(self, *participantes):
        self._participantes = participantes
        self._copias: list = []
        self.confirmadas = self.deshechas = 0

    def __enter__(self):
        # memo: los participantes que se apuntan entre sí (presupuestos → movimientos) siguen apuntándose al
        # MISMO objeto tras deshacer, no a una copia
        memo = {id(p): p for p in self._participantes}
        self._copias.append([copy.deepcopy(p.__dict__, memo.copy()) for p in self._participantes])

    def __exit__(self, tipo, *_):
        copias = self._copias.pop()
        if tipo is None:
            self.confirmadas += 1
            return None
        self.deshechas += 1
        for participante, copia in zip(self._participantes, copias, strict=True):
            participante.__dict__.update(copia)
        return None  # la excepción sigue su camino
