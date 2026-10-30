"""Módulo 105: el análisis del mes con Groq de verdad (gpt-oss-120b, grabado en un cassette) y la base de datos de los
tests: el orquestador y sus tres especialistas con los adapters de producción y lo que gasta cada uno; y, para
compararlo, la misma petición en el chat (un solo agente con todo el catálogo), en su propio cassette: es otra pregunta.

    ASISTENTE_API_KEY=… uv run pytest asistente/tests/subagentes/test_analisis_con_groq.py --record-mode=once -s
"""

from collections import defaultdict
from datetime import UTC, datetime

import pytest
import time_machine

from asistente.application.analizar_mes_use_case.dtos.analizar_mes_input_dto import AnalizarMesInputDTO
from asistente.application.ports.i_observador_agente import IObservadorAgente
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.uso import Uso
from asistente.infrastructure import container
from asistente.infrastructure.database.repositories.conversacion_query_service_orm import ConversacionQueryServiceORM
from asistente.tests.fakes.avisos_de_progreso_fake import AvisosDeProgresoFake

pytestmark = [pytest.mark.vcr, pytest.mark.usefixtures("clave"), pytest.mark.django_db]
TAREA = "0b6f6a2e-6d2a-4c8e-9f5e-1a2b3c4d5e6f"
PREGUNTA = "Prepara el análisis de septiembre de 2026 (2026-09)."  # la que escribe AnalizarMesUseCase


class PorAgente(IObservadorAgente):
    """Envuelve el observador del análisis y reparte el uso de cada llamada al modelo entre quien la hizo: entre la
    llamada a un especialista y su resultado, todo es de ese especialista (el orquestador los llama en serie)."""

    def __init__(self, dentro: IObservadorAgente):
        self.dentro, self.actual = dentro, "orquestador"
        self.llamadas: dict[str, int] = defaultdict(int)
        self.usos: dict[str, Uso] = defaultdict(Uso)

    def respuesta(self, respuesta):
        self.llamadas[self.actual] += 1
        self.usos[self.actual] += respuesta.uso
        self.dentro.respuesta(respuesta)

    def llamada(self, llamada):
        if llamada.nombre.startswith("especialista_"):
            self.actual = llamada.nombre
        self.dentro.llamada(llamada)

    def resultado(self, resultado, duracion_ms):
        if resultado.nombre == self.actual:
            self.actual = "orquestador"
        self.dentro.resultado(resultado, duracion_ms)


def fila(nombre: str, llamadas: int, uso: Uso) -> str:
    return f"  {nombre:<26} {llamadas:>2} llamadas · entrada {uso.entrada:>6} · salida {uso.salida:>5}"


def test_groq_el_analisis_del_mes(casa, settings, monkeypatch):
    settings.ASISTENTE_MODELOS_RESERVA = []  # si el principal no está, el cassette no se graba con otro modelo
    ana, hogar = casa
    avisos, reparto = AvisosDeProgresoFake(), []
    orquestador = container.orquestador

    def crear_orquestador(observador):
        reparto.append(PorAgente(observador))
        return orquestador(reparto[-1])

    monkeypatch.setattr(container, "orquestador", crear_orquestador)
    monkeypatch.setattr(container, "avisos_de_progreso", lambda: avisos)
    with time_machine.travel(datetime(2026, 10, 29, 10, 0, tzinfo=UTC), tick=False):
        conversacion_id = container.analizar_mes().ejecutar(AnalizarMesInputDTO(ana.pk, hogar.pk, "2026-09", TAREA))
        detalle = ConversacionQueryServiceORM().detalle(ana.pk, hogar.pk, conversacion_id)
    pregunta, informe = (m.texto for m in detalle.mensajes)
    assert pregunta == PREGUNTA

    p = reparto[0]
    lineas = [f"> {pregunta}", f"progreso: {' · '.join(avisos.pasos)}", "lo que gasta cada uno:"]
    lineas += [fila(n, p.llamadas[n], p.usos[n]) for n in p.usos]
    lineas.append(fila("análisis (total)", sum(p.llamadas.values()), sum(p.usos.values(), Uso())))
    lineas += [f"informe («{detalle.conversacion.titulo}»):", informe]
    salida = "\n".join(lineas)
    print(salida)  # con -s, al grabar: la salida real que enseña el módulo
    assert salida == SALIDAS["analisis"]


def test_groq_la_misma_peticion_en_el_chat(casa, settings):
    settings.ASISTENTE_MODELOS_RESERVA = []
    ana, hogar = casa
    with time_machine.travel(datetime(2026, 10, 29, 10, 0, tzinfo=UTC), tick=False):
        r = container.agente().responder((Mensaje.usuario(PREGUNTA),), container.contexto(ana.pk, hogar.pk))
    salida = "\n".join(
        [f"> {PREGUNTA} (en el chat: un agente, todo el catálogo)",
         fila("chat", r.iteraciones, r.uso) + f" · tools {[c.nombre for c in r.llamadas]}", r.texto]
    )  # fmt: skip
    print(salida)
    assert salida == SALIDAS["chat"]


SALIDAS: dict[str, str] = {
    "analisis": (
        "> Prepara el análisis de septiembre de 2026 (2026-09).\n"
        "progreso: Repartiendo el trabajo · Analizando el gasto · Listo: el gasto · Analizando los presupuestos · Listo: los presupuestos · Analizando los comercios · Listo: los comercios · Análisis listo\n"
        "lo que gasta cada uno:\n"
        "  orquestador                 4 llamadas · entrada   4761 · salida   985\n"
        "  especialista_gastos         3 llamadas · entrada   3426 · salida   382\n"
        "  especialista_presupuestos   2 llamadas · entrada   1427 · salida   380\n"
        "  especialista_comercios      2 llamadas · entrada   1770 · salida   839\n"
        "  análisis (total)           11 llamadas · entrada  11384 · salida  2586\n"
        "informe («Análisis de septiembre de 2026»):\n"
        "**Septiembre\u202f2026**  \n"
        "Gastasteis **776,59\u202f€**. El mayor gasto fue en **Supermercado (461,35\u202f€ – 59\u202f%)**, seguido de **Restaurantes (102,00\u202f€ – 13\u202f%)**, **Casa (92,75\u202f€ – 12\u202f%)**, **Ocio (82,85\u202f€ – 11\u202f%)** y **Transporte (37,50\u202f€ – 5\u202f%)**.\n"
        "\n"
        "**Comparativa con agosto\u202f2026**  \n"
        "En agosto habíais gastado **671,35\u202f€**, por lo que septiembre sube **+105,24\u202f€ (+15,7\u202f%)**. Los aumentos más significativos son:  \n"
        "* Ocio: +58,99\u202f€ (pasó de 23,86\u202f€ a 82,85\u202f€).  \n"
        "* Restaurantes: +55,20\u202f€ (de 46,80\u202f€ a 102,00\u202f€).  \n"
        "\n"
        "Transporte se mantuvo igual (37,50\u202f€).\n"
        "\n"
        "**Presupuestos**  \n"
        "No tenéis ningún presupuesto asignado para septiembre, por lo que no hay previsión automática de gasto.\n"
        "\n"
        "**Comercios destacados**  \n"
        "* **Mercadona**: 409,25\u202f€ (2 compras, ≈\u202f59\u202f% del total).  \n"
        "* **Lidl**: 52,10\u202f€.  \n"
        "* **Renfe**: 37,50\u202f€ (gasto puntual de transporte).  \n"
        "* **Bar Manolo**: 23,40\u202f€ (salida ocasional).  \n"
        "* **Netflix**: 17,99\u202f€ (suscripción mensual recurrente).\n"
        "\n"
        "**Sugerencias**  \n"
        "1. **Crear presupuestos por categoría** (ej. Supermercado\u202f≤\u202f500\u202f€, Ocio\u202f≤\u202f70\u202f€) para controlar los incrementos.  \n"
        "2. **Revisar los gastos de Ocio y Restaurantes**: considerar opciones más económicas o limitar la frecuencia.  \n"
        "3. **Aprovechar ofertas o tarjetas de fidelidad** en Mercadona/Lidl para reducir el gasto alimentario."
    ),
    "chat": (
        "> Prepara el análisis de septiembre de 2026 (2026-09). (en el chat: un agente, todo el catálogo)\n"
        "  chat                        3 llamadas · entrada   6135 · salida   641 · tools ['resumen_mes', 'gasto_por_categoria']\n"
        "En septiembre gastasteis **776,59\u202f€**, un **15,7\u202f% más** que en agosto; con ingresos de **2\u202f100,00\u202f€** el balance quedó en **1\u202f323,41\u202f€** (10 movimientos).\n"
        "\n"
        "**Desglose principal:**  \n"
        "- **Supermercado:** 461,35\u202f€\u202f(59\u202f%)  \n"
        "- **Restaurantes:** 102,00\u202f€\u202f(13\u202f%)  \n"
        "- **Casa:** 92,75\u202f€\u202f(12\u202f%)  \n"
        "- **Ocio:** 82,99\u202f€\u202f(11\u202f%)  \n"
        "- **Transporte:** 37,50\u202f€\u202f(5\u202f%)  \n"
        "\n"
        "En resumen, el gasto se concentró mayoritariamente en el supermercado, seguido de restaurantes y gastos del hogar. El aumento respecto al mes anterior indica que el consumo de alimentos y ocio fue más intenso en septiembre."
    ),
}
