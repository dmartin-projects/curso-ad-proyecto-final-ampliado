"""CrearPresupuestoUseCase con los fakes (módulo 87)."""

from datetime import date
from decimal import Decimal

import pytest

from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from finanzas.application.crear_presupuesto_use_case.dtos.crear_presupuesto_input_dto import CrearPresupuestoInputDTO
from finanzas.domain.events.presupuestos_cambiados_event import PresupuestosCambiadosEvent
from finanzas.domain.exceptions.importe_no_positivo_exception import ImporteNoPositivoException
from finanzas.domain.exceptions.presupuesto_duplicado_exception import PresupuestoDuplicadoException
from finanzas.tests.fakes.mundo import HOGAR, OCTUBRE, actor


def test_crear_presupuesto(mundo):
    super_ = mundo.categoria("Súper")
    entrada = CrearPresupuestoInputDTO(HOGAR, actor(Rol.ADMIN), super_.id, date(2026, 10, 15), Decimal("100"))
    p = mundo.crear_presupuesto.ejecutar(entrada)
    assert p.mes == OCTUBRE.inicio  # el día 15 no existe para un presupuesto: es de un mes
    assert mundo.eventos.publicados == [PresupuestosCambiadosEvent(HOGAR, frozenset({OCTUBRE}))]
    with pytest.raises(PresupuestoDuplicadoException):
        mundo.crear_presupuesto.ejecutar(entrada)
    with pytest.raises(ImporteNoPositivoException):
        mundo.crear_presupuesto.ejecutar(
            CrearPresupuestoInputDTO(HOGAR, actor(Rol.ADMIN), super_.id, date(2026, 11, 1), Decimal("0"))
        )
    with pytest.raises(SinPermisoException):  # el dinero lo reparte el admin
        mundo.crear_presupuesto.ejecutar(
            CrearPresupuestoInputDTO(HOGAR, actor(Rol.MIEMBRO), super_.id, date(2026, 12, 1), Decimal("10"))
        )
