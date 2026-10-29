"""Módulo 96: las fechas del prompt, con palabras y sin depender del locale del servidor."""

from datetime import date

from asistente.domain.services.fechas_en_castellano import fecha_larga, mes_largo
from core.domain.vo.mes import Mes


def test_fecha_larga_con_el_dia_de_la_semana():
    assert fecha_larga(date(2026, 10, 29)) == "jueves, 29 de octubre de 2026"
    assert fecha_larga(date(2027, 1, 3)) == "domingo, 3 de enero de 2027"


def test_mes_largo_con_su_forma_para_las_tools():
    assert mes_largo(Mes(2026, 9)) == "septiembre de 2026 (2026-09)"
