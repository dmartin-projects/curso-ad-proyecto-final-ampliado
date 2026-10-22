# estadisticas/infrastructure/telemetry/traza_otel.py — ITraza sobre un span de OpenTelemetry (módulo 89)
from opentelemetry.trace import Span

from estadisticas.application.ports.i_traza import ITraza
from estadisticas.domain.enums.resultado import Resultado


class TrazaOTel(ITraza):
    def __init__(self, span: Span):
        self.span = span

    def resultado(self, resultado: Resultado) -> None:
        self.span.set_attribute("estadisticas.resultado", resultado.value)
