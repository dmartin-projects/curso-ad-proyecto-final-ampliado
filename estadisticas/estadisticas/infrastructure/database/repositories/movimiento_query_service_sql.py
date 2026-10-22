# estadisticas/infrastructure/database/repositories/movimiento_query_service_sql.py — IMovimientoQueryService con
# SQLAlchemy (módulo 89; las consultas, del módulo 85)
#
# SQLAlchemy agrupa y suma en PostgreSQL y devuelve read models del dominio. La aritmética de fechas (qué meses,
# cuántos martes, hasta hoy) es del dominio (domain/vo/periodo.py), que se prueba sin base de datos.
from decimal import Decimal

from sqlalchemy import Integer, case, cast, extract, func, select
from sqlalchemy.orm import Session

from estadisticas.domain.read_models.mes_de_tendencia import MesDeTendencia
from estadisticas.domain.read_models.mes_sin_revisar import MesSinRevisar
from estadisticas.domain.repositories.i_movimiento_query_service import IMovimientoQueryService
from estadisticas.domain.repositories.queries.periodo_del_hogar_query import PeriodoDelHogarQuery
from estadisticas.domain.vo.mes import Mes
from estadisticas.infrastructure.database.models.movimiento_model import MovimientoModel

_mes = func.date_trunc("month", MovimientoModel.fecha).label("mes")
_gastos = func.coalesce(func.sum(case((MovimientoModel.importe < 0, -MovimientoModel.importe), else_=0)), 0)


def _en_periodo(query: PeriodoDelHogarQuery):
    return (
        MovimientoModel.hogar_id == query.hogar_id,
        MovimientoModel.fecha >= query.periodo.desde,
        MovimientoModel.fecha < query.periodo.antes_de,
    )


class MovimientoQueryServiceSQL(IMovimientoQueryService):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def tendencia(self, query: PeriodoDelHogarQuery) -> list[MesDeTendencia]:
        ingresos = func.coalesce(func.sum(case((MovimientoModel.importe > 0, MovimientoModel.importe), else_=0)), 0)
        filas = self.sesion.execute(select(_mes, _gastos, ingresos).where(*_en_periodo(query)).group_by(_mes)).all()
        por_mes = {Mes.de(f.mes): (Decimal(f[1]), Decimal(f[2])) for f in filas}
        meses = []
        for m in query.periodo.meses():  # todos los meses, también los que no tienen movimientos (para el gráfico)
            gastos, ingresos = por_mes.get(m, (Decimal("0"), Decimal("0")))
            meses.append(MesDeTendencia(mes=str(m), gastos=gastos, ingresos=ingresos, ahorro=ingresos - gastos))
        return meses

    def gasto_por_dia_de_la_semana(self, query: PeriodoDelHogarQuery) -> dict[int, Decimal]:
        dia = cast(extract("isodow", MovimientoModel.fecha), Integer).label("dia")
        return dict(
            self.sesion.execute(
                select(dia, func.sum(-MovimientoModel.importe))
                .where(*_en_periodo(query), MovimientoModel.importe < 0)
                .group_by(dia)
            ).all()
        )

    def sin_revisar(self, query: PeriodoDelHogarQuery) -> list[MesSinRevisar]:
        filas = self.sesion.execute(
            select(_mes, func.count(), _gastos)
            .where(*_en_periodo(query), MovimientoModel.revisado.is_(False))
            .group_by(_mes)
        ).all()
        por_mes = {Mes.de(f.mes): (f[1], Decimal(f[2])) for f in filas}
        meses = []
        for m in query.periodo.meses():
            n, gastos = por_mes.get(m, (0, Decimal("0")))
            meses.append(MesSinRevisar(mes=str(m), movimientos=n, gastos=gastos))
        return meses
