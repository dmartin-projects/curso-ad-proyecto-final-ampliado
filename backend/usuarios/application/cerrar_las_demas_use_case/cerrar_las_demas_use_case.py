# usuarios/application/cerrar_las_demas_use_case/cerrar_las_demas_use_case.py — cerrar todas mis sesiones menos esta (módulo 92)
from usuarios.application.cerrar_las_demas_use_case.dtos.cerrar_las_demas_input_dto import CerrarLasDemasInputDTO
from usuarios.application.cerrar_las_demas_use_case.i_cerrar_las_demas_use_case import ICerrarLasDemasUseCase
from usuarios.application.ports.i_sesiones import ISesiones


class CerrarLasDemasUseCase(ICerrarLasDemasUseCase):
    def __init__(self, *, sesiones: ISesiones):
        self.sesiones = sesiones

    def ejecutar(self, entrada: CerrarLasDemasInputDTO) -> int:
        return self.sesiones.cerrar_las_demas(entrada.usuario_id, entrada.sid)
