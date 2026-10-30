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
        "texto (124 trozos): 'Los gastos han ido variando en los últimos seis meses, con una tendencia a la baja en el último periodo: en octubre (mes en curso) lleváis **505,14\\u202f€**, frente a **776,59\\u202f€** en septiembre, el mes más alto del tramo.  \\n\\nEn general, los gastos han descendido de un pico de casi 800\\u202f€ a poco más de 500\\u202f€, mientras los ingresos se mantienen estables alrededor de los 2\\u202f100\\u202f€ mensuales.  \\n\\nEsto indica que el gasto mensual está bajo control y la diferencia entre ingresos y gastos sigue siendo positiva.'\n"
        "titulo: Evolución mensual de gastos\n"
        "fin: seguimiento ['¿Cuál ha sido el gasto promedio de los últimos seis meses?', '¿Qué categorías han consumido más dinero?', '¿Cómo puedo reducir los gastos de octubre?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 6020, salida 1172 · N ms]\n"
    ),
    "propuesta": (
        "> Apunta 3,50 € de churros de hoy, en Ocio\n"
        "inicio\n"
        "tool: Preparando el movimiento\n"
        "propuesta pendiente: Gasto de 3,50 €: «Churros», en Ocio, el 29/10/2026, en Cuenta común\n"
        "texto (52 trozos): 'Gasto de 3,50\\u202f€ preparado: «Churros», categoría Ocio, 29/10/2026, en la cuenta común.  \\nAún **no está apuntado**, necesitas confirmarlo en el chat para registrarlo.'\n"
        "titulo: Gasto churros hoy\n"
        "fin: seguimiento ['¿Quieres confirmar el gasto ahora?', '¿Quieres ver el total gastado este mes?', '¿Quieres añadir otro gasto?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 5765, salida 543 · N ms]\n"
    ),
    "sigue": (
        "> ¿Cuánto gastamos en septiembre?\n"
        "inicio\n"
        "tool: Mirando el resumen del mes\n"
        "texto (66 trozos): 'En septiembre gastasteis **776,59\\u202f€**.\\n\\nDetalle: ingresos 2\\u202f100,00\\u202f€, balance 1\\u202f323,41\\u202f€, 10 movimientos. El gasto subió 15,7\\u202f% respecto a agosto (de 671,35\\u202f€ a 776,59\\u202f€).'\n"
        "titulo: Gasto mensual en septiembre\n"
        "fin: seguimiento ['¿Cuáles fueron los mayores gastos del mes?', '¿Cómo se comparan los gastos de este mes con los de los últimos seis meses?', '¿Qué porcentaje del ingreso representa este gasto?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 5684, salida 570 · N ms]\n"
        "> ¿Y en agosto?\n"
        "inicio\n"
        "tool: Mirando el resumen del mes\n"
        "texto (67 trozos): 'En agosto gastasteis **671,35\\u202f€**.\\n\\nDetalle: ingresos 2\\u202f100,00\\u202f€, balance 1\\u202f428,65\\u202f€, 8 movimientos. En comparación, el gasto de septiembre subió a 776,59\\u202f€ (un incremento de 15,7\\u202f% respecto a agosto).'\n"
        "fin: seguimiento ['¿Cuál es el gasto medio mensual?', '¿Qué categorías consumen más?', '¿Cómo puedo reducir el gasto de septiembre?']\n"
        "  [3 llamadas · openai/gpt-oss-120b · entrada 5924, salida 952 · N ms]\n"
    ),
}
