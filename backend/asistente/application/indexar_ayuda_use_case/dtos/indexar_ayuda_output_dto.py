# asistente/application/indexar_ayuda_use_case/dtos/indexar_ayuda_output_dto.py (módulo 100)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IndexarAyudaOutputDTO:
    trozos: int  # los que hay ahora en el índice
    nuevos_o_cambiados: int  # los que se han (re)calculado
    borrados: int  # los que ya no están en la ayuda
    modelo: str  # el de embeddings ("" si se ha indexado solo para buscar por texto)
    rechazados: tuple[str, ...] = ()  # ejercicio 2 del 102: trozos que parecían una inyección (fuera del índice)
