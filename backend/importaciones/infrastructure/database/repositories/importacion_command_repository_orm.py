# importaciones/infrastructure/database/repositories/importacion_command_repository_orm.py — IImportacionCommandRepository con el ORM (módulo 88)
from django.db import IntegrityError, transaction
from django.db.models import F

from core.infrastructure.database.guardado import nombre_constraint
from importaciones.domain.bo.importacion import Importacion
from importaciones.domain.enums.accion import Accion
from importaciones.domain.enums.estado_importacion import PUEDEN_FALLAR
from importaciones.domain.enums.formato import Formato
from importaciones.domain.exceptions.extracto_repetido_exception import ExtractoRepetidoException
from importaciones.domain.exceptions.importacion_no_encontrada_exception import ImportacionNoEncontradaException
from importaciones.domain.repositories.i_importacion_command_repository import IImportacionCommandRepository
from importaciones.infrastructure.database.mappers.importacion_mapper import fila_a_bo, importacion_a_bo
from importaciones.infrastructure.database.models.fila_importacion_model import FilaImportacion as FilaImportacionModel
from importaciones.infrastructure.database.models.importacion_model import Importacion as ImportacionModel

CAMPOS = [
    "estado",
    "total_filas",
    "procesadas",
    "creados",
    "conciliados",
    "duplicados",
    "avisos",
    "resumen",
    "error",
    "terminado_en",
]


class ImportacionCommandRepositoryORM(IImportacionCommandRepository):
    def crear(self, importacion: Importacion, contenido) -> None:
        fila = ImportacionModel(
            hogar_id=importacion.hogar_id,
            cuenta_id=importacion.cuenta_id,
            subido_por_id=importacion.subido_por_id,
            archivo=contenido,
            nombre_original=importacion.nombre_original,
            formato=importacion.formato,
            huella_archivo=importacion.huella_archivo,
        )
        try:
            with transaction.atomic():
                fila.save(force_insert=True)
        except IntegrityError as e:
            if nombre_constraint(e) == "importacion_archivo_unico_activo":
                raise ExtractoRepetidoException() from e
            raise
        importacion.id, importacion.archivo = fila.pk, fila.archivo.name

    def _una(self, consulta, bloquear: bool) -> Importacion:
        if bloquear:
            consulta = consulta.select_for_update()
        fila = consulta.first()
        if fila is None:
            raise ImportacionNoEncontradaException()
        return importacion_a_bo(fila)

    def obtener(self, hogar_id, importacion_id, *, bloquear=False):
        return self._una(ImportacionModel.objects.filter(hogar_id=hogar_id, pk=importacion_id), bloquear)

    def por_id(self, importacion_id, *, bloquear=False):
        return self._una(ImportacionModel.objects.filter(pk=importacion_id), bloquear)

    def reclamar(self, importacion_id, de, a) -> bool:
        return bool(ImportacionModel.objects.filter(pk=importacion_id, estado=de).update(estado=a))

    def fallar(self, importacion_id, mensaje, ahora) -> Formato | None:
        actualizadas = ImportacionModel.objects.filter(pk=importacion_id, estado__in=PUEDEN_FALLAR).update(
            estado="error", error=mensaje, terminado_en=ahora
        )
        if not actualizadas:
            return None
        return Formato(ImportacionModel.objects.filter(pk=importacion_id).values_list("formato", flat=True).get())

    def guardar(self, importacion: Importacion) -> None:
        # Mientras corren los lotes (que suman los contadores con sumar()), nadie llama a guardar(): el cierre del
        # chord llega cuando han terminado todos y lee la importación bloqueada, ya con sus sumas.
        ImportacionModel.objects.filter(pk=importacion.id).update(**{c: getattr(importacion, c) for c in CAMPOS})

    def leer_archivo(self, importacion: Importacion) -> bytes:
        with ImportacionModel.objects.get(pk=importacion.id).archivo.open("rb") as f:
            return f.read()

    # ── Las filas ──
    def crear_filas(self, importacion_id, filas):
        nuevas = FilaImportacionModel.objects.bulk_create(
            [
                FilaImportacionModel(
                    importacion_id=importacion_id,
                    numero=f.numero,
                    fecha=f.fecha,
                    concepto=f.concepto,
                    importe=f.importe,
                    huella=f.huella,
                    accion=f.accion,
                    coincide_con_id=f.coincide_con_id,
                )
                for f in filas
            ],
            batch_size=1000,
        )
        for fila, nueva in zip(filas, nuevas, strict=True):
            fila.id = nueva.pk

    def separar(self, importacion_id, fila_ids):
        FilaImportacionModel.objects.filter(
            importacion_id=importacion_id, pk__in=list(fila_ids), accion=Accion.CONCILIAR
        ).update(accion=Accion.CREAR, coincide_con=None)

    def filas_a_importar(self, importacion_id):
        return list(
            FilaImportacionModel.objects.filter(importacion_id=importacion_id)
            .exclude(accion=Accion.DUPLICADA)
            .values_list("pk", flat=True)
        )

    def filas_pendientes(self, importacion_id, fila_ids):
        filas = (
            FilaImportacionModel.objects.select_for_update()
            .filter(importacion_id=importacion_id, pk__in=list(fila_ids), movimiento__isnull=True)
            .exclude(accion=Accion.DUPLICADA)
            .order_by("numero")
        )
        return [fila_a_bo(f) for f in filas]

    def guardar_filas(self, filas):
        FilaImportacionModel.objects.bulk_update(
            [FilaImportacionModel(pk=f.id, accion=f.accion, movimiento_id=f.movimiento_id) for f in filas],
            ["accion", "movimiento"],
        )

    def sumar(self, importacion_id, *, procesadas, creados, conciliados, duplicados):
        ImportacionModel.objects.filter(pk=importacion_id).update(
            procesadas=F("procesadas") + procesadas,
            creados=F("creados") + creados,
            conciliados=F("conciliados") + conciliados,
            duplicados=F("duplicados") + duplicados,
        )

    def movimientos(self, importacion_id, accion):
        return list(
            FilaImportacionModel.objects.filter(
                importacion_id=importacion_id, accion=accion, movimiento__isnull=False
            ).values_list("movimiento_id", flat=True)
        )
