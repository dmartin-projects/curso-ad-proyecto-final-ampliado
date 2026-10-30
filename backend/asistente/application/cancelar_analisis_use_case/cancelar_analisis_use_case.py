# asistente/application/cancelar_analisis_use_case/cancelar_analisis_use_case.py (ejercicio 1 del 105)
"""Cancelar es pedir que pare: el worker lo mira entre especialista y especialista (ObservadorDelAnalisis). No se mata
la tarea (`revoke(terminate=True)`): a medias, no anotaría lo gastado ni avisaría a la persona."""

from asistente.application.cancelar_analisis_use_case.dtos.cancelar_analisis_input_dto import CancelarAnalisisInputDTO
from asistente.application.cancelar_analisis_use_case.i_cancelar_analisis_use_case import ICancelarAnalisisUseCase
from asistente.application.ports.i_control_de_analisis import IControlDeAnalisis
from core.domain.enums.rol import Rol


class CancelarAnalisisUseCase(ICancelarAnalisisUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, control: IControlDeAnalisis):
        self.control = control

    def ejecutar(self, entrada: CancelarAnalisisInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        self.control.cancelar(entrada.actor.usuario_id, entrada.tarea)  # solo los de esa persona
