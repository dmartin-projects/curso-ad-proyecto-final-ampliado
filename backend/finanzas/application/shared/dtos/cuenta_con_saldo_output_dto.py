# finanzas/application/shared/dtos/cuenta_con_saldo_output_dto.py (módulo 87)
from dataclasses import asdict, dataclass
from decimal import Decimal

from finanzas.domain.read_models.cuenta_con_saldo import CuentaConSaldo


@dataclass(frozen=True, slots=True)
class CuentaConSaldoOutputDTO:
    id: int
    nombre: str
    tipo: str
    iban: str
    activa: bool
    saldo: Decimal

    @classmethod
    def desde_read_model(cls, rm: CuentaConSaldo) -> "CuentaConSaldoOutputDTO":
        return cls(**asdict(rm))  # los mismos campos: el read model es del dominio; el OutputDTO, del use case
