# usuarios/application/obtener_autenticacion_use_case/obtener_autenticacion_use_case.py — cómo y cuándo se autenticó una sesión abierta (módulo 92)
from usuarios.application.obtener_autenticacion_use_case.dtos.obtener_autenticacion_input_dto import (
    ObtenerAutenticacionInputDTO,
)
from usuarios.application.obtener_autenticacion_use_case.i_obtener_autenticacion_use_case import (
    IObtenerAutenticacionUseCase,
)
from usuarios.application.ports.i_sesiones import ISesiones
from usuarios.application.shared.dtos.autenticacion_output_dto import AutenticacionOutputDTO


class ObtenerAutenticacionUseCase(IObtenerAutenticacionUseCase):
    """None si la sesión está cerrada, ha caducado o no existe (el authorization server lo usa para saber si su
    sesión de Django sigue viva)."""

    def __init__(self, *, sesiones: ISesiones):
        self.sesiones = sesiones

    def ejecutar(self, entrada: ObtenerAutenticacionInputDTO) -> AutenticacionOutputDTO | None:
        autenticacion = self.sesiones.autenticacion(entrada.sid)
        return AutenticacionOutputDTO.desde_vo(autenticacion) if autenticacion is not None else None
