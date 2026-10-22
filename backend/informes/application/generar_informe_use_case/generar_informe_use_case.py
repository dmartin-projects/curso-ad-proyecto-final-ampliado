# informes/application/generar_informe_use_case/generar_informe_use_case.py (módulos 78 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from informes.application.generar_informe_use_case.dtos.generar_informe_input_dto import GenerarInformeInputDTO
from informes.application.generar_informe_use_case.i_generar_informe_use_case import IGenerarInformeUseCase
from informes.application.ports.i_maquetador import IMaquetador
from informes.application.shared.dtos.informe_output_dto import InformeOutputDTO
from informes.domain.bo.informe import Informe
from informes.domain.events.informe_generado_event import InformeGeneradoEvent
from informes.domain.repositories.i_informe_command_repository import IInformeCommandRepository


class GenerarInformeUseCase(IGenerarInformeUseCase):
    """Genera (o regenera) el PDF del mes. Idempotente: un informe por hogar y mes. Lo pide una tarea."""

    def __init__(
        self,
        *,
        informes: IInformeCommandRepository,
        maquetador: IMaquetador,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.informes, self.maquetador, self.eventos, self.uow = informes, maquetador, eventos, uow

    def ejecutar(self, entrada: GenerarInformeInputDTO) -> InformeOutputDTO:
        hogar_id, mes = entrada.hogar_id, entrada.mes
        pdf = self.maquetador.pdf(hogar_id, mes)  # FUERA de la transacción: puede tardar segundos
        with self.uow:
            informe = self.informes.del_mes(hogar_id, mes) or Informe(hogar_id=hogar_id, mes=mes)
            informe.generado_por_id, informe.tamano = entrada.usuario_id, len(pdf)
            anterior = self.informes.guardar(informe, pdf)
            self.eventos.publicar(InformeGeneradoEvent(informe.id, entrada.enviar, anterior))
        return InformeOutputDTO.desde_bo(informe)
