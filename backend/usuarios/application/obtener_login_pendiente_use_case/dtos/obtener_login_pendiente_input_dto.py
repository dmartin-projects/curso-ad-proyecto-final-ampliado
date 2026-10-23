# usuarios/application/obtener_login_pendiente_use_case/dtos/obtener_login_pendiente_input_dto.py (módulo 92)
from dataclasses import dataclass

from usuarios.domain.enums.canal import Canal


@dataclass(frozen=True)
class ObtenerLoginPendienteInputDTO:
    clave: str | None  # la de la cookie `mfa` (SPA) o la de la sesión del authorization server
    canal: Canal
