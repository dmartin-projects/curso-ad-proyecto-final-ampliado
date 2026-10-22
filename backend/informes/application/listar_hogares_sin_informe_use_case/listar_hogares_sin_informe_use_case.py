# informes/application/listar_hogares_sin_informe_use_case/listar_hogares_sin_informe_use_case.py (módulo 88)
from informes.application.listar_hogares_sin_informe_use_case.dtos.listar_hogares_sin_informe_input_dto import (
    ListarHogaresSinInformeInputDTO,
)
from informes.application.listar_hogares_sin_informe_use_case.i_listar_hogares_sin_informe_use_case import (
    IListarHogaresSinInformeUseCase,
)
from informes.domain.repositories.i_informe_query_service import IInformeQueryService


class ListarHogaresSinInformeUseCase(IListarHogaresSinInformeUseCase):
    """Lo pide la tarea de Beat del día 1, sin persona: no exige rol."""

    def __init__(self, *, informes: IInformeQueryService):
        self.informes = informes

    def ejecutar(self, entrada: ListarHogaresSinInformeInputDTO) -> list[int]:
        return self.informes.hogares_sin_informe(entrada.mes)
