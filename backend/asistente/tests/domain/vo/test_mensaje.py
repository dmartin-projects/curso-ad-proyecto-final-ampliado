"""Módulo 93: Mensaje, el idioma propio de la conversación, con sus reglas (sin Django ni SDK)."""

import pytest

from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.resultado_tool import ResultadoTool

LLAMADA = LlamadaTool("c1", "resumen_mes", '{"mes": "2026-09"}')
RESULTADO = ResultadoTool("c1", "resumen_mes", '{"gastos": "812.40"}')


def test_los_atajos_construyen_cada_rol():
    assert Mensaje.usuario("hola").rol == RolMensaje.USUARIO
    assert Mensaje.modelo(llamadas=(LLAMADA,)).llamadas == (LLAMADA,)
    assert Mensaje.de_tools((RESULTADO,)).resultados == (RESULTADO,)


def test_es_inmutable():
    with pytest.raises(AttributeError):
        Mensaje.usuario("hola").texto = "adiós"


@pytest.mark.parametrize(
    "construir, error",
    [
        (lambda: Mensaje(RolMensaje.USUARIO, "hola", llamadas=(LLAMADA,)), "Solo el modelo"),
        (lambda: Mensaje(RolMensaje.TOOL, llamadas=(LLAMADA,)), "Solo el modelo"),
        (lambda: Mensaje(RolMensaje.TOOL), "resultados de tools, y solo eso"),
        (lambda: Mensaje(RolMensaje.TOOL, "texto", resultados=(RESULTADO,)), "resultados de tools, y solo eso"),
        (lambda: Mensaje(RolMensaje.MODELO, resultados=(RESULTADO,)), "van en un mensaje TOOL"),
        (lambda: Mensaje.usuario("   "), "no puede estar vacío"),
    ],
)
def test_reglas(construir, error):
    with pytest.raises(ValueError, match=error):
        construir()
