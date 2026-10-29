# asistente/tests/fakes/consultas_de_finanzas_fake.py — IConsultasDeFinanzas en memoria (módulos 94 y 95)
from decimal import Decimal

from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.domain.read_models.gasto_de_categoria import GastoDeCategoria
from asistente.domain.read_models.resumen_del_mes import ResumenDelMes
from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.vo.mes import Mes


def resumen(mes: Mes, gastos="0", ingresos="0", categorias=(), num=0, anterior="0", pendientes=0) -> ResumenDelMes:
    gastos, ingresos, anterior = Decimal(gastos), Decimal(ingresos), Decimal(anterior)
    total = gastos or Decimal(1)
    return ResumenDelMes(
        mes=mes,
        gastos=gastos,
        ingresos=ingresos,
        balance=ingresos - gastos,
        num_movimientos=num,
        gastos_mes_anterior=anterior,
        variacion=round((gastos - anterior) * 100 / anterior, 1) if anterior else None,
        por_categoria=tuple(
            GastoDeCategoria(nombre, Decimal(t), round(Decimal(t) * 100 / total, 1)) for nombre, t in categorias
        ),
        pendientes_revision=pendientes,
    )


class ConsultasDeFinanzasFake(IConsultasDeFinanzas):
    """Los resúmenes de cada (hogar, mes); un mes sin datos, a cero. Como los use cases de verdad, exige LECTOR y
    apunta cada consulta (con su actor) para que los tests vean qué se pidió y en nombre de quién."""

    def __init__(self, resumenes: dict[tuple[int, Mes], ResumenDelMes] | None = None):
        self.resumenes = dict(resumenes or {})
        self.consultas: list[tuple] = []

    def resumen_del_mes(self, actor, hogar_id, mes):
        actor.exigir(Rol.LECTOR)
        self.consultas.append(("resumen_del_mes", actor, hogar_id, mes))
        if actor.usuario_id is None:
            raise SinPermisoException()
        return self.resumenes.get((hogar_id, mes)) or resumen(mes)
