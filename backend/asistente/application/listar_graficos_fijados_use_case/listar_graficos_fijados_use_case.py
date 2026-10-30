# asistente/application/listar_graficos_fijados_use_case/listar_graficos_fijados_use_case.py (módulo 97)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.chat.artefactos import especificacion_a_datos, grafico_a_datos
from asistente.application.chat.calculadora_de_graficos import CalculadoraDeGraficos
from asistente.application.listar_graficos_fijados_use_case.dtos.listar_graficos_fijados_input_dto import (
    ListarGraficosFijadosInputDTO,
)
from asistente.application.listar_graficos_fijados_use_case.i_listar_graficos_fijados_use_case import (
    IListarGraficosFijadosUseCase,
)
from asistente.application.ports.i_membresias import IMembresias
from asistente.application.shared.dtos.grafico_fijado_output_dto import GraficoFijadoOutputDTO
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.repositories.i_grafico_fijado_query_service import IGraficoFijadoQueryService
from core.application.ports.i_reloj import IReloj
from core.domain.enums.rol import Rol


class ListarGraficosFijadosUseCase(IListarGraficosFijadosUseCase):
    """Los gráficos se recalculan al mirarlos, con el contexto de QUIEN MIRA: su Actor (lector, como el agente) y su
    "hoy". "Los últimos 6 meses" fijado en septiembre enseña en noviembre los 6 meses hasta noviembre. Si uno ya no se
    puede calcular (una categoría que se borró), sale con su motivo en vez de tumbar el dashboard."""

    rol_minimo = Rol.LECTOR

    def __init__(
        self,
        *,
        consultas: IGraficoFijadoQueryService,
        calculadora: CalculadoraDeGraficos,
        membresias: IMembresias,
        reloj: IReloj,
    ):
        self.consultas, self.calculadora, self.membresias, self.reloj = consultas, calculadora, membresias, reloj

    def ejecutar(self, entrada: ListarGraficosFijadosInputDTO) -> list[GraficoFijadoOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        fijados = self.consultas.listar(entrada.hogar_id)
        if not fijados:
            return []
        contexto = ContextoPregunta.abrir(
            usuario_id=entrada.actor.usuario_id, hogar_id=entrada.hogar_id, membresias=self.membresias, reloj=self.reloj
        )
        salida = []
        for f in fijados:
            grafico, error = None, None
            try:
                grafico = grafico_a_datos(self.calculadora.calcular(contexto, f.especificacion))
            except ToolException as e:
                error = str(e)
            salida.append(
                GraficoFijadoOutputDTO(f.id, especificacion_a_datos(f.especificacion), f.fijado_por, grafico, error)
            )
        return salida
