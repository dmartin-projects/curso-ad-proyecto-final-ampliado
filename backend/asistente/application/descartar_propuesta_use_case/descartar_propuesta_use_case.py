# asistente/application/descartar_propuesta_use_case/descartar_propuesta_use_case.py (módulo 97)
from asistente.application.descartar_propuesta_use_case.dtos.descartar_propuesta_input_dto import (
    DescartarPropuestaInputDTO,
)
from asistente.application.descartar_propuesta_use_case.i_descartar_propuesta_use_case import (
    IDescartarPropuestaUseCase,
)
from asistente.application.shared.dtos.propuesta_output_dto import PropuestaOutputDTO
from asistente.domain.repositories.i_propuesta_command_repository import IPropuestaCommandRepository
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol


class DescartarPropuestaUseCase(IDescartarPropuestaUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, propuestas: IPropuestaCommandRepository, uow: IUnidadDeTrabajo):
        self.propuestas, self.uow = propuestas, uow

    def ejecutar(self, entrada: DescartarPropuestaInputDTO) -> PropuestaOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            propuesta = self.propuestas.obtener(
                entrada.actor.usuario_id, entrada.hogar_id, entrada.propuesta_id, bloquear=True
            )
            propuesta.descartar()
            self.propuestas.guardar(propuesta)
        return PropuestaOutputDTO.desde_bo(propuesta)
