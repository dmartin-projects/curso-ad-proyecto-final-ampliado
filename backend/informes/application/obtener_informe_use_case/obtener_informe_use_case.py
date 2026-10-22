# informes/application/obtener_informe_use_case/obtener_informe_use_case.py (módulo 88)
from core.domain.enums.rol import Rol
from informes.application.obtener_informe_use_case.dtos.obtener_informe_input_dto import ObtenerInformeInputDTO
from informes.application.obtener_informe_use_case.i_obtener_informe_use_case import IObtenerInformeUseCase
from informes.application.shared.dtos.informe_listado_output_dto import InformeListadoOutputDTO
from informes.domain.repositories.i_informe_query_service import IInformeQueryService


class ObtenerInformeUseCase(IObtenerInformeUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, informes: IInformeQueryService):
        self.informes = informes

    def ejecutar(self, entrada: ObtenerInformeInputDTO) -> InformeListadoOutputDTO | None:
        entrada.actor.exigir(self.rol_minimo)
        leido = self.informes.detalle(entrada.hogar_id, entrada.mes)
        return None if leido is None else InformeListadoOutputDTO.desde_read_model(leido)
