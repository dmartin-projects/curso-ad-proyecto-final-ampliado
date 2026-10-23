# usuarios/application/obtener_acceso_use_case/obtener_acceso_use_case.py — «Métodos de acceso» (módulo 91)
from usuarios.application.obtener_acceso_use_case.dtos.acceso_output_dto import AccesoOutputDTO
from usuarios.application.obtener_acceso_use_case.dtos.obtener_acceso_input_dto import ObtenerAccesoInputDTO
from usuarios.application.obtener_acceso_use_case.i_obtener_acceso_use_case import IObtenerAccesoUseCase
from usuarios.domain.repositories.i_acceso_query_service import IAccesoQueryService


class ObtenerAccesoUseCase(IObtenerAccesoUseCase):
    """Las formas de entrar de MI cuenta: la contraseña (si tiene) y los proveedores vinculados."""

    def __init__(self, *, acceso: IAccesoQueryService):
        self.acceso = acceso

    def ejecutar(self, entrada: ObtenerAccesoInputDTO) -> AccesoOutputDTO:
        return AccesoOutputDTO.desde_read_model(self.acceso.de_usuario(entrada.usuario_id))
