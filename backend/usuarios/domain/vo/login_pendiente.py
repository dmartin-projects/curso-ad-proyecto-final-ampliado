# usuarios/domain/vo/login_pendiente.py — el inicio de sesión a medias (módulo 92)
from dataclasses import dataclass

from usuarios.domain.enums.factor import Factor


@dataclass(frozen=True, slots=True)
class LoginPendiente:
    """Entre el primer factor y el segundo: unos minutos, unos pocos intentos y nada más. No es una sesión."""

    usuario_id: int
    primero: Factor
    canal: str  # Canal (sesiones.py): dónde se abrirá la sesión al completarlo
    intentos: int = 0
    volver: str = "/"

    MAX_INTENTOS = 5

    @property
    def agotado(self) -> bool:
        return self.intentos >= self.MAX_INTENTOS
