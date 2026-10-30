# asistente/tests/fakes/consultas_de_finanzas_fake.py — IConsultasDeFinanzas en memoria (módulos 94, 95 y 97)
from datetime import date
from decimal import Decimal

from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.domain.read_models.categoria_del_hogar import CategoriaDelHogar
from asistente.domain.read_models.cuenta_del_hogar import CuentaDelHogar
from asistente.domain.read_models.gasto_de_categoria import GastoDeCategoria
from asistente.domain.read_models.movimiento_encontrado import MovimientoEncontrado
from asistente.domain.read_models.movimientos_encontrados import MovimientosEncontrados
from asistente.domain.read_models.resumen_del_mes import ResumenDelMes
from asistente.tests.fakes import casa
from core.domain.enums.rol import Rol
from core.domain.vo.mes import Mes


def resumen(
    mes: Mes, gastos="0", ingresos="0", categorias=(), num=0, anterior="0", pendientes=0, **resto
) -> ResumenDelMes:
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
        **resto,
    )


class ConsultasDeFinanzasFake(IConsultasDeFinanzas):
    """Los resúmenes de cada (hogar, mes), y los movimientos y categorías de cada hogar; lo que no se le da, vacío.
    Como los use cases de verdad, exige LECTOR y apunta cada consulta (con su actor) para los tests."""

    def __init__(self, resumenes: dict[tuple[int, Mes], ResumenDelMes] | None = None):
        self.resumenes = dict(resumenes or {})
        self.categorias_por_hogar: dict[int, tuple[CategoriaDelHogar, ...]] = {}
        self.movimientos_por_hogar: dict[int, list[tuple]] = {}  # (fecha, importe, concepto, categoría, comercio)
        self.cuentas_por_hogar: dict[int, tuple[CuentaDelHogar, ...]] = {}
        self.consultas: list[tuple] = []

    @classmethod
    def de_casa(cls, hogar_id: int) -> "ConsultasDeFinanzasFake":
        """Las categorías y los movimientos de fakes/casa.py, los mismos que la fixture `casa` escribe en la BD."""
        fake = cls()
        ids = {nombre: i for i, (nombre, *_) in enumerate(casa.CATEGORIAS, start=1)}
        fake.categorias_por_hogar[hogar_id] = tuple(  # ordenadas por nombre, como las devuelve finanzas
            CategoriaDelHogar(ids[nombre], nombre, padre, es_ingreso)
            for nombre, padre, es_ingreso in sorted(casa.CATEGORIAS)
        )
        fake.movimientos_por_hogar[hogar_id] = [
            (date.fromisoformat(f), Decimal(i), concepto, categoria, comercio)
            for f, i, concepto, categoria, comercio in casa.MOVIMIENTOS
        ]
        saldo = sum((Decimal(i) for _, i, *_ in casa.MOVIMIENTOS), Decimal(0))
        fake.cuentas_por_hogar[hogar_id] = (CuentaDelHogar(1, casa.CUENTA, "banco", True, saldo),)
        return fake

    def resumen_del_mes(self, actor, hogar_id, mes):
        actor.exigir(Rol.LECTOR)
        self.consultas.append(("resumen_del_mes", actor, hogar_id, mes))
        return self.resumenes.get((hogar_id, mes)) or resumen(mes)

    def movimientos(self, actor, hogar_id, filtro, limite):
        actor.exigir(Rol.LECTOR)
        self.consultas.append(("movimientos", actor, hogar_id, filtro, limite))
        categorias = {c.id: c for c in self.categorias_por_hogar.get(hogar_id, ())}
        incluidas = set()
        if filtro.categoria_id is not None and filtro.categoria_id in categorias:
            elegida = categorias[filtro.categoria_id].nombre  # una principal incluye a sus hijas, como en finanzas
            incluidas = {c.nombre for c in categorias.values() if elegida in (c.nombre, c.padre)}
        encontrados = sorted(
            (
                m
                for m in self.movimientos_por_hogar.get(hogar_id, [])
                if filtro.desde <= m[0] <= filtro.hasta
                and (filtro.categoria_id is None or m[3] in incluidas)
                and (filtro.tipo is None or (m[1] < 0) == (filtro.tipo == "gasto"))
                and (
                    not filtro.texto
                    or all(t.casefold() in f"{m[2]} {m[4] or ''}".casefold() for t in filtro.texto.split())
                )
            ),
            key=lambda m: m[0],
            reverse=True,
        )
        return MovimientosEncontrados(
            total=len(encontrados),
            gastos=-sum((m[1] for m in encontrados if m[1] < 0), Decimal(0)),
            ingresos=sum((m[1] for m in encontrados if m[1] > 0), Decimal(0)),
            primeros=tuple(MovimientoEncontrado(*m) for m in encontrados[:limite]),
        )

    def categorias(self, actor, hogar_id):
        actor.exigir(Rol.LECTOR)
        return self.categorias_por_hogar.get(hogar_id, ())

    def cuentas(self, actor, hogar_id):
        actor.exigir(Rol.LECTOR)
        return self.cuentas_por_hogar.get(hogar_id, ())
