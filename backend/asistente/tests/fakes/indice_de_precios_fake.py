# asistente/tests/fakes/indice_de_precios_fake.py — IIndiceDePrecios con series fijas (módulo 95)
from asistente.application.ports.i_indice_de_precios import IIndiceDePrecios
from asistente.domain.read_models.serie_de_precios import SerieDePrecios


class IndiceDePreciosFake(IIndiceDePrecios):
    def __init__(self, series: dict[str, SerieDePrecios] | None = None, fallo: Exception | None = None):
        self.series, self.fallo = dict(series or {}), fallo
        self.pedidos: list[str] = []

    def serie(self, grupo):
        self.pedidos.append(grupo)
        if self.fallo:
            raise self.fallo
        return self.series.get(grupo) or SerieDePrecios(grupo, grupo, {})
