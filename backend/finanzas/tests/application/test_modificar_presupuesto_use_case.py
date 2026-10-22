"""ModificarPresupuestoUseCase con los fakes (módulo 87)."""

from datetime import date
from decimal import Decimal

import pytest

from core.domain.enums.rol import Rol
from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from finanzas.application.modificar_presupuesto_use_case.dtos.modificar_presupuesto_input_dto import (
    ModificarPresupuestoInputDTO,
)
from finanzas.domain.events.presupuestos_cambiados_event import PresupuestosCambiadosEvent
from finanzas.domain.exceptions.importe_no_positivo_exception import ImporteNoPositivoException
from finanzas.tests.fakes.mundo import HOGAR, OCTUBRE, actor


def test_modificar_presupuesto_de_mes_avisa_de_los_dos(mundo):
    p = mundo.presupuesto(mundo.categoria("Súper"))
    entrada = ModificarPresupuestoInputDTO(
        HOGAR, actor(Rol.ADMIN), p.id, {"mes": date(2026, 11, 3), "importe": Decimal("80")}
    )
    mundo.modificar_presupuesto.ejecutar(entrada)
    guardado = mundo.presupuestos.obtener(HOGAR, p.id)
    assert (guardado.mes, guardado.importe) == (Mes(2026, 11), Dinero("80"))
    assert mundo.eventos.publicados == [PresupuestosCambiadosEvent(HOGAR, frozenset({OCTUBRE, Mes(2026, 11)}))]
    with pytest.raises(ImporteNoPositivoException):
        mundo.modificar_presupuesto.ejecutar(
            ModificarPresupuestoInputDTO(HOGAR, actor(Rol.ADMIN), p.id, {"importe": Decimal("-1")})
        )
    assert mundo.presupuestos.obtener(HOGAR, p.id).importe == Dinero("80")  # todo o nada
