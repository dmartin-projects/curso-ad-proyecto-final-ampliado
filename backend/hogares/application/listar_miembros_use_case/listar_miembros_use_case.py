# hogares/application/listar_miembros_use_case/listar_miembros_use_case.py (módulo 88)
from core.domain.enums.rol import Rol
from core.domain.repositories.queries.listado_del_hogar_query import ListadoDelHogarQuery
from hogares.application.listar_miembros_use_case.dtos.listar_miembros_input_dto import ListarMiembrosInputDTO
from hogares.application.listar_miembros_use_case.i_listar_miembros_use_case import IListarMiembrosUseCase
from hogares.application.shared.dtos.miembro_listado_output_dto import MiembroListadoOutputDTO
from hogares.domain.repositories.i_miembro_query_service import IMiembroQueryService


class ListarMiembrosUseCase(IListarMiembrosUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, miembros: IMiembroQueryService):
        self.miembros = miembros

    def ejecutar(self, entrada: ListarMiembrosInputDTO) -> list[MiembroListadoOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        leidos = self.miembros.listar(ListadoDelHogarQuery(entrada.hogar_id, entrada.orden))
        return [MiembroListadoOutputDTO.desde_read_model(m) for m in leidos]
