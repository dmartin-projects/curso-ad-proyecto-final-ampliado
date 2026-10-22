# importaciones/domain/vo/lectura.py — lo que se lee de un extracto (módulos 75 y 88)
#
# Los lectores (CSV de cualquier banco, PDF) son adapters: infrastructure/lectores/. Todos devuelven esto.
from dataclasses import dataclass, field

from importaciones.domain.vo.fila_leida import FilaLeida


@dataclass
class Lectura:
    filas: list[FilaLeida] = field(default_factory=list)
    avisos: list[dict] = field(default_factory=list)

    def aviso(self, linea: int, mensaje: str) -> None:
        self.avisos.append({"linea": linea, "mensaje": mensaje})
