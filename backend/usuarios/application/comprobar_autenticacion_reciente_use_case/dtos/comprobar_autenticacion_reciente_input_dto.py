# usuarios/application/comprobar_autenticacion_reciente_use_case/dtos/comprobar_autenticacion_reciente_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class ComprobarAutenticacionRecienteInputDTO:
    sid: str | None  # el de la sesión de la petición (None con un token OAuth o sin sesión)
    segundos: int  # la antigüedad máxima (REAUTENTICACION_SEGUNDOS)
