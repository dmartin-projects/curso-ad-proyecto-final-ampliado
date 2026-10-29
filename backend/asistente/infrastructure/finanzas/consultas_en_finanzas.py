# asistente/infrastructure/finanzas/consultas_en_finanzas.py — IConsultasDeFinanzas con los use cases de finanzas (módulo 94)
#
# Anti-corruption layer: llama a los use cases de CONSULTA de finanzas, por su container y con el Actor de quien
# pregunta (sus permisos por hogar se aplican solos), y traduce sus OutputDTOs a los read models del asistente.
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.domain.read_models.gasto_de_categoria import GastoDeCategoria
from asistente.domain.read_models.resumen_del_mes import ResumenDelMes
from finanzas.application.obtener_dashboard_use_case.dtos.obtener_dashboard_input_dto import ObtenerDashboardInputDTO
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
        )
