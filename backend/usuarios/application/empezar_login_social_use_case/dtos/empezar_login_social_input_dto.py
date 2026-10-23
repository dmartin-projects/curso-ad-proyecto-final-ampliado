# usuarios/application/empezar_login_social_use_case/dtos/empezar_login_social_input_dto.py (módulos 91 y 92)
from dataclasses import dataclass

from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor


@dataclass(frozen=True)
class EmpezarLoginSocialInputDTO:
    proveedor: Proveedor
    proposito: Proposito = Proposito.ENTRAR
    volver: str | None = None  # ENTRAR: la ruta de la SPA a la que volver
    usuario_id: int | None = None  # VINCULAR: quién (ya autenticado)
    sid: str | None = None  # módulo 92, ej. 3 (REAUTENTICAR): la sesión que confirma quién es
