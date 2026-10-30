"""Módulo 97: el chat de punta a punta con Groq de verdad (grabado en cassettes) y la base de datos: el use case del
chat con los adapters de producción, en streaming, con el título del modelo auxiliar.

    ASISTENTE_API_KEY=… uv run pytest asistente/tests/infrastructure/test_chat_con_groq.py --record-mode=once -s

Lo que se compara es el registro de eventos que vería el navegador, con los trozos de texto contados (no uno por uno:
cuántos trozos llegan depende del servidor, no de nosotros) y sin milisegundos.
"""

import re
from datetime import UTC, datetime

import pytest
import time_machine

from asistente.application.responder_pregunta_use_case.dtos.responder_pregunta_input_dto import (
    ResponderPreguntaInputDTO,
)
from asistente.domain.bo.conversacion import Conversacion
from asistente.infrastructure import container
from asistente.infrastructure.database.repositories.conversacion_command_repository_orm import (
    ConversacionCommandRepositoryORM,
)
from asistente.tests.fakes.emisor_de_eventos_fake import EmisorDeEventosFake
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor

pytestmark = [pytest.mark.vcr, pytest.mark.usefixtures("clave"), pytest.mark.django_db]


@pytest.fixture(autouse=True)
def hoy(settings):
    settings.ASISTENTE_MODELO_AUXILIAR = "openai/gpt-oss-20b"
    with time_machine.travel(datetime(2026, 10, 29, 10, 0, tzinfo=UTC), tick=False):
        yield


def registro(emisor: EmisorDeEventosFake) -> str:
    """Los eventos, como los vería el navegador: los trozos de texto seguidos, juntos en una línea."""
    lineas, texto, trozos = [], [], 0
    for tipo, datos in [*emisor.eventos, ("", {})]:
        if tipo == "texto":
            texto.append(datos["delta"])
            trozos += 1
            continue
        if texto:
            lineas.append(f"texto ({trozos} trozos): {''.join(texto)!r}")
            texto, trozos = [], 0
        if tipo == "inicio":
            lineas.append("inicio")
        elif tipo == "tool":
            lineas.append(f"tool: {datos['texto']}")
        elif tipo == "grafico":
            lineas.append(
                f"grafico: {datos['tipo']} «{datos['titulo']}» con {datos['fuente']} {datos['argumentos']}: "
                f"{len(datos['etiquetas'])} puntos ({datos['etiquetas'][0]} … {datos['etiquetas'][-1]}), "
                f"series {[s['nombre'] for s in datos['series']]}"
            )
        elif tipo == "archivo":
            lineas.append(f"archivo: {datos['nombre']} ({datos['filas']} filas)")
        elif tipo == "propuesta":
            lineas.append(f"propuesta {datos['estado']}: {datos['resumen']}")
        elif tipo == "titulo":
            lineas.append(f"titulo: {datos['titulo']}")
        elif tipo == "fin":
            u = datos["uso"]
            lineas.append(f"fin: seguimiento {datos['seguimiento']}")
            lineas.append(
                f"  [{u['vueltas']} llamadas · {', '.join(u['modelos'])} · entrada {u['entrada']}"
                f"{f' ({u["cache"]} de caché)' if u['cache'] else ''}, salida {u['salida']} · {u['ms']} ms]"
            )
        elif tipo == "error":
            lineas.append(f"error: {datos['detalle']}")
    return "\n".join(lineas) + "\n"


def preguntar(casa, *preguntas: str) -> str:
    ana, hogar = casa
    conversacion = Conversacion(ana.pk, hogar.pk)
    ConversacionCommandRepositoryORM().guardar(conversacion)
    salidas = []
    for pregunta in preguntas:
        emisor = EmisorDeEventosFake()
        entrada = ResponderPreguntaInputDTO(hogar.pk, Actor(ana.pk, Rol.ADMIN), conversacion.id, pregunta, emisor)
        container.responder_pregunta().ejecutar(entrada)
        salidas.append(f"> {pregunta}\n{registro(emisor)}")
    salida = "".join(salidas)
    print(salida)  # con -s, al grabar: la salida real que enseña el módulo
    return re.sub(r"\b\d+ ms\b", "N ms", salida)


def test_groq_un_grafico_de_la_evolucion(casa):
    salida = preguntar(casa, "Dibújame cómo han ido los gastos estos últimos meses")
    assert salida == SALIDAS["grafico"]


def test_groq_apuntar_un_gasto_con_confirmacion(casa):
    salida = preguntar(casa, "Apunta 3,50 € de churros de hoy, en Ocio")
    assert salida == SALIDAS["propuesta"]


def test_groq_una_conversacion_que_sigue(casa):
    salida = preguntar(casa, "¿Cuánto gastamos en septiembre?", "¿Y en agosto?")
    assert salida == SALIDAS["sigue"]


SALIDAS: dict[str, str] = {
    "grafico": (
        "> Dibújame cómo han ido los gastos estos últimos meses\n"
        "inicio\n"
        "tool: Preparando el gráfico\n"
        "grafico: lineas «Gastos de los últimos 6 meses» con tendencia {'meses': 6}: 6 puntos (2026-05 … 2026-10), series ['Gastos', 'Ingresos']\n"
        "texto (230 trozos): 'Aquí tienes el gráfico de la evolución de los gastos en los últimos\\u202f6\\u202fmeses (márcalo en la interfaz):\\n\\n**Resumen rápido**  \\n- Los gastos totales de los últimos 6\\u202fmeses suman\\u202f≈\\u202f1\\u202f953\\u202f€, con una tendencia a la baja.  \\n- El mes más alto fue septiembre\\u202f2026 con\\u202f≈\\u202f777\\u202f€, mientras que el mes actual (octubre\\u202f2026) está en\\u202f≈\\u202f505\\u202f€.  \\n- Los ingresos han sido bastante estables, con un pico de\\u202f2\\u202f100\\u202f€ en agosto\\u202f2026 y el mismo valor en octubre\\u202f2026.\\n\\n**Detalle**  \\n- La línea de gastos muestra una clara reducción desde el pico de septiembre, indicando que estáis controlando mejor el consumo.  \\n- La línea de ingresos se mantiene plana, lo que permite que el balance mensual mejore progresivamente.  \\n- Si mantenéis este ritmo, el gasto mensual se situará alrededor de los\\u202f500\\u202f€ a final de octubre.\\n\\nEl gráfico está dibujado justo debajo de esta respuesta; puedes visualizar la evolución completa allí.'\n"
        "titulo: Evolución de gastos mensuales\n"
        "fin: seguimiento ['¿Cuál fue el gasto desglosado por categoría en septiembre?', '¿Cómo puedo reducir los gastos este mes?', '¿Cuál es el balance entre ingresos y gastos este mes?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 6918 (256 de caché), salida 1817 · N ms]\n"
    ),
    "propuesta": (
        "> Apunta 3,50 € de churros de hoy, en Ocio\n"
        "inicio\n"
        "tool: Preparando el movimiento\n"
        "propuesta pendiente: Gasto de 3,50 €: «Churros», en Ocio, el 29/10/2026, en Cuenta común\n"
        "texto (42 trozos): 'Gasto preparado: 3,50\\u202f€ en «Churros», categoría Ocio, para hoy (29/10/2026). Queda pendiente que lo confirmes para que se registre.'\n"
        "titulo: Gasto de churros hoy\n"
        "fin: seguimiento ['¿Quieres ver el total gastado en Ocio este mes?', '¿Deseas añadir otro gasto?', '¿Quieres el resumen de tus últimos movimientos?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 6547 (2304 de caché), salida 882 · N ms]\n"
    ),
    "sigue": (
        "> ¿Cuánto gastamos en septiembre?\n"
        "inicio\n"
        "tool: Mirando el resumen del mes\n"
        "texto (60 trozos): 'En septiembre gastasteis **776,59\\u202f€**.\\n\\nDetalle: ingresos 2\\u202f100,00\\u202f€, balance 1\\u202f323,41\\u202f€, 10 movimientos, gasto del mes anterior 671,35\\u202f€, variación\\u202f+15,7\\u202f% respecto a agosto.'\n"
        "titulo: Gastos de septiembre\n"
        "fin: seguimiento ['¿Cuál fue el mayor gasto de septiembre?', '¿Cómo se distribuyeron los gastos por categoría?', '¿Qué gastos podemos reducir?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 6470 (2816 de caché), salida 639 · N ms]\n"
        "> ¿Y en agosto?\n"
        "inicio\n"
        "tool: Mirando el resumen del mes\n"
        "texto (13 trozos): 'En agosto gastasteis **671,35\\u202f€**.'\n"
        "fin: seguimiento ['¿Cuál fue el ingreso total en agosto?', '¿Cuál es la variación respecto a julio?', '¿Cuántos movimientos hubo en agosto?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 6644, salida 508 · N ms]\n"
    ),
}
