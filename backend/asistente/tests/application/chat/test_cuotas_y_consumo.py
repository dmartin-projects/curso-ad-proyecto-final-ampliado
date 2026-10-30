"""Módulo 98: lo que gasta una pregunta (por modelo, también si se cancela) y la cuota en el día del hogar."""

from datetime import UTC, datetime
from decimal import Decimal

from asistente.application.agent.observador_mudo import ObservadorMudo
from asistente.application.chat.contador_de_uso import ContadorDeUso
from asistente.application.cuotas.calcular_cuota import calcular_cuota
from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.enums.plan import Plan
from asistente.domain.vo.consumo import Consumo
from asistente.domain.vo.uso import Uso
from asistente.tests.fakes.consumo_repositorio_fake import ConsumoRepositorioFake
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import ANA, HOGAR, contexto
from asistente.tests.fakes.plan_del_hogar_repositorio_fake import PlanDelHogarRepositorioFake
from asistente.tests.fakes.tarifas_fake import TarifasFake

AHORA = datetime(2026, 10, 29, 10, 0, tzinfo=UTC)


def test_el_contador_suma_por_modelo_y_pone_precio_al_que_lo_tiene():
    contador = ContadorDeUso(ObservadorMudo())
    contador.respuesta(LLMFake.responder("a", Uso(1000, 200, cache=600), modelo="openai/gpt-oss-120b"))
    contador.respuesta(LLMFake.responder("b", Uso(500, 100), modelo="openai/gpt-oss-120b"))
    contador.respuesta(LLMFake.responder("c", Uso(300, 50), modelo="openai/gpt-oss-20b"))  # la reserva: sin precio
    contador.respuesta(LLMFake.responder("d", Uso(0, 0), modelo="otro"))  # sin uso: no se apunta

    consumos = contador.consumos(
        usuario_id=ANA,
        hogar_id=HOGAR,
        conversacion_id=4,
        canal=CanalDeConsumo.CHAT,
        tarifas=TarifasFake(),
        momento=AHORA,
    )
    assert [(c.modelo, c.uso, c.coste) for c in consumos] == [
        # 900 sin caché × 0,15 + 600 de caché × 0,075 + 300 de salida × 0,60, por millón
        ("openai/gpt-oss-120b", Uso(1500, 300, cache=600), Decimal("0.000360")),
        ("openai/gpt-oss-20b", Uso(300, 50), None),
    ]


def test_el_turno_se_apunta_aunque_quien_escucha_corte():
    """El de dentro lanza (la persona se ha ido) DESPUÉS de que el contador haya sumado: ese turno se pagó."""

    class Corta(ObservadorMudo):
        def respuesta(self, respuesta):
            raise RuntimeError("cancelada")

    contador = ContadorDeUso(Corta())
    try:
        contador.respuesta(LLMFake.responder("a", Uso(100, 10), modelo="m"))
    except RuntimeError:
        pass
    assert contador.usos["m"] == Uso(100, 10)


def consumo(tokens: int, momento: datetime, coste="0.001", usuario=ANA) -> Consumo:
    return Consumo(usuario, HOGAR, CanalDeConsumo.CHAT, "m", Uso(tokens, 0), Decimal(coste), momento)


def test_el_dia_y_el_mes_son_los_del_hogar():
    """En Madrid, el 29 de octubre de 2026 empieza a las 23:00 UTC del 28 (UTC+1: el domingo 25 cambió la hora)."""
    consumos = ConsumoRepositorioFake()
    consumos.anotar(
        [
            consumo(100, datetime(2026, 10, 28, 22, 59, tzinfo=UTC)),  # el 28 en Madrid: no cuenta hoy, sí en el mes
            consumo(200, datetime(2026, 10, 28, 23, 0, tzinfo=UTC)),  # las 00:00 del 29 en Madrid
            consumo(
                400, datetime(2026, 10, 29, 9, 0, tzinfo=UTC), usuario=8
            ),  # Luis: el mes del hogar, no el día de Ana
            consumo(800, datetime(2026, 9, 30, 21, 59, tzinfo=UTC)),  # el 30 de septiembre en Madrid (UTC+2)
        ]
    )
    e = calcular_cuota(
        contexto(ahora=AHORA), AHORA, planes=PlanDelHogarRepositorioFake(), tarifas=TarifasFake(), consumos=consumos
    )
    assert (e.plan, e.tokens_hoy, e.coste_mes) == (Plan.BASICO, 200, Decimal("0.003"))
    assert e.manana == datetime(2026, 10, 29, 23, 0, tzinfo=UTC)
    assert e.mes_siguiente == datetime(2026, 10, 31, 23, 0, tzinfo=UTC)


def test_otro_plan_otra_cuota():
    planes = PlanDelHogarRepositorioFake()
    planes.asignar(HOGAR, Plan.PLUS)
    e = calcular_cuota(contexto(), AHORA, planes=planes, tarifas=TarifasFake(), consumos=ConsumoRepositorioFake())
    assert (e.plan, e.cuota.tokens_dia_persona) == (Plan.PLUS, 100_000)
