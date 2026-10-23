# usuarios/application/empezar_totp_use_case/empezar_totp_use_case.py — un secreto TOTP nuevo, todavía sin activar (módulo 92)
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from usuarios.application.empezar_totp_use_case.dtos.alta_totp_output_dto import AltaTotpOutputDTO
from usuarios.application.empezar_totp_use_case.dtos.empezar_totp_input_dto import EmpezarTotpInputDTO
from usuarios.application.empezar_totp_use_case.i_empezar_totp_use_case import IEmpezarTotpUseCase
from usuarios.application.ports.i_codigo_qr import ICodigoQr
from usuarios.application.ports.i_totp import ITotp
from usuarios.domain.repositories.i_segundo_factor_command_repository import ISegundoFactorCommandRepository


class EmpezarTotpUseCase(IEmpezarTotpUseCase):
    """Un secreto nuevo, todavía sin activar: el MFA no cuenta hasta que la persona demuestra que su app genera bien
    los códigos (ConfirmarTotpUseCase). Así nadie se queda fuera por un QR mal escaneado."""

    def __init__(self, *, segundos: ISegundoFactorCommandRepository, totp: ITotp, qr: ICodigoQr, uow: IUnidadDeTrabajo):
        self.segundos, self.totp, self.qr, self.uow = segundos, totp, qr, uow

    def ejecutar(self, entrada: EmpezarTotpInputDTO) -> AltaTotpOutputDTO:
        with self.uow:
            segundo = self.segundos.de(entrada.usuario_id, bloquear=True)
            segundo.empezar(self.totp.nuevo_secreto())  # MfaYaActivoException
            self.segundos.guardar(segundo)
        uri = self.totp.uri(segundo.secreto, entrada.cuenta)
        return AltaTotpOutputDTO(segundo.secreto, uri, self.qr.svg(uri))
