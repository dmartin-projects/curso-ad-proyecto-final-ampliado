# usuarios/domain/vo/segundo_factor_pendiente.py — en vez de la sesión: falta el segundo factor (módulo 92)
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SegundoFactorPendiente:
    """En vez de la sesión: falta el segundo factor. `clave` va en una cookie HttpOnly (o en la sesión del
    authorization server), nunca en una URL; `factores`, lo que la pantalla puede ofrecer."""

    clave: str
    factores: list[str] = field(default_factory=list)
