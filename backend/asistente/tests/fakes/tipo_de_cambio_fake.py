# asistente/tests/fakes/tipo_de_cambio_fake.py — ITipoDeCambio con tipos fijos (módulo 95)
from datetime import date
from decimal import Decimal

from asistente.application.ports.i_tipo_de_cambio import ITipoDeCambio
from asistente.domain.exceptions.moneda_desconocida_exception import MonedaDesconocidaException
from asistente.domain.read_models.conversion import Conversion


class TipoDeCambioFake(ITipoDeCambio):
    """{(de, a): (tipo, fecha del tipo)}; una moneda que no está, desconocida. `fallo`: lo que lanza siempre."""

    def __init__(self, tipos: dict[tuple[str, str], tuple[str, date]] | None = None, fallo: Exception | None = None):
        self.tipos, self.fallo = dict(tipos or {}), fallo
        self.pedidos: list[tuple] = []

    def convertir(self, importe, de, a, fecha=None):
        self.pedidos.append((importe, de, a, fecha))
        if self.fallo:
            raise self.fallo
        if (de, a) not in self.tipos:
            raise MonedaDesconocidaException()
        tipo, fecha_del_tipo = Decimal(self.tipos[(de, a)][0]), self.tipos[(de, a)][1]
        return Conversion(importe, de, a, (importe * tipo).quantize(Decimal("0.01")), tipo, fecha_del_tipo)
