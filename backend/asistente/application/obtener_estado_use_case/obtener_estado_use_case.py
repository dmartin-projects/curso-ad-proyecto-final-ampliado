# asistente/application/obtener_estado_use_case/obtener_estado_use_case.py (módulo 107)
"""Para la interfaz: si el asistente está, y si no, por qué. El chat lo pregunta al abrirse y deja de ofrecer lo que no
puede hacer (en vez de dejar escribir una pregunta que va a fallar)."""

from asistente.application.obtener_estado_use_case.dtos.obtener_estado_input_dto import ObtenerEstadoInputDTO
from asistente.application.obtener_estado_use_case.i_obtener_estado_use_case import IObtenerEstadoUseCase
from asistente.application.ports.i_estado_del_asistente import IEstadoDelAsistente
from core.domain.enums.rol import Rol


class ObtenerEstadoUseCase(IObtenerEstadoUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, estado: IEstadoDelAsistente):
        self.estado = estado

    def ejecutar(self, entrada: ObtenerEstadoInputDTO):
        entrada.actor.exigir(self.rol_minimo)
        return self.estado.estado()
