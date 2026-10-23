# usuarios/application/pedir_reto_use_case/pedir_reto_use_case.py — las opciones de navigator.credentials.get() de un ámbito (módulo 92)
from usuarios.application.pedir_reto_use_case.dtos.pedir_reto_input_dto import PedirRetoInputDTO
from usuarios.application.pedir_reto_use_case.i_pedir_reto_use_case import IPedirRetoUseCase
from usuarios.application.ports.i_retos import IRetos
from usuarios.application.ports.i_webauthn import IWebAuthn
from usuarios.domain.repositories.i_passkey_command_repository import IPasskeyCommandRepository


class PedirRetoUseCase(IPedirRetoUseCase):
    """Las opciones de navigator.credentials.get() para un ámbito. Con `usuario_id` (segundo paso, step-up), solo sus
    passkeys; sin él (entrar sin contraseña), ninguna: el autenticador ofrece las que tenga para este sitio.

    Los retos se guardan por `ambito`: el registro y el step-up, por usuario (ya tienen sesión); el segundo paso, por
    su login pendiente; entrar sin contraseña, por una cookie de ese navegador (todavía no se sabe quién es)."""

    def __init__(self, *, passkeys: IPasskeyCommandRepository, webauthn: IWebAuthn, retos: IRetos):
        self.passkeys, self.webauthn, self.retos = passkeys, webauthn, retos

    def ejecutar(self, entrada: PedirRetoInputDTO) -> dict:
        permitir = self.passkeys.de_usuario(entrada.usuario_id) if entrada.usuario_id is not None else []
        # Sin contraseña, la passkey es los dos factores: la verificación del usuario (huella, PIN) es obligatoria
        reto = self.webauthn.opciones_de_entrada(permitir=permitir, exigir_verificacion=entrada.usuario_id is None)
        self.retos.guardar(entrada.ambito, reto.challenge)
        return reto.opciones
