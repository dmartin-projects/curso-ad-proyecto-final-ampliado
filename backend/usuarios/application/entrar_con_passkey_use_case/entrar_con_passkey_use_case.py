# usuarios/application/entrar_con_passkey_use_case/entrar_con_passkey_use_case.py — entrar sin contraseña (discoverable credentials) (módulo 92)
import secrets

from usuarios.application.entrar_con_passkey_use_case.dtos.entrar_con_passkey_input_dto import EntrarConPasskeyInputDTO
from usuarios.application.entrar_con_passkey_use_case.i_entrar_con_passkey_use_case import IEntrarConPasskeyUseCase
from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.application.iniciar_sesion_use_case.i_iniciar_sesion_use_case import IIniciarSesionUseCase
from usuarios.application.ports.i_retos import IRetos
from usuarios.application.ports.i_webauthn import IWebAuthn
from usuarios.application.shared.dtos.segundo_factor_pendiente_output_dto import SegundoFactorPendienteOutputDTO
from usuarios.application.shared.dtos.sesion_abierta_output_dto import SesionAbiertaOutputDTO
from usuarios.domain.enums.factor import Factor
from usuarios.domain.exceptions.passkey_no_valida_exception import PasskeyNoValidaException
from usuarios.domain.repositories.i_passkey_command_repository import IPasskeyCommandRepository


class EntrarConPasskeyUseCase(IEntrarConPasskeyUseCase):
    """Sin contraseña (discoverable credentials): el autenticador dice de quién es la passkey (userHandle) y Gastos
    comprueba que la firma es de la clave pública que tiene guardada para ella."""

    def __init__(
        self,
        *,
        passkeys: IPasskeyCommandRepository,
        webauthn: IWebAuthn,
        retos: IRetos,
        inicio: IIniciarSesionUseCase,
    ):
        self.passkeys, self.webauthn, self.retos, self.inicio = passkeys, webauthn, retos, inicio

    def ejecutar(self, entrada: EntrarConPasskeyInputDTO) -> SesionAbiertaOutputDTO | SegundoFactorPendienteOutputDTO:
        challenge = self.retos.consumir(f"entrar:{entrada.clave}") if entrada.clave else None
        credencial_id, manija = self.webauthn.credencial(entrada.respuesta)
        passkey = self.passkeys.por_credencial(credencial_id)
        if challenge is None or passkey is None:
            raise PasskeyNoValidaException()
        # El userHandle que manda el autenticador tiene que ser el de la cuenta dueña de esa credencial
        if manija is None or not secrets.compare_digest(manija, self.passkeys.manija(passkey.usuario_id)):
            raise PasskeyNoValidaException()
        firma = self.webauthn.comprobar_entrada(entrada.respuesta, challenge, passkey, exigir_verificacion=True)
        passkey.contador, passkey.sincronizada = firma.contador, firma.sincronizada
        self.passkeys.guardar(passkey)
        return self.inicio.ejecutar(
            IniciarSesionInputDTO(passkey.usuario_id, Factor.PASSKEY, entrada.canal, entrada.contexto,
                                  passkey_sincronizada=firma.sincronizada)
        )  # fmt: skip
