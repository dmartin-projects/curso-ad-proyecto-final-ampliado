# finanzas/infrastructure/api/v1/presenters/cuenta_presenter.py — del OutputDTO a lo que lee el serializer (módulo 87)
from types import SimpleNamespace

from finanzas.application.shared.dtos.cuenta_con_saldo_output_dto import CuentaConSaldoOutputDTO


def presentar(c: CuentaConSaldoOutputDTO) -> SimpleNamespace:
    return SimpleNamespace(id=c.id, nombre=c.nombre, tipo=c.tipo, iban=c.iban, activa=c.activa, saldo=c.saldo)
