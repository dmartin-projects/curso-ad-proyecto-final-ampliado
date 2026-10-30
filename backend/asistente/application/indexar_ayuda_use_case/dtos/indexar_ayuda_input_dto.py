# asistente/application/indexar_ayuda_use_case/dtos/indexar_ayuda_input_dto.py (módulo 100)
from dataclasses import dataclass


@dataclass(frozen=True)
class IndexarAyudaInputDTO:
    reconstruir: bool = False  # True: todo de cero (p. ej., tras cambiar de modelo de embeddings)
