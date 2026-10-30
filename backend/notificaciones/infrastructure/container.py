# notificaciones/infrastructure/container.py — composition root de las notificaciones (módulo 88)
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from notificaciones.application.contar_no_leidas_use_case.contar_no_leidas_use_case import ContarNoLeidasUseCase
from notificaciones.application.contar_no_leidas_use_case.i_contar_no_leidas_use_case import IContarNoLeidasUseCase
from notificaciones.application.listar_notificaciones_use_case.i_listar_notificaciones_use_case import (
    IListarNotificacionesUseCase,
)
from notificaciones.application.listar_notificaciones_use_case.listar_notificaciones_use_case import (
    ListarNotificacionesUseCase,
)
from notificaciones.application.notificar_use_case.i_notificar_use_case import INotificarUseCase
from notificaciones.application.notificar_use_case.notificar_use_case import NotificarUseCase
from notificaciones.application.obtener_estado_inicial_use_case.i_obtener_estado_inicial_use_case import (
    IObtenerEstadoInicialUseCase,
)
from notificaciones.application.obtener_estado_inicial_use_case.obtener_estado_inicial_use_case import (
    ObtenerEstadoInicialUseCase,
)
from notificaciones.application.obtener_notificacion_use_case.i_obtener_notificacion_use_case import (
    IObtenerNotificacionUseCase,
)
from notificaciones.application.obtener_notificacion_use_case.obtener_notificacion_use_case import (
    ObtenerNotificacionUseCase,
)
from notificaciones.infrastructure.database.repositories.destinatarios_orm import DestinatariosORM
from notificaciones.infrastructure.database.repositories.notificacion_command_repository_orm import (
    NotificacionCommandRepositoryORM,
)
from notificaciones.infrastructure.database.repositories.notificacion_query_service_orm import (
    NotificacionQueryServiceORM,
)
from notificaciones.infrastructure.i18n.traductor_django import TraductorDjango
from notificaciones.infrastructure.messaging.publicador_eventos_django import PublicadorEventosDjango
from notificaciones.infrastructure.realtime import tiempo_real


def notificar() -> INotificarUseCase:
    return NotificarUseCase(
        notificaciones=NotificacionCommandRepositoryORM(),
        destinatarios=DestinatariosORM(),
        traductor=TraductorDjango(),
        eventos=PublicadorEventosDjango(),
        uow=UnidadDeTrabajoDjango(),
    )


# ── Lectura ──
def listar_notificaciones() -> IListarNotificacionesUseCase:
    return ListarNotificacionesUseCase(notificaciones=NotificacionQueryServiceORM())


def obtener_notificacion() -> IObtenerNotificacionUseCase:
    return ObtenerNotificacionUseCase(notificaciones=NotificacionQueryServiceORM())


def contar_no_leidas() -> IContarNoLeidasUseCase:
    return ContarNoLeidasUseCase(notificaciones=NotificacionQueryServiceORM())


def obtener_estado_inicial() -> IObtenerEstadoInicialUseCase:
    return ObtenerEstadoInicialUseCase(destinatarios=DestinatariosORM(), notificaciones=NotificacionQueryServiceORM())


def emitir_evento_a_usuario(usuario_id: int, hogar_id: int, evento: str, datos: dict) -> None:
    """Módulo 105: para otras apps (el progreso del análisis del asistente), sin tocar los adapters de notificaciones."""
    tiempo_real.emitir_evento_a_usuario(usuario_id, hogar_id, evento, datos)
