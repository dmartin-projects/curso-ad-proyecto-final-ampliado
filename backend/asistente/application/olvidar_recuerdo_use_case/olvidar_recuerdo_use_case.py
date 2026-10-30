# asistente/application/olvidar_recuerdo_use_case/olvidar_recuerdo_use_case.py (módulo 99)
from asistente.application.olvidar_recuerdo_use_case.dtos.olvidar_recuerdo_input_dto import OlvidarRecuerdoInputDTO
from asistente.application.olvidar_recuerdo_use_case.i_olvidar_recuerdo_use_case import IOlvidarRecuerdoUseCase
from asistente.domain.repositories.i_recuerdo_command_repository import IRecuerdoCommandRepository
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol


class OlvidarRecuerdoUseCase(IOlvidarRecuerdoUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, recuerdos: IRecuerdoCommandRepository, uow: IUnidadDeTrabajo):
        self.recuerdos, self.uow = recuerdos, uow

    def ejecutar(self, entrada: OlvidarRecuerdoInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            recuerdo = self.recuerdos.obtener(entrada.actor.usuario_id, entrada.hogar_id, entrada.recuerdo_id)
            self.recuerdos.eliminar(recuerdo)
