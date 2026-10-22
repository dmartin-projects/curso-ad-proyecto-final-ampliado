# importaciones/application/analizar_extracto_use_case/analizar_extracto_use_case.py (módulos 75 y 88)
from datetime import timedelta

from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from importaciones.application.analizar_extracto_use_case.dtos.analizar_extracto_input_dto import (
    AnalizarExtractoInputDTO,
)
from importaciones.application.analizar_extracto_use_case.i_analizar_extracto_use_case import IAnalizarExtractoUseCase
from importaciones.application.fallar_importacion_use_case.dtos.fallar_importacion_input_dto import (
    FallarImportacionInputDTO,
)
from importaciones.application.fallar_importacion_use_case.i_fallar_importacion_use_case import (
    IFallarImportacionUseCase,
)
from importaciones.application.ports.i_lector_de_extractos import ILectorDeExtractos
from importaciones.application.ports.i_movimientos import IMovimientos
from importaciones.application.shared.dtos.importacion_output_dto import ImportacionOutputDTO
from importaciones.domain.enums.estado_importacion import E
from importaciones.domain.events.importacion_analizada_event import ImportacionAnalizadaEvent
from importaciones.domain.exceptions.extracto_no_valido_exception import ExtractoNoValidoException
from importaciones.domain.repositories.i_importacion_command_repository import IImportacionCommandRepository
from importaciones.domain.services.deduplicacion import clasificar, huellas
from importaciones.domain.services.saldos import comprobar_saldos


class AnalizarExtractoUseCase(IAnalizarExtractoUseCase):
    """Leer y clasificar cada fila, sin crear ningún movimiento. Lo pide una tarea. Si el archivo no se puede leer, la
    importación acaba en error (con IFallarImportacionUseCase: un use case puede usar otro, si se lo da el
    contenedor)."""

    def __init__(
        self,
        *,
        importaciones: IImportacionCommandRepository,
        lector: ILectorDeExtractos,
        movimientos: IMovimientos,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
        fallar: IFallarImportacionUseCase,
        margen: timedelta,
    ):
        self.importaciones, self.lector, self.movimientos = importaciones, lector, movimientos
        self.eventos, self.uow, self.fallar, self.margen = eventos, uow, fallar, margen

    def _fallar(self, importacion_id: int, mensaje: str) -> None:
        self.fallar.ejecutar(FallarImportacionInputDTO(importacion_id, mensaje))

    def ejecutar(self, entrada: AnalizarExtractoInputDTO) -> ImportacionOutputDTO | None:
        importacion_id = entrada.importacion_id
        if not self.importaciones.reclamar(importacion_id, de=E.PENDIENTE, a=E.ANALIZANDO):
            return None  # entrega duplicada: otro worker ya lo está analizando
        importacion = self.importaciones.por_id(importacion_id)
        try:
            lectura = self.lector.leer(self.importaciones.leer_archivo(importacion), importacion.formato)
        except ExtractoNoValidoException as e:
            self._fallar(importacion_id, str(e.mensaje))
            return None
        if not lectura.filas:
            self._fallar(importacion_id, "No se ha encontrado ningún movimiento en el archivo.")
            return None
        comprobar_saldos(lectura)

        cuenta = importacion.cuenta_id
        de_las_filas = huellas(cuenta, lectura.filas)
        fechas = [f.fecha for f in lectura.filas]
        filas = clasificar(
            lectura.filas,
            de_las_filas,
            existentes=self.movimientos.huellas_existentes(cuenta, de_las_filas),
            candidatos=self.movimientos.candidatos(cuenta, min(fechas) - self.margen, max(fechas) + self.margen),
            margen=self.margen,
        )
        with self.uow:
            self.importaciones.crear_filas(importacion_id, filas)
            importacion.analizada(filas, lectura.avisos)
            self.importaciones.guardar(importacion)
            self.eventos.publicar(ImportacionAnalizadaEvent(importacion_id))
        return ImportacionOutputDTO.desde_bo(importacion)
