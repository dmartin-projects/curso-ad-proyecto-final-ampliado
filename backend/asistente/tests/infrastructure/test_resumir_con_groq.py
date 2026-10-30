"""Módulo 99: resumir una conversación de verdad con el modelo auxiliar de Groq (gpt-oss-20b, grabado en un cassette).

    ASISTENTE_API_KEY=… uv run pytest asistente/tests/infrastructure/test_resumir_con_groq.py --record-mode=once -s

Lo que se compara es el resumen y lo que costó: el resumen de un modelo no se "acierta", se revisa. El test fija el que
salió al grabar; lo que se comprueba a mano está en el módulo (§ las salidas reales).
"""

from datetime import UTC, datetime

import pytest
import time_machine

from asistente.application.compactar_conversacion_use_case.compactar_conversacion_use_case import (
    CompactarConversacionUseCase,
)
from asistente.application.compactar_conversacion_use_case.dtos.compactar_conversacion_input_dto import (
    CompactarConversacionInputDTO,
)
from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion
from asistente.infrastructure import container
from asistente.infrastructure.database.models.consumo_model import Consumo as ConsumoModel
from asistente.infrastructure.database.repositories.consumo_repository_orm import ConsumoRepositoryORM
from asistente.infrastructure.database.repositories.conversacion_command_repository_orm import (
    ConversacionCommandRepositoryORM,
)
from asistente.infrastructure.tarifas.tarifas_desde_ajustes import TarifasDesdeAjustes
from core.infrastructure.clock.reloj_django import RelojDjango
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango

pytestmark = [pytest.mark.vcr, pytest.mark.usefixtures("clave"), pytest.mark.django_db]

# Una conversación como las del chat (las respuestas, las del módulo 97 acortadas)
CONVERSACION = [
    ("¿Cuánto gastamos en septiembre?", "En septiembre gastasteis 776,59 €. Lo que más, Supermercado (312,40 €) y "
     "Restaurantes (148,20 €)."),
    ("¿Y en agosto?", "En agosto, 1.120,35 €: más que en septiembre por las vacaciones (Viajes, 402,10 €)."),
    ("La cuenta común es la de ING, por cierto", "Entendido: la cuenta común es la de ING."),
    ("¿Cuánto llevamos este mes?", "En octubre lleváis 505,14 € hasta hoy, día 29."),
    ("¿Vamos mejor que el mes pasado?", "Sí: a estas alturas de septiembre llevabais 701,80 €; ahora, 196,66 € menos."),
]  # fmt: skip


def test_groq_resumir_lo_antiguo(casa):
    ana, hogar = casa
    repo = ConversacionCommandRepositoryORM()
    conversacion = Conversacion(ana.pk, hogar.pk)
    repo.guardar(conversacion)
    for pregunta, respuesta in CONVERSACION:
        repo.anadir(
            conversacion.id,
            [
                MensajeDeConversacion(Mensaje.usuario(pregunta), visible=True, texto=pregunta),
                MensajeDeConversacion(Mensaje.modelo(texto=respuesta), visible=True, texto=respuesta),
            ],
        )
    caso = CompactarConversacionUseCase(
        conversaciones=repo,
        llm=container.llm("openai/gpt-oss-20b"),  # solo el auxiliar: sin reserva, el cassette no cambia de modelo
        consumos=ConsumoRepositoryORM(),
        tarifas=TarifasDesdeAjustes(),
        reloj=RelojDjango(),
        uow=UnidadDeTrabajoDjango(),
        umbral=100,
    )
    with time_machine.travel(datetime(2026, 10, 29, 10, 0, tzinfo=UTC), tick=False):
        assert caso.ejecutar(CompactarConversacionInputDTO(ana.pk, hogar.pk, conversacion.id)) is True

    guardada = repo.obtener(ana.pk, hogar.pk, conversacion.id)
    consumo = ConsumoModel.objects.get(canal="resumen")
    resumidos = sum(i.hasta <= guardada.resumido_hasta for i in repo.intercambios(conversacion.id))
    salida = (
        f"{guardada.resumen}\n"
        f"  [{resumidos} de {len(CONVERSACION)} intercambios resumidos · {consumo.modelo} · entrada "
        f"{consumo.tokens_entrada}, salida {consumo.tokens_salida} (razonamiento {consumo.tokens_razonamiento}) · "
        f"{consumo.coste} USD]\n"
    )
    print(salida)
    assert salida == SALIDA


SALIDA = (
    "Preguntó por gastos de septiembre; el asistente contestó 776,59\u202f€, con mayor gasto en Supermercado (312,40\u202f€) y Restaurantes (148,20\u202f€).  \n"
    "Preguntó por gastos de agosto; el asistente contestó 1.120,35\u202f€, más que septiembre por Viajes (402,10\u202f€).  \n"
    "Preguntó sobre la cuenta común; el asistente confirmó que es la de ING.  \n"
    "El usuario comentó que la cuenta común es la de ING.\n"
    "  [3 de 5 intercambios resumidos · openai/gpt-oss-20b · entrada 302, salida 129 (razonamiento 10) · 0.000061 USD]\n"
)
