# hogares/application/crear_hogar_use_case/dtos/crear_hogar_input_dto.py (módulos 71 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class CrearHogarInputDTO:
    usuario_id: int  # quien lo crea: será su administrador (aún no tiene rol en ningún hogar)
    nombre: str
    moneda: str = "EUR"
    zona_horaria: str = "Europe/Madrid"
