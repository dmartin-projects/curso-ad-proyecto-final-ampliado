# usuarios/application/empezar_login_social_use_case/dtos/empezar_login_social_input_dto.py (módulo 91)
from dataclasses import dataclass

from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor


@dataclass(frozen=True)
class EmpezarLoginSocialInputDTO:
    proveedor: Proveedor
    proposito: Proposito = Proposito.ENTRAR
    volver: str | None = None  # ENTRAR: la ruta de la SPA a la que volver
    usuario_id: int | None = None  # VINCULAR: quién (ya autenticado)
