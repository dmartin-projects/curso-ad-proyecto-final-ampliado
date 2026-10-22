# backoffice/application/obtener_hogar_de_categoria_use_case/dtos/obtener_hogar_de_categoria_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerHogarDeCategoriaInputDTO:
    categoria_id: int
