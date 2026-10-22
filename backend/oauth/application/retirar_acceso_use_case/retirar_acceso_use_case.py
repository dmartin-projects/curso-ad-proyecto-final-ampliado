# oauth/application/retirar_acceso_use_case/retirar_acceso_use_case.py — retirar el acceso a una aplicación (ejercicio 1 del módulo 90)
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from oauth.application.retirar_acceso_use_case.dtos.retirar_acceso_input_dto import RetirarAccesoInputDTO
from oauth.application.retirar_acceso_use_case.i_retirar_acceso_use_case import IRetirarAccesoUseCase
from oauth.domain.exceptions.aplicacion_no_conectada_exception import AplicacionNoConectadaException
from oauth.domain.repositories.i_concesion_command_repository import IConcesionCommandRepository


class RetirarAccesoUseCase(IRetirarAccesoUseCase):
    """El usuario retira a una aplicación el acceso a su cuenta: sus tokens dejan de valer en ese instante (el
    refresh token y el access token; de nada serviría revocar solo el refresh y dejar 10 minutos de access)."""

    def __init__(self, *, concesiones: IConcesionCommandRepository, uow: IUnidadDeTrabajo):
        self.concesiones, self.uow = concesiones, uow

    def ejecutar(self, entrada: RetirarAccesoInputDTO) -> int:
        with self.uow:
            if not self.concesiones.tiene(entrada.usuario_id, entrada.client_id):
                raise AplicacionNoConectadaException()
            return self.concesiones.revocar(entrada.usuario_id, entrada.client_id)
