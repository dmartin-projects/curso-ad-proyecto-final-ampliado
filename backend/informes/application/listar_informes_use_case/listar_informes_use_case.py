# informes/application/listar_informes_use_case/listar_informes_use_case.py (módulo 88)
from core.domain.enums.rol import Rol
from informes.application.listar_informes_use_case.dtos.listar_informes_input_dto import ListarInformesInputDTO
from informes.application.listar_informes_use_case.i_listar_informes_use_case import IListarInformesUseCase
from informes.application.shared.dtos.informe_listado_output_dto import InformeListadoOutputDTO
from informes.domain.repositories.i_informe_query_service import IInformeQueryService


class ListarInformesUseCase(IListarInformesUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, informes: IInformeQueryService):
        self.informes = informes

    def ejecutar(self, entrada: ListarInformesInputDTO) -> list[InformeListadoOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        return [InformeListadoOutputDTO.desde_read_model(i) for i in self.informes.listar(entrada.hogar_id)]
