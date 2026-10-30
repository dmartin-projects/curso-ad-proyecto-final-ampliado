"""Módulo 104: el servidor MCP de Gastos, de punta a punta: el token por el flujo OAuth de verdad (con `resource`), el
SDK de MCP delante y las tools del asistente detrás, contra PostgreSQL (la casa de los tests)."""

import json

import pytest
from django.conf import settings
from django.test import Client

from asistente.application.tools.resumen_mes_tool import ResumenMesTool
from asistente.infrastructure.api.mcp.servidor_mcp import declaracion_mcp
from asistente.tests.fakes.consultas_de_finanzas_fake import ConsultasDeFinanzasFake
from asistente.tests.mcp.conftest import URL, mcp, token
from conftest import HogarFactory, MembresiaFactory, UsuarioFactory

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.usefixtures("cliente_cli")]


def resultado(respuesta) -> dict:
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["result"]


def test_sin_token_401_con_el_camino_hasta_el_authorization_server():
    r = mcp("tools/list")
    assert r.status_code == 401
    assert (
        'resource_metadata="http://testserver/.well-known/oauth-protected-resource/api/mcp"'
        in r.headers["WWW-Authenticate"]
    )
    metadata = mcp("", ruta="/.well-known/oauth-protected-resource/api/mcp", get=True).json()
    assert metadata["resource"] == URL
    assert metadata["authorization_servers"] == [settings.OAUTH_ISSUER]
    assert metadata["scopes_supported"] == ["gastos:leer"]


def test_un_token_de_la_api_sin_recurso_no_vale(casa):
    ana, _ = casa
    assert mcp("tools/list", token=token(ana, resource=None)).status_code == 401


def test_un_token_para_otro_recurso_no_vale(casa):
    ana, _ = casa
    assert mcp("tools/list", token=token(ana, resource="http://testserver/api/otro")).status_code == 401


def test_sin_el_scope_403_y_dice_cual_falta(casa):
    ana, _ = casa
    r = mcp("tools/list", token=token(ana, scope="openid email"))
    assert r.status_code == 403
    assert 'error="insufficient_scope"' in r.headers["WWW-Authenticate"]


def test_con_su_token_las_tools_del_asistente_y_los_datos_de_su_hogar(casa):
    ana, hogar = casa
    t = token(ana)
    tools = {x["name"] for x in resultado(mcp("tools/list", token=t))["tools"]}
    assert {"listar_hogares", "resumen_mes", "gasto_por_categoria", "buscar_movimientos"} <= tools
    assert "proponer_movimiento" not in tools and "recordar" not in tools  # solo las de consulta

    hogares = resultado(mcp("tools/call", {"name": "listar_hogares", "arguments": {}}, token=t))
    assert hogares["structuredContent"]["hogares"] == [
        {"id": hogar.pk, "nombre": "Casa de Ana y Luis", "moneda": "EUR", "rol": "admin"}
    ]
    r = resultado(
        mcp("tools/call", {"name": "resumen_mes", "arguments": {"hogar": hogar.pk, "mes": "2026-09"}}, token=t)
    )
    assert (r["isError"], r["structuredContent"]["gastos"]) == (False, "776.59")


def test_otro_hogar_el_mismo_error_exista_o_no(casa):
    ana, _ = casa
    otro = HogarFactory(nombre="Casa de otros")
    MembresiaFactory(hogar=otro, usuario=UsuarioFactory(), rol="admin")
    t = token(ana)
    for hogar in (otro.pk, 999_999):
        r = resultado(mcp("tools/call", {"name": "resumen_mes", "arguments": {"hogar": hogar}}, token=t))
        assert r["isError"] and r["content"][0]["text"] == "El hogar no existe o no eres miembro."


def test_los_errores_de_la_tool_son_resultados_que_el_modelo_lee(casa):
    ana, hogar = casa
    t = token(ana)
    sin_hogar = resultado(mcp("tools/call", {"name": "resumen_mes", "arguments": {}}, token=t))
    assert sin_hogar["isError"] and "Falta el argumento 'hogar'" in sin_hogar["content"][0]["text"]
    mal = resultado(
        mcp("tools/call", {"name": "resumen_mes", "arguments": {"hogar": hogar.pk, "mes": "sept"}}, token=t)
    )
    assert mal["isError"] and "Argumentos no válidos para resumen_mes" in mal["content"][0]["text"]


def test_el_token_del_mcp_no_vale_en_la_api_rest(casa):
    ana, _ = casa
    r = Client().get("/api/v1/hogares/", HTTP_AUTHORIZATION=f"Bearer {token(ana)}")
    assert r.status_code == 401  # su recurso es /api/mcp: para la API, no es suyo (RFC 8707)


def test_una_cuenta_desactivada_ya_no_entra(casa):
    ana, _ = casa
    t = token(ana)
    ana.is_active = False
    ana.save(update_fields=["is_active"])
    assert mcp("tools/list", token=t).status_code == 401


def test_un_token_revocado_ya_no_entra(casa):
    from oauth2_provider.models import get_access_token_model

    ana, _ = casa
    t = token(ana)
    get_access_token_model().objects.get(user=ana).revoke()  # el único: el de este test
    assert mcp("tools/list", token=t).status_code == 401


def test_dns_rebinding_ni_otro_host_ni_otro_origen(casa):
    ana, _ = casa
    t = token(ana)
    assert mcp("tools/list", token=t, cabeceras={"Host": "atacante.example"}).status_code == 421
    assert mcp("tools/list", token=t, cabeceras={"Origin": "https://atacante.example"}).status_code == 403
    assert mcp("tools/list", token=t, cabeceras={"Origin": settings.FRONTEND_URL}).status_code == 200


def test_la_declaracion_lleva_el_hogar_obligatorio():
    d = declaracion_mcp(ResumenMesTool(finanzas=ConsultasDeFinanzasFake()))
    assert d.input_schema["required"][0] == "hogar"
    assert d.input_schema["properties"]["hogar"]["type"] == "integer"
    assert d.annotations.read_only_hint is True
    json.dumps(d.input_schema)  # serializable tal cual
