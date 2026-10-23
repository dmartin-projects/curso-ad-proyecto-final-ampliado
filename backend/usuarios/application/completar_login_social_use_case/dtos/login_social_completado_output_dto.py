# usuarios/application/completar_login_social_use_case/dtos/login_social_completado_output_dto.py (módulo 91)
from dataclasses import dataclass

from usuarios.domain.enums.proposito import Proposito


@dataclass(frozen=True, slots=True)
class LoginSocialCompletadoOutputDTO:
    usuario_id: int
    proposito: Proposito
    volver: str
    cuenta_nueva: bool = False
