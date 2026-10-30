# asistente/application/ports/i_exportador_de_movimientos.py — un CSV con los movimientos de un filtro (módulo 97)
from abc import ABC, abstractmethod

from asistente.domain.vo.archivo_exportado import ArchivoExportado
from asistente.domain.vo.filtro_de_movimientos import FiltroDeMovimientos
from core.domain.vo.actor import Actor


class IExportadorDeMovimientos(ABC):
    """finanzas exporta (su use case de consulta, con el Actor de quien pregunta) y el archivo se guarda en el
    almacenamiento: al modelo solo le llega cuántas filas tiene, no las filas."""

    @abstractmethod
    def exportar(self, actor: Actor, hogar_id: int, filtro: FiltroDeMovimientos, nombre: str) -> ArchivoExportado: ...
