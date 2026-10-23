# usuarios/application/confirmar_totp_use_case/confirmar_totp_use_case.py — el primer código bueno activa el MFA (módulo 92)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.confirmar_totp_use_case.dtos.confirmar_totp_input_dto import ConfirmarTotpInputDTO
from usuarios.application.confirmar_totp_use_case.i_confirmar_totp_use_case import IConfirmarTotpUseCase
from usuarios.application.ports.i_codigos_de_recuperacion import ICodigosDeRecuperacion
from usuarios.application.ports.i_totp import ITotp
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.codigo_no_valido_exception import CodigoNoValidoException
from usuarios.domain.repositories.i_segundo_factor_command_repository import ISegundoFactorCommandRepository


class ConfirmarTotpUseCase(IConfirmarTotpUseCase):
    """El primer código bueno activa el MFA y da los códigos de recuperación (se enseñan una vez)."""

    def __init__(
        self,
        *,
        segundos: ISegundoFactorCommandRepository,
        totp: ITotp,
        codigos: ICodigosDeRecuperacion,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
        reloj: IReloj,
    ):
        self.segundos, self.totp, self.codigos, self.eventos, self.uow, self.reloj = (
            segundos, totp, codigos, eventos, uow, reloj
        )  # fmt: skip

    def ejecutar(self, entrada: ConfirmarTotpInputDTO) -> list[str]:
        with self.uow:
            segundo = self.segundos.de(entrada.usuario_id, bloquear=True)
            codigo = "".join(entrada.codigo.split())
            paso = self.totp.paso(segundo.secreto, codigo, self.reloj.ahora()) if segundo.secreto else None
            if paso is None:
                raise CodigoNoValidoException()
            segundo.confirmar(paso)  # MfaYaActivoException
            self.segundos.guardar(segundo)
            codigos = self.codigos.generar(entrada.usuario_id)
            self.eventos.publicar(SeguridadCambiadaEvent(entrada.usuario_id, "mfa_activado"))
        return codigos
