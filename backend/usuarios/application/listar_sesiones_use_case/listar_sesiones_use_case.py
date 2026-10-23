# usuarios/application/listar_sesiones_use_case/listar_sesiones_use_case.py — las sesiones abiertas de MI cuenta (módulo 92)
from usuarios.application.listar_sesiones_use_case.dtos.listar_sesiones_input_dto import ListarSesionesInputDTO
from usuarios.application.listar_sesiones_use_case.dtos.sesion_activa_output_dto import SesionActivaOutputDTO
from usuarios.application.listar_sesiones_use_case.i_listar_sesiones_use_case import IListarSesionesUseCase
from usuarios.domain.repositories.i_sesion_activa_query_service import ISesionActivaQueryService


class ListarSesionesUseCase(IListarSesionesUseCase):
    def __init__(self, *, sesiones: ISesionActivaQueryService):
        self.sesiones = sesiones

    def ejecutar(self, entrada: ListarSesionesInputDTO) -> list[SesionActivaOutputDTO]:
        filas = self.sesiones.de_usuario(entrada.usuario_id, entrada.sid_actual)
        return [SesionActivaOutputDTO.desde_read_model(s) for s in filas]
