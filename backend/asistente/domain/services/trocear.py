# asistente/domain/services/trocear.py — un Markdown de la ayuda, en trozos (módulo 100)
"""El chunking. La unidad natural de la ayuda es la SECCIÓN (`##`): tiene un título que dice de qué va y contesta una
pregunta. Por eso se corta por secciones y no cada N caracteres (un corte a ciegas parte una explicación por la mitad
y deja trozos que no se entienden solos). Solo si una sección es muy larga se parte, por párrafos, y cada parte lleva
el título delante (para_indexar).

La cabecera del archivo (entre `---`) da el título del documento."""

import re

from asistente.domain.vo.trozo_de_ayuda import TrozoDeAyuda

MAX_CARACTERES = 1200  # ~300 tokens: un trozo cabe holgado en lo que se le da al modelo, y dice una sola cosa


def trocear(documento: str, markdown: str) -> list[TrozoDeAyuda]:
    cabecera, cuerpo = _cabecera(markdown)
    titulo = cabecera.get("titulo") or documento
    trozos = []
    for seccion in re.split(r"^## ", cuerpo, flags=re.M)[1:]:
        nombre, _, texto = seccion.partition("\n")
        for parte, trozo in enumerate(_partir(texto.strip()), start=1):
            trozos.append(TrozoDeAyuda(documento, nombre.strip(), titulo, trozo, parte))
    return trozos


def _cabecera(markdown: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n", markdown, re.S)
    if not m:
        return {}, markdown
    campos = dict(linea.split(":", 1) for linea in m.group(1).splitlines() if ":" in linea)
    return {k.strip(): v.strip() for k, v in campos.items()}, markdown[m.end() :]


def _partir(texto: str) -> list[str]:
    """Por párrafos, juntando los que quepan. Un párrafo más largo que el máximo va solo: no se corta una frase."""
    partes, actual = [], ""
    for parrafo in texto.split("\n\n"):
        if actual and len(actual) + len(parrafo) + 2 > MAX_CARACTERES:
            partes.append(actual)
            actual = parrafo
        else:
            actual = f"{actual}\n\n{parrafo}" if actual else parrafo
    return [*partes, actual] if actual else partes
