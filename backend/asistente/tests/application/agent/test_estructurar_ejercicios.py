"""Módulo 96, ejercicio 3: una cifra de la respuesta estructurada tiene que estar en la respuesta."""

import json

from asistente.application.agent.estructurar import estructurar
from asistente.domain.read_models.respuesta_estructurada import Cifra
from asistente.domain.vo.mensaje import Mensaje
from asistente.tests.fakes.llm_fake import LLMFake

CONVERSACION = (
    Mensaje.usuario("¿Cuánto gastamos en septiembre?"),
    Mensaje.modelo(texto="En septiembre gastasteis **776,59 €**; lo que más, Supermercado: 461,35 €."),
)


def test_solo_las_cifras_que_estan_en_el_texto_con_cualquier_separador():
    cifras = [
        {"concepto": "Gasto de septiembre", "importe": "776.59 €"},  # otro separador: es la misma
        {"concepto": "Supermercado", "importe": "461,35 €"},
        {"concepto": "Resto", "importe": "315,24 €"},  # 776,59 - 461,35: calculada al estructurar, no dicha
    ]
    respuesta = json.dumps({"texto": "…", "cifras": cifras, "seguimiento": []})
    forma, _ = estructurar(LLMFake([LLMFake.responder(respuesta)]), CONVERSACION)
    assert forma.cifras == (Cifra("Gasto de septiembre", "776.59 €"), Cifra("Supermercado", "461,35 €"))
