"""OpenTelemetry (módulo 84): qué se genera, y qué NO debe salir del proceso."""

import logging

import pytest
from django.urls import path
from opentelemetry import trace
from opentelemetry.trace import SpanKind

from conftest import MovimientoFactory
from core.infrastructure.telemetry import telemetria as modulo

pytestmark = pytest.mark.django_db


def test_apagado_por_defecto_no_configura_nada(monkeypatch):
    monkeypatch.setattr(modulo, "_configurado", False)
    monkeypatch.delenv("OTEL_ENABLED", raising=False)
    assert modulo.configurar("gastos") is False


def test_una_peticion_es_una_traza_con_sus_consultas(telemetria, hogar_con_roles, cliente):
    hogar, roles = hogar_con_roles
    MovimientoFactory.create_batch(3, cuenta__hogar=hogar, concepto="Farmacia Sol")

    r = cliente(roles["miembro"]).get(f"/api/v1/hogares/{hogar.pk}/movimientos/?search=farmacia&page=1")
    assert r.status_code == 200

    [servidor] = [s for s in telemetria.spans() if s.kind == SpanKind.SERVER]
    # el nombre es la RUTA (el patrón de Django, aquí el que genera el router de DRF), no la URL:
    # todas las peticiones a esta vista se agrupan igual en Tempo y en las métricas, sea cual sea el hogar
    assert servidor.name == r"GET api/<str:version>/hogares/(?P<hogar_pk>\d+)/movimientos/$"
    assert str(hogar.pk) not in servidor.name
    assert servidor.attributes["http.response.status_code"] == 200
    # las consultas de ESTA petición son spans hijos dentro de su misma traza (las de los factories, no)
    consultas = [
        s
        for s in telemetria.spans()
        if s.attributes.get("db.system") == "postgresql" and s.context.trace_id == servidor.context.trace_id
    ]
    assert len(consultas) >= 2  # la membresía (permisos) y los movimientos
    assert all(s.parent.span_id == servidor.context.span_id for s in consultas)


def test_ningun_dato_personal_sale_en_la_traza(telemetria, hogar_con_roles, cliente):
    hogar, roles = hogar_con_roles
    MovimientoFactory(cuenta__hogar=hogar, concepto="Farmacia Sol")

    cliente(roles["miembro"]).get(f"/api/v1/hogares/{hogar.pk}/movimientos/?search=farmacia")

    texto = repr([(s.name, dict(s.attributes)) for s in telemetria.spans()])
    assert "farmacia" not in texto.lower()  # ni en la URL ni en los parámetros del SQL
    assert roles["miembro"].email not in texto
    [servidor] = [s for s in telemetria.spans() if s.kind == SpanKind.SERVER]
    assert "url.query" not in servidor.attributes  # con las convenciones estables, el servidor no la guarda


def test_las_urls_salen_sin_los_valores_de_sus_parametros(telemetria):
    # Un cliente HTTP (httpx a la IA, por ejemplo) sí guarda la URL completa: el procesador la limpia
    tracer = trace.get_tracer("pruebas")
    with tracer.start_as_current_span("llamada", attributes={"url.full": "https://api.x/v1/?q=farmacia&token=abc"}):
        pass
    [span] = telemetria.spans("llamada")
    assert span.attributes["url.full"] == "https://api.x/v1/?q=…&token=…"


def test_los_logs_llevan_el_trace_id_de_su_traza(telemetria):
    from core.infrastructure.logging.request_id import RequestIdFilter

    tracer = trace.get_tracer("pruebas")
    with tracer.start_as_current_span("operacion") as span:
        logging.getLogger("gastos.pruebas").info("algo ha pasado")
        # el filtro del handler de consola, aplicado a un registro creado dentro del span
        registro = logging.LogRecord("x", logging.INFO, __file__, 1, "dentro", None, None)
        RequestIdFilter().filter(registro)
    trace_id = format(span.get_span_context().trace_id, "032x")

    assert registro.traza == trace_id  # 1) en la consola (y en los logs JSON de producción)
    [enviado] = [log for log in telemetria.logs() if log.body == "algo ha pasado"]
    assert format(enviado.trace_id, "032x") == trace_id  # 2) en el log que sale por OTLP hacia Loki


def test_sin_traza_el_log_lleva_un_guion():
    from core.infrastructure.logging.request_id import RequestIdFilter

    registro = logging.LogRecord("x", logging.INFO, __file__, 1, "fuera", None, None)
    RequestIdFilter().filter(registro)
    assert registro.traza == "-"


def test_un_error_en_sentry_lleva_el_enlace_a_su_traza(monkeypatch, telemetria):
    monkeypatch.setenv("GRAFANA_TRAZA_URL", "https://grafana.example/traza/{trace_id}")
    with trace.get_tracer("pruebas").start_as_current_span("peticion") as span:
        evento = modulo.enlazar_sentry({"exception": {}}, hint=None)
    trace_id = format(span.get_span_context().trace_id, "032x")
    assert evento["tags"]["otel.trace_id"] == trace_id
    assert evento["contexts"]["grafana"]["traza"] == f"https://grafana.example/traza/{trace_id}"
    assert modulo.enlazar_sentry({}, hint=None) == {}  # fuera de una traza, el evento sale igual


def _vista_que_falla(request):
    raise ZeroDivisionError("fallo de prueba")


urlpatterns = [path("falla/", _vista_que_falla)]  # este módulo hace de ROOT_URLCONF en el test siguiente


def test_sentry_y_la_traza_comparten_trace_id_en_un_error_real(telemetria, settings, client):
    """De punta a punta: un 500 de verdad, capturado por la integración de Django de Sentry."""
    import sentry_sdk
    from sentry_sdk.transport import Transport

    capturados = []

    class EnMemoria(Transport):
        def capture_envelope(self, envelope):
            capturados.extend(item.payload.json for item in envelope.items if item.type == "event")

    settings.ROOT_URLCONF = __name__
    sentry_sdk.init(dsn="https://clave@sentry.example/1", transport=EnMemoria, before_send=modulo.enlazar_sentry)
    try:
        client.raise_request_exception = False
        assert client.get("/falla/").status_code == 500
    finally:
        sentry_sdk.get_client().close()
        sentry_sdk.init()  # deja Sentry apagado para el resto de tests

    [evento] = capturados
    [servidor] = [s for s in telemetria.spans() if s.name.startswith("GET falla")]
    assert evento["tags"]["otel.trace_id"] == format(servidor.context.trace_id, "032x")


def test_al_salir_un_hijo_de_celery_se_envia_lo_pendiente():
    """Los hijos de Celery salen con os._exit() (sin atexit): la señal es la última oportunidad."""
    from celery.signals import worker_process_shutdown

    vaciados = []

    class Proveedor:
        def force_flush(self, timeout_millis):
            vaciados.append(timeout_millis)

    modulo._vaciar_al_salir(Proveedor(), Proveedor())
    worker_process_shutdown.send(sender=None, pid=1, exitcode=0)
    assert vaciados == [5000, 5000]


def test_los_avisos_del_propio_sdk_no_se_envian_por_otlp(telemetria):
    # con el collector caído, cada aviso de exportación generaría otro envío fallido (un bucle)
    logging.getLogger("opentelemetry.exporter.otlp").warning("no hay collector")
    logging.getLogger("gastos.pruebas").warning("esto sí")
    cuerpos = [log.body for log in telemetria.logs()]
    assert "esto sí" in cuerpos and "no hay collector" not in cuerpos
