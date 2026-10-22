# backoffice/infrastructure/container.py — composition root del backoffice: solo lectura (para cambiar algo, los use cases de la app dueña) (módulo 88)
from backoffice.application.listar_auditoria_use_case.i_listar_auditoria_use_case import IListarAuditoriaUseCase
from backoffice.application.listar_auditoria_use_case.listar_auditoria_use_case import ListarAuditoriaUseCase
from backoffice.application.listar_hogares_soporte_use_case.i_listar_hogares_soporte_use_case import (
    IListarHogaresSoporteUseCase,
)
from backoffice.application.listar_hogares_soporte_use_case.listar_hogares_soporte_use_case import (
    ListarHogaresSoporteUseCase,
)
from backoffice.application.listar_importaciones_soporte_use_case.i_listar_importaciones_soporte_use_case import (
    IListarImportacionesSoporteUseCase,
)
from backoffice.application.listar_importaciones_soporte_use_case.listar_importaciones_soporte_use_case import (
    ListarImportacionesSoporteUseCase,
)
from backoffice.application.listar_movimientos_soporte_use_case.i_listar_movimientos_soporte_use_case import (
    IListarMovimientosSoporteUseCase,
)
from backoffice.application.listar_movimientos_soporte_use_case.listar_movimientos_soporte_use_case import (
    ListarMovimientosSoporteUseCase,
)
from backoffice.application.listar_tareas_programadas_use_case.i_listar_tareas_programadas_use_case import (
    IListarTareasProgramadasUseCase,
)
from backoffice.application.listar_tareas_programadas_use_case.listar_tareas_programadas_use_case import (
    ListarTareasProgramadasUseCase,
)
from backoffice.application.listar_tickets_soporte_use_case.i_listar_tickets_soporte_use_case import (
    IListarTicketsSoporteUseCase,
)
from backoffice.application.listar_tickets_soporte_use_case.listar_tickets_soporte_use_case import (
    ListarTicketsSoporteUseCase,
)
from backoffice.application.listar_usuarios_soporte_use_case.i_listar_usuarios_soporte_use_case import (
    IListarUsuariosSoporteUseCase,
)
from backoffice.application.listar_usuarios_soporte_use_case.listar_usuarios_soporte_use_case import (
    ListarUsuariosSoporteUseCase,
)
from backoffice.application.localizar_tickets_use_case.i_localizar_tickets_use_case import ILocalizarTicketsUseCase
from backoffice.application.localizar_tickets_use_case.localizar_tickets_use_case import LocalizarTicketsUseCase
from backoffice.application.obtener_hogar_de_categoria_use_case.i_obtener_hogar_de_categoria_use_case import (
    IObtenerHogarDeCategoriaUseCase,
)
from backoffice.application.obtener_hogar_de_categoria_use_case.obtener_hogar_de_categoria_use_case import (
    ObtenerHogarDeCategoriaUseCase,
)
from backoffice.application.obtener_hogar_soporte_use_case.i_obtener_hogar_soporte_use_case import (
    IObtenerHogarSoporteUseCase,
)
from backoffice.application.obtener_hogar_soporte_use_case.obtener_hogar_soporte_use_case import (
    ObtenerHogarSoporteUseCase,
)
from backoffice.application.obtener_importacion_soporte_use_case.i_obtener_importacion_soporte_use_case import (
    IObtenerImportacionSoporteUseCase,
)
from backoffice.application.obtener_importacion_soporte_use_case.obtener_importacion_soporte_use_case import (
    ObtenerImportacionSoporteUseCase,
)
from backoffice.application.obtener_movimiento_soporte_use_case.i_obtener_movimiento_soporte_use_case import (
    IObtenerMovimientoSoporteUseCase,
)
from backoffice.application.obtener_movimiento_soporte_use_case.obtener_movimiento_soporte_use_case import (
    ObtenerMovimientoSoporteUseCase,
)
from backoffice.application.obtener_registro_auditoria_use_case.i_obtener_registro_auditoria_use_case import (
    IObtenerRegistroAuditoriaUseCase,
)
from backoffice.application.obtener_registro_auditoria_use_case.obtener_registro_auditoria_use_case import (
    ObtenerRegistroAuditoriaUseCase,
)
from backoffice.application.obtener_resumen_soporte_use_case.i_obtener_resumen_soporte_use_case import (
    IObtenerResumenSoporteUseCase,
)
from backoffice.application.obtener_resumen_soporte_use_case.obtener_resumen_soporte_use_case import (
    ObtenerResumenSoporteUseCase,
)
from backoffice.application.obtener_tarea_programada_use_case.i_obtener_tarea_programada_use_case import (
    IObtenerTareaProgramadaUseCase,
)
from backoffice.application.obtener_tarea_programada_use_case.obtener_tarea_programada_use_case import (
    ObtenerTareaProgramadaUseCase,
)
from backoffice.application.obtener_ticket_soporte_use_case.i_obtener_ticket_soporte_use_case import (
    IObtenerTicketSoporteUseCase,
)
from backoffice.application.obtener_ticket_soporte_use_case.obtener_ticket_soporte_use_case import (
    ObtenerTicketSoporteUseCase,
)
from backoffice.application.obtener_usuario_soporte_use_case.i_obtener_usuario_soporte_use_case import (
    IObtenerUsuarioSoporteUseCase,
)
from backoffice.application.obtener_usuario_soporte_use_case.obtener_usuario_soporte_use_case import (
    ObtenerUsuarioSoporteUseCase,
)
from backoffice.infrastructure.database.repositories.auditoria_soporte_query_service_orm import (
    AuditoriaSoporteQueryServiceORM,
)
from backoffice.infrastructure.database.repositories.hogar_soporte_query_service_orm import HogarSoporteQueryServiceORM
from backoffice.infrastructure.database.repositories.importacion_soporte_query_service_orm import (
    ImportacionSoporteQueryServiceORM,
)
from backoffice.infrastructure.database.repositories.movimiento_soporte_query_service_orm import (
    MovimientoSoporteQueryServiceORM,
)
from backoffice.infrastructure.database.repositories.resumen_soporte_query_service_orm import (
    ResumenSoporteQueryServiceORM,
)
from backoffice.infrastructure.database.repositories.tarea_programada_soporte_query_service_orm import (
    TareaProgramadaSoporteQueryServiceORM,
)
from backoffice.infrastructure.database.repositories.ticket_soporte_query_service_orm import (
    TicketSoporteQueryServiceORM,
)
from backoffice.infrastructure.database.repositories.usuario_soporte_query_service_orm import (
    UsuarioSoporteQueryServiceORM,
)


def obtener_resumen_soporte() -> IObtenerResumenSoporteUseCase:
    return ObtenerResumenSoporteUseCase(resumen=ResumenSoporteQueryServiceORM())


def listar_tickets_soporte() -> IListarTicketsSoporteUseCase:
    return ListarTicketsSoporteUseCase(tickets=TicketSoporteQueryServiceORM())


def obtener_ticket_soporte() -> IObtenerTicketSoporteUseCase:
    return ObtenerTicketSoporteUseCase(tickets=TicketSoporteQueryServiceORM())


def localizar_tickets() -> ILocalizarTicketsUseCase:
    return LocalizarTicketsUseCase(tickets=TicketSoporteQueryServiceORM())


def listar_importaciones_soporte() -> IListarImportacionesSoporteUseCase:
    return ListarImportacionesSoporteUseCase(importaciones=ImportacionSoporteQueryServiceORM())


def obtener_importacion_soporte() -> IObtenerImportacionSoporteUseCase:
    return ObtenerImportacionSoporteUseCase(importaciones=ImportacionSoporteQueryServiceORM())


def listar_hogares_soporte() -> IListarHogaresSoporteUseCase:
    return ListarHogaresSoporteUseCase(hogares=HogarSoporteQueryServiceORM())


def obtener_hogar_soporte() -> IObtenerHogarSoporteUseCase:
    return ObtenerHogarSoporteUseCase(hogares=HogarSoporteQueryServiceORM())


def listar_usuarios_soporte() -> IListarUsuariosSoporteUseCase:
    return ListarUsuariosSoporteUseCase(usuarios=UsuarioSoporteQueryServiceORM())


def obtener_usuario_soporte() -> IObtenerUsuarioSoporteUseCase:
    return ObtenerUsuarioSoporteUseCase(usuarios=UsuarioSoporteQueryServiceORM())


def listar_movimientos_soporte() -> IListarMovimientosSoporteUseCase:
    return ListarMovimientosSoporteUseCase(movimientos=MovimientoSoporteQueryServiceORM())


def obtener_movimiento_soporte() -> IObtenerMovimientoSoporteUseCase:
    return ObtenerMovimientoSoporteUseCase(movimientos=MovimientoSoporteQueryServiceORM())


def obtener_hogar_de_categoria() -> IObtenerHogarDeCategoriaUseCase:
    return ObtenerHogarDeCategoriaUseCase(movimientos=MovimientoSoporteQueryServiceORM())


def listar_auditoria() -> IListarAuditoriaUseCase:
    return ListarAuditoriaUseCase(auditoria=AuditoriaSoporteQueryServiceORM())


def obtener_registro_auditoria() -> IObtenerRegistroAuditoriaUseCase:
    return ObtenerRegistroAuditoriaUseCase(auditoria=AuditoriaSoporteQueryServiceORM())


def listar_tareas_programadas() -> IListarTareasProgramadasUseCase:
    return ListarTareasProgramadasUseCase(tareas=TareaProgramadaSoporteQueryServiceORM())


def obtener_tarea_programada() -> IObtenerTareaProgramadaUseCase:
    return ObtenerTareaProgramadaUseCase(tareas=TareaProgramadaSoporteQueryServiceORM())
