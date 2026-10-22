# core/domain/repositories/queries/paginacion.py — paginación por número de página (módulo 87)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Paginacion:
    numero: str = "1"  # como llega ("2"); si no es un número válido, PaginaNoValidaException
    tamano: int = 20
    ultima: bool = False  # la última página, sea cual sea
