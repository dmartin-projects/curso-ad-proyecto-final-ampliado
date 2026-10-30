# asistente/application/fijar_grafico_use_case/fijar_grafico_use_case.py (módulo 97)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.chat.artefactos import especificacion_a_datos, grafico_a_datos
from asistente.application.chat.calculadora_de_graficos import CalculadoraDeGraficos
from asistente.application.fijar_grafico_use_case.dtos.fijar_grafico_input_dto import FijarGraficoInputDTO
from asistente.application.fijar_grafico_use_case.i_fijar_grafico_use_case import IFijarGraficoUseCase
from asistente.application.ports.i_membresias import IMembresias
from asistente.application.shared.dtos.grafico_fijado_output_dto import GraficoFijadoOutputDTO
from asistente.domain.bo.grafico_fijado import GraficoFijado
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.repositories.i_grafico_fijado_command_repository import IGraficoFijadoCommandRepository
from asistente.domain.vo.especificacion_de_grafico import EspecificacionDeGrafico
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from core.domain.exceptions.validacion_exception import ValidacionException


class FijarGraficoUseCase(IFijarGraficoUseCase):
    # Cambia el dashboard de TODO el hogar: como cualquier otro cambio en él, un miembro (no un lector)
    rol_minimo = Rol.MIEMBRO

    def __init__(
        self,
        *,
        graficos: IGraficoFijadoCommandRepository,
        calculadora: CalculadoraDeGraficos,
        membresias: IMembresias,
        reloj: IReloj,
        uow: IUnidadDeTrabajo,
    ):
        self.graficos, self.calculadora, self.membresias = graficos, calculadora, membresias
        self.reloj, self.uow = reloj, uow

    def ejecutar(self, entrada: FijarGraficoInputDTO) -> GraficoFijadoOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        e = entrada.especificacion
        try:
            especificacion = EspecificacionDeGrafico(e["tipo"], e["titulo"], e["fuente"], dict(e.get("argumentos", {})))
        except (KeyError, ValueError) as error:  # ValueError: un tipo que no existe
            raise ValidacionException(
                f"Especificación de gráfico no válida: {error}", campo="especificacion"
            ) from error
        contexto = ContextoPregunta.abrir(
            usuario_id=entrada.actor.usuario_id, hogar_id=entrada.hogar_id, membresias=self.membresias, reloj=self.reloj
        )
        try:  # se calcula antes de fijarlo: un gráfico que no se puede dibujar no llega al dashboard
            grafico = self.calculadora.calcular(contexto, especificacion)
        except ToolException as error:
            raise ValidacionException(str(error), campo="especificacion") from error
        fijado = GraficoFijado(entrada.hogar_id, entrada.actor.usuario_id, especificacion)
        with self.uow:
            self.graficos.guardar(fijado)
        # fijado_por: None, lo acaba de fijar quien pide (al listar, sale su nombre)
        return GraficoFijadoOutputDTO(fijado.id, especificacion_a_datos(especificacion), None, grafico_a_datos(grafico))
