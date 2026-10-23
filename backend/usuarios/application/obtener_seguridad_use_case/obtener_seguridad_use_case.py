# usuarios/application/obtener_seguridad_use_case/obtener_seguridad_use_case.py — la pantalla «Seguridad» (módulo 92)
from usuarios.application.obtener_seguridad_use_case.dtos.obtener_seguridad_input_dto import ObtenerSeguridadInputDTO
from usuarios.application.obtener_seguridad_use_case.dtos.seguridad_output_dto import SeguridadOutputDTO
from usuarios.application.obtener_seguridad_use_case.i_obtener_seguridad_use_case import IObtenerSeguridadUseCase
from usuarios.domain.repositories.i_seguridad_query_service import ISeguridadQueryService


class ObtenerSeguridadUseCase(IObtenerSeguridadUseCase):
    """La verificación en dos pasos y las passkeys de MI cuenta."""

    def __init__(self, *, seguridad: ISeguridadQueryService):
        self.seguridad = seguridad

    def ejecutar(self, entrada: ObtenerSeguridadInputDTO) -> SeguridadOutputDTO:
        return SeguridadOutputDTO.desde_read_model(self.seguridad.de_usuario(entrada.usuario_id))
