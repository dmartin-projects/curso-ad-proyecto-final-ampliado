# usuarios/application/shared/dtos/segundo_factor_pendiente_output_dto.py — en vez de la sesión: falta el segundo
# factor (módulo 92)
from dataclasses import dataclass

from usuarios.domain.vo.segundo_factor_pendiente import SegundoFactorPendiente


@dataclass(frozen=True)
class SegundoFactorPendienteOutputDTO:
    """`clave` va en una cookie HttpOnly (o en la sesión del authorization server), nunca en una URL; `factores`, lo
    que la pantalla puede ofrecer."""

    clave: str
    factores: list[str]

    @classmethod
    def desde_vo(cls, pendiente: SegundoFactorPendiente) -> "SegundoFactorPendienteOutputDTO":
        return cls(clave=pendiente.clave, factores=list(pendiente.factores))
