"""Módulo 98: manage.py coste_asistente y plan_asistente."""

from datetime import UTC, datetime
from decimal import Decimal
from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.enums.plan import Plan
from asistente.domain.vo.consumo import Consumo
from asistente.domain.vo.uso import Uso
from asistente.infrastructure.database.repositories.consumo_repository_orm import ConsumoRepositoryORM
from asistente.infrastructure.database.repositories.plan_del_hogar_repository_orm import PlanDelHogarRepositoryORM
from conftest import HogarFactory, UsuarioFactory

pytestmark = pytest.mark.django_db


def test_el_coste_de_un_mes_por_hogar_y_modelo():
    ana, casa = UsuarioFactory(), HogarFactory(nombre="Casa de Ana")
    momento = datetime(2026, 10, 15, tzinfo=UTC)
    ConsumoRepositoryORM().anotar(
        [
            Consumo(ana.pk, casa.pk, CanalDeConsumo.CHAT, "openai/gpt-oss-120b", Uso(12000, 900, cache=8000),
                    Decimal("0.001740"), momento),
            Consumo(ana.pk, casa.pk, CanalDeConsumo.TITULO, "otro", Uso(80, 20), None, momento),
        ]
    )  # fmt: skip
    salida = StringIO()
    call_command("coste_asistente", "--mes", "2026-10", stdout=salida)
    lineas = salida.getvalue().splitlines()
    assert lineas[0] == "Coste del asistente, 2026-10 (USD, con los precios de cada momento)"
    assert lineas[2].split() == ["Casa", "de", "Ana", f"({casa.pk})", "openai/gpt-oss-120b", "1", "12000", "8000", "900",
                                 "0.0017"]  # fmt: skip
    assert lineas[3].split()[-1] == "0.0000*"
    assert lineas[4].split()[-1] == "0.0017" and lineas[-1].startswith("* hay apuntes de modelos sin precio")


def test_un_mes_mal_escrito():
    with pytest.raises(CommandError, match="AAAA-MM"):
        call_command("coste_asistente", "--mes", "octubre")


def test_cambiar_el_plan_de_un_hogar():
    casa, salida = HogarFactory(), StringIO()
    call_command("plan_asistente", "--hogar", str(casa.pk), "plus", stdout=salida)
    assert PlanDelHogarRepositoryORM().plan_de(casa.pk) == Plan.PLUS
    assert "plan plus (400000 tokens al día por persona, 5.00 USD al mes por hogar)" in salida.getvalue()
