"""Los ejercicios del 104: el límite de llamadas por persona y cliente, el recurso en la pantalla de consentimiento y
la métrica de las llamadas."""

import pytest
from django.core.cache import cache

from asistente.infrastructure.api.mcp.limite_de_llamadas import LimiteDeLlamadas
from asistente.infrastructure.api.mcp.servidor_mcp import ServidorMCP
from asistente.tests.mcp.conftest import URL, mcp, token
from oauth.tests.infrastructure.flujo import con_sesion, peticion, pkce


@pytest.fixture(autouse=True)
def cache_vacia():
    cache.clear()


class Reloj:
    def __init__(self, t: float):
        self.t = t

    def __call__(self) -> float:
        return self.t


def test_el_limite_cuenta_por_minuto_y_dice_cuanto_esperar():
    reloj = Reloj(600.0 + 15)  # el segundo 15 de un minuto
    limite = LimiteDeLlamadas(2, reloj=reloj)
    assert [limite.espera("app", "7") for _ in range(3)] == [0, 0, 45]
    assert limite.espera("otra-app", "7") == 0  # otro cliente de la misma persona: su propia cuenta
    assert limite.espera("app", "8") == 0  # otra persona
    reloj.t = 660.0  # el minuto siguiente
    assert limite.espera("app", "7") == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("cliente_cli")
def test_pasado_el_limite_un_error_que_el_modelo_lee_y_la_metrica(casa, settings, monkeypatch):
    from asistente.infrastructure import container

    llamadas = []
    monkeypatch.setattr(container, "contar_llamada_mcp", lambda *a: llamadas.append(a))
    settings.ASISTENTE_MCP_LLAMADAS_POR_MINUTO = 1
    ana, hogar = casa
    t = token(ana)
    llamar = {"name": "resumen_mes", "arguments": {"hogar": hogar.pk, "mes": "2026-09"}}
    assert mcp("tools/call", llamar, token=t).json()["result"]["isError"] is False
    r = mcp("tools/call", llamar, token=t).json()["result"]
    assert r["isError"] and r["content"][0]["text"].startswith("Demasiadas llamadas. Vuelve a intentarlo dentro de")
    assert llamadas == [("gastos-cli", "resumen_mes", "ok"), ("gastos-cli", "resumen_mes", "limite")]


def test_sin_limite_ni_metrica_el_servidor_funciona_igual():
    servidor = ServidorMCP(tools=[], contexto=None, hogares=lambda _: [])
    assert servidor.limite is None and servidor.al_llamar is None


@pytest.mark.django_db
@pytest.mark.usefixtures("cliente_cli")
def test_la_pantalla_de_consentimiento_dice_para_que_recurso(casa):
    ana, _ = casa
    _, challenge = pkce()
    pantalla = con_sesion(ana).get("/api/oauth/authorize/", peticion(challenge, resource=URL))
    assert pantalla.status_code == 200
    assert f'<code id="recurso">{URL}</code>' in pantalla.content.decode()
    sin = con_sesion(ana).get("/api/oauth/authorize/", peticion(challenge))
    assert 'id="recurso"' not in sin.content.decode()
