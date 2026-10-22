# importaciones/application/ports/i_lector_de_extractos.py — los lectores de extractos (CSV de cualquier banco, PDF) (módulo 88)
from abc import ABC, abstractmethod

from importaciones.domain.enums.formato import Formato
from importaciones.domain.vo.lectura import Lectura


class ILectorDeExtractos(ABC):
    @abstractmethod
    def leer(self, contenido: bytes, formato: Formato) -> Lectura:
        """ExtractoNoValidoException si el archivo no se puede leer."""
