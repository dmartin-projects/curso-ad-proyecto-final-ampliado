# usuarios/application/renovar_sesion_use_case/dtos/renovar_sesion_input_dto.py (módulo 92)
from dataclasses import dataclass

from usuarios.domain.vo.contexto import Contexto


@dataclass(frozen=True)
class RenovarSesionInputDTO:
    sid: str
    presentado: str  # el jti del refresh token que trae la cookie
    jti: str  # el del refresh token nuevo (rotado)
    contexto: Contexto = Contexto()
