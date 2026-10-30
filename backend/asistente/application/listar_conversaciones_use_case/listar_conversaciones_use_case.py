# asistente/application/listar_conversaciones_use_case/listar_conversaciones_use_case.py (módulo 97)
from asistente.application.listar_conversaciones_use_case.dtos.listar_conversaciones_input_dto import (
    ListarConversacionesInputDTO,
)
from asistente.application.listar_conversaciones_use_case.i_listar_conversaciones_use_case import (
    IListarConversacionesUseCase,
)
from asistente.application.shared.dtos.conversacion_output_dto import ConversacionOutputDTO
from asistente.domain.repositories.i_conversacion_query_service import IConversacionQueryService
from core.domain.enums.rol import Rol


class ListarConversacionesUseCase(IListarConversacionesUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, consultas: IConversacionQueryService):
        self.consultas = consultas

    def ejecutar(self, entrada: ListarConversacionesInputDTO) -> list[ConversacionOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        leidas = self.consultas.listar(entrada.actor.usuario_id, entrada.hogar_id, entrada.carpeta_id)
        return [ConversacionOutputDTO.desde_read_model(c) for c in leidas]
