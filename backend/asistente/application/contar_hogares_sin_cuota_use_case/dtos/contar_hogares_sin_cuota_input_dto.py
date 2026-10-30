# asistente/application/contar_hogares_sin_cuota_use_case/dtos/contar_hogares_sin_cuota_input_dto.py (98, ejercicio 2)
from dataclasses import dataclass


@dataclass(frozen=True)
class ContarHogaresSinCuotaInputDTO:
    pass  # para todos los hogares: lo pide la métrica, no una persona
