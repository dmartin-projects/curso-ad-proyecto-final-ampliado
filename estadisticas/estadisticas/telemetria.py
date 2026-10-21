"""OpenTelemetry del servicio (módulo 85, sobre lo del 84). Apagado salvo con OTEL_ENABLED=true.

Mismas variables estándar que Django (OTEL_SERVICE_NAME, OTEL_EXPORTER_OTLP_ENDPOINT…) y el mismo
collector: en Grafana, una petición a Django y su procesamiento aquí aparecen en la misma traza.
"""

import logging
import os

logger = logging.getLogger(__name__)
_configurado = False


def activo() -> bool:
    return os.environ.get("OTEL_ENABLED", "").lower() in {"1", "true", "yes"}


def configurar(servicio: str, *, exportador=None) -> bool:
    """Trazas por OTLP. `exportador` solo para tests (uno en memoria)."""
    global _configurado
    if _configurado:
        return True
    if not (activo() or exportador):
        return False
    from opentelemetry import trace
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor

    proveedor = TracerProvider(resource=Resource.create({SERVICE_NAME: os.environ.get("OTEL_SERVICE_NAME", servicio)}))
    if exportador:
        proveedor.add_span_processor(SimpleSpanProcessor(exportador))
    else:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        proveedor.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(proveedor)

    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    from .bd import motor

    SQLAlchemyInstrumentor().instrument(engine=motor())  # un span por consulta, como psycopg en Django
    _configurado = True
    logger.info("OpenTelemetry activo")
    return True


def instrumentar_api(app) -> None:
    """Un span por petición HTTP, que continúa la traza si la petición trae `traceparent`."""
    if _configurado:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app, excluded_urls="salud")
