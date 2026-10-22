# backoffice/infrastructure/database/repositories/importacion_soporte_query_service_orm.py — IImportacionSoporteQueryService con el ORM (módulo 88)
from backoffice.domain.read_models.importacion_soporte import ImportacionSoporte
from backoffice.domain.repositories.i_importacion_soporte_query_service import IImportacionSoporteQueryService
from backoffice.infrastructure.database.repositories.listados import listar
from importaciones.models import Importacion as ImportacionModel

BUSQUEDA = ("=id", "hogar__nombre", "nombre_original")


def _a_read_model(i: ImportacionModel) -> ImportacionSoporte:
    return ImportacionSoporte(
        id=i.pk,
        hogar_id=i.hogar_id,
        hogar_nombre=i.hogar.nombre,
        nombre_original=i.nombre_original,
        estado=i.estado,
        progreso=i.progreso,
        total_filas=i.total_filas,
        creados=i.creados,
        conciliados=i.conciliados,
        duplicados=i.duplicados,
        error=i.error,
        creado=i.creado,
    )


class ImportacionSoporteQueryServiceORM(IImportacionSoporteQueryService):
    @staticmethod
    def _todas():
        return ImportacionModel.objects.select_related("hogar")

    def listar(self, query):
        return listar(self._todas(), query, BUSQUEDA, _a_read_model)

    def detalle(self, importacion_id):
        fila = self._todas().filter(pk=importacion_id).first()
        return None if fila is None else _a_read_model(fila)
