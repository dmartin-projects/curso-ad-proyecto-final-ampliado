"""ITraza en memoria (módulo 89): guarda el resultado que se le anota."""

from estadisticas.application.ports.i_traza import ITraza
from estadisticas.domain.enums.resultado import Resultado


class TrazaFake(ITraza):
    valor: Resultado | None = None

    def resultado(self, resultado: Resultado) -> None:
        self.valor = resultado
