"""El BO Presupuesto: la alerta, sin base de datos (módulo 87)."""

from datetime import date

import pytest

from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from finanzas.domain.bo.presupuesto import Presupuesto
from finanzas.domain.exceptions.importe_no_positivo_exception import ImporteNoPositivoException


def test_presupuesto_alerta():
    p = Presupuesto(hogar_id=1, categoria_id=1, mes=date(2026, 10, 15), importe=Dinero("100"))
    assert p.mes == Mes(2026, 10)  # un presupuesto es de un MES, no de un día
    assert p.nueva_alerta(Dinero("-99.99")) is None  # por debajo y sin avisar: nada
    assert p.nueva_alerta(Dinero("-100")) is True  # justo el importe: superado
    p.alerta_enviada = True
    assert p.nueva_alerta(Dinero("-150")) is None  # ya avisado: no se repite
    assert p.nueva_alerta(Dinero("-20")) is False  # ha vuelto a estar por debajo: se rearma
    with pytest.raises(ImporteNoPositivoException):
        Presupuesto(1, 1, Mes(2026, 10), Dinero("0"))
