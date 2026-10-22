"""Módulo 84, ejercicio 4: detectar consultas N+1 con las trazas, en un test.

Las trazas de producción enseñan las N+1 cuando ya están ahí (una petición con 200 spans SELECT).
El mismo dato, en un test: cuántas consultas SQL cuelgan de la traza de una petición. Si crece con el
número de filas, hay una N+1.
"""

import pytest
from django.core.cache import cache
from django.utils import timezone
from opentelemetry.trace import SpanKind

from conftest import CategoriaFactory, CuentaFactory, MovimientoFactory

pytestmark = pytest.mark.django_db


def consultas_de_la_peticion(telemetria) -> list[str]:
    """Las sentencias SQL de la (única) petición registrada, en orden."""
    [servidor] = [s for s in telemetria.spans() if s.kind == SpanKind.SERVER]
    hijos = [
        s
        for s in telemetria.spans()
        if s.attributes.get("db.system") == "postgresql" and s.context.trace_id == servidor.context.trace_id
    ]
    return [s.attributes["db.statement"] for s in sorted(hijos, key=lambda s: s.start_time)]


@pytest.mark.parametrize(
    "ruta",
    ["movimientos/", "presupuestos/", "categorias/", "dashboard/"],
)
def test_las_consultas_no_crecen_con_el_numero_de_filas(telemetria, hogar_con_roles, cliente, ruta):
    hogar, roles = hogar_con_roles
    cuenta = CuentaFactory(hogar=hogar)

    def medir(n):
        for _ in range(n):
            categoria = CategoriaFactory(hogar=hogar)
            # este mes: con fechas al azar, el dashboard se salta alguna consulta si un mes queda vacío,
            # y el test fallaría por los datos, no por una N+1
            MovimientoFactory(cuenta=cuenta, categoria=categoria, fecha=timezone.localdate())
        url = f"/api/v1/hogares/{hogar.pk}/{ruta}"
        cliente(roles["miembro"]).get(url)  # la 1.ª petición rellena cachés de Django (ContentType…)
        cache.clear()  # el dashboard se cachea (módulo 77): se mide el cálculo, no la caché
        telemetria.limpiar()
        assert cliente(roles["miembro"]).get(url).status_code == 200
        return consultas_de_la_peticion(telemetria)

    pocas, muchas = medir(2), medir(20)  # 2 y 22 movimientos con su categoría
    assert len(muchas) == len(pocas), "\n".join(c[:120] for c in muchas)
