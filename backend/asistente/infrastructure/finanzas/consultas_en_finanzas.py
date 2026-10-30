# asistente/infrastructure/finanzas/consultas_en_finanzas.py — IConsultasDeFinanzas con los use cases de finanzas
# (módulos 94, 95 y 97)
#
# Anti-corruption layer: llama a los use cases de CONSULTA de finanzas, por su container y con el Actor de quien
# pregunta (sus permisos por hogar se aplican solos), y traduce sus OutputDTOs a los read models del asistente.
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.domain.read_models.categoria_del_hogar import CategoriaDelHogar
from asistente.domain.read_models.cuenta_del_hogar import CuentaDelHogar
from asistente.domain.read_models.estado_de_presupuesto import EstadoDePresupuesto
from asistente.domain.read_models.gasto_de_categoria import GastoDeCategoria
from asistente.domain.read_models.gasto_de_comercio import GastoDeComercio
from asistente.domain.read_models.gasto_del_dia import GastoDelDia
from asistente.domain.read_models.mes_resumido import MesResumido
from asistente.domain.read_models.movimiento_encontrado import MovimientoEncontrado
from asistente.domain.read_models.movimientos_encontrados import MovimientosEncontrados
from asistente.domain.read_models.resumen_del_mes import ResumenDelMes
from core.domain.repositories.queries.paginacion_cursor import PaginacionCursor
from core.domain.vo.mes import Mes
from finanzas.application.listar_categorias_use_case.dtos.listar_categorias_input_dto import ListarCategoriasInputDTO
from finanzas.application.listar_cuentas_use_case.dtos.listar_cuentas_input_dto import ListarCuentasInputDTO
from finanzas.application.listar_movimientos_use_case.dtos.listar_movimientos_input_dto import ListarMovimientosInputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.obtener_dashboard_input_dto import ObtenerDashboardInputDTO
from finanzas.application.obtener_totales_movimientos_use_case.dtos.obtener_totales_movimientos_input_dto import (
    ObtenerTotalesMovimientosInputDTO,
)
from finanzas.domain.repositories.queries.filtros_movimientos_query import FiltrosMovimientosQuery
from finanzas.infrastructure import container as finanzas


class ConsultasEnFinanzas(IConsultasDeFinanzas):
    def resumen_del_mes(self, actor, hogar_id, mes):
        d = finanzas.obtener_dashboard().ejecutar(ObtenerDashboardInputDTO(hogar_id=hogar_id, actor=actor, mes=mes))
        return ResumenDelMes(
            mes=mes,
            gastos=d.gastos,
            ingresos=d.ingresos,
            balance=d.balance,
            num_movimientos=d.num_movimientos,
            gastos_mes_anterior=d.gastos_mes_anterior,
            variacion=d.variacion,
            por_categoria=tuple(GastoDeCategoria(c.nombre, c.total, c.porcentaje) for c in d.por_categoria),
            pendientes_revision=d.pendientes_revision,
            top_comercios=tuple(GastoDeComercio(c.nombre, c.total, c.veces) for c in d.top_comercios),
            presupuestos=tuple(
                EstadoDePresupuesto(p.categoria, p.importe, p.gastado, p.porcentaje) for p in d.presupuestos
            ),
            evolucion=tuple(MesResumido(Mes.de(m.mes), m.gastos, m.ingresos) for m in d.evolucion),
            por_dia=tuple(GastoDelDia(x.fecha, x.gasto, x.acumulado) for x in d.acumulado),
        )

    def movimientos(self, actor, hogar_id, filtro, limite):
        filtros = FiltrosMovimientosQuery(
            fecha_desde=filtro.desde,
            fecha_hasta=filtro.hasta,
            categorias=(filtro.categoria_id,) if filtro.categoria_id is not None else (),
            tipo=filtro.tipo,
            busqueda=tuple(filtro.texto.split()) if filtro.texto else (),  # como el ?search= de la API
        )
        t = finanzas.obtener_totales_movimientos().ejecutar(ObtenerTotalesMovimientosInputDTO(hogar_id, actor, filtros))
        primeros = ()
        if limite:  # los más recientes, en una página por cursor (sin contar la tabla: el total ya lo tenemos)
            entrada = ListarMovimientosInputDTO(hogar_id, actor, filtros, paginacion=PaginacionCursor(tamano=limite))
            pagina = finanzas.listar_movimientos().ejecutar(entrada)
            primeros = tuple(
                MovimientoEncontrado(m.fecha, m.importe, m.concepto, m.categoria_nombre, m.comercio_nombre)
                for m in pagina.results
            )
        return MovimientosEncontrados(total=t.num, gastos=t.gastos, ingresos=t.ingresos, primeros=primeros)

    def categorias(self, actor, hogar_id):
        todas = finanzas.listar_categorias().ejecutar(ListarCategoriasInputDTO(hogar_id, actor))
        nombres = {c.id: c.nombre for c in todas}
        return tuple(CategoriaDelHogar(c.id, c.nombre, nombres.get(c.padre_id), c.es_ingreso) for c in todas)

    def cuentas(self, actor, hogar_id):
        leidas = finanzas.listar_cuentas().ejecutar(ListarCuentasInputDTO(hogar_id, actor, orden=("nombre",)))
        return tuple(CuentaDelHogar(c.id, c.nombre, c.tipo, c.activa, c.saldo) for c in leidas)
