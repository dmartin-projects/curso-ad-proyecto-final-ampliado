# asistente/application/listar_carpetas_use_case/listar_carpetas_use_case.py (módulo 97)
from asistente.application.listar_carpetas_use_case.dtos.listar_carpetas_input_dto import ListarCarpetasInputDTO
from asistente.application.listar_carpetas_use_case.i_listar_carpetas_use_case import IListarCarpetasUseCase
from asistente.application.shared.dtos.carpeta_output_dto import CarpetaOutputDTO
from asistente.domain.repositories.i_conversacion_query_service import IConversacionQueryService
from core.domain.enums.rol import Rol


class ListarCarpetasUseCase(IListarCarpetasUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, consultas: IConversacionQueryService):
        self.consultas = consultas

    def ejecutar(self, entrada: ListarCarpetasInputDTO) -> list[CarpetaOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        return [
            CarpetaOutputDTO.desde_read_model(c)
            for c in self.consultas.carpetas(entrada.actor.usuario_id, entrada.hogar_id)
        ]
