# core/infrastructure/database/paginacion.py — paginar un QuerySet dentro de un query service (módulo 87)
#
# Los query services del ORM devuelven `Pagina[T]` (core/domain/read_models): el QuerySet, con todas sus
# optimizaciones, no sale de aquí. Por número, con el Paginator de Django (como PageNumberPagination de DRF);
# por cursor, keyset sobre los campos de orden (como CursorPagination, sin COUNT y con rendimiento constante).
import base64
import json
from collections.abc import Callable

from django.core.exceptions import ValidationError
from django.core.paginator import InvalidPage, Paginator
from django.db.models import Q

from core.domain.exceptions.cursor_no_valido_exception import CursorNoValidoException
from core.domain.exceptions.pagina_no_valida_exception import PaginaNoValidaException
from core.domain.read_models.pagina import Pagina
from core.domain.repositories.queries.paginacion import Paginacion
from core.domain.repositories.queries.paginacion_cursor import PaginacionCursor


def por_numero(qs, paginacion: Paginacion, a_read_model: Callable) -> Pagina:
    paginator = Paginator(qs, paginacion.tamano)
    try:
        pagina = paginator.page(paginator.num_pages if paginacion.ultima else paginacion.numero)
    except InvalidPage:
        raise PaginaNoValidaException() from None
    return Pagina(
        results=[a_read_model(fila) for fila in pagina],
        tamano=paginacion.tamano,
        siguiente=str(pagina.next_page_number()) if pagina.has_next() else None,
        anterior=str(pagina.previous_page_number()) if pagina.has_previous() else None,
        count=paginator.count,
        numero=pagina.number,
        total_paginas=paginator.num_pages,
    )


# ── Por cursor: keyset sobre campos descendentes ("-fecha", "-id"). El cursor guarda la posición de una fila ──
def _codificar(fila, campos: tuple[str, ...], hacia_atras: bool) -> str:
    posicion = [str(getattr(fila, c.lstrip("-"))) for c in campos]
    return base64.urlsafe_b64encode(json.dumps({"p": posicion, "r": hacia_atras}).encode()).decode()


def _decodificar(cursor: str) -> tuple[list[str], bool]:
    try:
        datos = json.loads(base64.urlsafe_b64decode(cursor.encode()))
        return [str(v) for v in datos["p"]], bool(datos["r"])
    except (ValueError, KeyError, TypeError):
        raise CursorNoValidoException() from None


def _despues_de(campos: tuple[str, ...], posicion: list[str], hacia_atras: bool) -> Q:
    """Las filas que van después de `posicion` en el orden de `campos` (o antes, si `hacia_atras`)."""
    condicion, iguales = Q(), Q()
    for campo, valor in zip(campos, posicion, strict=True):
        nombre = campo.lstrip("-")
        descendente = campo.startswith("-") != hacia_atras
        condicion |= iguales & Q(**{f"{nombre}__{'lt' if descendente else 'gt'}": valor})
        iguales &= Q(**{nombre: valor})
    return condicion


def por_cursor(qs, paginacion: PaginacionCursor, campos: tuple[str, ...], a_read_model: Callable) -> Pagina:
    n = paginacion.tamano
    if not paginacion.cursor:
        filas = list(qs.order_by(*campos)[: n + 1])
        hay_mas, hacia_atras, desde_cursor = len(filas) > n, False, False
    else:
        posicion, hacia_atras = _decodificar(paginacion.cursor)
        if len(posicion) != len(campos):
            raise CursorNoValidoException()
        orden = campos if not hacia_atras else tuple(c[1:] if c.startswith("-") else f"-{c}" for c in campos)
        try:
            filas = list(qs.filter(_despues_de(campos, posicion, hacia_atras)).order_by(*orden)[: n + 1])
        except (ValidationError, ValueError, TypeError) as e:  # un valor que no encaja ("fecha": "patata")
            raise CursorNoValidoException() from e
        hay_mas, desde_cursor = len(filas) > n, True
    filas = filas[:n]
    if hacia_atras:
        filas.reverse()
    siguiente = anterior = None
    if filas:
        if hacia_atras:
            anterior = _codificar(filas[0], campos, True) if hay_mas else None
            siguiente = _codificar(filas[-1], campos, False)
        else:
            siguiente = _codificar(filas[-1], campos, False) if hay_mas else None
            anterior = _codificar(filas[0], campos, True) if desde_cursor else None
    return Pagina(results=[a_read_model(f) for f in filas], tamano=n, siguiente=siguiente, anterior=anterior)
