# importaciones/infrastructure/database/repositories/importacion_query_service_orm.py — IImportacionQueryService con el ORM (módulo 88)
from core.infrastructure.database import paginacion
from importaciones.domain.read_models.fila_listada import FilaListada
from importaciones.domain.read_models.importacion_listada import ImportacionListada
from importaciones.domain.repositories.i_importacion_query_service import IImportacionQueryService
from importaciones.domain.repositories.queries.filas_query import FilasQuery
from importaciones.domain.repositories.queries.importaciones_query import ImportacionesQuery
from importaciones.infrastructure.database.models.fila_importacion_model import (
    FilaImportacion as FilaImportacionModel,
)
from importaciones.infrastructure.database.models.importacion_model import Importacion as ImportacionModel


def _importacion(i: ImportacionModel) -> ImportacionListada:
    return ImportacionListada(
        id=i.pk,
        estado=i.estado,
        cuenta_id=i.cuenta_id,
        nombre_original=i.nombre_original,
        formato=i.formato,
        total_filas=i.total_filas,
        procesadas=i.procesadas,
        progreso=i.progreso,
        creados=i.creados,
        conciliados=i.conciliados,
        duplicados=i.duplicados,
        resumen=i.resumen,
        avisos=i.avisos,
        error=i.error,
        creado=i.creado,
        terminado_en=i.terminado_en,
    )


def _fila(f: FilaImportacionModel) -> FilaListada:
    return FilaListada(
        id=f.pk,
        numero=f.numero,
        fecha=f.fecha,
        concepto=f.concepto,
        importe=f.importe,
        accion=f.accion,
        coincide_con_id=f.coincide_con_id,
        coincide_con_concepto=None if f.coincide_con is None else f.coincide_con.concepto,
        movimiento_id=f.movimiento_id,
    )


class ImportacionQueryServiceORM(IImportacionQueryService):
    def listar(self, query: ImportacionesQuery):
        qs = ImportacionModel.objects.filter(hogar_id=query.hogar_id)
        if query.estado is not None:
            qs = qs.filter(estado=query.estado)
        if query.cuenta_id is not None:
            qs = qs.filter(cuenta_id=query.cuenta_id)
        return paginacion.por_numero(qs.order_by(*(query.orden or ("-creado",))), query.paginacion, _importacion)

    def detalle(self, hogar_id, importacion_id):
        fila = ImportacionModel.objects.filter(hogar_id=hogar_id, pk=importacion_id).first()
        return None if fila is None else _importacion(fila)

    def filas(self, query: FilasQuery):
        qs = FilaImportacionModel.objects.filter(importacion_id=query.importacion_id).select_related("coincide_con")
        if query.accion in FilaImportacionModel.Accion.values:
            qs = qs.filter(accion=query.accion)
        return paginacion.por_numero(qs.order_by("numero"), query.paginacion, _fila)
