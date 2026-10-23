# usuarios/application/shared/factores_de_cuenta.py — con qué puede completar una cuenta el segundo paso (módulo 92)
from usuarios.application.ports.i_codigos_de_recuperacion import ICodigosDeRecuperacion
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from usuarios.domain.repositories.i_passkey_command_repository import IPasskeyCommandRepository
from usuarios.domain.repositories.i_segundo_factor_command_repository import ISegundoFactorCommandRepository
from usuarios.domain.vo.factores_disponibles import FactoresDisponibles


class FactoresDeCuenta:
    """Lo que la pantalla del segundo paso (o la del step-up) puede ofrecer a una cuenta."""

    def __init__(
        self,
        *,
        cuentas: ICuentaCommandRepository,
        segundos: ISegundoFactorCommandRepository,
        codigos: ICodigosDeRecuperacion,
        passkeys: IPasskeyCommandRepository,
    ):
        self.cuentas, self.segundos, self.codigos, self.passkeys = cuentas, segundos, codigos, passkeys

    def de(self, usuario_id: int) -> FactoresDisponibles:
        return FactoresDisponibles(
            totp=self.segundos.de(usuario_id).activo,
            passkeys=bool(self.passkeys.de_usuario(usuario_id)),
            recuperacion=self.codigos.quedan(usuario_id) > 0,
            contrasena=self.cuentas.tiene_contrasena(usuario_id),
        )
