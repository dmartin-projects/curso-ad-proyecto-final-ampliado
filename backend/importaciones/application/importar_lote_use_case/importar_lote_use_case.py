# importaciones/application/importar_lote_use_case/importar_lote_use_case.py (módulos 75 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.vo.actor import Actor
from importaciones.application.importar_lote_use_case.dtos.importar_lote_input_dto import ImportarLoteInputDTO
from importaciones.application.importar_lote_use_case.i_importar_lote_use_case import IImportarLoteUseCase
from importaciones.application.ports.i_movimientos import IMovimientos
from importaciones.domain.enums.accion import Accion
from importaciones.domain.enums.estado_importacion import E
from importaciones.domain.events.lote_importado_event import LoteImportadoEvent
from importaciones.domain.repositories.i_importacion_command_repository import IImportacionCommandRepository
from importaciones.domain.services.deduplicacion import repartir


class ImportarLoteUseCase(IImportarLoteUseCase):
    """Un lote de filas (lo pide una tarea del chord; varios lotes corren a la vez en distintos workers)."""

    def __init__(
        self,
        *,
        importaciones: IImportacionCommandRepository,
        movimientos: IMovimientos,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.importaciones, self.movimientos, self.eventos, self.uow = importaciones, movimientos, eventos, uow

    def ejecutar(self, entrada: ImportarLoteInputDTO) -> dict:
        importacion_id, fila_ids = entrada.importacion_id, entrada.fila_ids
        with self.uow:
            importacion = self.importaciones.por_id(importacion_id)
            if importacion.estado != E.IMPORTANDO:
                return {"omitido": True}
            filas = self.importaciones.filas_pendientes(importacion_id, fila_ids)
            ya = self.movimientos.huellas_existentes(importacion.cuenta_id, [f.huella for f in filas])
            duplicadas, a_conciliar, a_crear = repartir(filas, ya)
            # los movimientos, a nombre de quien subió el extracto; el proceso ya se autorizó al confirmar
            comun = {"hogar_id": importacion.hogar_id, "actor": Actor.sistema(en_nombre_de=importacion.subido_por_id)}

            conciliadas = self.movimientos.conciliar(
                **comun, huellas={f.coincide_con_id: f.huella for f in a_conciliar}
            )
            for fila in a_conciliar:
                if fila.coincide_con_id in conciliadas:  # el gasto apuntado a mano "absorbe" la fila del banco
                    fila.movimiento_id = fila.coincide_con_id
                else:  # ya tenía otra fila del banco, o ya no existe: la fila se importa como un movimiento nuevo
                    fila.accion = Accion.CREAR
                    a_crear.append(fila)
            a_crear.sort(key=lambda f: f.numero)
            ids = self.movimientos.apuntar(**comun, cuenta_id=importacion.cuenta_id, filas=a_crear)
            for fila, movimiento_id in zip(a_crear, ids, strict=True):
                fila.movimiento_id = movimiento_id

            self.importaciones.guardar_filas(filas)
            hechos = {"creados": len(a_crear), "conciliados": len(filas) - len(a_crear) - len(duplicadas)}
            self.importaciones.sumar(importacion_id, procesadas=len(fila_ids), duplicados=len(duplicadas), **hechos)
            self.eventos.publicar(LoteImportadoEvent(importacion_id))
        return hechos | {"duplicados": len(duplicadas)}
