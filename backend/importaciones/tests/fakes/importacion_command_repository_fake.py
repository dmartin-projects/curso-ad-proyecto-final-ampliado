# importaciones/tests/fakes/importacion_command_repository_fake.py — IImportacionCommandRepository en memoria (módulo 88)
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia
from importaciones.domain.enums.accion import Accion
from importaciones.domain.enums.estado_importacion import PUEDEN_FALLAR, EstadoImportacion
from importaciones.domain.exceptions.extracto_repetido_exception import ExtractoRepetidoException
from importaciones.domain.exceptions.importacion_no_encontrada_exception import ImportacionNoEncontradaException
from importaciones.domain.repositories.i_importacion_command_repository import IImportacionCommandRepository

ACTIVAS = set(EstadoImportacion) - {EstadoImportacion.DESHECHA, EstadoImportacion.ERROR}


class ImportacionCommandRepositoryFake(AlmacenEnMemoria, IImportacionCommandRepository):
    def __init__(self):
        super().__init__()
        self.archivos: dict[int, bytes] = {}
        self.filas: dict[int, object] = {}  # id de fila → Fila (con importacion_id)
        self._siguiente_fila = 1

    def crear(self, importacion, contenido):
        if any(
            (i.hogar_id, i.huella_archivo) == (importacion.hogar_id, importacion.huella_archivo) and i.estado in ACTIVAS
            for i in self._datos.values()
        ):
            raise ExtractoRepetidoException()
        self._asignar_id(importacion)
        importacion.archivo = f"importaciones/{importacion.id}.csv"
        self.archivos[importacion.id] = contenido
        self._datos[importacion.id] = copia(importacion)

    def obtener(self, hogar_id, importacion_id, *, bloquear=False):
        i = self._datos.get(importacion_id)
        if i is None or i.hogar_id != hogar_id:
            raise ImportacionNoEncontradaException()
        return copia(i)

    def por_id(self, importacion_id, *, bloquear=False):
        if importacion_id not in self._datos:
            raise ImportacionNoEncontradaException()
        return copia(self._datos[importacion_id])

    def reclamar(self, importacion_id, de, a):
        i = self._datos[importacion_id]
        if i.estado != de:
            return False
        i.estado = a
        return True

    def fallar(self, importacion_id, mensaje, ahora):
        i = self._datos[importacion_id]
        if i.estado not in PUEDEN_FALLAR:
            return None
        i.estado, i.error, i.terminado_en = EstadoImportacion.ERROR, mensaje, ahora
        return i.formato

    def guardar(self, importacion):
        self._datos[importacion.id] = copia(importacion)

    def leer_archivo(self, importacion):
        return self.archivos[importacion.id]

    def crear_filas(self, importacion_id, filas):
        for f in filas:
            f.id = self._siguiente_fila
            self._siguiente_fila += 1
            guardada = copia(f)
            guardada.importacion_id = importacion_id
            self.filas[f.id] = guardada

    def _de(self, importacion_id):
        return sorted((f for f in self.filas.values() if f.importacion_id == importacion_id), key=lambda f: f.numero)

    def separar(self, importacion_id, fila_ids):
        for f in self._de(importacion_id):
            if f.id in set(fila_ids) and f.accion == Accion.CONCILIAR:
                f.accion, f.coincide_con_id = Accion.CREAR, None

    def filas_a_importar(self, importacion_id):
        return [f.id for f in self._de(importacion_id) if f.accion != Accion.DUPLICADA]

    def filas_pendientes(self, importacion_id, fila_ids):
        return [
            copia(f)
            for f in self._de(importacion_id)
            if f.id in set(fila_ids) and f.movimiento_id is None and f.accion != Accion.DUPLICADA
        ]

    def guardar_filas(self, filas):
        for f in filas:
            self.filas[f.id].accion, self.filas[f.id].movimiento_id = f.accion, f.movimiento_id

    def sumar(self, importacion_id, *, procesadas, creados, conciliados, duplicados):
        i = self._datos[importacion_id]
        i.procesadas += procesadas
        i.creados += creados
        i.conciliados += conciliados
        i.duplicados += duplicados

    def movimientos(self, importacion_id, accion):
        return [f.movimiento_id for f in self._de(importacion_id) if f.accion == accion and f.movimiento_id]
