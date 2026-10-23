# usuarios/application/desactivar_mfa_use_case/desactivar_mfa_use_case.py — quitar la verificación en dos pasos (módulo 92)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.desactivar_mfa_use_case.dtos.desactivar_mfa_input_dto import DesactivarMfaInputDTO
from usuarios.application.desactivar_mfa_use_case.i_desactivar_mfa_use_case import IDesactivarMfaUseCase
from usuarios.application.ports.i_codigos_de_recuperacion import ICodigosDeRecuperacion
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.repositories.i_segundo_factor_command_repository import ISegundoFactorCommandRepository


class DesactivarMfaUseCase(IDesactivarMfaUseCase):
    def __init__(
        self,
        *,
        segundos: ISegundoFactorCommandRepository,
        codigos: ICodigosDeRecuperacion,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.segundos, self.codigos, self.eventos, self.uow = segundos, codigos, eventos, uow

    def ejecutar(self, entrada: DesactivarMfaInputDTO) -> None:
        with self.uow:
            segundo = self.segundos.de(entrada.usuario_id, bloquear=True)
            segundo.desactivar()  # MfaNoActivoException
            self.segundos.guardar(segundo)
            self.codigos.borrar(entrada.usuario_id)
            self.eventos.publicar(SeguridadCambiadaEvent(entrada.usuario_id, "mfa_desactivado"))
