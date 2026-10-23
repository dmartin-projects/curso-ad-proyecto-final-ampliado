# usuarios/application/completar_login_social_use_case/dtos/completar_login_social_input_dto.py (módulo 91)
from dataclasses import dataclass

from usuarios.domain.enums.proveedor import Proveedor


@dataclass(frozen=True)
class CompletarLoginSocialInputDTO:
    proveedor: Proveedor
    clave: str | None  # la de la cookie (sin cookie: None)
    parametros: dict[str, str]  # los de la vuelta: state, code, error… (Apple: también `user`)
