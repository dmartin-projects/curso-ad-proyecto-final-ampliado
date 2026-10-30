# asistente/application/listar_recuerdos_use_case/listar_recuerdos_use_case.py (módulo 99)
from asistente.application.listar_recuerdos_use_case.dtos.listar_recuerdos_input_dto import ListarRecuerdosInputDTO
from asistente.application.listar_recuerdos_use_case.i_listar_recuerdos_use_case import IListarRecuerdosUseCase
from asistente.application.shared.dtos.recuerdo_output_dto import RecuerdoOutputDTO
from asistente.domain.repositories.i_recuerdo_query_service import IRecuerdoQueryService
from core.domain.enums.rol import Rol


class ListarRecuerdosUseCase(IListarRecuerdosUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, consultas: IRecuerdoQueryService):
        self.consultas = consultas

    def ejecutar(self, entrada: ListarRecuerdosInputDTO) -> list[RecuerdoOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        return [
            RecuerdoOutputDTO.desde_read_model(r)
            for r in self.consultas.listar(entrada.actor.usuario_id, entrada.hogar_id)
        ]
