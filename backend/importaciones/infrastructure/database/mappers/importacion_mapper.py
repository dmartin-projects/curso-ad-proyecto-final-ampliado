# importaciones/infrastructure/database/mappers/importacion_mapper.py — BO ↔ fila (la importación y sus filas) (módulo 88)
from importaciones.domain.bo.fila import Fila
from importaciones.domain.bo.importacion import Importacion
from importaciones.domain.enums.accion import Accion
from importaciones.infrastructure.database.models.fila_importacion_model import FilaImportacion as FilaImportacionModel
from importaciones.infrastructure.database.models.importacion_model import Importacion as ImportacionModel


def importacion_a_bo(f: ImportacionModel) -> Importacion:
    return Importacion(
        id=f.pk,
        hogar_id=f.hogar_id,
        cuenta_id=f.cuenta_id,
        subido_por_id=f.subido_por_id,
        archivo=f.archivo.name,
        nombre_original=f.nombre_original,
        formato=f.formato,
        huella_archivo=f.huella_archivo,
        estado=f.estado,
        total_filas=f.total_filas,
        procesadas=f.procesadas,
        creados=f.creados,
        conciliados=f.conciliados,
        duplicados=f.duplicados,
        avisos=list(f.avisos),
        resumen=dict(f.resumen),
        error=f.error,
        terminado_en=f.terminado_en,
    )


def fila_a_bo(f: FilaImportacionModel) -> Fila:
    return Fila(
        id=f.pk,
        numero=f.numero,
        fecha=f.fecha,
        concepto=f.concepto,
        importe=f.importe,
        huella=f.huella,
        accion=Accion(f.accion),
        coincide_con_id=f.coincide_con_id,
        movimiento_id=f.movimiento_id,
    )
