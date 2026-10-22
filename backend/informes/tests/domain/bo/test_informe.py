"""El informe mensual (módulo 88), sin base de datos."""

from core.domain.vo.mes import Mes
from informes.domain.bo.informe import Informe


def test_automatico_si_no_lo_pidio_nadie():
    assert Informe(1, Mes(2026, 9)).automatico and not Informe(1, Mes(2026, 9), generado_por_id=3).automatico
