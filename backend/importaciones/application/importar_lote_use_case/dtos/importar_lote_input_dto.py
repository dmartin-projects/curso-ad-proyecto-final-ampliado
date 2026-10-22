# importaciones/application/importar_lote_use_case/dtos/importar_lote_input_dto.py (módulos 75 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ImportarLoteInputDTO:
    importacion_id: int
    fila_ids: list[int]
