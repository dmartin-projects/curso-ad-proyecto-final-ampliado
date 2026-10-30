"""Módulo 98, ejercicios: el coste por canal, los hogares sin cuota como métrica y las versiones del prompt."""

from datetime import UTC, datetime
from decimal import Decimal
from io import StringIO

import pytest
import time_machine
from django.core.management import call_command

from asistente.application.agent.agente import Agente
from asistente.application.agent.instrucciones import VERSION
from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.enums.plan import Plan
from asistente.domain.vo.consumo import Consumo
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.uso import Uso
from asistente.infrastructure.database.repositories.consumo_repository_orm import ConsumoRepositoryORM
from asistente.infrastructure.database.repositories.plan_del_hogar_repository_orm import PlanDelHogarRepositoryORM
from asistente.infrastructure.telemetria.telemetria_otel import TelemetriaOTel
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import Mundo, contexto
from conftest import HogarFactory, UsuarioFactory

pytestmark = pytest.mark.django_db
OCT = datetime(2026, 10, 15, tzinfo=UTC)


def apuntar(hogar, coste: str, canal=CanalDeConsumo.CHAT, momento=OCT):
    usuario = UsuarioFactory()
    ConsumoRepositoryORM().anotar([Consumo(usuario.pk, hogar.pk, canal, "m", Uso(100, 10), Decimal(coste), momento)])


def test_ejercicio_1_el_coste_por_canal():
    casa = HogarFactory(nombre="Casa")
    apuntar(casa, "0.002")
    apuntar(casa, "0.0001", CanalDeConsumo.TITULO)
    salida = StringIO()
    call_command("coste_asistente", "--mes", "2026-10", "--por-canal", stdout=salida)
    filas = [linea.split() for linea in salida.getvalue().splitlines()[2:4]]
    assert [(f[2], f[3], f[-1]) for f in filas] == [("m", "(chat)", "0.0020"), ("m", "(titulo)", "0.0001")]


def test_ejercicio_2_los_hogares_sin_cuota_como_metrica(telemetria, settings):
    settings.ASISTENTE_PLANES = {
        "basico": {"tokens_dia_persona": 1000, "coste_mes_hogar": "0.50"},
        "plus": {"tokens_dia_persona": 1000, "coste_mes_hogar": "5"},
    }
    agotado, plus, con_margen, de_septiembre = HogarFactory(), HogarFactory(), HogarFactory(), HogarFactory()
    apuntar(agotado, "0.30")
    apuntar(agotado, "0.20")  # 0,50: justo la cuota del básico
    PlanDelHogarRepositoryORM().asignar(plus.pk, Plan.PLUS)
    apuntar(plus, "1.00")  # se pasaría del básico, pero es plus
    apuntar(con_margen, "0.10")
    apuntar(de_septiembre, "9", momento=datetime(2026, 9, 30, tzinfo=UTC))  # otro mes
    with time_machine.travel(datetime(2026, 10, 29, 10, tzinfo=UTC), tick=False):
        assert telemetria.metrica("gastos.asistente.hogares_sin_cuota") == {(): 1}


def test_ejercicio_3_vueltas_y_tokens_por_version_del_prompt(telemetria):
    clave = (("gen_ai.prompt.version", VERSION),)
    antes = telemetria.metrica("gastos.asistente.vueltas").get(clave, (0, 0))
    agente = Agente(
        llm=LLMFake([LLMFake.llamar("listar_categorias"), LLMFake.responder("Hay cuatro.", Uso(900, 50))]),
        tools=Mundo().tools(),
        telemetria=TelemetriaOTel(),
    )
    agente.responder((Mensaje.usuario("¿Qué categorías hay?"),), contexto())
    veces, suma = telemetria.metrica("gastos.asistente.vueltas")[clave]
    assert (veces - antes[0], suma - antes[1]) == (1, 2)  # una pregunta, dos vueltas
    veces, suma = telemetria.metrica("gastos.asistente.tokens_por_pregunta")[clave]
    assert suma >= 1060  # 110 de la vuelta de la tool + 950 de la respuesta (más las de los tests anteriores)
