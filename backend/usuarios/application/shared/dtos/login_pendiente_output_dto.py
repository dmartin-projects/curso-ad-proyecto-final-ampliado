# usuarios/application/shared/dtos/login_pendiente_output_dto.py — el inicio de sesión a medias (módulo 92)
from dataclasses import dataclass

from usuarios.domain.enums.factor import Factor
from usuarios.domain.vo.login_pendiente import LoginPendiente


@dataclass(frozen=True, slots=True)
class LoginPendienteOutputDTO:
    usuario_id: int
    primero: Factor
    canal: str
    volver: str

    @classmethod
    def desde_vo(cls, pendiente: LoginPendiente) -> "LoginPendienteOutputDTO":
        return cls(pendiente.usuario_id, pendiente.primero, pendiente.canal, pendiente.volver)
