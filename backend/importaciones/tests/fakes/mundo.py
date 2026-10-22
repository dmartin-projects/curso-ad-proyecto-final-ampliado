"""Todos los fakes de las importaciones y los use cases montados con ellos: lo que hace
infrastructure/container.py, en memoria (módulo 88). Contract tests: tests/infrastructure/database/repositories/ y
tests/infrastructure/finanzas/.
"""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from core.tests.fakes.auditoria_fake import AuditoriaFake
from core.tests.fakes.publicador_eventos_fake import PublicadorEventosFake
from core.tests.fakes.reloj_fake import RelojFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake
from importaciones.application.analizar_extracto_use_case.analizar_extracto_use_case import AnalizarExtractoUseCase
from importaciones.application.analizar_extracto_use_case.dtos.analizar_extracto_input_dto import (
    AnalizarExtractoInputDTO,
)
from importaciones.application.confirmar_importacion_use_case.confirmar_importacion_use_case import (
    ConfirmarImportacionUseCase,
)
from importaciones.application.deshacer_importacion_use_case.deshacer_importacion_use_case import (
    DeshacerImportacionUseCase,
)
from importaciones.application.fallar_importacion_use_case.fallar_importacion_use_case import FallarImportacionUseCase
from importaciones.application.finalizar_importacion_use_case.finalizar_importacion_use_case import (
    FinalizarImportacionUseCase,
)
from importaciones.application.importar_lote_use_case.importar_lote_use_case import ImportarLoteUseCase
from importaciones.application.subir_extracto_use_case.subir_extracto_use_case import SubirExtractoUseCase
from importaciones.domain.bo.importacion import Importacion
from importaciones.domain.enums.estado_importacion import EstadoImportacion
from importaciones.domain.vo.fila_leida import FilaLeida
from importaciones.domain.vo.lectura import Lectura
from importaciones.tests.fakes.importacion_command_repository_fake import ImportacionCommandRepositoryFake
from importaciones.tests.fakes.lector_de_extractos_fake import LectorDeExtractosFake
from importaciones.tests.fakes.movimientos_fake import MovimientosFake

AHORA = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)
HOGAR, OTRO_HOGAR = 1, 2


def actor(rol: Rol = Rol.MIEMBRO, usuario_id: int = 7) -> Actor:
    return Actor(usuario_id=usuario_id, rol=rol)


class Mundo:
    def __init__(self, lectura=None):
        self.importaciones, self.lector = ImportacionCommandRepositoryFake(), LectorDeExtractosFake(lectura)
        self.movimientos = MovimientosFake((HOGAR, 10), (OTRO_HOGAR, 20))
        self.auditoria, self.eventos = AuditoriaFake(), PublicadorEventosFake()
        self.uow = UnidadDeTrabajoFake(self.importaciones, self.movimientos, self.auditoria, self.eventos)
        comun = {"importaciones": self.importaciones, "eventos": self.eventos, "uow": self.uow}
        reloj = {"reloj": RelojFake(AHORA.date(), AHORA)}
        self.subir = SubirExtractoUseCase(movimientos=self.movimientos, **comun)
        self.fallar = FallarImportacionUseCase(**comun, **reloj)
        self.analizar = AnalizarExtractoUseCase(
            lector=self.lector, movimientos=self.movimientos, fallar=self.fallar, margen=timedelta(days=3), **comun
        )
        self.confirmar = ConfirmarImportacionUseCase(**comun)
        self.importar_lote = ImportarLoteUseCase(movimientos=self.movimientos, **comun)
        self.finalizar = FinalizarImportacionUseCase(**comun, **reloj)
        self.deshacer = DeshacerImportacionUseCase(
            importaciones=self.importaciones, movimientos=self.movimientos, auditoria=self.auditoria, uow=self.uow
        )

    def importacion(self, estado=EstadoImportacion.PENDIENTE, hogar_id=HOGAR) -> Importacion:
        i = Importacion(
            hogar_id=hogar_id,
            cuenta_id=10,
            nombre_original="x.csv",
            formato="csv",
            huella_archivo=f"h{len(self.importaciones.todos())}",
            subido_por_id=7,
            estado=estado,
        )
        self.importaciones.crear(i, b"csv")
        return i


# ── Datos de partida de los tests de los use cases ──
def lectura(*filas) -> Lectura:
    return Lectura([FilaLeida(i, date(2026, 10, d), c, Decimal(imp)) for i, (d, c, imp) in enumerate(filas, start=1)])


EXTRACTO = lectura((1, "MERCADONA", "-45.30"), (2, "NOMINA", "2100.00"), (5, "CAFE", "-1.50"), (5, "CAFE", "-1.50"))


def preparada(mundo, a_mano=True):
    """Un extracto analizado (vista previa) con un gasto apuntado a mano el día 2 por el mismo importe que el súper."""
    if a_mano:
        mundo.movimientos.nuevo(10, date(2026, 10, 2), Decimal("-45.30"))
    imp = mundo.importacion()
    mundo.analizar.ejecutar(AnalizarExtractoInputDTO(imp.id))
    return imp
