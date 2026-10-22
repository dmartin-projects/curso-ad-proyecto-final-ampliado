# importaciones/domain/bo/importacion.py — una importación de un extracto y sus reglas (módulos 75 y 88)
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import ClassVar

from core.domain.bo.i_auditable import IAuditable
from importaciones.domain.bo.fila import Fila
from importaciones.domain.enums.estado_importacion import E, EstadoImportacion
from importaciones.domain.enums.formato import Formato
from importaciones.domain.exceptions.estado_no_permitido_exception import EstadoNoPermitidoException
from importaciones.domain.services.resumen import resumen


@dataclass(eq=False)
class Importacion(IAuditable):
    tipo: ClassVar[str] = "importaciones.importacion"  # para la auditoría

    hogar_id: int
    cuenta_id: int
    nombre_original: str
    formato: Formato
    huella_archivo: str
    subido_por_id: int | None = None
    archivo: str = ""
    estado: EstadoImportacion = E.PENDIENTE
    total_filas: int = 0
    procesadas: int = 0
    creados: int = 0
    conciliados: int = 0
    duplicados: int = 0
    avisos: list = field(default_factory=list)
    resumen: dict = field(default_factory=dict)
    error: str = ""
    terminado_en: datetime | None = None
    id: int | None = None

    def __post_init__(self):
        self.estado, self.formato = EstadoImportacion(self.estado), Formato(self.formato)

    def _exigir(self, *estados: EstadoImportacion) -> None:
        if self.estado not in estados:
            raise EstadoNoPermitidoException()

    def analizada(self, filas: list[Fila], avisos: list[dict]) -> None:
        self._exigir(E.ANALIZANDO)
        self.total_filas, self.avisos, self.resumen = len(filas), avisos, resumen(filas)
        self.duplicados = self.resumen["duplicadas"]
        self.estado = E.VISTA_PREVIA

    def confirmar(self) -> None:
        self._exigir(E.VISTA_PREVIA)
        self.estado, self.procesadas = E.IMPORTANDO, 0

    def completar(self, ahora: datetime) -> None:
        self._exigir(E.IMPORTANDO)
        self.estado, self.terminado_en = E.COMPLETADA, ahora

    def deshacer(self) -> None:
        """También vale para una con error a medias (algunos lotes terminaron y otros no)."""
        self._exigir(E.COMPLETADA, E.ERROR)
        self.estado = E.DESHECHA

    @property
    def progreso(self) -> int:
        if self.estado == E.COMPLETADA:
            return 100
        a_importar = self.resumen.get("a_importar", 0)
        return min(100, self.procesadas * 100 // a_importar) if a_importar else 0

    def instantanea(self) -> "Importacion":
        return replace(self, avisos=list(self.avisos), resumen=dict(self.resumen))

    def datos_auditables(self) -> dict:
        return {
            "estado": str(self.estado),
            "creados": self.creados,
            "conciliados": self.conciliados,
            "duplicados": self.duplicados,
            "error": self.error,
        }

    def __str__(self) -> str:
        return f"{self.nombre_original} ({self.estado})"
