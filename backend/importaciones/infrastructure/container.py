# importaciones/infrastructure/container.py — composition root de las importaciones (módulo 88)
from datetime import timedelta

from django.conf import settings

from core.infrastructure.clock.reloj_django import RelojDjango
from core.infrastructure.database.auditoria_django import AuditoriaDjango
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from importaciones.application.analizar_extracto_use_case.analizar_extracto_use_case import AnalizarExtractoUseCase
from importaciones.application.analizar_extracto_use_case.i_analizar_extracto_use_case import IAnalizarExtractoUseCase
from importaciones.application.confirmar_importacion_use_case.confirmar_importacion_use_case import (
    ConfirmarImportacionUseCase,
)
from importaciones.application.confirmar_importacion_use_case.i_confirmar_importacion_use_case import (
    IConfirmarImportacionUseCase,
)
from importaciones.application.deshacer_importacion_use_case.deshacer_importacion_use_case import (
    DeshacerImportacionUseCase,
)
from importaciones.application.deshacer_importacion_use_case.i_deshacer_importacion_use_case import (
    IDeshacerImportacionUseCase,
)
from importaciones.application.fallar_importacion_use_case.fallar_importacion_use_case import FallarImportacionUseCase
from importaciones.application.fallar_importacion_use_case.i_fallar_importacion_use_case import (
    IFallarImportacionUseCase,
)
from importaciones.application.finalizar_importacion_use_case.finalizar_importacion_use_case import (
    FinalizarImportacionUseCase,
)
from importaciones.application.finalizar_importacion_use_case.i_finalizar_importacion_use_case import (
    IFinalizarImportacionUseCase,
)
from importaciones.application.importar_lote_use_case.i_importar_lote_use_case import IImportarLoteUseCase
from importaciones.application.importar_lote_use_case.importar_lote_use_case import ImportarLoteUseCase
from importaciones.application.listar_filas_importacion_use_case.i_listar_filas_importacion_use_case import (
    IListarFilasImportacionUseCase,
)
from importaciones.application.listar_filas_importacion_use_case.listar_filas_importacion_use_case import (
    ListarFilasImportacionUseCase,
)
from importaciones.application.listar_importaciones_use_case.i_listar_importaciones_use_case import (
    IListarImportacionesUseCase,
)
from importaciones.application.listar_importaciones_use_case.listar_importaciones_use_case import (
    ListarImportacionesUseCase,
)
from importaciones.application.obtener_importacion_use_case.i_obtener_importacion_use_case import (
    IObtenerImportacionUseCase,
)
from importaciones.application.obtener_importacion_use_case.obtener_importacion_use_case import (
    ObtenerImportacionUseCase,
)
from importaciones.application.subir_extracto_use_case.i_subir_extracto_use_case import ISubirExtractoUseCase
from importaciones.application.subir_extracto_use_case.subir_extracto_use_case import SubirExtractoUseCase
from importaciones.infrastructure.database.repositories.importacion_command_repository_orm import (
    ImportacionCommandRepositoryORM,
)
from importaciones.infrastructure.database.repositories.importacion_query_service_orm import ImportacionQueryServiceORM
from importaciones.infrastructure.finanzas.movimientos_en_finanzas import MovimientosEnFinanzas
from importaciones.infrastructure.lectores.lector_de_archivos import LectorDeArchivos
from importaciones.infrastructure.messaging.publicador_eventos_django import PublicadorEventosDjango


def _comun() -> dict:
    return {
        "importaciones": ImportacionCommandRepositoryORM(),
        "eventos": PublicadorEventosDjango(),
        "uow": UnidadDeTrabajoDjango(),
    }


def subir_extracto() -> ISubirExtractoUseCase:
    return SubirExtractoUseCase(movimientos=MovimientosEnFinanzas(), **_comun())


def fallar_importacion() -> IFallarImportacionUseCase:
    return FallarImportacionUseCase(reloj=RelojDjango(), **_comun())


def analizar_extracto() -> IAnalizarExtractoUseCase:
    return AnalizarExtractoUseCase(
        lector=LectorDeArchivos(),
        movimientos=MovimientosEnFinanzas(),
        fallar=fallar_importacion(),
        margen=timedelta(days=settings.IMPORTACION_DIAS_CONCILIACION),
        **_comun(),
    )


def confirmar_importacion() -> IConfirmarImportacionUseCase:
    return ConfirmarImportacionUseCase(**_comun())


def importar_lote() -> IImportarLoteUseCase:
    return ImportarLoteUseCase(movimientos=MovimientosEnFinanzas(), **_comun())


def finalizar_importacion() -> IFinalizarImportacionUseCase:
    return FinalizarImportacionUseCase(reloj=RelojDjango(), **_comun())


def deshacer_importacion() -> IDeshacerImportacionUseCase:
    return DeshacerImportacionUseCase(
        importaciones=ImportacionCommandRepositoryORM(),
        movimientos=MovimientosEnFinanzas(),
        auditoria=AuditoriaDjango(),
        uow=UnidadDeTrabajoDjango(),
    )


# ── Lectura ──
def listar_importaciones() -> IListarImportacionesUseCase:
    return ListarImportacionesUseCase(importaciones=ImportacionQueryServiceORM())


def obtener_importacion() -> IObtenerImportacionUseCase:
    return ObtenerImportacionUseCase(importaciones=ImportacionQueryServiceORM())


def listar_filas_importacion() -> IListarFilasImportacionUseCase:
    return ListarFilasImportacionUseCase(importaciones=ImportacionQueryServiceORM())
