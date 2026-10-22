# backoffice/application/obtener_usuario_soporte_use_case/obtener_usuario_soporte_use_case.py (módulo 88)
from backoffice.application.obtener_usuario_soporte_use_case.dtos.obtener_usuario_soporte_input_dto import (
    ObtenerUsuarioSoporteInputDTO,
)
from backoffice.application.obtener_usuario_soporte_use_case.i_obtener_usuario_soporte_use_case import (
    IObtenerUsuarioSoporteUseCase,
)
from backoffice.application.shared.dtos.usuario_soporte_output_dto import UsuarioSoporteOutputDTO
from backoffice.domain.repositories.i_usuario_soporte_query_service import IUsuarioSoporteQueryService


class ObtenerUsuarioSoporteUseCase(IObtenerUsuarioSoporteUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, usuarios: IUsuarioSoporteQueryService):
        self.usuarios = usuarios

    def ejecutar(self, entrada: ObtenerUsuarioSoporteInputDTO) -> UsuarioSoporteOutputDTO | None:
        leido = self.usuarios.detalle(entrada.usuario_id)
        return None if leido is None else UsuarioSoporteOutputDTO.desde_read_model(leido)
