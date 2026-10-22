# finanzas/infrastructure/database/repositories/movimiento_query_service_orm.py — IMovimientoQueryService con el ORM
# (módulos 34, 37, 73, 87 y 88)
#
# Todo el ORM dentro: select_related para los nombres (una consulta, no N), Count de los adjuntos, values_list e
# iterator para el CSV, keyset para el cursor. Fuera solo salen read models.
from collections.abc import Iterator
from functools import reduce
from operator import and_

from django.db.models import Count, Q

from core.domain.read_models.pagina import Pagina
from core.domain.repositories.queries.paginacion_cursor import PaginacionCursor
from core.infrastructure.database import paginacion
from finanzas.domain.read_models.movimiento_del_mes import MovimientoDelMes
from finanzas.domain.read_models.movimiento_exportado import MovimientoExportado
from finanzas.domain.read_models.movimiento_listado import MovimientoListado
from finanzas.domain.read_models.movimiento_sin_conciliar import MovimientoSinConciliar
from finanzas.domain.repositories.i_movimiento_query_service import IMovimientoQueryService
from finanzas.domain.repositories.queries.filtros_movimientos_query import FiltrosMovimientosQuery
from finanzas.domain.repositories.queries.movimientos_query import MovimientosQuery
from finanzas.infrastructure.database.models.movimiento_model import Movimiento as MovimientoModel

RECIENTES_PRIMERO = ("-fecha", "-id")  # el orden por defecto y el del cursor (índice mov_hogar_fecha)
CAMPOS_BUSQUEDA = ("concepto", "comercio__nombre", "notas")


def _filtrar(qs, f: FiltrosMovimientosQuery):
    if f.fecha_desde is not None:
        qs = qs.filter(fecha__gte=f.fecha_desde)
    if f.fecha_hasta is not None:
        qs = qs.filter(fecha__lte=f.fecha_hasta)
    if f.importe_min is not None:
        qs = qs.filter(importe__gte=f.importe_min)
    if f.importe_max is not None:
        qs = qs.filter(importe__lte=f.importe_max)
    if f.cuentas:
        qs = qs.filter(cuenta_id__in=f.cuentas)
    if f.categorias:  # una categoría principal incluye a sus hijas
        qs = qs.filter(Q(categoria_id__in=f.categorias) | Q(categoria__padre_id__in=f.categorias))
    if f.sin_categoria is not None:
        qs = qs.filter(categoria__isnull=f.sin_categoria)
    if f.tipo == "gasto":
        qs = qs.gastos()
    elif f.tipo == "ingreso":
        qs = qs.ingresos()
    if f.etiqueta:
        qs = qs.filter(etiquetas__contains=[f.etiqueta.lower()])
    if f.origen:
        qs = qs.filter(origen=f.origen)
    if f.revisado is not None:
        qs = qs.filter(revisado=f.revisado)
    if f.busqueda:  # cada término en alguno de los campos; todos los términos a la vez
        terminos = (reduce(Q.__or__, (Q(**{f"{c}__icontains": t}) for c in CAMPOS_BUSQUEDA)) for t in f.busqueda)
        qs = qs.filter(reduce(and_, terminos))
    return qs


def _a_listado(fila: MovimientoModel) -> MovimientoListado:
    return MovimientoListado(
        id=fila.pk,
        fecha=fila.fecha,
        importe=fila.importe,
        concepto=fila.concepto,
        cuenta_id=fila.cuenta_id,
        cuenta_nombre=fila.cuenta.nombre,
        categoria_id=fila.categoria_id,
        categoria_nombre=fila.categoria.nombre if fila.categoria_id else None,
        categoria_color=fila.categoria.color if fila.categoria_id else None,
        comercio_id=fila.comercio_id,
        comercio_nombre=fila.comercio.nombre if fila.comercio_id else None,
        etiquetas=tuple(fila.etiquetas),
        notas=fila.notas,
        origen=fila.origen,
        revisado=fila.revisado,
        num_adjuntos=getattr(fila, "num_adjuntos", None),
        creado=fila.creado,
    )


def _categoria(nombre: str | None, padre: str | None) -> str | None:
    """Como la enseña la app (Categoria.__str__): «Padre › Hija» si es una subcategoría."""
    if nombre is None:
        return None
    return f"{padre} › {nombre}" if padre else nombre


class MovimientoQueryServiceORM(IMovimientoQueryService):
    @staticmethod
    def _del_hogar(hogar_id: int):
        return MovimientoModel.objects.filter(hogar_id=hogar_id).con_detalle()

    def listar(self, query: MovimientosQuery) -> Pagina[MovimientoListado]:
        qs = _filtrar(self._del_hogar(query.hogar_id), query.filtros).annotate(num_adjuntos=Count("adjuntos"))
        if isinstance(query.paginacion, PaginacionCursor):
            return paginacion.por_cursor(qs, query.paginacion, RECIENTES_PRIMERO, _a_listado)
        return paginacion.por_numero(qs.order_by(*(query.orden or RECIENTES_PRIMERO)), query.paginacion, _a_listado)

    def detalle(self, hogar_id: int, movimiento_id: int) -> MovimientoListado | None:
        fila = self._del_hogar(hogar_id).filter(pk=movimiento_id).first()
        return None if fila is None else _a_listado(fila)

    def exportar(self, query: MovimientosQuery) -> Iterator[MovimientoExportado]:
        qs = _filtrar(MovimientoModel.objects.filter(hogar_id=query.hogar_id), query.filtros)
        filas = qs.order_by(*(query.orden or RECIENTES_PRIMERO)).values_list(
            "fecha", "concepto", "importe", "cuenta__nombre", "categoria__nombre", "etiquetas"
        )
        for fecha, concepto, importe, cuenta, categoria, etiquetas in filas.iterator(chunk_size=2000):
            yield MovimientoExportado(fecha, concepto, importe, cuenta, categoria, tuple(etiquetas))

    # ── Lo que leen otras apps (módulo 88) ──
    def del_mes(self, hogar_id, mes):
        # {% regroup %} del informe agrupa elementos CONSECUTIVOS: ordenados por la categoría
        filas = (
            MovimientoModel.objects.filter(hogar_id=hogar_id)
            .del_mes(mes.inicio)
            .order_by("categoria__nombre", "categoria_id", "fecha", "id")
            .values_list(
                "pk",
                "fecha",
                "concepto",
                "importe",
                "cuenta__nombre",
                "categoria_id",
                "categoria__nombre",
                "categoria__padre__nombre",
            )
        )
        return [
            MovimientoDelMes(pk, fecha, concepto, importe, cuenta, categoria_id, _categoria(nombre, padre))
            for pk, fecha, concepto, importe, cuenta, categoria_id, nombre, padre in filas
        ]

    def huellas_existentes(self, cuenta_id, huellas):
        filas = MovimientoModel.objects.filter(cuenta_id=cuenta_id, huella__in=list(huellas))
        return set(filas.values_list("huella", flat=True))

    def sin_conciliar(self, cuenta_id, desde, hasta):
        filas = MovimientoModel.objects.filter(cuenta_id=cuenta_id, huella="", fecha__range=(desde, hasta))
        # el orden de siempre (Meta.ordering): a igual distancia, se empareja el mismo que en el módulo 75
        return [MovimientoSinConciliar(*fila) for fila in filas.values_list("pk", "fecha", "importe")]
