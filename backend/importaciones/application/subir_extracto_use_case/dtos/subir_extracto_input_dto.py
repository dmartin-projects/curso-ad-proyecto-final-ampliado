# importaciones/application/subir_extracto_use_case/dtos/subir_extracto_input_dto.py (módulos 75 y 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor
from importaciones.domain.enums.formato import Formato


@dataclass(frozen=True)
class SubirExtractoInputDTO:
    hogar_id: int
    actor: Actor
    cuenta_id: int
    contenido: object  # el file-like del adapter de entrada: el use case no lo abre
    nombre_original: str
    formato: Formato
    huella_archivo: str
