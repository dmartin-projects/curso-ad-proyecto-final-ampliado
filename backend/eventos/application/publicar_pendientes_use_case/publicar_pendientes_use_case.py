# eventos/application/publicar_pendientes_use_case/publicar_pendientes_use_case.py — publicar lo pendiente del outbox (módulos 85 y 88)
#
# Garantía: AL MENOS UNA VEZ. Un mensaje se marca como publicado solo después de que el broker lo confirme; si el
# proceso muere entre la confirmación y la marca, al volver lo publica otra vez. Los consumidores tienen que ser
# idempotentes (el servicio de estadísticas lo es: se queda con la versión más alta de cada objeto).
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from eventos.application.ports.i_broker import IBroker
from eventos.application.publicar_pendientes_use_case.dtos.evento_publicado_output_dto import EventoPublicadoOutputDTO
from eventos.application.publicar_pendientes_use_case.dtos.lote_publicado_output_dto import LotePublicadoOutputDTO
from eventos.application.publicar_pendientes_use_case.dtos.publicar_pendientes_input_dto import (
    PublicarPendientesInputDTO,
)
from eventos.application.publicar_pendientes_use_case.i_publicar_pendientes_use_case import IPublicarPendientesUseCase
from eventos.domain.repositories.i_evento_pendiente_command_repository import IEventoPendienteCommandRepository


class PublicarPendientesUseCase(IPublicarPendientesUseCase):
    """Lo pide el relay (el comando publicar_eventos), sin persona: no exige rol."""

    def __init__(
        self, *, pendientes: IEventoPendienteCommandRepository, broker: IBroker, uow: IUnidadDeTrabajo, reloj: IReloj
    ):
        self.pendientes, self.broker, self.uow, self.reloj = pendientes, broker, uow, reloj

    def ejecutar(self, entrada: PublicarPendientesInputDTO) -> LotePublicadoOutputDTO:
        """Si el broker falla, PublicacionNoConfirmadaException y no se marca nada: se reintentará entero."""
        with self.uow:
            lote = self.pendientes.pendientes(entrada.tamano)
            if not lote:
                return LotePublicadoOutputDTO((), None)
            self.broker.publicar(lote)
            cuando = self.reloj.ahora()
            self.pendientes.marcar_publicados([p.id for p in lote], cuando)
        return LotePublicadoOutputDTO(tuple(EventoPublicadoOutputDTO.desde_bo(p) for p in lote), cuando)
