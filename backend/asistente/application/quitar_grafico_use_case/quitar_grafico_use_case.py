# asistente/application/quitar_grafico_use_case/quitar_grafico_use_case.py (módulo 97)
from asistente.application.quitar_grafico_use_case.dtos.quitar_grafico_input_dto import QuitarGraficoInputDTO
from asistente.application.quitar_grafico_use_case.i_quitar_grafico_use_case import IQuitarGraficoUseCase
from asistente.domain.repositories.i_grafico_fijado_command_repository import IGraficoFijadoCommandRepository
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol


class QuitarGraficoUseCase(IQuitarGraficoUseCase):
    rol_minimo = Rol.MIEMBRO

    def __init__(self, *, graficos: IGraficoFijadoCommandRepository, uow: IUnidadDeTrabajo):
        self.graficos, self.uow = graficos, uow

    def ejecutar(self, entrada: QuitarGraficoInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            self.graficos.eliminar(self.graficos.obtener(entrada.hogar_id, entrada.grafico_id))
