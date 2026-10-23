# usuarios/infrastructure/api/v1/views/a_la_spa.py — volver a una ruta de la SPA (módulo 91)
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect


def a_la_spa(ruta: str, **parametros) -> HttpResponseRedirect:
    """A una ruta de la SPA, en el dominio de la app. `ruta` es relativa (destino_seguro): nunca sale de Gastos."""
    return HttpResponseRedirect(settings.FRONTEND_URL + ruta + (f"?{urlencode(parametros)}" if parametros else ""))
