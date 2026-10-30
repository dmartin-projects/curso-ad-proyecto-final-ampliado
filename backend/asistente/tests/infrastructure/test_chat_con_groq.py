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
        "texto (146 trozos): 'Aquí tienes el gráfico de la evolución de los gastos (y los ingresos) en los últimos\\u202f6\\u202fmeses.  \\n\\n- En septiembre\\u202f2026 se alcanzó el pico de gasto con **776,59\\u202f€**.  \\n- En el mes en curso, octubre\\u202f2026, el gasto acumulado es de **505,14\\u202f€**, más bajo que el mes anterior.  \\n- Los ingresos se han mantenido estables, con **2\\u202f100\\u202f€** en el último mes.  \\n\\nEn conjunto, el total gastado en este periodo es de **1\\u202f953,08\\u202f€**, mientras que los ingresos suman **6\\u202f300\\u202f€**, lo que indica un balance positivo.'\n"
        "titulo: Evolución de gastos mensuales\n"
        "fin: seguimiento ['¿Cuál fue el gasto promedio mensual?', '¿En qué categoría se concentró la mayor parte del gasto?', '¿Cómo puedo reducir los gastos de octubre?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 6250 (2304 de caché), salida 1018 · N ms]\n"
    ),
    "propuesta": (
        "> Apunta 3,50 € de churros de hoy, en Ocio\n"
        "inicio\n"
        "tool: Preparando el movimiento\n"
        "propuesta pendiente: Gasto de 3,50 €: «churros», en Ocio, el 29/10/2026, en Cuenta común\n"
        "texto (44 trozos): 'He quedado **pendiente** de apuntar el gasto: 3,50\\u202f€ en Ocio (concepto\\u202f«churros») del día de hoy. Cuando lo confirmes, lo registraré.'\n"
        "titulo: Registro de churros en ocio\n"
        "fin: seguimiento ['¿Quieres añadir alguna nota al gasto?', '¿En qué cuenta lo registro?', '¿Quieres ver el resumen de tus gastos de Ocio?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 5947, salida 619 · N ms]\n"
    ),
    "sigue": (
        "> ¿Cuánto gastamos en septiembre?\n"
        "inicio\n"
        "tool: Mirando el resumen del mes\n"
        "texto (56 trozos): 'En septiembre gastasteis **776,59\\u202f€**.\\n\\nDetalle: ingresos 2\\u202f100,00\\u202f€, balance 1\\u202f323,41\\u202f€, 10 movimientos, gasto un 15,7\\u202f% superior al mes anterior (671,35\\u202f€).'\n"
        "titulo: Gasto total de septiembre\n"
        "fin: seguimiento ['¿Cuál fue el gasto más alto del mes?', '¿Puedes ver la distribución de mis gastos por categorías en septiembre?', '¿Cómo ha evolucionado mi gasto en los últimos seis meses?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 5882 (5120 de caché), salida 1040 · N ms]\n"
        "> ¿Y en agosto?\n"
        "inicio\n"
        "tool: Mirando el resumen del mes\n"
        "texto (55 trozos): 'En agosto gastasteis **671,35\\u202f€**.\\n\\nDetalle: ingresos 2\\u202f100,00\\u202f€, balance 1\\u202f428,65\\u202f€, 8 movimientos. No hay datos de variación respecto al mes anterior porque ese mes aún no está registrado.'\n"
        "fin: seguimiento ['¿Cuál fue el gasto mayor en agosto?', '¿Cuál es la media de gasto mensual?', '¿Podemos comparar septiembre con julio?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 6090 (4096 de caché), salida 813 · N ms]\n"
    ),
}
