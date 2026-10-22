"""Un fake es código, y también tiene tests (módulo 87)."""

from datetime import date
from decimal import Decimal

import pytest

from core.domain.enums.rol import Rol
from core.domain.vo.dinero import Dinero
from finanzas.application.crear_presupuesto_use_case.dtos.crear_presupuesto_input_dto import CrearPresupuestoInputDTO
from finanzas.domain.exceptions.presupuesto_duplicado_exception import PresupuestoDuplicadoException
from finanzas.tests.fakes.mundo import HOGAR, OCTUBRE, Mundo, actor


def test_tras_deshacer_los_fakes_siguen_conectados():
    mundo = Mundo()
    super_ = mundo.categoria("Súper")
    with pytest.raises(PresupuestoDuplicadoException):
        mundo.presupuesto(super_)
        mundo.crear_presupuesto.ejecutar(
            CrearPresupuestoInputDTO(HOGAR, actor(Rol.ADMIN), super_.id, date(2026, 10, 1), Decimal("5"))
        )
    mundo.movimiento(importe="-500", categoria=super_)  # después del rollback
    [(_, gastado)] = mundo.presupuestos.con_gastado(HOGAR, [OCTUBRE])
    assert gastado == Dinero("-500")  # el fake de presupuestos ve el MISMO repositorio de movimientos
