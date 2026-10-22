# core/infrastructure/database/busqueda.py — ?search=… dentro de un query service (módulo 88)
#
# Lo mismo que hace SearchFilter de DRF con los `search_fields` de una vista: cada término, en alguno de los campos;
# todos los términos a la vez. Los prefijos de siempre: "=" exacto, "^" empieza por, "@" búsqueda de texto completo,
# "$" expresión regular; sin prefijo, contiene (sin distinguir mayúsculas). Si algún campo cruza una relación de
# "muchos" (membresias__usuario__email), una fila podría salir repetida: se filtra con un EXISTS, como SearchFilter.
import operator
from functools import reduce

from django.db.models import Exists, OuterRef, Q

PREFIJOS = {"^": "istartswith", "=": "iexact", "@": "search", "$": "iregex"}


def _consulta(campo: str) -> str:
    if campo[0] in PREFIJOS:
        return f"{campo[1:]}__{PREFIJOS[campo[0]]}"
    return f"{campo}__icontains"


def _cruza_muchos(modelo, campo: str) -> bool:
    opts = modelo._meta
    for parte in campo.lstrip("".join(PREFIJOS)).split("__"):
        field = opts.get_field(parte)
        if not hasattr(field, "get_path_info"):
            return False
        caminos = field.get_path_info()
        if any(c.m2m for c in caminos):
            return True
        opts = caminos[-1].to_opts
    return False


def buscar(qs, campos: tuple[str, ...], terminos: tuple[str, ...]):
    if not campos or not terminos:
        return qs
    consultas = [_consulta(c) for c in campos]
    condiciones = (reduce(operator.or_, (Q(**{c: t}) for c in consultas)) for t in terminos)
    filtrado = qs.filter(reduce(operator.and_, condiciones))
    if any(_cruza_muchos(qs.model, c) for c in campos):
        return qs.filter(Exists(filtrado.filter(pk=OuterRef("pk"))))
    return filtrado
