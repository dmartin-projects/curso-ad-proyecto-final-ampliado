# notificaciones/application/notificar_use_case/notificar_use_case.py (módulos 76 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from notificaciones.application.notificar_use_case.dtos.notificar_input_dto import NotificarInputDTO
from notificaciones.application.notificar_use_case.i_notificar_use_case import INotificarUseCase
from notificaciones.application.ports.i_destinatarios import IDestinatarios
from notificaciones.application.ports.i_traductor import ITraductor
from notificaciones.application.shared.dtos.notificacion_output_dto import NotificacionOutputDTO
from notificaciones.domain.bo.notificacion import Notificacion
from notificaciones.domain.events.notificaciones_creadas_event import NotificacionesCreadasEvent
from notificaciones.domain.repositories.i_notificacion_command_repository import INotificacionCommandRepository


class NotificarUseCase(INotificarUseCase):
    """Una notificación por persona, en SU idioma (RNF7), y el aviso en tiempo real al confirmar.

    Lo piden los receivers: las demás apps no saben que existen las notificaciones, solo emiten señales (módulo 15).
    No exige rol: no lo pide una persona, lo pide lo que ha pasado en otra app.
    """

    def __init__(
        self,
        *,
        notificaciones: INotificacionCommandRepository,
        destinatarios: IDestinatarios,
        traductor: ITraductor,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.notificaciones, self.destinatarios, self.traductor = notificaciones, destinatarios, traductor
        self.eventos, self.uow = eventos, uow

    def ejecutar(self, entrada: NotificarInputDTO) -> list[NotificacionOutputDTO]:
        usuarios = list(entrada.usuarios)
        if entrada.miembros_de is not None:
            usuarios += self.destinatarios.miembros_activos(entrada.miembros_de)
        idiomas = self.destinatarios.idiomas(usuarios)
        nuevas = [
            Notificacion(
                usuario_id=usuario_id,
                tipo=entrada.tipo,
                titulo=self.traductor.traducir(entrada.titulo, idioma, entrada.contexto),
                mensaje=self.traductor.traducir(entrada.mensaje, idioma, entrada.contexto) if entrada.mensaje else "",
                hogar_id=entrada.hogar_id,
                enlace=entrada.enlace,
                datos=entrada.contexto,
            )
            for usuario_id, idioma in idiomas.items()
        ]
        with self.uow:
            self.notificaciones.crear_varias(nuevas)
            if nuevas:
                self.eventos.publicar(NotificacionesCreadasEvent(tuple(x.id for x in nuevas), entrada.email))
        return [NotificacionOutputDTO.desde_bo(x) for x in nuevas]
