# importaciones/application/subir_extracto_use_case/subir_extracto_use_case.py (módulos 75 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from importaciones.application.ports.i_movimientos import IMovimientos
from importaciones.application.shared.dtos.importacion_output_dto import ImportacionOutputDTO
from importaciones.application.subir_extracto_use_case.dtos.subir_extracto_input_dto import SubirExtractoInputDTO
from importaciones.application.subir_extracto_use_case.i_subir_extracto_use_case import ISubirExtractoUseCase
from importaciones.domain.bo.importacion import Importacion
from importaciones.domain.events.extracto_subido_event import ExtractoSubidoEvent
from importaciones.domain.exceptions.cuenta_no_encontrada_exception import CuentaNoEncontradaException
from importaciones.domain.repositories.i_importacion_command_repository import IImportacionCommandRepository


class SubirExtractoUseCase(ISubirExtractoUseCase):
    rol_minimo = Rol.MIEMBRO

    def __init__(
        self,
        *,
        importaciones: IImportacionCommandRepository,
        movimientos: IMovimientos,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.importaciones, self.movimientos, self.eventos, self.uow = importaciones, movimientos, eventos, uow

    def ejecutar(self, entrada: SubirExtractoInputDTO) -> ImportacionOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        importacion = Importacion(
            hogar_id=entrada.hogar_id,
            cuenta_id=entrada.cuenta_id,
            subido_por_id=entrada.actor.usuario_id,
            nombre_original=entrada.nombre_original[:200],
            formato=entrada.formato,
            huella_archivo=entrada.huella_archivo,
        )
        with self.uow:
            if not self.movimientos.cuenta_del_hogar(entrada.hogar_id, entrada.cuenta_id):
                raise CuentaNoEncontradaException()
            self.importaciones.crear(importacion, entrada.contenido)
            self.eventos.publicar(ExtractoSubidoEvent(importacion.id))
        return ImportacionOutputDTO.desde_bo(importacion)
