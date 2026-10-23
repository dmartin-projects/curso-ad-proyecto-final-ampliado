import factory
import pytest
from django.core.cache import cache
from django.db import transaction
from factory.django import DjangoModelFactory
from rest_framework.test import APIClient

from core.infrastructure.signals.red_de_seguridad import escrituras_directas
from hogares.models import Hogar, Membresia
from usuarios.models import Usuario


class FactoriaAtomica(DjangoModelFactory):
    """Datos de PARTIDA: los que ya estaban antes de lo que prueba el test (módulos 85 y 88).

    Movimientos, presupuestos, categorías y membresías solo se escriben con use cases (que publican sus eventos):
    escribirlos con el ORM hace saltar la alarma (EXIGIR_CASOS_DE_USO). Las factorías no son
    cambios de la aplicación, como un loaddata: `escrituras_directas()` lo dice explícitamente, y no publican nada.
    Un test que quiera eventos (outbox, avisos) hace el cambio con un use case o con la API.
    """

    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with escrituras_directas(), transaction.atomic():
            return super()._create(model_class, *args, **kwargs)


class UsuarioFactory(DjangoModelFactory):
    class Meta:
        model = Usuario
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"usuario{n}@example.com")
    nombre = factory.Faker("first_name", locale="es_ES")
    password = factory.django.Password("clave-segura-123")


class HogarFactory(FactoriaAtomica):
    class Meta:
        model = Hogar

    nombre = factory.Sequence(lambda n: f"Hogar {n}")


class MembresiaFactory(FactoriaAtomica):
    class Meta:
        model = Membresia

    hogar = factory.SubFactory(HogarFactory)
    usuario = factory.SubFactory(UsuarioFactory)
    rol = Membresia.Rol.ADMIN


@pytest.fixture(autouse=True)
def cache_limpia():
    """La caché locmem vive mientras dura el proceso: sin esto, un test hereda la del anterior (módulo 31)."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def cliente():
    """cliente(usuario) → APIClient autenticado como ese usuario."""

    def _cliente(usuario):
        c = APIClient()
        c.force_authenticate(usuario)
        return c

    return _cliente


@pytest.fixture
def sesion(db):
    """sesion(usuario) → APIClient con el access token de una sesión de verdad (módulo 92). Para las acciones
    sensibles (step-up): miran cuándo se autenticó esa sesión, y force_authenticate no abre ninguna."""
    from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
    from usuarios.domain.enums.factor import Factor
    from usuarios.infrastructure import container

    def _sesion(usuario):
        abierta = container.iniciar_sesion().ejecutar(IniciarSesionInputDTO(usuario.pk, Factor.CONTRASENA))
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {abierta.tokens.access}")
        return c

    return _sesion


@pytest.fixture
def hogar_con_roles(db):
    """Un hogar con un admin, un miembro, un lector y un usuario ajeno."""
    hogar = HogarFactory()
    roles = {rol: MembresiaFactory(hogar=hogar, rol=rol).usuario for rol in Membresia.Rol.values}
    roles["ajeno"] = UsuarioFactory()
    return hogar, roles


class CuentaFactory(FactoriaAtomica):
    class Meta:
        model = "finanzas.Cuenta"

    hogar = factory.SubFactory(HogarFactory)
    nombre = factory.Sequence(lambda n: f"Cuenta {n}")


class CategoriaFactory(FactoriaAtomica):
    class Meta:
        model = "finanzas.Categoria"

    hogar = factory.SubFactory(HogarFactory)
    nombre = factory.Sequence(lambda n: f"Categoría {n}")


class PresupuestoFactory(FactoriaAtomica):
    class Meta:
        model = "finanzas.Presupuesto"

    categoria = factory.SubFactory(CategoriaFactory)
    hogar = factory.SelfAttribute("categoria.hogar")
    mes = factory.Faker("date_this_month", before_today=True)
    importe = 100


class MovimientoFactory(FactoriaAtomica):
    class Meta:
        model = "finanzas.Movimiento"

    cuenta = factory.SubFactory(CuentaFactory)
    hogar = factory.SelfAttribute("cuenta.hogar")
    fecha = factory.Faker("date_this_year")
    importe = factory.Faker("pydecimal", left_digits=3, right_digits=2, max_value=-1, min_value=-500)
    concepto = factory.Faker("company", locale="es_ES")


# ── OpenTelemetry en los tests (módulo 84) ──
class Telemetria:
    """Lo que ha generado el código bajo prueba: spans, métricas y logs, en memoria."""

    def __init__(self, trazas, metricas, logs):
        self._trazas, self._metricas, self._logs = trazas, metricas, logs

    def spans(self, nombre=None):
        todos = self._trazas.get_finished_spans()
        return [s for s in todos if nombre is None or s.name == nombre]

    def logs(self):
        return [r.log_record for r in self._logs.get_finished_logs()]

    def metrica(self, nombre) -> dict:
        """{atributos (como tupla ordenada): valor} de una métrica (contador o histograma)."""
        datos = self._metricas.get_metrics_data()
        valores = {}
        for rm in datos.resource_metrics if datos else []:
            for sm in rm.scope_metrics:
                for m in sm.metrics:
                    if m.name == nombre:
                        for p in m.data.data_points:
                            clave = tuple(sorted(p.attributes.items()))
                            # contador: su valor; histograma: (cuántas medidas, suma)
                            valores[clave] = p.value if hasattr(p, "value") else (p.count, p.sum)
        return valores

    def limpiar(self):
        self._trazas.clear()
        self._logs.clear()


@pytest.fixture(scope="session")
def _telemetria_sesion():
    # Los proveedores globales de OpenTelemetry solo se pueden fijar UNA vez por proceso: se configura
    # al primer uso y se reutiliza en toda la sesión (cada test empieza con los exportadores vacíos)
    from opentelemetry.sdk._logs.export import InMemoryLogRecordExporter
    from opentelemetry.sdk.metrics.export import InMemoryMetricReader
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    from core.infrastructure.telemetry import telemetria

    trazas, metricas, logs = InMemorySpanExporter(), InMemoryMetricReader(), InMemoryLogRecordExporter()
    telemetria.configurar("gastos-tests", exportadores={"trazas": trazas, "metricas": metricas, "logs": logs})
    return Telemetria(trazas, metricas, logs)


@pytest.fixture
def _conexion_instrumentada(_telemetria_sesion):
    """psycopg se instrumenta al CONECTAR: una conexión abierta por un test anterior no generaría spans.
    En producción no pasa: configurar() se ejecuta en ready(), antes de la primera conexión."""
    from django.db import connections
    from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor

    for conexion in connections.all():
        if conexion.connection is not None and not getattr(
            conexion.connection, "_is_instrumented_by_opentelemetry", False
        ):
            PsycopgInstrumentor.instrument_connection(conexion.connection)


@pytest.fixture
def telemetria(_telemetria_sesion, db, _conexion_instrumentada):
    _telemetria_sesion.limpiar()
    return _telemetria_sesion
