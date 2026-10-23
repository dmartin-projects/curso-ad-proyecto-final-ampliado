# usuarios/application/empezar_registro_passkey_use_case/empezar_registro_passkey_use_case.py — las opciones de navigator.credentials.create() (módulo 92)
from usuarios.application.empezar_registro_passkey_use_case.dtos.empezar_registro_passkey_input_dto import (
    EmpezarRegistroPasskeyInputDTO,
)
from usuarios.application.empezar_registro_passkey_use_case.i_empezar_registro_passkey_use_case import (
    IEmpezarRegistroPasskeyUseCase,
)
from usuarios.application.ports.i_retos import IRetos
from usuarios.application.ports.i_webauthn import IWebAuthn
from usuarios.domain.repositories.i_passkey_command_repository import IPasskeyCommandRepository


class EmpezarRegistroPasskeyUseCase(IEmpezarRegistroPasskeyUseCase):
    def __init__(self, *, passkeys: IPasskeyCommandRepository, webauthn: IWebAuthn, retos: IRetos):
        self.passkeys, self.webauthn, self.retos = passkeys, webauthn, retos

    def ejecutar(self, entrada: EmpezarRegistroPasskeyInputDTO) -> dict:
        reto = self.webauthn.opciones_de_registro(
            manija=self.passkeys.manija(entrada.usuario_id), cuenta=entrada.cuenta, nombre=entrada.nombre,
            excluir=[p.credencial_id for p in self.passkeys.de_usuario(entrada.usuario_id)],  # no registrar dos veces la misma
        )  # fmt: skip
        self.retos.guardar(f"registro:{entrada.usuario_id}", reto.challenge)
        return reto.opciones
