# finanzas/infrastructure/database/repositories/dashboard_query_service_orm.py — IDashboardQueryService con el ORM
# (módulos 77 y 87)
"""Datos del dashboard de un mes: agregaciones en la base de datos (nunca bucles en Python sobre movimientos).

El lado de LECTURA de CQRS: sin BOs ni command repositories, con todo el ORM (agregación condicional, ventanas,
subconsultas). Devuelve el read model del dominio (finanzas/domain/read_models/dashboard.py).
"""

from decimal import Decimal

from django.db.models import Count, F, Q, Sum, Window
from django.db.models.functions import Coalesce, TruncMonth

from core.domain.vo.mes import Mes
from finanzas.domain.read_models.categoria_del_mes import CategoriaDelMes
from finanzas.domain.read_models.comercio_del_mes import ComercioDelMes
from finanzas.domain.read_models.dashboard import Dashboard
from finanzas.domain.read_models.dia_del_mes import DiaDelMes
from finanzas.domain.read_models.mes_en_resumen import MesEnResumen
from finanzas.domain.read_models.presupuesto_del_mes import PresupuestoDelMes
from finanzas.domain.repositories.i_dashboard_query_service import IDashboardQueryService
from finanzas.domain.repositories.queries.dashboard_query import DashboardQuery
from finanzas.infrastructure.database.models.categoria_model import Categoria as CategoriaModel
from finanzas.infrastructure.database.models.movimiento_model import Movimiento as MovimientoModel
from finanzas.infrastructure.database.models.presupuesto_model import Presupuesto as PresupuestoModel

CERO = Decimal("0")


class DashboardQueryServiceORM(IDashboardQueryService):
    def resumen(self, query: DashboardQuery) -> Dashboard:
        hogar_id, mes = query.hogar_id, query.mes
        del_mes = MovimientoModel.objects.filter(hogar_id=hogar_id).del_mes(mes)
        t = self._totales(hogar_id, mes)
        gastos, gastos_antes = -t["gastos"], -t["gastos_antes"]
        return Dashboard(
            mes=mes.inicio,
            gastos=gastos,
            ingresos=t["ingresos"],
            balance=t["ingresos"] - gastos,
            num_movimientos=t["num"],
            gastos_mes_anterior=gastos_antes,
            variacion=round((gastos - gastos_antes) * 100 / gastos_antes, 1) if gastos_antes else None,
            por_categoria=self._por_categoria(del_mes),
            acumulado=self._acumulado_diario(del_mes),
            evolucion=self._evolucion(hogar_id, mes),
            top_comercios=[
                ComercioDelMes(**fila)
                for fila in del_mes.gastos()
                .filter(comercio__isnull=False)
                .values("comercio", nombre=F("comercio__nombre"))
                .annotate(total=-Sum("importe"), veces=Count("id"))
                .order_by("-total")[:5]
            ],
            presupuestos=[
                PresupuestoDelMes(
                    categoria=p.categoria.nombre,
                    importe=p.importe,
                    gastado=-p.gastado,
                    porcentaje=int(-p.gastado * 100 / p.importe),
                )
                for p in PresupuestoModel.objects.filter(hogar_id=hogar_id, mes=mes.inicio)
                .con_gastado()
                .select_related("categoria")
            ],
            pendientes_revision=MovimientoModel.objects.filter(hogar_id=hogar_id).pendientes_revision().count(),
        )

    @staticmethod
    def _totales(hogar_id: int, mes: Mes) -> dict:
        """Totales del mes y del anterior en UNA consulta: agregación condicional (Sum(..., filter=Q(...)), módulo 07)."""
        este_mes, mes_previo = Q(fecha__gte=mes.inicio), Q(fecha__lt=mes.inicio)
        return (
            MovimientoModel.objects.filter(hogar_id=hogar_id)
            .filter(fecha__gte=mes.anterior().inicio, fecha__lt=mes.fin)  # el índice (hogar, -fecha) acota a dos meses
            .aggregate(
                gastos=Coalesce(Sum("importe", filter=este_mes & Q(importe__lt=0)), CERO),
                ingresos=Coalesce(Sum("importe", filter=este_mes & Q(importe__gt=0)), CERO),
                num=Count("id", filter=este_mes),
                gastos_antes=Coalesce(Sum("importe", filter=mes_previo & Q(importe__lt=0)), CERO),
            )
        )

    @staticmethod
    def _por_categoria(movimientos) -> list[CategoriaDelMes]:
        """Gasto por categoría PRINCIPAL: las subcategorías suman en su padre (Coalesce(padre, categoría))."""
        filas = (
            movimientos.gastos()
            .annotate(principal=Coalesce("categoria__padre", "categoria"))
            .values("principal")
            .annotate(total=Sum("importe"))
            .order_by("total")  # negativos: el mayor gasto primero
        )
        principales = [f["principal"] for f in filas if f["principal"]]
        nombres = {c.pk: c for c in CategoriaModel.objects.filter(pk__in=principales)}
        total = sum(f["total"] for f in filas) or Decimal("1")
        return [
            CategoriaDelMes(
                categoria=f["principal"],
                nombre=nombres[f["principal"]].nombre if f["principal"] else "Sin categoría",
                color=nombres[f["principal"]].color if f["principal"] else "#9e9e9e",
                total=-f["total"],
                porcentaje=round(f["total"] * 100 / total, 1),
            )
            for f in filas
        ]

    @staticmethod
    def _acumulado_diario(movimientos) -> list[DiaDelMes]:
        """Gasto de cada día y acumulado del mes con funciones de ventana (módulo 11).

        Ventana con marco RANGE (el de por defecto con ORDER BY): las filas del mismo día son "pares" y
        comparten el acumulado del final del día. Por eso basta un DISTINCT sobre (fecha, dia, acumulado).
        """
        filas = (
            movimientos.gastos()
            .annotate(
                dia=Window(Sum("importe"), partition_by=[F("fecha")]),
                acumulado=Window(Sum("importe"), order_by=F("fecha").asc()),
            )
            .values("fecha", "dia", "acumulado")
            .order_by("fecha")
            .distinct()
        )
        return [DiaDelMes(fecha=f["fecha"], gasto=-f["dia"], acumulado=-f["acumulado"]) for f in filas]

    @staticmethod
    def _evolucion(hogar_id: int, hasta: Mes, meses: int = 12) -> list[MesEnResumen]:
        periodo = hasta.ultimos(meses)
        filas = (
            MovimientoModel.objects.filter(hogar_id=hogar_id)
            .filter(fecha__gte=periodo[0].inicio, fecha__lt=hasta.fin)
            .annotate(mes=TruncMonth("fecha"))
            .values("mes")
            .annotate(
                gastos=Coalesce(Sum("importe", filter=Q(importe__lt=0)), CERO),
                ingresos=Coalesce(Sum("importe", filter=Q(importe__gt=0)), CERO),
            )
            .order_by("mes")
        )
        por_mes = {f["mes"]: f for f in filas}
        vacio = {"gastos": CERO, "ingresos": CERO}  # los meses sin movimientos, a cero: el gráfico necesita los 12
        return [
            MesEnResumen(
                mes=m.inicio,
                gastos=-por_mes.get(m.inicio, vacio)["gastos"],
                ingresos=por_mes.get(m.inicio, vacio)["ingresos"],
            )
            for m in periodo
        ]
