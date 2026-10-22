# finanzas/tests/fakes/presupuesto_command_repository_fake.py — IPresupuestoCommandRepository en memoria (módulo 87)
from core.domain.vo.dinero import Dinero
from finanzas.domain.exceptions.presupuesto_duplicado_exception import PresupuestoDuplicadoException
from finanzas.domain.exceptions.presupuesto_no_encontrado_exception import PresupuestoNoEncontradoException
from finanzas.domain.repositories.i_presupuesto_command_repository import IPresupuestoCommandRepository
from finanzas.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia
from finanzas.tests.fakes.categoria_command_repository_fake import CategoriaCommandRepositoryFake
from finanzas.tests.fakes.movimiento_command_repository_fake import MovimientoCommandRepositoryFake


class PresupuestoCommandRepositoryFake(AlmacenEnMemoria, IPresupuestoCommandRepository):
    def __init__(self, movimientos: MovimientoCommandRepositoryFake, categorias: CategoriaCommandRepositoryFake):
        super().__init__()
        self._movimientos, self._categorias = movimientos, categorias
        self.carrera_perdida = False  # simula que otro proceso cambia la alerta justo antes

    def obtener(self, hogar_id, presupuesto_id):
        p = self._datos.get(presupuesto_id)
        if p is None or p.hogar_id != hogar_id:
            raise PresupuestoNoEncontradoException()
        return copia(p)

    def guardar(self, presupuesto):
        clave = (presupuesto.hogar_id, presupuesto.categoria_id, presupuesto.mes)
        if any((p.hogar_id, p.categoria_id, p.mes) == clave and p.id != presupuesto.id for p in self._datos.values()):
            raise PresupuestoDuplicadoException()
        self._asignar_id(presupuesto)
        self._datos[presupuesto.id] = copia(presupuesto)

    def eliminar(self, presupuesto):
        self._datos.pop(presupuesto.id, None)

    def con_gastado(self, hogar_id, meses):
        meses = set(meses)
        resultado = []
        for p in self._datos.values():
            if p.hogar_id != hogar_id or p.mes not in meses:
                continue
            categorias = {p.categoria_id} | {c.id for c in self._categorias.todos() if c.padre_id == p.categoria_id}
            gastado = sum(
                (
                    m.importe
                    for m in self._movimientos.todos()
                    if m.hogar_id == hogar_id and m.es_gasto and m.categoria_id in categorias and m.mes == p.mes
                ),
                Dinero.cero(),
            )
            resultado.append((copia(p), gastado))
        return resultado

    def cambiar_alerta(self, presupuesto_id, *, de, a):
        p = self._datos[presupuesto_id]
        if self.carrera_perdida:
            p.alerta_enviada = a  # el otro proceso ya lo ha hecho
        if p.alerta_enviada != de:
            return False
        p.alerta_enviada = a
        return True
