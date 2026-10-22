# core/infrastructure/logging/request_id.py — el id de cada petición en los logs (módulos 30, 84 y 88)
import logging
import re
import uuid
from contextvars import ContextVar

from opentelemetry import trace

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
# Lo envía el cliente o el proxy: solo se acepta con forma de id (un "\n" inyectaría líneas falsas en los logs)
ID_VALIDO = re.compile(r"[A-Za-z0-9-]{1,64}")


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        # Módulo 84: el trace_id de la traza en curso, para buscar en Grafana la traza de una línea de log
        # de la consola. Sin OpenTelemetry activo, el span actual es "inválido" y queda "-".
        # Se llama "traza" y no "trace_id": el log que sale por OTLP ya lleva su trace_id, y un atributo
        # con el mismo nombre lo pisaría en Loki (y los logs de fuera de una traza llegarían con "-")
        contexto = trace.get_current_span().get_span_context()
        record.traza = format(contexto.trace_id, "032x") if contexto.is_valid else "-"
        return True


def request_id_middleware(get_response):
    def middleware(request):
        recibido = request.headers.get("X-Request-ID", "")  # el proxy o Angular pueden enviarlo
        rid = recibido if ID_VALIDO.fullmatch(recibido) else uuid.uuid4().hex
        token = request_id_var.set(rid)
        try:
            response = get_response(request)
        finally:
            request_id_var.reset(token)
        response["X-Request-ID"] = rid  # el cliente puede reportarlo
        return response

    return middleware
