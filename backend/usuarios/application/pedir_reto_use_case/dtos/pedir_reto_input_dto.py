# usuarios/application/pedir_reto_use_case/dtos/pedir_reto_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class PedirRetoInputDTO:
    ambito: str  # "segundo:<clave>", "reautenticar:<usuario>" o "entrar:<cookie>"
    usuario_id: int | None = None
