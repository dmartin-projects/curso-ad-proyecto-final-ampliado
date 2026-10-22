# importaciones/domain/repositories/i_importacion_command_repository.py — el lado de escritura de las importaciones (módulo 88)
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime

from importaciones.domain.bo.fila import Fila
from importaciones.domain.bo.importacion import Importacion
from importaciones.domain.enums.accion import Accion
from importaciones.domain.enums.estado_importacion import EstadoImportacion
from importaciones.domain.enums.formato import Formato


class IImportacionCommandRepository(ABC):
    @abstractmethod
    def crear(self, importacion: Importacion, contenido: object) -> None:
        """Con su archivo. El mismo extracto activo dos veces en el hogar: ExtractoRepetidoException."""

    @abstractmethod
    def obtener(self, hogar_id: int, importacion_id: int, *, bloquear: bool = False) -> Importacion:
        """De ESE hogar, o ImportacionNoEncontradaException."""

    @abstractmethod
    def por_id(self, importacion_id: int, *, bloquear: bool = False) -> Importacion:
        """Para los procesos (tareas): el id no viene de fuera."""

    @abstractmethod
    def reclamar(self, importacion_id: int, de: EstadoImportacion, a: EstadoImportacion) -> bool:
        """Cambia el estado SOLO si sigue siendo `de` (UPDATE condicional): una entrega duplicada no hace nada."""

    @abstractmethod
    def fallar(self, importacion_id: int, mensaje: str, ahora: datetime) -> Formato | None:
        """A error, si aún podía fallar (UPDATE condicional). Devuelve su formato, o None si ya había terminado."""

    @abstractmethod
    def guardar(self, importacion: Importacion) -> None: ...

    @abstractmethod
    def leer_archivo(self, importacion: Importacion) -> bytes: ...

    # ── Las filas (el área de preparación) ──
    @abstractmethod
    def crear_filas(self, importacion_id: int, filas: list[Fila]) -> None: ...

    @abstractmethod
    def separar(self, importacion_id: int, fila_ids: Iterable[int]) -> None:
        """Filas a conciliar que la persona quiere importar como movimientos nuevos."""

    @abstractmethod
    def filas_a_importar(self, importacion_id: int) -> list[int]: ...

    @abstractmethod
    def filas_pendientes(self, importacion_id: int, fila_ids: Iterable[int]) -> list[Fila]:
        """Las del lote que aún no tienen movimiento, BLOQUEADAS: una entrega duplicada del lote espera y después
        no encuentra nada que hacer."""

    @abstractmethod
    def guardar_filas(self, filas: list[Fila]) -> None:
        """Solo la acción y el movimiento de cada fila."""

    @abstractmethod
    def sumar(self, importacion_id: int, *, procesadas: int, creados: int, conciliados: int, duplicados: int) -> None:
        """Contadores que varios lotes suman A LA VEZ: un UPDATE … SET x = x + n, nunca leer y escribir."""

    @abstractmethod
    def movimientos(self, importacion_id: int, accion: Accion) -> list[int]:
        """Los movimientos que representan sus filas con esa acción (para deshacer)."""
