# informes/application/pedir_informe_use_case/pedir_informe_use_case.py (módulos 78 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from core.domain.vo.mes import Mes
from informes.application.pedir_informe_use_case.dtos.pedir_informe_input_dto import PedirInformeInputDTO
from informes.application.pedir_informe_use_case.i_pedir_informe_use_case import IPedirInformeUseCase
from informes.domain.events.informe_pedido_event import InformePedidoEvent
from informes.domain.services.meses import comprobar_mes


class PedirInformeUseCase(IPedirInformeUseCase):
    """Bajo demanda (POST /informes/): se genera en segundo plano y la API responde 202 al momento."""

    rol_minimo = Rol.MIEMBRO

    def __init__(self, *, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo, reloj: IReloj):
        self.eventos, self.uow, self.reloj = eventos, uow, reloj

    def ejecutar(self, entrada: PedirInformeInputDTO) -> Mes:
        entrada.actor.exigir(self.rol_minimo)
        mes = comprobar_mes(entrada.mes, self.reloj.hoy())
        with self.uow:
            self.eventos.publicar(InformePedidoEvent(entrada.hogar_id, mes, entrada.actor.usuario_id, entrada.enviar))
        return mes
