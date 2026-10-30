# asistente/infrastructure/api/v1/views/sin_negociacion.py — la respuesta de error, siempre en JSON (módulo 97)
from rest_framework.negotiation import BaseContentNegotiation


class SinNegociacion(BaseContentNegotiation):
    """La vista de streaming contesta text/event-stream (una StreamingHttpResponse que DRF no renderiza) y, si falla
    antes de empezar (400, 404, 429), JSON. Un cliente que manda "Accept: text/event-stream" no debe recibir un 406
    por eso: se ignora el Accept y los errores salen con el primer renderer, el de JSON."""

    def select_parser(self, request, parsers):
        return parsers[0]

    def select_renderer(self, request, renderers, format_suffix=None):
        return renderers[0], renderers[0].media_type
