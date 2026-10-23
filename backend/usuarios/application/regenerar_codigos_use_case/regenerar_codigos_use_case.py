# usuarios/application/regenerar_codigos_use_case/regenerar_codigos_use_case.py — códigos de recuperación nuevos (módulo 92, ejercicio 2)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.ports.i_codigos_de_recuperacion import ICodigosDeRecuperacion
from usuarios.application.regenerar_codigos_use_case.dtos.regenerar_codigos_input_dto import RegenerarCodigosInputDTO
from usuarios.application.regenerar_codigos_use_case.i_regenerar_codigos_use_case import IRegenerarCodigosUseCase
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.mfa_no_activo_exception import MfaNoActivoException
from usuarios.domain.repositories.i_segundo_factor_command_repository import ISegundoFactorCommandRepository


class RegenerarCodigosUseCase(IRegenerarCodigosUseCase):
    """Ejercicio 2: diez códigos nuevos; los anteriores (los que queden) dejan de valer. Solo con el MFA activo."""

    def __init__(
        self,
        *,
        segundos: ISegundoFactorCommandRepository,
        codigos: ICodigosDeRecuperacion,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.segundos, self.codigos, self.eventos, self.uow = segundos, codigos, eventos, uow

    def ejecutar(self, entrada: RegenerarCodigosInputDTO) -> list[str]:
        with self.uow:
            if not self.segundos.de(entrada.usuario_id, bloquear=True).activo:
                raise MfaNoActivoException()
            codigos = self.codigos.generar(entrada.usuario_id)
            self.eventos.publicar(SeguridadCambiadaEvent(entrada.usuario_id, "codigos_regenerados"))
        return codigos
