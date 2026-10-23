# usuarios/application/comprobar_autenticacion_reciente_use_case/comprobar_autenticacion_reciente_use_case.py — ¿se autenticó esta sesión hace poco? (step-up) (módulo 92)
from core.application.ports.i_reloj import IReloj
from usuarios.application.comprobar_autenticacion_reciente_use_case.dtos.comprobar_autenticacion_reciente_input_dto import (
    ComprobarAutenticacionRecienteInputDTO,
)
from usuarios.application.comprobar_autenticacion_reciente_use_case.i_comprobar_autenticacion_reciente_use_case import (
    IComprobarAutenticacionRecienteUseCase,
)
from usuarios.application.ports.i_sesiones import ISesiones


class ComprobarAutenticacionRecienteUseCase(IComprobarAutenticacionRecienteUseCase):
    def __init__(self, *, sesiones: ISesiones, reloj: IReloj):
        self.sesiones, self.reloj = sesiones, reloj

    def ejecutar(self, entrada: ComprobarAutenticacionRecienteInputDTO) -> bool:
        autenticacion = self.sesiones.autenticacion(entrada.sid) if entrada.sid else None
        return autenticacion is not None and autenticacion.reciente(self.reloj.ahora(), entrada.segundos)
