# tickets/infrastructure/ia/extractor_ia.py — IExtractorDeDatos con el cliente de la IA y su circuit breaker (módulos 74, 84 y 88)
from opentelemetry import trace

from tickets.application.ports.i_extractor_de_datos import IExtractorDeDatos
from tickets.domain.exceptions.datos_ilegibles_exception import DatosIlegiblesException
from tickets.domain.vo.datos_ticket import DatosTicket
from tickets.domain.vo.linea import Linea
from tickets.infrastructure.ia.cliente_ia import ClienteIA, breaker_ia
from tickets.infrastructure.ia.respuesta_ia_exception import RespuestaIAException

tracer = trace.get_tracer("gastos.tickets")


def a_datos(validados: dict) -> DatosTicket:
    return DatosTicket(
        comercio=validados["comercio"],
        nif=validados["nif"],
        fecha=validados["fecha"],
        total=validados["total"],
        moneda=validados["moneda"],
        categoria=validados["categoria"],
        lineas=tuple(Linea(li["descripcion"], li["cantidad"], li["precio_unitario"]) for li in validados["lineas"]),
        confianza=validados["confianza"],
    )


class ExtractorIA(IExtractorDeDatos):
    """Lo que la IA responde mal (RespuestaIAException) es DatosIlegiblesException para el dominio; los errores
    pasajeros y CircuitoAbiertoException siguen su camino hasta la tarea, que reintenta (módulo 74)."""

    def extraer(self, texto: str, categorias: list[str], imagen_png: bytes | None = None) -> DatosTicket:
        with tracer.start_as_current_span("ticket.ia") as span:
            span.set_attribute("ia.con_imagen", imagen_png is not None)
            try:
                with ClienteIA.desde_settings() as cliente:
                    datos = breaker_ia.llamar(cliente.extraer_ticket, texto, categorias, imagen_png)
            except RespuestaIAException as e:
                raise DatosIlegiblesException(str(e)) from e
            span.set_attribute("ia.confianza", datos["confianza"])
        return a_datos(datos)
