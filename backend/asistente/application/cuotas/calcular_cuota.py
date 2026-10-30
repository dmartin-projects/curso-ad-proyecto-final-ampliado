# asistente/application/cuotas/calcular_cuota.py — cuánto lleva gastado alguien, según su plan (módulo 98)
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_tarifas import ITarifas
from asistente.domain.repositories.i_consumo_query_service import IConsumoQueryService
from asistente.domain.repositories.i_plan_del_hogar_repository import IPlanDelHogarRepository
from asistente.domain.vo.estado_de_cuota import EstadoDeCuota


def calcular_cuota(
    contexto: ContextoPregunta,
    ahora: datetime,
    *,
    planes: IPlanDelHogarRepository,
    tarifas: ITarifas,
    consumos: IConsumoQueryService,
) -> EstadoDeCuota:
    """El día y el mes son los del HOGAR (su zona horaria, como "este mes" en las tools): "vuelve mañana" significa
    mañana para quien lo lee, no a la una de la madrugada porque el servidor está en UTC."""
    zona = ZoneInfo(contexto.hogar.zona_horaria)
    hoy = ahora.astimezone(zona).date()
    plan = planes.plan_de(contexto.hogar.id)
    return EstadoDeCuota(
        plan=plan,
        cuota=tarifas.cuota(plan),
        tokens_hoy=consumos.tokens(contexto.usuario_id, contexto.hogar.id, _medianoche(hoy, zona)),
        coste_mes=consumos.coste(contexto.hogar.id, _medianoche(hoy.replace(day=1), zona)),
        manana=_medianoche(hoy + timedelta(days=1), zona),
        mes_siguiente=_medianoche((hoy.replace(day=1) + timedelta(days=32)).replace(day=1), zona),
    )


def _medianoche(dia: date, zona: ZoneInfo) -> datetime:
    """Las 00:00 de ese día allí (con su cambio de hora, si lo hay: no se suma 24 h a la de hoy)."""
    return datetime(dia.year, dia.month, dia.day, tzinfo=zona)
