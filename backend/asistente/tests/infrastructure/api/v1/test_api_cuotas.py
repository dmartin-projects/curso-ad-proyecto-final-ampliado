"""Módulo 98: la cuota en la API. Lo que queda, y el 429 ANTES de abrir el stream (después ya no se puede)."""

from decimal import Decimal

import pytest
from django.utils import timezone

from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.vo.consumo import Consumo
from asistente.domain.vo.uso import Uso
from asistente.infrastructure.database.models.consumo_model import Consumo as ConsumoModel
from asistente.infrastructure.database.repositories.consumo_repository_orm import ConsumoRepositoryORM
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.infrastructure.api.v1.test_api_chat import estructurada, eventos, url

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.filterwarnings("ignore:StreamingHttpResponse must consume asynchronous iterators"),
]


@pytest.fixture
def planes(settings):
    settings.ASISTENTE_PLANES = {
        "basico": {"tokens_dia_persona": 1000, "coste_mes_hogar": "0.01"},
        "plus": {"tokens_dia_persona": 100000, "coste_mes_hogar": "5"},
    }


def gastar(usuario, hogar, tokens: int, coste="0") -> None:
    consumo = Consumo(usuario.pk, hogar.pk, CanalDeConsumo.CHAT, "m", Uso(tokens, 0), Decimal(coste), timezone.now())
    ConsumoRepositoryORM().anotar([consumo])


def test_lo_que_queda(casa, cliente, planes):
    ana, hogar = casa
    gastar(ana, hogar, 400, "0.002")
    r = cliente(ana).get(url(hogar, "cuota"))
    assert r.status_code == 200
    assert {k: r.json()[k] for k in ("plan", "tokens_hoy", "tokens_dia", "coste_mes", "agotada")} == {
        "plan": "basico",
        "tokens_hoy": 400,
        "tokens_dia": 1000,
        "coste_mes": "0.002000",
        "agotada": False,
    }
    gastar(ana, hogar, 0, "0.008")  # el hogar llega al límite del mes: manda sobre la persona
    assert cliente(ana).get(url(hogar, "cuota")).json()["agotada_por"] == "hogar"


def test_sin_cuota_un_429_con_retry_after_antes_del_stream(casa, cliente, planes, llm):
    ana, hogar = casa
    c = cliente(ana)
    cid = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    gastar(ana, hogar, 1000)

    r = c.post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "¿Una más?"}, format="json")
    assert r.status_code == 429
    assert (r.json()["type"], r.json()["title"]) == (
        "cuota_agotada",
        "Has llegado al límite de preguntas de hoy. Mañana vuelves a tenerlo.",
    )
    assert 0 < int(r["Retry-After"]) <= 24 * 3600
    assert llm.peticiones == []


def test_una_pregunta_apunta_lo_gastado(casa, cliente, planes, llm):
    ana, hogar = casa
    c = cliente(ana)
    cid = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    llm.guion += [LLMFake.responder("Hola."), estructurada("Hola.")]
    eventos(c.post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "Hola"}, format="json"))
    assert sorted(ConsumoModel.objects.values_list("canal", "tokens_entrada", "tokens_salida")) == [
        ("chat", 200, 40),
        ("titulo", 100, 20),
    ]
    assert cliente(ana).get(url(hogar, "cuota")).json()["tokens_hoy"] == 360
