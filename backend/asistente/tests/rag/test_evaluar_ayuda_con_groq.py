"""Módulo 100: la búsqueda en la ayuda, medida con el conjunto de evaluación y el modelo auxiliar de Groq de verdad
(gpt-oss-20b, grabado en un cassette): la búsqueda por texto sola, con la pregunta reescrita y reordenada.

    ASISTENTE_API_KEY=… PAUSA=12 uv run pytest asistente/tests/rag/test_evaluar_ayuda_con_groq.py --record-mode=once -s

(PAUSA: segundos entre llamadas al grabar, por los 8.000 tokens por minuto de la capa gratuita.) Sin vectores: aquí
no hay modelo de embeddings (ASISTENTE_EMBEDDINGS vacío en los tests); `manage.py evaluar_ayuda` mide también esa fila.
"""

import os
import time

import pytest
import yaml

from asistente.application.ayuda.buscador_de_ayuda import BuscadorDeAyuda
from asistente.application.indexar_ayuda_use_case.dtos.indexar_ayuda_input_dto import IndexarAyudaInputDTO
from asistente.application.ports.i_llm import ILLM
from asistente.infrastructure import container
from asistente.infrastructure.database.repositories.indice_de_ayuda_pg import IndiceDeAyudaPG
from asistente.management.commands.evaluar_ayuda import PREGUNTAS, evaluar, tabla

pytestmark = [pytest.mark.vcr, pytest.mark.usefixtures("clave"), pytest.mark.django_db]


class Pausado(ILLM):
    """Al grabar, una pausa antes de cada llamada (el límite por minuto); al reproducir, ninguna."""

    def __init__(self, dentro: ILLM, segundos: float):
        self.dentro, self.segundos = dentro, segundos

    @property
    def modelo(self):
        return self.dentro.modelo

    def generar(self, peticion):
        time.sleep(self.segundos)
        return self.dentro.generar(peticion)


def test_groq_la_busqueda_en_la_ayuda_paso_a_paso():
    container.indexar_ayuda().ejecutar(IndexarAyudaInputDTO())
    preguntas = yaml.safe_load(PREGUNTAS.read_text())
    llm = Pausado(container.llm("openai/gpt-oss-20b"), float(os.environ.get("PAUSA", "0")))
    filas = evaluar(BuscadorDeAyuda(indice=IndiceDeAyudaPG(), embeddings=None, llm=None), preguntas, False)
    filas += evaluar(BuscadorDeAyuda(indice=IndiceDeAyudaPG(), embeddings=None, llm=llm), preguntas, True)
    salida = tabla(filas) + "\n"
    print(salida)
    (texto, solo), (_, reescrita), (_, reordenada) = filas
    assert reordenada["recall@3"] >= solo["recall@3"]  # si el modelo no mejora la búsqueda, sobra
    assert salida == SALIDA


SALIDA = (
    "texto                              recall@1 0.50 · recall@3 0.71 · MRR 0.62 · en los 8 candidatos 0.85 · 0 tokens\n"
    "    fuera de los 3 primeros: ¿cómo meto los movimientos de mi banco sin teclearlos uno a uno?\n"
    "    fuera de los 3 primeros: quiero que mi pareja pueda ver nuestras cuentas, ¿cómo la meto?\n"
    "    fuera de los 3 primeros: mi hijo solo debería mirar, no tocar nada\n"
    "    fuera de los 3 primeros: ¿pueden mis compañeros de piso leer lo que hablo con el asistente?\n"
    "    fuera de los 3 primeros: quiero ponerme un tope de gasto para comer fuera\n"
    "    fuera de los 3 primeros: ¿me avisáis cuando me paso de lo que quería gastar?\n"
    "    fuera de los 3 primeros: no me fío solo de la contraseña, ¿hay algo más seguro?\n"
    "    fuera de los 3 primeros: ¿cómo apunto lo que me ha costado la gasolina?\n"
    "    fuera de los 3 primeros: ¿dónde busco un pago de Amazon de hace meses?\n"
    "    fuera de los 3 primeros: quiero que el asistente se acuerde de que no cuento el alquiler\n"
    "texto + reescrita                  recall@1 0.44 · recall@3 0.68 · MRR 0.60 · en los 8 candidatos 0.91\n"
    "    fuera de los 3 primeros: ¿cómo meto los movimientos de mi banco sin teclearlos uno a uno?\n"
    "    fuera de los 3 primeros: mi hijo solo debería mirar, no tocar nada\n"
    "    fuera de los 3 primeros: ¿pueden mis compañeros de piso leer lo que hablo con el asistente?\n"
    "    fuera de los 3 primeros: quiero ponerme un tope de gasto para comer fuera\n"
    "    fuera de los 3 primeros: ¿me avisáis cuando me paso de lo que quería gastar?\n"
    "    fuera de los 3 primeros: necesito sacar los gastos a una hoja de cálculo\n"
    "    fuera de los 3 primeros: ¿dónde busco un pago de Amazon de hace meses?\n"
    "    fuera de los 3 primeros: ¿por qué un gasto del día 31 por la noche me sale en ese mes?\n"
    "    fuera de los 3 primeros: ¿el asistente me apunta cosas sin preguntarme?\n"
    "    fuera de los 3 primeros: quiero que el asistente se acuerde de que no cuento el alquiler\n"
    "    fuera de los 3 primeros: me dice que no puedo hacer más preguntas hoy\n"
    "texto + reescrita + reordenada     recall@1 0.88 · recall@3 0.91 · MRR 0.90 · 43059 tokens\n"
    "    fuera de los 3 primeros: ¿pueden mis compañeros de piso leer lo que hablo con el asistente?\n"
    "    fuera de los 3 primeros: ¿me avisáis cuando me paso de lo que quería gastar?\n"
    "    fuera de los 3 primeros: quiero que el asistente se acuerde de que no cuento el alquiler\n"
)
