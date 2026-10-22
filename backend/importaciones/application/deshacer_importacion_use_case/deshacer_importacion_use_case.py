# importaciones/application/deshacer_importacion_use_case/deshacer_importacion_use_case.py (módulos 75 y 88)
from core.application.ports.i_auditoria import IAuditoria
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.accion import Accion as AccionAuditoria
from core.domain.enums.rol import Rol
from importaciones.application.deshacer_importacion_use_case.dtos.deshacer_importacion_input_dto import (
    DeshacerImportacionInputDTO,
)
from importaciones.application.deshacer_importacion_use_case.i_deshacer_importacion_use_case import (
    IDeshacerImportacionUseCase,
)
from importaciones.application.ports.i_movimientos import IMovimientos
from importaciones.application.shared.dtos.importacion_output_dto import ImportacionOutputDTO
from importaciones.domain.enums.accion import Accion
from importaciones.domain.repositories.i_importacion_command_repository import IImportacionCommandRepository


class DeshacerImportacionUseCase(IDeshacerImportacionUseCase):
    """Borra lo que creó la importación y devuelve los gastos conciliados a como estaban.

    Los movimientos los borra finanzas (con su auditoría y sus tombstones) y la importación se audita, la deshaga
    un admin del hogar o el personal de soporte: los dos llaman a este use case.
    """

    rol_minimo = Rol.ADMIN

    def __init__(
        self,
        *,
        importaciones: IImportacionCommandRepository,
        movimientos: IMovimientos,
        auditoria: IAuditoria,
        uow: IUnidadDeTrabajo,
    ):
        self.importaciones, self.movimientos, self.auditoria, self.uow = importaciones, movimientos, auditoria, uow

    def ejecutar(self, entrada: DeshacerImportacionInputDTO) -> ImportacionOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            importacion = self.importaciones.obtener(entrada.hogar_id, entrada.importacion_id, bloquear=True)
            antes = importacion.instantanea()
            importacion.deshacer()
            comun = {"hogar_id": entrada.hogar_id, "actor": entrada.actor}
            self.movimientos.eliminar(**comun, ids=self.importaciones.movimientos(importacion.id, Accion.CREAR))
            self.movimientos.desconciliar(**comun, ids=self.importaciones.movimientos(importacion.id, Accion.CONCILIAR))
            self.importaciones.guardar(importacion)
            self.auditoria.registrar(AccionAuditoria.MODIFICAR, importacion, entrada.actor.usuario_id, antes=antes)
        return ImportacionOutputDTO.desde_bo(importacion)
