# usuarios/application/completar_segundo_factor_use_case/dtos/completar_segundo_factor_input_dto.py (módulo 92)
from dataclasses import dataclass

from usuarios.domain.enums.canal import Canal
from usuarios.domain.enums.factor import Factor
from usuarios.domain.vo.contexto import Contexto


@dataclass(frozen=True)
class CompletarSegundoFactorInputDTO:
    clave: str | None  # la del LoginPendiente (cookie o sesión del authorization server)
    canal: Canal
    factor: Factor  # TOTP, RECUPERACION o PASSKEY
    codigo: str = ""
    respuesta: dict | None = None  # la de navigator.credentials.get(), en JSON
    contexto: Contexto = Contexto()
