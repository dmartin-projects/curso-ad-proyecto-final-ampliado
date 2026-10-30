# asistente/tests/fakes/exportador_de_movimientos_fake.py — IExportadorDeMovimientos en memoria (módulo 97)
from asistente.application.ports.i_exportador_de_movimientos import IExportadorDeMovimientos
from asistente.domain.vo.archivo_exportado import ArchivoExportado
from core.domain.enums.rol import Rol


class ExportadorDeMovimientosFake(IExportadorDeMovimientos):
    def __init__(self, filas: int = 12):
        self.filas = filas
        self.pedidos: list[tuple] = []

    def exportar(self, actor, hogar_id, filtro, nombre):
        actor.exigir(Rol.LECTOR)
        self.pedidos.append((actor, hogar_id, filtro, nombre))
        return ArchivoExportado(nombre, f"asistente/{hogar_id}/exportaciones/x" if self.filas else "", self.filas)
