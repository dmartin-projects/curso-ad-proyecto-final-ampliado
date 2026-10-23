# usuarios/application/cerrar_sesion_use_case/cerrar_sesion_use_case.py — cerrar una sesión de MI cuenta (módulo 92)
from usuarios.application.cerrar_sesion_use_case.dtos.cerrar_sesion_input_dto import CerrarSesionInputDTO
from usuarios.application.cerrar_sesion_use_case.i_cerrar_sesion_use_case import ICerrarSesionUseCase
from usuarios.application.ports.i_sesiones import ISesiones


class CerrarSesionUseCase(ICerrarSesionUseCase):
    def __init__(self, *, sesiones: ISesiones):
        self.sesiones = sesiones

    def ejecutar(self, entrada: CerrarSesionInputDTO) -> None:
        self.sesiones.cerrar(entrada.usuario_id, entrada.sid)  # SesionNoEncontradaException si no es suya
