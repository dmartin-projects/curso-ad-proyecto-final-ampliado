# backoffice/application/listar_usuarios_soporte_use_case/listar_usuarios_soporte_use_case.py (módulo 88)
from backoffice.application.listar_usuarios_soporte_use_case.dtos.listar_usuarios_soporte_input_dto import (
    ListarUsuariosSoporteInputDTO,
)
from backoffice.application.listar_usuarios_soporte_use_case.i_listar_usuarios_soporte_use_case import (
    IListarUsuariosSoporteUseCase,
)
from backoffice.application.shared.dtos.usuario_soporte_output_dto import UsuarioSoporteOutputDTO
from backoffice.domain.repositories.i_usuario_soporte_query_service import IUsuarioSoporteQueryService
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class ListarUsuariosSoporteUseCase(IListarUsuariosSoporteUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, usuarios: IUsuarioSoporteQueryService):
        self.usuarios = usuarios

    def ejecutar(self, entrada: ListarUsuariosSoporteInputDTO) -> PaginaOutputDTO[UsuarioSoporteOutputDTO]:
        return PaginaOutputDTO.desde_pagina(
            self.usuarios.listar(entrada.query), UsuarioSoporteOutputDTO.desde_read_model
        )
