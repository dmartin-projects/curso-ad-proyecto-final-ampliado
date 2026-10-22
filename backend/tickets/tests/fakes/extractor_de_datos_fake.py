# tickets/tests/fakes/extractor_de_datos_fake.py — IExtractorDeDatos: devuelve (o lanza) lo que cada test le pide (módulo 88)
from datetime import date
from decimal import Decimal

from tickets.application.ports.i_extractor_de_datos import IExtractorDeDatos
from tickets.domain.vo.datos_ticket import DatosTicket
from tickets.domain.vo.linea import Linea


def datos(**cambios) -> DatosTicket:
    base = {
        "comercio": "Mercadona",
        "fecha": date(2026, 10, 12),
        "total": Decimal("4.85"),
        "confianza": 0.93,
        "nif": "A46103834",
        "categoria": "Supermercado",
        "lineas": (Linea("Leche", Decimal("2"), Decimal("0.95")), Linea("Pan", Decimal("1"), Decimal("2.95"))),
    }
    return DatosTicket(**base | cambios)


class ExtractorDeDatosFake(IExtractorDeDatos):
    """Devuelve `respuesta` (un DatosTicket) o la lanza (si es una excepción)."""

    def __init__(self, respuesta=None):
        self.respuesta = respuesta if respuesta is not None else datos()
        self.llamadas: list[tuple] = []

    def extraer(self, texto, categorias, imagen_png=None):
        self.llamadas.append((texto, list(categorias), imagen_png))
        if isinstance(self.respuesta, Exception):
            raise self.respuesta
        return self.respuesta
