"""OpenTelemetry: trazas, métricas y logs de Gastos (módulos 84 y 88).

Apagado por defecto: solo se activa con OTEL_ENABLED=true. Sin esa variable no se carga el SDK (solo la
API de OpenTelemetry, que sin SDK no hace nada) y la aplicación se comporta igual que en el módulo 83.

Todo lo demás se configura con las variables ESTÁNDAR de OpenTelemetry, que entiende cualquier SDK
(Python, Java, Node…) y cualquier backend (Grafana, Datadog, Honeycomb…):

    OTEL_SERVICE_NAME=gastos-web                       quién genera la telemetría
    OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318  a dónde se envía (el collector, por HTTP)
    OTEL_TRACES_SAMPLER=parentbased_traceidratio       qué trazas se guardan…
    OTEL_TRACES_SAMPLER_ARG=1.0                        …y en qué proporción (1.0 = todas)
    OTEL_RESOURCE_ATTRIBUTES=deployment.environment.name=produccion

Se llama UNA vez por proceso, desde CoreConfig.ready() (core/apps.py): la web, cada worker de Celery,
beat y los comandos de manage.py pasan todos por ahí.
"""

import logging
import os
import re

logger = logging.getLogger(__name__)

_configurado = False


def activo() -> bool:
    return os.environ.get("OTEL_ENABLED", "").lower() in {"1", "true", "yes"}


def configurar(servicio: str, *, exportadores=None) -> bool:
    """Prepara los proveedores de trazas, métricas y logs e instrumenta las librerías.

    `servicio` es el nombre por defecto (gastos-web, gastos-worker…); OTEL_SERVICE_NAME lo sustituye.
    `exportadores` solo para tests: {"trazas": ..., "metricas": ..., "logs": ...} en memoria.
    Devuelve True si OpenTelemetry ha quedado activo.
    """
    global _configurado
    if _configurado:
        return True
    if not (activo() or exportadores):
        return False

    from opentelemetry import metrics, trace
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.instrumentation.logging.handler import LoggingHandler
    from opentelemetry.sdk._logs import LoggerProvider
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, SimpleLogRecordProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.metrics.view import ExplicitBucketHistogramAggregation, View
    from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor

    # Resource: quién es este proceso. Resource.create() añade OTEL_SERVICE_NAME y OTEL_RESOURCE_ATTRIBUTES
    recurso = Resource.create(
        {
            SERVICE_NAME: os.environ.get("OTEL_SERVICE_NAME", servicio),
            SERVICE_VERSION: os.environ.get("VERSION", "dev"),
        }
    )

    # ── Trazas ── El sampler sale de OTEL_TRACES_SAMPLER/OTEL_TRACES_SAMPLER_ARG (por defecto: todas)
    trazas = TracerProvider(resource=recurso)
    trazas.add_span_processor(SinDatosPersonales())  # antes de exportar: limpia atributos sensibles
    if exportadores:
        trazas.add_span_processor(SimpleSpanProcessor(exportadores["trazas"]))
    else:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        # Batch: acumula y envía en segundo plano; la petición del usuario no espera al collector
        trazas.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(trazas)

    # ── Métricas ── Se agregan en memoria y se envían cada OTEL_METRIC_EXPORT_INTERVAL ms (60 s)
    if exportadores:
        lector = exportadores["metricas"]
    else:
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

        lector = PeriodicExportingMetricReader(OTLPMetricExporter())
    # Una View cambia cómo se agrega una métrica. La duración de las tareas de Celery viene con los
    # cubos por defecto (0, 5, 10, 25… s): un OCR de 2 s y un aviso de 30 ms caen en el mismo y el p95
    # sale 4,75 s para TODAS las tareas. Con cubos pensados para nuestras tareas, el p95 dice algo.
    cubos_tareas = View(
        instrument_name="flower.task.runtime.seconds",
        aggregation=ExplicitBucketHistogramAggregation([0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60]),
    )
    metrics.set_meter_provider(MeterProvider(resource=recurso, metric_readers=[lector], views=[cubos_tareas]))

    # ── Logs ── Los logging.* de siempre salen también por OTLP (a Loki), con el trace_id de su traza
    logs = LoggerProvider(resource=recurso)
    if exportadores:
        logs.add_log_record_processor(SimpleLogRecordProcessor(exportadores["logs"]))
    else:
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

        logs.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
    set_logger_provider(logs)
    manejador = LoggingHandler(level=logging.INFO, logger_provider=logs)
    # Los avisos del propio SDK ("no puedo conectar con el collector") NO se envían por OTLP: con el
    # collector caído, cada aviso generaría otro envío fallido y otro aviso (lo detecta y lo corta con
    # "recursive logging", pero llena la consola). Siguen saliendo por la consola, que es donde sirven.
    manejador.addFilter(lambda registro: not registro.name.startswith("opentelemetry"))
    logging.getLogger().addHandler(manejador)

    _instrumentar()
    _vaciar_al_salir(trazas, metrics.get_meter_provider(), logs)
    _configurado = True
    logger.info("OpenTelemetry activo", extra={"servicio": recurso.attributes[SERVICE_NAME]})
    return True


def _vaciar_al_salir(*proveedores) -> None:
    """Envía lo pendiente cuando un proceso hijo de Celery termina.

    Los procesadores "batch" acumulan y envían cada pocos segundos, y vacían su cola al salir… con
    atexit. Pero los hijos de Celery salen con os._exit(), que se salta atexit: con
    --max-tasks-per-child (worker-ocr recicla su proceso cada 50 tickets) se perderían los spans de la
    última tarea de cada hijo. Con --max-tasks-per-child 1 se ve enseguida: de cada ticket solo llegaría
    a Tempo la parte de la petición web.
    """
    from celery.signals import worker_process_shutdown

    def vaciar(**_):
        for proveedor in proveedores:
            proveedor.force_flush(timeout_millis=5000)

    worker_process_shutdown.connect(vaciar, weak=False)


def _instrumentar() -> None:
    """Instrumentación automática: cada librería crea sus spans sin tocar nuestro código."""
    # Nombres de atributos ESTABLES de las convenciones semánticas HTTP (url.query,
    # http.response.status_code…). Sin esto, las instrumentaciones usan aún los antiguos (http.url…)
    os.environ.setdefault("OTEL_SEMCONV_STABILITY_OPT_IN", "http")
    from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
    from opentelemetry.instrumentation.celery import CeleryInstrumentor
    from opentelemetry.instrumentation.django import DjangoInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.propagators import TraceResponsePropagator, set_global_response_propagator
    from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor

    # Cabecera "traceresponse" en cada respuesta: el trace_id de la petición, para buscarla en Grafana
    # desde las herramientas del navegador o desde un informe de error del frontend
    set_global_response_propagator(TraceResponsePropagator())
    # Las sondas de Docker (cada 30 s, por réplica) llenarían Tempo de trazas sin interés
    DjangoInstrumentor().instrument(excluded_urls="health/live,health/ready")
    CeleryInstrumentor().instrument()  # encolar y ejecutar; propaga la traza en las cabeceras del mensaje
    PsycopgInstrumentor().instrument()  # cada consulta SQL, con el texto pero SIN los valores
    RedisInstrumentor().instrument()  # caché, channel layer y resultados de Celery
    HTTPXClientInstrumentor().instrument()  # las llamadas a la IA
    BotocoreInstrumentor().instrument()  # S3/R2: subir y leer las fotos de los tickets


# ── Privacidad ──

# Parámetros de la URL que pueden llevar datos personales o secretos: ?search=farmacia, ?token=…
_QUERY = re.compile(r"([?&][^=&#]+=)[^&#]*")
_ATRIBUTOS_URL = ("url.query", "url.full", "http.url", "http.target")


def _sin_valores(url: str) -> str:
    """/api/v1/movimientos/?search=farmacia&page=2 → /api/v1/movimientos/?search=…&page=…"""
    return _QUERY.sub(r"\1…", url)


try:
    from opentelemetry.sdk.trace import SpanProcessor as _Base
except ImportError:  # OpenTelemetry no instalado: la clase no se usa
    _Base = object


class SinDatosPersonales(_Base):
    """Quita los VALORES de los parámetros de las URLs antes de que el span salga del proceso.

    Los nombres se conservan (saber que se buscó es útil; qué se buscó, no hace falta). Las cabeceras
    y los cuerpos no se capturan por defecto, y las consultas SQL llegan con %s en lugar de los valores.
    """

    def on_start(self, span, parent_context=None) -> None:
        # Las instrumentaciones ponen la URL al CREAR el span: aquí aún se puede cambiar. En on_end
        # ya no (un span terminado es de solo lectura).
        for clave in _ATRIBUTOS_URL:
            valor = (span.attributes or {}).get(clave)
            if isinstance(valor, str) and "=" in valor:
                span.set_attribute(clave, _sin_valores(valor))


# ── Sentry → Grafana ──


def enlazar_sentry(evento: dict, hint) -> dict:
    """before_send de Sentry: añade al error el trace_id de OpenTelemetry y un enlace a su traza.

    Sentry dice QUÉ se ha roto (la excepción, la línea); Grafana, POR DÓNDE pasó esa petición antes
    (qué consultas, qué tarea, cuánto tardó cada paso). Con el trace_id como etiqueta, desde el error en
    Sentry se abre la traza completa en Grafana con un clic, y se puede buscar al revés.
    """
    from opentelemetry import trace

    contexto = trace.get_current_span().get_span_context()
    if not contexto.is_valid:
        return evento
    trace_id = format(contexto.trace_id, "032x")
    evento.setdefault("tags", {})["otel.trace_id"] = trace_id
    if base := os.environ.get("GRAFANA_TRAZA_URL"):  # p. ej. https://tu-stack.grafana.net/explore?…
        evento.setdefault("contexts", {})["grafana"] = {"traza": base.replace("{trace_id}", trace_id)}
    return evento
